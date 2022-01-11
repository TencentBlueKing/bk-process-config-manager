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
from typing import Dict, List

from django.db.models import Q, Max

from apps.gsekit.configfile import exceptions
from apps.gsekit.configfile.models import ConfigInstance, ConfigTemplateVersion, ConfigTemplate
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.process.models import ProcessInst
from apps.utils import APIModel
from apps.utils.models import model_to_dict
from common.log import logger


class ConfigInstanceHandler(APIModel):
    def __init__(self, config_instance_id: int = None):
        super().__init__()
        self.config_instance_id = int(config_instance_id)

    def _get_data(self) -> ConfigInstance:
        try:
            config_instance = ConfigInstance.objects.get(id=self.config_instance_id)
        except ConfigInstance.DoesNotExist:
            logger.error("配置实例不存在, config_instance_id={}".format(self.config_instance_id))
            raise exceptions.ConfigInstanceDoseNotExistException()
        return config_instance

    @property
    def data(self) -> ConfigInstance:
        return super().data

    def retrieve(self):
        config_instance_info = model_to_dict(self.data)

        # 补充配置模板信息
        try:
            config_template_info = model_to_dict(
                ConfigTemplate.objects.get(config_template_id=self.data.config_template_id)
            )
        except ConfigTemplate.DoesNotExist:
            logger.exception(
                "[config_instance:{config_instance_id}] 配置模板不存在或已被删除".format(config_instance_id=self.config_instance_id)
            )
            config_template_info = {}
        config_template_info.update(config_instance_info)
        return config_template_info

    @classmethod
    def list(
        cls,
        bk_biz_id: int,
        scope: Dict,
        expression_scope: Dict,
        process_status: int,
        is_auto: bool,
        config_template_id: str = None,
        config_version_ids: List = None,
        filter_released: bool = None,
    ):
        """
        :param bk_biz_id:
        :param scope:
        :param expression_scope:
        :param process_status:
        :param is_auto:
        :param config_template_id:
        :param config_version_ids:
        :param filter_released: 是否过滤出已部署的配置实例，为True时，取已部署的最新版本的配置。否则不过滤是否部署
        :return:
        """
        # 根据过滤条件查询进程
        bk_process_ids = []
        process_list = []

        for process in ProcessHandler(bk_biz_id=bk_biz_id).list(
            scope=scope, expression_scope=expression_scope, process_status=process_status, is_auto=is_auto
        ):
            bk_process_ids.append(process.bk_process_id)
            process_list.append(model_to_dict(process))

        process_list = ProcessHandler.fill_extra_info_to_process(process_list, topo_name=True, bound_template=True)

        process_inst_map = ProcessInst.get_process_inst_map(bk_process_ids=bk_process_ids)

        # 通过进程绑定的配置模板进行分类
        process_ids = []
        config_template_ids = []
        process_config_template_mapping = {}
        for process in process_list:
            bk_process_id = process["bk_process_id"]
            process_ids.append(bk_process_id)

            # 指定了单个配置模板
            if config_template_id:
                process["config_templates"] = [
                    config_template
                    for config_template in process["config_templates"]
                    if config_template["config_template_id"] == config_template_id
                ]

            # 未指定配置模板，则查询全部
            for config_template in process["config_templates"]:
                cfg_tmpl_id = config_template["config_template_id"]
                config_template_ids.append(cfg_tmpl_id)
                for proc_inst in process_inst_map.get(bk_process_id, []):
                    inst_id = proc_inst["inst_id"]
                    key = ConfigInstance.IDENTITY_KEY_TEMPLATE.format(
                        bk_process_id=bk_process_id, config_template_id=cfg_tmpl_id, inst_id=inst_id
                    )
                    process_config_template_mapping[key] = dict(
                        status=ConfigInstance.Status.NOT_GENERATED,
                        config_template=config_template,
                        inst_id=inst_id,
                        created_at="-",
                        config_version_id=ConfigInstance.NOT_RELEASED_VERSION,
                        **process,
                    )
                    process_config_template_mapping[key].pop("config_templates", None)

        # 查询确认是否最新的配置并补充配置实例相关信息
        latest_config_version_mapping = ConfigTemplateVersion.get_latest_version_mapping(config_template_ids)

        only_fields = [
            "id",
            "config_template_id",
            "config_version_id",
            "bk_process_id",
            "is_latest",
            "is_released",
            "created_at",
            "bk_process_id",
            "inst_id",
        ]
        config_instance_list = ConfigInstance.objects.filter(
            config_template_id__in=set(config_template_ids), bk_process_id__in=process_ids
        ).only(*only_fields)
        latest_generated_config_instance_list = config_instance_list.filter(is_latest=True)
        # 最新生成的配置实例映射表
        latest_gen_cfg_inst_map = {}
        for latest_gen_cfg_inst in latest_generated_config_instance_list:
            key = latest_gen_cfg_inst.identity_key
            # 进程启动数量调整后，config_instance.identity_key 不一定能匹配到相应的进程实例，执行key存在性校验，避免KeyError
            if key not in process_config_template_mapping:
                continue
            latest_gen_cfg_inst_map[key] = latest_gen_cfg_inst
            process_config_template_mapping[key].update({"status": ConfigInstance.Status.GENERATED})

        # 最新下发的配置实例映射表
        max_config_instance_ids = (
            config_instance_list.filter(is_released=True)
            .order_by()
            .values("bk_process_id", "inst_id", "config_template_id")
            .annotate(Max("id"))
        )
        config_instance_ids = [config_instance["id__max"] for config_instance in max_config_instance_ids]
        latest_released_config_instance_list = ConfigInstance.objects.filter(id__in=config_instance_ids).only(
            *only_fields
        )
        latest_released_cfg_inst_map = {
            conf_inst.identity_key: conf_inst for conf_inst in latest_released_config_instance_list
        }

        if filter_released:
            target_config_instance_list = latest_released_config_instance_list
        else:
            target_config_instance_list = latest_generated_config_instance_list
        for config_instance in target_config_instance_list:
            config_template_id = config_instance.config_template_id
            key = config_instance.identity_key
            latest_config_version = latest_config_version_mapping.get(config_template_id)
            latest_gen_cfg_inst = latest_gen_cfg_inst_map.get(key)
            latest_released_cfg_inst = latest_released_cfg_inst_map.get(key)
            if key not in process_config_template_mapping:
                continue

            if process_config_template_mapping[key].get("config_instance_id"):
                # 已填充过 config_instance_id，直接跳过
                continue

            released_config_version_id = getattr(latest_released_cfg_inst, "config_version_id", "")
            generated_config_version_id = getattr(latest_gen_cfg_inst, "config_version_id", "")
            process_config_template_mapping[key].update(
                {
                    "created_at": config_instance.created_at,
                    "released_config_version_id": released_config_version_id,
                    "generated_config_version_id": generated_config_version_id,
                    "config_version_id": released_config_version_id if filter_released else generated_config_version_id,
                    "config_instance_id": config_instance.id,
                }
            )
            if generated_config_version_id != latest_config_version.config_version_id:
                process_config_template_mapping[key].update({"status": ConfigInstance.Status.NOT_LATEST})

        # 过滤掉指定的配置版本的配置实例
        if config_version_ids:
            return [
                value
                for value in process_config_template_mapping.values()
                if value.get("released_config_version_id") in config_version_ids
            ]

        return process_config_template_mapping.values()

    @classmethod
    def latest_config_instance(cls, bk_process_id: int, config_template_id: int, inst_id: int = None) -> Dict:
        filter_conditions = dict(bk_process_id=bk_process_id, config_template_id=config_template_id)
        if inst_id:
            filter_conditions.update(inst_id=inst_id)
        config_inst_list = (
            ConfigInstance.objects.filter(**filter_conditions)
            .filter(Q(is_latest=True) | Q(is_released=True))
            .order_by("inst_id", "-id")
            .values("id", "created_at", "content", "is_latest", "is_released", "config_version_id")
        )
        first_latest_config = next((inst for inst in config_inst_list if inst["is_latest"]), None)
        first_released_config = next((inst for inst in config_inst_list if inst["is_released"]), None)
        first_latest_released_config = next(
            (inst for inst in config_inst_list if inst["is_released"] & inst["is_latest"]), None
        )

        result = {"generated_config": first_latest_config, "released_config": first_released_config, "is_latest": True}
        if first_latest_released_config:
            result = {
                "generated_config": first_latest_released_config,
                "released_config": first_latest_released_config,
                "is_latest": True,
            }

        if not result["generated_config"]:
            return result

        # 获取已生成配置版本号，检查配置模板是否最新
        generated_config_version = result["generated_config"]["config_version_id"]
        if ConfigTemplateVersion.objects.filter(
            config_template_id=config_template_id, config_version_id__gt=generated_config_version, is_active=True
        ).exists():
            # 当前配置文件模板有更高的版本，is_latest置为False
            result["is_latest"] = False
        return result
