# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸 (Blueking) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at https://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from typing import Dict

from django.db import transaction, IntegrityError

from apps.api import BscpApi
from apps.exceptions import ApiResultError
from apps.gsekit.adapters.base.adapter import (
    BaseActivityManager,
    BaseChannelAdapters,
    BulkBaseActivityManager,
)
from apps.gsekit.adapters.bscp.exceptions import BscpErrorCode
from apps.gsekit.adapters.bscp.models import BscpApplication, BscpConfig
from apps.gsekit.configfile.models import (
    ConfigTemplate,
    ConfigTemplateBindingRelationship,
)
from apps.gsekit.job.models import Job, JobTask
from apps.gsekit.pipeline_plugins.components.collections.configfile import (
    BulkGenerateConfigComponent,
    GenerateConfigComponent,
)
from apps.utils.batch_request import request_multi_thread
from common.log import logger
from bamboo_engine.builder import Data, ServiceActivity, Var

from .pipeline_managers import ManagerFactory


class BscpAdapter(BaseChannelAdapters):
    """BSCP适配器"""

    BIZ_ID_TEMPLATE = "GSEKIT_{process_object_type}_{process_object_id}"

    PIPELINE_MANAGER_FACTORY = ManagerFactory

    @staticmethod
    def line_separator_to_bscp_file_format(line_separator):
        mapping = {
            ConfigTemplate.LineSeparator.CRLF: BscpConfig.FileFormat.WINDOWS,
            ConfigTemplate.LineSeparator.CR: BscpConfig.FileFormat.UNIX,
            ConfigTemplate.LineSeparator.LF: BscpConfig.FileFormat.UNIX,
        }
        return mapping.get(line_separator, BscpConfig.FileFormat.UNIX)

    def post_update_config_template(self, config_template: ConfigTemplate):
        self.update_config(config_template)

    def post_create_config_template_relation(self, relation: ConfigTemplateBindingRelationship):
        """创建绑定关系时需创建BSCP配置"""
        pass
        # 由于要支持文件名渲染，此处还不能确定文件名，因此改为在下发配置时创建bscp config
        # config_template = ConfigTemplate.objects.get(config_template_id=relation.config_template_id)
        # self.get_or_create_config(config_template, relation.process_object_type, relation.process_object_id)

    def post_delete_config_template_relation(self, relation: ConfigTemplateBindingRelationship):
        """删除绑定关系时需删除BSCP配置"""
        bscp_app = self.get_or_create_app(relation.bk_biz_id, relation.process_object_type, relation.process_object_id)
        self.delete_config(relation.config_template_id, bscp_app)

    def get_or_create_app(self, bk_biz_id: int, process_object_type: str, process_object_id: int) -> BscpApplication:
        """创建BSCP应用"""
        biz_name = self.BIZ_ID_TEMPLATE.format(
            process_object_type=process_object_type, process_object_id=process_object_id
        )
        with transaction.atomic():
            try:
                bscp_app = BscpApplication.objects.get(biz_id=bk_biz_id, biz_name=biz_name)
            except BscpApplication.DoesNotExist:
                logger.warning("{biz_name}对应的BSCP应用不存在，需创建".format(biz_name=biz_name))
                try:
                    app_id = BscpApi.create_app(
                        {
                            "biz_id": bk_biz_id,
                            "biz_name": biz_name,
                            "name": biz_name,
                            "deploy_type": BscpApplication.DeployType.PROCESS,
                        }
                    )["app_id"]
                except ApiResultError as error:
                    if error.code == BscpErrorCode.BSCP_OBJ_ALREADY_EXIST:
                        logger.warning("{biz_name}对应的BSCP应用已存在，无需重复创建".format(biz_name=biz_name))
                        app_id = error.data["app_id"]
                    else:
                        raise error

                bscp_app = BscpApplication.objects.create(
                    biz_id=bk_biz_id,
                    biz_name=biz_name,
                    app_id=app_id,
                    process_object_type=process_object_type,
                    process_object_id=process_object_id,
                )
        return bscp_app

    def get_or_create_config(
        self,
        config_template: ConfigTemplate,
        process_object_type: str = None,
        process_object_id: int = None,
        file_name: str = None,
        path: str = None,
        bscp_app: BscpApplication = None,
    ) -> BscpConfig:
        """创建BSCP配置"""
        config_template_id = config_template.config_template_id
        if bscp_app is None:
            bscp_app = self.get_or_create_app(
                config_template.bk_biz_id, process_object_type=process_object_type, process_object_id=process_object_id
            )
        try:
            bscp_config = BscpConfig.objects.get(
                config_template_id=config_template_id, app_id=bscp_app.app_id, file_name=file_name, path=path
            )
        except BscpConfig.DoesNotExist:
            logger.info("配置模板[{config_template_id}]对应的BSCP配置不存在，需创建".format(config_template_id=config_template_id))
            params = {
                "biz_id": bscp_app.biz_id,
                "app_id": bscp_app.app_id,
                "name": file_name or config_template.file_name,
                "fpath": path or config_template.abs_path,
                "user": config_template.owner,
                "user_group": config_template.group,
                "file_privilege": config_template.filemode,
                "file_format": self.line_separator_to_bscp_file_format(config_template.line_separator),
                "file_mode": BscpConfig.FileMode.TEMPLATE,
            }
            try:
                cfg_id = BscpApi.create_config(params)["cfg_id"]
            except ApiResultError as error:
                if error.code == BscpErrorCode.BSCP_OBJ_ALREADY_EXIST:
                    logger.warning(
                        "配置模板[{config_template_id}]对应的BSCP应用已存在，需更新信息".format(config_template_id=config_template_id)
                    )
                    cfg_id = error.data["cfg_id"]
                    params["cfg_id"] = cfg_id
                    BscpApi.update_config(params)
                    BscpConfig.objects.filter(cfg_id=cfg_id).update(
                        app_id=bscp_app.app_id, config_template_id=config_template_id, file_name=file_name, path=path
                    )
                else:
                    raise error
            try:
                bscp_config = BscpConfig.objects.create(
                    app_id=bscp_app.app_id,
                    config_template_id=config_template_id,
                    cfg_id=cfg_id,
                    file_name=file_name,
                    path=path,
                )
            except IntegrityError:
                bscp_config = BscpConfig.objects.get(
                    app_id=bscp_app.app_id,
                    config_template_id=config_template_id,
                    cfg_id=cfg_id,
                    file_name=file_name,
                    path=path,
                )
        return bscp_config

    def update_config(self, config_template: ConfigTemplate):
        """更新BSCP配置"""
        bscp_configs = BscpConfig.objects.filter(config_template_id=config_template.config_template_id)
        bscp_app_ids = bscp_configs.values_list("app_id", flat=True)
        bscp_apps = BscpApplication.objects.filter(app_id__in=bscp_app_ids)
        bscp_app_map = {bscp_app.app_id: bscp_app for bscp_app in bscp_apps}
        params_list = []
        for bscp_config in bscp_configs:
            bscp_app = bscp_app_map[bscp_config.app_id]
            params_list.append(
                {
                    "params": {
                        "cfg_id": bscp_config.cfg_id,
                        "biz_id": bscp_app.biz_id,
                        "app_id": bscp_app.app_id,
                        "name": config_template.file_name,
                        # "fpath": "/",
                        "fpath": config_template.abs_path,
                        "user": config_template.owner,
                        "user_group": config_template.group,
                        "file_privilege": config_template.filemode,
                        "file_format": self.line_separator_to_bscp_file_format(config_template.line_separator),
                        "file_mode": BscpConfig.FileMode.TEMPLATE,
                    }
                }
            )
        try:
            request_multi_thread(BscpApi.update_config, params_list, get_data=lambda x: [])
        except ApiResultError as err:
            if err.code == BscpErrorCode.BSCP_OBJ_ALREADY_EXIST:
                logger.info(err.message)

    def delete_config(self, config_template_id: int, bscp_app: BscpApplication):
        bscp_configs = BscpConfig.objects.filter(config_template_id=config_template_id, app_id=bscp_app.app_id,)
        for bscp_config in bscp_configs:
            with transaction.atomic():
                try:
                    BscpApi.delete_config(
                        {"biz_id": bscp_app.biz_id, "app_id": bscp_app.app_id, "cfg_id": bscp_config.cfg_id}
                    )
                except ApiResultError as err:
                    # BSCP配置不存在时忽略，其他情况继续抛出异常
                    if err.code != BscpErrorCode.CFG_DOSE_NOT_EXIST:
                        raise err
                bscp_config.delete()

    class GenerateConfigActivityManager(BaseActivityManager):
        def generate_activities(self, global_pipeline_data: Data = None) -> Dict:
            return {
                "activities": [self.generate_config(), self.upload_content()],
                "sub_process_data": None,
            }

        def generate_config(self):
            act = ServiceActivity(component_code=GenerateConfigComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.job.created_by)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

        def upload_content(self):
            from apps.gsekit.pipeline_plugins.components.collections.bscp import UploadContentComponent

            act = ServiceActivity(component_code=UploadContentComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

    class BulkGenerateConfigActivityManager(BulkBaseActivityManager):
        def bulk_generate_activities(self, global_pipeline_data: Data = None) -> Dict:
            return {
                "activities": [self.bulk_generate_config(), self.bulk_upload_content()],
                "sub_process_data": None,
            }

        def bulk_upload_content(self):
            from apps.gsekit.pipeline_plugins.components.collections.bscp import BulkUploadContentComponent

            act = ServiceActivity(component_code=BulkUploadContentComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

        def bulk_generate_config(self):
            act = ServiceActivity(component_code=BulkGenerateConfigComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.job.created_by)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

    class ReleaseConfigActivityManager(BaseActivityManager):
        def __init__(self, job: Job, job_task: JobTask, *args, **kwargs):
            self.job = job
            self.job_task = job_task
            self.job_task_ids = kwargs["job_task_ids"]
            super().__init__(job, job_task, *args, **kwargs)

        def generate_activities(self, global_pipeline_data: Data = None) -> Dict:
            return {
                "activities": [self.commit_and_release_config()],
                "sub_process_data": None,
            }

        def commit_and_release_config(self):
            from apps.gsekit.pipeline_plugins.components.collections.bscp import CommitAndReleaseComponent

            act = ServiceActivity(component_code=CommitAndReleaseComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            return act

        def set_config_released(self):
            from apps.gsekit.pipeline_plugins.components.collections.configfile import SetConfigReleasedComponent

            act = ServiceActivity(component_code=SetConfigReleasedComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            return act
