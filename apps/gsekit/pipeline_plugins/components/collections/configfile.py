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
import datetime
import base64
import hashlib
import itertools
import logging
import shlex
from asyncio import sleep
from collections import defaultdict
from typing import List, Dict

from django.db import OperationalError
from django.utils.translation import ugettext as _

from apps.api import JobApi, EsbApi
from apps.exceptions import ApiResultError
from apps.gsekit import constants
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.configfile.exceptions import NoActiveConfigVersionException, ProcessDoseNotBindTemplate
from apps.gsekit.configfile.handlers.config_version import ConfigVersionHandler
from apps.gsekit.configfile.models import (
    ConfigInstance,
    ConfigTemplate,
    ConfigTemplateVersion,
)
from apps.gsekit.job.models import JobStatus, JobTask
from apps.gsekit.meta.models import GlobalSettings
from apps.gsekit.pipeline_plugins.components.collections.base import (
    JobTaskBaseService,
    MultiJobTaskBaseService,
    JOB_POLLING_INTERVAL as POLLING_INTERVAL,
)
from apps.gsekit.pipeline_plugins.exceptions import JobApiException
from apps.gsekit.constants import JOB_TASK_OS_TYPE
from apps.utils.batch_request import request_multi_thread
from apps.utils.mako_utils.render import mako_render
from pipeline.component_framework.component import Component
from pipeline.core.flow import StaticIntervalGenerator, Service

logger = logging.getLogger("app")


class GenerateConfigService(JobTaskBaseService):
    """
    生成配置
    """

    def _execute(self, data, parent_data):
        job_task = data.get_one_of_inputs("job_task")
        bk_username = data.get_one_of_inputs("bk_username")
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        inst_id = job_task.extra_data["inst_id"]

        config_template_ids = job_task.get_job_task_config_template_ids()

        context = ConfigVersionHandler.get_process_context(
            job_task.extra_data["process_info"],
            bk_biz_id,
            inst_id=inst_id,
            local_inst_id=job_task.extra_data["local_inst_id"],
        )

        to_be_created_config_instances = []
        config_template_id_obj_map = {}

        for config_template in ConfigTemplate.objects.filter(config_template_id__in=config_template_ids):
            config_template_id_obj_map[config_template.config_template_id] = config_template
            latest_config_version = ConfigTemplateVersion.get_latest_version_mapping(
                [config_template.config_template_id]
            ).get(config_template.config_template_id)
            if not latest_config_version:
                raise NoActiveConfigVersionException(template_name=config_template.template_name)

            content = ConfigVersionHandler.fill_template_dependencies(bk_biz_id, latest_config_version.content)
            rendered_content = mako_render(content, context)
            path = mako_render(config_template.abs_path, context)

            sha256 = hashlib.sha256()
            sha256.update(rendered_content.encode())
            sha256sum = sha256.hexdigest()
            to_be_created_config_instances.append(
                ConfigInstance(
                    config_version_id=latest_config_version.config_version_id,
                    config_template_id=config_template.config_template_id,
                    bk_process_id=job_task.bk_process_id,
                    content=rendered_content,
                    sha256=sha256sum,
                    expression="TODO",
                    is_latest=True,
                    inst_id=inst_id,
                    created_by=bk_username,
                    path=path,
                )
            )

        # 设置老的配置实例为非最新
        try:
            ConfigInstance.objects.filter(
                config_template_id__in=config_template_ids,
                bk_process_id=job_task.bk_process_id,
                inst_id=inst_id,
            ).update(is_latest=False)
        except OperationalError as err:
            logger.info(f"{err}: update {config_template_ids}--{job_task.bk_process_id}--{inst_id} set is_latest=false")
            raise err
        ConfigInstance.objects.bulk_create(to_be_created_config_instances)

        # 回写生成的模板实例
        new_config_instances = ConfigInstance.objects.filter(
            config_template_id__in=config_template_ids, bk_process_id=job_task.bk_process_id, is_latest=True
        ).values("id", "config_template_id", "sha256")
        config_instances = []
        for config_instance in new_config_instances:
            config_instance.update(
                template_name=config_template_id_obj_map[config_instance["config_template_id"]].template_name,
                file_name=config_template_id_obj_map[config_instance["config_template_id"]].file_name,
            )
            config_instances.append(config_instance)

        job_extra_data = {"config_instances": config_instances}
        return self.return_data(result=True, job_extra_data=job_extra_data)

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="bk_username", key="bk_username", required=True),
            JobTaskBaseService.InputItem(name="bk_biz_id", key="bk_biz_id", required=True),
        ]


class ReleaseConfigService(JobTaskBaseService):
    """
    下发配置
    """

    @staticmethod
    def release_by_job(job_task, bk_biz_id):
        host_info = job_task.extra_data["process_info"]["host"]

        config_template_ids = job_task.get_job_task_config_template_ids()
        for config_template in ConfigTemplate.objects.filter(config_template_id__in=config_template_ids):
            # 查询最新的配置版本
            latest_config_version = ConfigTemplateVersion.objects.filter(
                config_template_id=config_template.config_template_id, is_active=True
            ).first()
            if not latest_config_version:
                logger.warning(f"配置模板ID：[{config_template.config_template_id}] 没有可用的版本")
                continue

            # 根据配置模板、最新版本、进程实例查询最新的配置实例
            latest_config_instance = ConfigInstance.objects.filter(
                config_template_id=config_template.config_template_id,
                config_version_id=latest_config_version.config_version_id,
                bk_process_id=job_task.bk_process_id,
            ).first()
            if not latest_config_instance:
                logger.warning(f"配置模板ID：[{config_template.config_template_id}] 未使用最新版本生成配置实例")
                continue

            # 把最新的配置实例分发到机器上
            script_content = """#!/bin/bash
        # 创建文件目录
        mkdir -p -- `dirname {abs_path}`
        # 重定向文件内容
        printf "%q" {content} | xargs echo -ne > {abs_path}
        # 修改文件权限和所属
        chmod {file_mod} {abs_path}
        chown {owner}:{group} {abs_path}
        ls -l {abs_path}
        md5sum {abs_path}
        cat {abs_path}
                    """.format(
                content=shlex.quote(latest_config_instance.content),
                abs_path="{abs_path}/{file_name}".format(
                    abs_path=config_template.abs_path, file_name=config_template.file_name
                ),
                file_mod=config_template.filemode,
                owner=config_template.owner,
                group=config_template.group,
            )
            JobApi.fast_execute_script(
                {
                    "bk_biz_id": bk_biz_id,
                    "ip_list": [{"ip": host_info["bk_host_innerip"], "bk_cloud_id": host_info["bk_cloud_id"]}],
                    "task_name": _("[gsekit]下发配置_{bk_process_id}_{config_instance_id}").format(
                        bk_process_id=job_task.bk_process_id, config_instance_id=latest_config_instance.id
                    ),
                    "script_timeout": 300,
                    "script_type": 1,
                    "account": "root",
                    "script_content": base64.b64encode(script_content.encode()).decode(),
                }
            )

    def _execute(self, data, parent_data):
        job_task = data.get_one_of_inputs("job_task")
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        self.release_by_job(job_task, bk_biz_id)
        return self.return_data(result=True)


class SetConfigReleasedService(JobTaskBaseService):
    """
    设置下发状态
    """

    def _execute(self, data, parent_data):
        job_task = data.get_one_of_inputs("job_task")
        config_instance_ids = job_task.get_job_task_config_instance_ids()
        ConfigInstance.objects.filter(id__in=config_instance_ids).update(is_released=True)
        return self.return_data(result=True)


class GenerateConfigComponent(Component):
    name = "GenerateConfigComponent"
    code = "generate_config"
    bound_service = GenerateConfigService


class ReleaseConfigComponent(Component):
    name = "ReleaseConfigComponent"
    code = "release_config"
    bound_service = ReleaseConfigService


class SetConfigReleasedComponent(Component):
    name = "SetConfigReleaseService"
    code = "set_config_released"
    bound_service = SetConfigReleasedService


class BulkGenerateConfigService(MultiJobTaskBaseService):
    """
    生成配置
    """

    def _execute(self, data, parent_data):
        job_tasks = data.get_one_of_inputs("job_tasks")
        bk_username = data.get_one_of_inputs("bk_username")
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        bk_set_env = job_tasks[0].extra_data["process_info"]["set"]["bk_set_env"]

        job_tasks_config_template_ids_map = JobTask.get_job_tasks_config_template_ids_map(job_tasks)
        all_config_template_ids = set(itertools.chain.from_iterable(job_tasks_config_template_ids_map.values()))
        latest_config_version_map = ConfigTemplateVersion.get_latest_version_mapping(all_config_template_ids)
        config_template_id_obj_map = {
            config_template.config_template_id: config_template
            for config_template in ConfigTemplate.objects.filter(config_template_id__in=all_config_template_ids)
        }
        to_be_created_config_instances = []
        to_be_update_config_instances = defaultdict(list)
        cc_context = ConfigVersionHandler.get_cc_context(bk_biz_id, bk_set_env)
        biz_global_variables = CMDBHandler(bk_biz_id=bk_biz_id).biz_global_variables()
        xpath_cache = {}
        job_task_tpl_sha256_map = defaultdict(lambda: defaultdict(list))
        all_config_template_ids = set()
        all_process_ids = set()
        job_task_id_obj_map = {}
        for job_task in job_tasks:
            all_process_ids.add(job_task.bk_process_id)
            job_task_id_obj_map[job_task.id] = job_task
            inst_id = job_task.extra_data["inst_id"]

            config_template_ids = job_tasks_config_template_ids_map.get(job_task.id, [])

            context = ConfigVersionHandler.get_process_context(
                job_task.extra_data["process_info"],
                bk_biz_id,
                inst_id=inst_id,
                local_inst_id=job_task.extra_data["local_inst_id"],
                cc_context=cc_context,
                biz_global_variables=biz_global_variables,
                xpath_cache=xpath_cache,
            )
            inst_to_be_created_config_instances = []
            for config_template_id in config_template_ids:
                all_config_template_ids.add(config_template_id)
                config_template = config_template_id_obj_map[config_template_id]
                latest_config_version = latest_config_version_map.get(config_template.config_template_id)
                if not latest_config_version:
                    error = NoActiveConfigVersionException(template_name=config_template.template_name)
                    job_task.set_status(
                        JobStatus.FAILED,
                        extra_data={"failed_reason": error.message, "err_code": error.code},
                    )
                    continue

                # 补充模板依赖
                content = ConfigVersionHandler.fill_template_dependencies(bk_biz_id, latest_config_version.content)
                rendered_content = mako_render(content, context)
                name = mako_render(config_template.file_name, context)
                path = mako_render(config_template.abs_path, context)
                # path = "/"

                sha256 = hashlib.sha256()
                sha256.update(rendered_content.encode())
                sha256sum = sha256.hexdigest()
                config_inst = ConfigInstance(
                    config_version_id=latest_config_version.config_version_id,
                    config_template_id=config_template.config_template_id,
                    bk_process_id=job_task.bk_process_id,
                    content=rendered_content,
                    sha256=sha256sum,
                    expression="TODO",
                    is_latest=True,
                    inst_id=inst_id,
                    created_by=bk_username,
                    path=path,
                    name=name,
                )
                inst_to_be_created_config_instances.append(config_inst)
                to_be_created_config_instances.append(config_inst)
                to_be_update_config_instances[config_template_id].append(job_task.bk_process_id)

                job_task_tpl_sha256_map[job_task.id][config_template_id].append(sha256sum)

        # 设置老的配置实例为非最新
        for config_template_id, bk_process_ids in to_be_update_config_instances.items():
            ConfigInstance.objects.filter(
                config_template_id=config_template_id, bk_process_id__in=bk_process_ids
            ).update(is_latest=False)
        ConfigInstance.objects.bulk_create(to_be_created_config_instances, batch_size=500)

        # 回写生成的模板实例 TODO 任务量大时这里可能有耗时，可以做pipeline分片进行优化
        new_config_instances = ConfigInstance.objects.filter(
            config_template_id__in=all_config_template_ids, bk_process_id__in=all_process_ids, is_latest=True
        ).values("id", "config_template_id", "sha256", "name")
        new_config_inst_map = defaultdict(dict)
        for config_instance in new_config_instances:
            new_config_inst_map[config_instance["config_template_id"]][config_instance["sha256"]] = config_instance

        for job_task_id, tpl_sha256_map in job_task_tpl_sha256_map.items():
            config_instances = []
            for config_template_id, sha256_list in tpl_sha256_map.items():
                for sha256 in sha256_list:
                    config_instances.append(new_config_inst_map[config_template_id][sha256])
            job_task = job_task_id_obj_map[job_task_id]
            job_task.set_extra_data(
                {
                    "config_instances": [
                        {
                            "id": config_instance["id"],
                            "config_template_id": config_instance["config_template_id"],
                            "template_name": config_template_id_obj_map[
                                config_instance["config_template_id"]
                            ].template_name,
                            "file_name": config_instance["name"]
                            or config_template_id_obj_map[config_instance["config_template_id"]].file_name,
                        }
                        for config_instance in config_instances
                    ]
                }
            )
        return self.return_data(result=True)

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="bk_username", key="bk_username", required=True),
            JobTaskBaseService.InputItem(name="bk_biz_id", key="bk_biz_id", required=True),
        ]


class BulkGenerateConfigComponent(Component):
    name = "BulkGenerateConfigComponent"
    code = "bulk_generate_config"
    bound_service = BulkGenerateConfigService


class BulkExecuteJobPlatformService(MultiJobTaskBaseService):
    """
    批量执行与作业平台相关的动作
    eg: 文件下发，脚本执行
    """

    __need_schedule__ = True
    interval = StaticIntervalGenerator(POLLING_INTERVAL)

    def request_single_job_and_create_map(
        self, job_func, job_id: int, job_task_ids: List, job_params: Dict, pipeline_data
    ):
        """请求作业平台并创建与订阅实例的映射"""
        job_params.update(
            {
                "bk_biz_id": job_params["bk_biz_id"],
                "script_language": job_params["os_type"],  # TODO 兼容Windows
                "script_content": base64.b64encode(job_params.get("script_content", "").encode()).decode(),
                "script_param": base64.b64encode(job_params.get("script_param", "").encode()).decode(),
                "task_name": f"GSEKIT_{job_id}_{self.__class__.__name__}",
            }
        )
        if "timeout" not in job_params:
            job_params["timeout"] = 300

        try:
            # 请求作业平台
            job_instance_id = job_func(job_params)["job_instance_id"]
        except ApiResultError as err:
            if err.code in EsbApi.ErrorCode.RATE_LIMIT_EXCEEDED_ERR_LIST:
                # 超过ESB频率限制，进行重试
                sleep(0.5)
                return self.request_single_job_and_create_map(job_func, job_id, job_task_ids, job_params, pipeline_data)
            for job_task in JobTask.objects.filter(id__in=job_task_ids):
                job_task.set_status(
                    JobStatus.FAILED,
                    extra_data={"failed_reason": err.message, "err_code": err.code},
                )
        else:
            # 并发请求记录作业平台 instance_id 和 job_task_ids 的映射关系和状态
            pipeline_data.outputs.job_instance_id__job_task_ids_map[job_instance_id] = {
                "job_task_ids": job_task_ids,
                "status": constants.BkJobStatus.PENDING,
            }
            return

    def _execute(self, data, parent_data):
        job_tasks = data.get_one_of_inputs("job_tasks")
        bk_biz_id = data.get_one_of_inputs("bk_biz_id")
        data.outputs.job_instance_id__job_task_ids_map = {}

        multi_job_params_map = {}
        job_tasks_config_template_ids_map = JobTask.get_job_tasks_config_template_ids_map(job_tasks)
        all_config_template_ids = set(itertools.chain.from_iterable(job_tasks_config_template_ids_map.values()))

        bk_process_ids = set()
        process_inst_map = {}
        process_inst_map_key_tmpl = "{bk_process_id}-{inst_id}"
        for job_task in job_tasks:
            bk_process_id = job_task.extra_data["process_info"]["process"]["bk_process_id"]
            inst_id = job_task.extra_data["inst_id"]
            bk_process_ids.add(bk_process_id)
            process_inst_map[process_inst_map_key_tmpl.format(bk_process_id=bk_process_id, inst_id=inst_id)] = job_task

            # 任务进程没有绑定任何配置模板，忽略
            config_template_ids = job_tasks_config_template_ids_map.get(job_task.id, [])
            if not config_template_ids:
                job_task.set_status(
                    JobStatus.IGNORED, extra_data={"failed_reason": str(ProcessDoseNotBindTemplate().message)}
                )

        config_template_id_obj_map = {
            config_template.config_template_id: config_template
            for config_template in ConfigTemplate.objects.filter(config_template_id__in=all_config_template_ids)
        }
        config_instance_id_content_map = {}
        for config_instance in ConfigInstance.objects.filter(
            config_template_id__in=all_config_template_ids, bk_process_id__in=bk_process_ids, is_latest=True
        ):
            inst_job_task = process_inst_map.get(
                process_inst_map_key_tmpl.format(
                    bk_process_id=config_instance.bk_process_id, inst_id=config_instance.inst_id
                )
            )

            if not inst_job_task:
                continue

            # 更新config_instances
            config_instances = inst_job_task.extra_data["config_instances"]
            config_instance_ids = {config_instance["id"] for config_instance in config_instances}

            if config_instance.id not in config_instance_ids:
                config_template = config_template_id_obj_map[config_instance.config_template_id]
                config_instances.append(
                    {
                        "id": config_instance.id,
                        "config_template_id": config_instance.config_template_id,
                        "template_name": config_template.template_name,
                        "user": config_template.owner,
                        "file_name": config_template.file_name,
                        "inst_id": config_instance.inst_id,
                        "path": config_instance.path,
                        "os_type": JOB_TASK_OS_TYPE["linux"]
                        if config_template.line_separator == ConfigTemplate.LineSeparator.LF
                        else JOB_TASK_OS_TYPE["win"],
                    }
                )
            config_instance_id_content_map[config_instance.id] = config_instance
            inst_job_task.extra_data["config_instances"] = config_instances
            inst_job_task.save(update_fields=["extra_data"])

            host_info = inst_job_task.extra_data["process_info"]["host"]

            for config_inst in config_instances:

                file_target_path = config_inst["path"]
                file_name = config_inst["file_name"]
                user = config_inst["user"]
                file_content = config_instance_id_content_map[config_inst["id"]].content
                file_sha256 = config_instance_id_content_map[config_inst["id"]].sha256
                key = f"{file_target_path}-{file_name}-{file_sha256}-{user}"
                os_type = config_inst["os_type"]
                # 路径、文件名、文件内容一致，则认为是同一个文件，合并到一个作业中，提高执行效率
                if key in multi_job_params_map:
                    multi_job_params_map[key]["job_task_ids"].append(inst_job_task.id)
                    multi_job_params_map[key]["job_params"]["target_server"]["ip_list"].append(
                        {"bk_cloud_id": host_info["bk_cloud_id"], "ip": host_info["bk_host_innerip"]}
                    )
                else:
                    multi_job_params_map[key] = {
                        "job_func": data.get_one_of_inputs("job_func"),
                        "job_id": inst_job_task.job_id,
                        "job_task_ids": [inst_job_task.id],
                        "job_params": {
                            "os_type": os_type,
                            "bk_biz_id": bk_biz_id,
                            "account_alias": user,
                            "target_server": {
                                "ip_list": [
                                    {"bk_cloud_id": host_info["bk_cloud_id"], "ip": host_info["bk_host_innerip"]}
                                ]
                            },
                        },
                        "pipeline_data": data,
                    }
                    # 添加额外的job_params字段参数
                    job_params = data.get_one_of_inputs("job_params")
                    for job_params_key in job_params:
                        job_params_field = job_params[job_params_key]
                        # 这里不能用列表推导式，会造成作用域更改
                        args = []
                        for arg in job_params_field["args"]:
                            args.append(locals().get(str(arg)) or arg)
                        multi_job_params_map[key]["job_params"].update(
                            {job_params_key: job_params_field["func"](*args)}
                        )

        data.inputs.job_params = ""  # 由于pickle不能序列化lambda，所以需要清空
        if multi_job_params_map:
            request_multi_thread(self.request_single_job_and_create_map, multi_job_params_map.values())
        return self.return_data(result=True)

    def request_get_job_instance_status(self, pipeline_data, job_instance_id, job_task_ids):
        """查询作业平台执行状态"""
        bk_biz_id = pipeline_data.get_one_of_inputs("bk_biz_id")
        try:
            result = JobApi.get_job_instance_status(
                {"bk_biz_id": bk_biz_id, "job_instance_id": job_instance_id, "return_ip_result": False}
            )
        except ApiResultError as err:
            # 超过ESB频率限制，认为是running，等待下次查询
            if err.code in EsbApi.ErrorCode.RATE_LIMIT_EXCEEDED_ERR_LIST:
                return [constants.BkJobStatus.RUNNING]
            raise err

        job_status = result["job_instance"]["status"]

        if job_status in [constants.BkJobStatus.PENDING, constants.BkJobStatus.RUNNING]:
            # 任务未完成，直接跳过，等待下次查询
            return [job_status]

        succeeded_config_inst_ids = []
        pipeline_data.outputs.job_instance_id__job_task_ids_map[job_instance_id]["status"] = job_status
        if job_status == constants.BkJobStatus.SUCCEEDED:
            # 任务成功，记录状态，避免下次继续查询
            pipeline_data.outputs.job_instance_id__job_task_ids_map[job_instance_id]["status"] = job_status

            for job_task in JobTask.objects.filter(id__in=job_task_ids):
                for config_inst in job_task.extra_data.get("config_instances", []):
                    succeeded_config_inst_ids.append(config_inst["id"])
                job_task.set_status(JobStatus.SUCCEEDED)
            ConfigInstance.objects.filter(id__in=succeeded_config_inst_ids).update(is_released=True)
            return [job_status]

        # 其它都认为存在失败的情况，需要具体查作业平台的接口查IP详情
        try:
            ip_results = JobApi.get_job_instance_status(
                {"bk_biz_id": bk_biz_id, "job_instance_id": job_instance_id, "return_ip_result": True}
            )
        except ApiResultError as err:
            # 超过ESB频率限制，认为是running，等待下次查询
            if err.code in EsbApi.ErrorCode.RATE_LIMIT_EXCEEDED_ERR_LIST:
                return [constants.BkJobStatus.RUNNING]
            raise err

        # 构造主机作业状态映射表
        cloud_ip_status_map = {}
        for ip_result in ip_results["step_instance_list"][0]["step_ip_result_list"]:
            cloud_ip_status_map[f'{ip_result["bk_cloud_id"]}-{ip_result["ip"]}'] = ip_result

        job_tasks = JobTask.objects.filter(id__in=job_task_ids)

        for job_task in job_tasks:
            ip = job_task.extra_data["process_info"]["host"]["bk_host_innerip"]
            cloud_id = job_task.extra_data["process_info"]["host"]["bk_cloud_id"]
            cloud_ip = f"{cloud_id}-{ip}"
            try:
                ip_result = cloud_ip_status_map[cloud_ip]
            except KeyError:
                ip_status = constants.BkJobIpStatus.NOT_RUNNING
                err_code = constants.BkJobErrorCode.NOT_RUNNING
            else:
                ip_status = ip_result["status"]
                err_code = ip_result["error_code"]
            err_msg = "{ip_status_msg}, {err_msg}".format(
                ip_status_msg=constants.BkJobErrorCode.BK_JOB_ERROR_CODE_MAP.get(ip_status),
                err_msg=constants.BkJobErrorCode.BK_JOB_ERROR_CODE_MAP.get(err_code),
            )
            if ip_status != constants.BkJobIpStatus.SUCCEEDED:
                job_task.set_status(
                    JobStatus.FAILED,
                    extra_data={
                        "failed_reason": _("作业平台执行失败: {err_msg}").format(err_msg=err_msg),
                        "err_code": JobApiException().code,
                    },
                )
            else:
                job_task.set_status(JobStatus.SUCCEEDED)
                for config_inst in job_task.extra_data.get("config_instances", []):
                    succeeded_config_inst_ids.append(config_inst["id"])
        ConfigInstance.objects.filter(id__in=succeeded_config_inst_ids).update(is_released=True)
        return [job_status]

    def _schedule(self, data, parent_data, callback_data=None):
        polling_time = data.get_one_of_outputs("polling_time") or 0
        job_instance_id__job_task_ids_map = data.get_one_of_outputs("job_instance_id__job_task_ids_map") or {}

        # 没有任务，直接完成
        if not job_instance_id__job_task_ids_map:
            return self.return_data(result=True, is_finished=True)

        to_be_check_job = []
        for job_instance_id, job_tasks_status in job_instance_id__job_task_ids_map.items():
            if job_tasks_status["status"] in [constants.BkJobStatus.PENDING, constants.BkJobStatus.RUNNING]:
                to_be_check_job.append(
                    {
                        "pipeline_data": data,
                        "job_instance_id": job_instance_id,
                        "job_task_ids": job_tasks_status["job_task_ids"],
                    }
                )
        all_job_result = request_multi_thread(
            self.request_get_job_instance_status, to_be_check_job, get_data=lambda x: x
        )

        # 判断 JobSubscriptionInstanceMap 中对应的 job_instance_id 都执行完成的，把成功的 subscription_instance_ids 向下传递
        is_finished = not (
            constants.BkJobStatus.PENDING in all_job_result or constants.BkJobStatus.RUNNING in all_job_result
        )
        if polling_time + POLLING_INTERVAL > GlobalSettings.pipeline_polling_timeout():
            # 由于JOB的超时机制可能会失效，因此这里自己需要有超时机制进行兜底
            is_finished = True
            for job_instance_id, job_tasks_status in job_instance_id__job_task_ids_map.items():
                status = job_instance_id__job_task_ids_map[job_instance_id]["status"]
                if status in [constants.BkJobStatus.PENDING, constants.BkJobStatus.RUNNING]:
                    job_instance_id__job_task_ids_map[job_instance_id]["status"] = constants.BkJobStatus.FAILED

        # 没完成时result为True，继续下次查询
        result = True
        if is_finished:
            # 完成时，需确定所有任务都是成功的
            result = set(all_job_result) == {constants.BkJobStatus.SUCCEEDED}

        data.outputs.polling_time = polling_time + POLLING_INTERVAL
        data.outputs.job_instance_id__job_task_ids_map = job_instance_id__job_task_ids_map
        return self.return_data(result=result, is_finished=is_finished)

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="bk_username", key="bk_username", required=True),
            JobTaskBaseService.InputItem(name="bk_biz_id", key="bk_biz_id", required=True),
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="polling_time", key="polling_time", type="int"),
            Service.OutputItem(
                name="job_instance_id__job_task_ids_map", key="job_instance_id__job_task_ids_map", type="dict"
            ),
        ]


class BulkPushConfigService(BulkExecuteJobPlatformService):
    """
    下发配置
    """

    def _execute(self, data, parent_data):
        job_params = {
            "file_target_path": {"args": ["file_target_path"], "func": lambda file_target_path: file_target_path},
            "file_list": {
                "args": ["file_name", "file_content"],
                "func": lambda file_name, file_content: [
                    {"file_name": file_name, "content": base64.b64encode(file_content).decode()}
                ],
            },
        }
        data.inputs.job_params = job_params
        data.inputs.job_func = JobApi.push_config_file

        return super()._execute(data, parent_data)


class BulkPushConfigComponent(Component):
    name = "BulkPushConfigComponent"
    code = "bulk_push_config"
    bound_service = BulkPushConfigService


class BulkExecuteJobService(MultiJobTaskBaseService):
    """
    执行脚本
    """

    def _execute(self, data, parent_data):
        pass

    def inputs_format(self):
        return super().inputs_format() + [
            JobTaskBaseService.InputItem(name="bk_username", key="bk_username", required=True),
            JobTaskBaseService.InputItem(name="bk_biz_id", key="bk_biz_id", required=True),
        ]


class BulkExecuteJobComponent(Component):
    name = "BulkExecuteJobComponent"
    code = "bulk_execute_job"
    bound_service = BulkExecuteJobService


class BulkBackupConfigService(BulkExecuteJobPlatformService):
    """
    配置文件备份
    """

    def _execute(self, data, parent_data):
        with open("apps/gsekit/scripts/backup_cfg.bat") as bat, open("apps/gsekit/scripts/backup_cfg.sh") as sh:
            script_content = {JOB_TASK_OS_TYPE["win"]: bat.read(), JOB_TASK_OS_TYPE["linux"]: sh.read()}
        job_params = {
            "script_content": {
                "args": ["file_target_path", "file_name", "os_type", script_content],
                "func": lambda file_target_path, file_name, os_type, script_details: script_details[os_type].format(
                    file_target_path=file_target_path,
                    file_name=file_name,
                    now_time=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
                ),
            }
        }
        data.inputs.job_params = job_params
        data.inputs.job_func = JobApi.fast_execute_script

        return super()._execute(data, parent_data)


class BulkBackupConfigComponent(Component):
    name = "BulkBackupConfigComponent"
    code = "bulk_backup_job"
    bound_service = BulkBackupConfigService
