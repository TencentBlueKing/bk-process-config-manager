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
from collections import defaultdict
from time import sleep
from typing import Dict, List

from django.db import IntegrityError
from django.db.models import Count

from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.configfile import exceptions
from apps.gsekit.configfile.exceptions import DuplicateTemplateNameException, ConfigTemplateDraftAlreadyExistException
from apps.gsekit.configfile.models import ConfigTemplate, ConfigTemplateVersion, ConfigTemplateBindingRelationship
from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import Job, JobStatus
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.process.models import Process
from apps.utils import APIModel
from apps.utils.local import get_request_username
from apps.utils.models import model_to_dict
from common.log import logger


class ConfigTemplateHandler(APIModel):
    def __init__(self, bk_biz_id: int = None, config_template_id: int = None):
        super().__init__()
        self.config_template_id = None if config_template_id is None else int(config_template_id)
        self.bk_biz_id = None if bk_biz_id is None else int(bk_biz_id)

    def _get_data(self) -> ConfigTemplate:
        try:
            config_template = ConfigTemplate.objects.get(
                config_template_id=self.config_template_id, bk_biz_id=self.bk_biz_id
            )
        except ConfigTemplate.DoesNotExist:
            logger.error("配置模板不存在, config_template_id={}".format(self.config_template_id))
            raise exceptions.ConfigTemplateDoseNotExistException()
        return config_template

    @property
    def data(self) -> ConfigTemplate:
        return super().data

    @staticmethod
    def build_process_key(process_object: Dict) -> str:
        """
        构造进程对象key
        :param process_object: 进程对象
            {
                "process_object_type": "INSTANCE",
                "process_object_id": 1
            }
        :return:
        """
        process_key_template = "{process_object_type}-{process_object_id}"
        return process_key_template.format(
            process_object_type=process_object["process_object_type"],
            process_object_id=process_object["process_object_id"],
        )

    @staticmethod
    def list_config_templates(bk_biz_id: int):
        return ConfigTemplate.objects.filter(bk_biz_id=bk_biz_id)

    @staticmethod
    def create_config_template(
        bk_biz_id: int,
        template_name: str,
        file_name: str,
        abs_path: str,
        owner: str,
        group: str,
        filemode: str,
        line_separator: str,
    ) -> Dict:
        try:
            config_template = ConfigTemplate.objects.create(
                bk_biz_id=bk_biz_id,
                template_name=template_name,
                file_name=file_name,
                abs_path=abs_path,
                owner=owner,
                group=group,
                filemode=filemode,
                line_separator=line_separator,
            )
        except IntegrityError:
            raise DuplicateTemplateNameException(template_name=template_name)
        data = model_to_dict(config_template)
        return data

    def retrieve_config_template(self):
        data = model_to_dict(self.data)
        data["relation_count"] = self.data.relation_count
        data["is_bound"] = self.data.is_bound
        data["has_version"] = self.data.has_version
        return data

    def update_config_template(
        self,
        template_name: str,
        file_name: str,
        abs_path: str,
        owner: str,
        group: str,
        filemode: str,
        line_separator: str,
    ) -> Dict:
        self.data.template_name = template_name
        self.data.file_name = file_name
        self.data.abs_path = abs_path
        self.data.owner = owner
        self.data.group = group
        self.data.filemode = filemode
        self.data.line_separator = line_separator
        try:
            self.data.save()
        except IntegrityError:
            raise DuplicateTemplateNameException(template_name=template_name)
        return model_to_dict(self.data)

    def delete_config_template(self):
        self.data.delete()

    def create_config_version(self, description: str, content: str, file_format: str, is_active: bool = False) -> Dict:
        """新建配置版本"""
        if ConfigTemplateVersion.objects.filter(config_template_id=self.config_template_id, is_draft=True).exists():
            raise ConfigTemplateDraftAlreadyExistException
        if is_active:
            # 不保存草稿直接上线的情况，更新DB的其它版本为非active
            ConfigTemplateVersion.objects.filter(config_template_id=self.config_template_id).update(is_active=False)

        config_version = ConfigTemplateVersion.objects.create(
            config_template_id=self.config_template_id,
            description=description,
            content=content,
            file_format=file_format,
            is_draft=not is_active,
            is_active=is_active,
        )
        return model_to_dict(config_version)

    def list_config_version(self):
        config_version_list = ConfigTemplateVersion.objects.filter(config_template_id=self.config_template_id)
        return [model_to_dict(config_version) for config_version in config_version_list]

    def sync_generate_config(self, bk_biz_id: int, bk_process_id: int):
        """
        单个生成配置，复用 generate_config, 同步查询任务状态
        :return:
        """
        process = ProcessHandler(bk_biz_id=bk_biz_id, bk_process_id=bk_process_id).data
        scope = {"bk_set_env": str(process.bk_set_env), "bk_process_ids": [bk_process_id]}
        job_id = self.generate_config(bk_biz_id, self.config_template_id, scope)["job_id"]

        # 单个配置生成，一般在几秒内就能完成，
        job_handler = JobHandlers(bk_biz_id=bk_biz_id, job_id=job_id)
        max_retry_times = 60
        query_times = 0
        while job_handler.data.status in [JobStatus.PENDING, JobStatus.RUNNING] and query_times < max_retry_times:
            sleep(0.5)
            # 这里不能复用job_handler，因为data有缓存
            job_handler = JobHandlers(bk_biz_id=bk_biz_id, job_id=job_id)
            query_times += 1
            if not job_handler.data.is_ready:
                continue

        return job_handler.get_job_task()["list"]

    def list_binding_relationship(self) -> List:
        proc_type = Process.ProcessObjectType
        cmdb_handler = CMDBHandler(self.bk_biz_id)
        relationships = [
            model_to_dict(relationship)
            for relationship in ConfigTemplateBindingRelationship.objects.filter(
                config_template_id=self.config_template_id
            )
        ]
        proc_template_ids = []
        proc_ids = []
        for relationship in relationships:
            if relationship["process_object_type"] == proc_type.TEMPLATE:
                proc_template_ids.append(relationship["process_object_id"])
            else:
                proc_ids.append(relationship["process_object_id"])

        # 获取模板进程所需信息
        proc_tmpl_id_map = {
            proc_tmpl["id"]: proc_tmpl
            for proc_tmpl in cmdb_handler.process_template(process_template_ids=proc_template_ids)
        }
        service_tmpl_id_name_map = {
            service_tmpl["id"]: service_tmpl["name"] for service_tmpl in cmdb_handler.service_template()
        }

        # 获取进程所需信息
        processes = Process.objects.filter(bk_process_id__in=proc_ids).values("bk_process_id", "expression")
        proc_id_exp_map = {proc["bk_process_id"]: proc["expression"] for proc in processes}

        # 填充进程对象回填信息
        for relationship in relationships:
            if relationship["process_object_type"] == proc_type.TEMPLATE:
                proc_tmpl = proc_tmpl_id_map.get(relationship["process_object_id"], {})
                relationship["process_obj_info"] = {
                    "process_object_name": proc_tmpl.get("bk_process_name"),
                    "service_template_name": service_tmpl_id_name_map.get(proc_tmpl.get("service_template_id")),
                }
            else:
                relationship["process_obj_info"] = ProcessHandler.process_expression_to_name(
                    proc_id_exp_map.get(relationship["process_object_id"], "*.*.*.*.*")
                )
        return relationships

    def bind_template_to_process(self, process_object_list: List[Dict]) -> Dict:
        """
        绑定模板到进程实例/模板
        :param process_object_list: 进程对象列表
        [
            {
                "process_object_type": "INSTANCE",
                "process_object_id": 1
            },
            {
                "process_object_type": "TEMPLATE",
                "process_object_id": 2
            }
        ]
        :return:
        """
        to_be_deleted_relation_id_list = []
        to_be_created_relations = []
        exist_relation_mapping = defaultdict(list)
        process_object_key_mapping = {
            self.build_process_key(process_object): process_object for process_object in process_object_list
        }

        relations = ConfigTemplateBindingRelationship.objects.filter(config_template_id=self.config_template_id)

        # 计算得出要被删除的绑定关系
        for relation in relations:
            process_key = self.build_process_key(
                {"process_object_type": relation.process_object_type, "process_object_id": relation.process_object_id}
            )
            exist_relation_mapping[relation.config_template_id].append(process_key)
            if process_key not in process_object_key_mapping:
                to_be_deleted_relation_id_list.append(relation.id)

        # 计算出需创建的关系
        for process_key, process_object in process_object_key_mapping.items():
            if process_key not in exist_relation_mapping[self.config_template_id]:
                to_be_created_relations.append(
                    ConfigTemplateBindingRelationship(
                        bk_biz_id=self.data.bk_biz_id,
                        config_template_id=self.config_template_id,
                        process_object_type=process_object["process_object_type"],
                        process_object_id=process_object["process_object_id"],
                    )
                )

        deleted_count = len(to_be_deleted_relation_id_list)
        created_count = len(to_be_created_relations)
        logger.info(
            "[bind_template_to_process] config_template_id: {config_template_id},"
            "process_object_key_mapping: {process_object_key_mapping}. "
            "There are {deleted_count} relations to be deleted and {created_count} relations to be created.".format(
                config_template_id=self.config_template_id,
                process_object_key_mapping=process_object_key_mapping,
                deleted_count=deleted_count,
                created_count=created_count,
            )
        )
        if to_be_deleted_relation_id_list:
            ConfigTemplateBindingRelationship.objects.filter(id__in=to_be_deleted_relation_id_list).delete()
        if to_be_created_relations:
            ConfigTemplateBindingRelationship.objects.bulk_create(to_be_created_relations)
        return {"deleted_relations_count": deleted_count, "created_relations_count": created_count}

    def bind_process_to_template(
        self, process_object_type: str, process_object_id: int, config_template_id_list: List[int]
    ) -> Dict:
        """
        绑定进程到配置模板
        :param config_template_id_list: 配置模板列表
        :param process_object_id: 进程对象id
        :param process_object_type: 进程对象类型, INSTANCE/TEMPLATE
        :return:
        """

        relations = ConfigTemplateBindingRelationship.objects.filter(
            process_object_type=process_object_type, process_object_id=process_object_id
        )
        exist_config_template_id_list = relations.values_list("config_template_id", flat=True)

        to_be_created_relations = []
        to_be_deleted_relation_id_list = []

        # 计算得出要被删除的绑定关系
        for relation in relations:
            if relation.config_template_id not in config_template_id_list:
                to_be_deleted_relation_id_list.append(relation.id)

        # 计算出需创建的关系
        for config_template_id in config_template_id_list:
            if config_template_id not in exist_config_template_id_list:
                to_be_created_relations.append(
                    ConfigTemplateBindingRelationship(
                        bk_biz_id=self.bk_biz_id,
                        config_template_id=config_template_id,
                        process_object_type=process_object_type,
                        process_object_id=process_object_id,
                    )
                )

        deleted_count = len(to_be_deleted_relation_id_list)
        created_count = len(to_be_created_relations)
        logger.info(
            f"[bind_process_to_template] config_template_id_list: {config_template_id_list},"
            f"process_object_type: {process_object_type}, process_object_id: {process_object_id}. "
            f"There are {deleted_count} relations to be deleted and {created_count} relations to be created."
        )
        ConfigTemplateBindingRelationship.objects.filter(id__in=to_be_deleted_relation_id_list).delete()
        ConfigTemplateBindingRelationship.objects.bulk_create(to_be_created_relations)
        return {"deleted_relations_count": deleted_count, "created_relations_count": created_count}

    @classmethod
    def generate_config(
        cls,
        bk_biz_id: int,
        config_template_id: int,
        scope: Dict,
        expression_scope: Dict = None,
        config_version_ids: List = None,
    ):
        """
        生成配置
        :param bk_biz_id: 业务ID
        :param config_template_id: 配置模板ID
        :param scope: 进程范围
        :param expression_scope: 进程表达式范围
        :param config_version_ids: 配置模板版本列表
        :return:
        """
        extra_data = {}
        if config_template_id:
            extra_data = {"config_template_ids": [config_template_id]}
            if config_version_ids:
                extra_data.update(
                    {
                        "config_version_ids_map": [
                            {"config_template_id": config_template_id, "config_version_ids": config_version_ids}
                        ]
                    }
                )
        return JobHandlers(bk_biz_id=bk_biz_id).create_job(
            job_action=Job.JobAction.GENERATE,
            job_object=Job.JobObject.CONFIGFILE,
            created_by=get_request_username(),
            scope=scope,
            expression_scope=expression_scope,
            extra_data=extra_data,
        )

    @classmethod
    def fill_with_is_bound(cls, config_templates: List[Dict]) -> List[Dict]:
        """检查配置模板是否已绑定进程/进程模板，并补充is_bound字段"""
        config_template_ids = [config_template["config_template_id"] for config_template in config_templates]

        # 统计配置模板绑定关系
        binding_counts = (
            ConfigTemplateBindingRelationship.objects.filter(config_template_id__in=config_template_ids)
            .values("config_template_id", "process_object_type")
            .annotate(relation_count=Count("config_template_id"))
        )
        config_template_binding_count_map = defaultdict(
            lambda: {process_object_type_tup[0]: 0 for process_object_type_tup in Process.PROCESS_OBJECT_TYPE_CHOICE}
        )
        for binding_count in binding_counts:
            config_template_binding_count_map[binding_count["config_template_id"]][
                binding_count["process_object_type"]
            ] = binding_count["relation_count"]

        # 统计配置模板版本数
        config_version_counts = (
            ConfigTemplateVersion.objects.filter(config_template_id__in=config_template_ids, is_draft=False)
            .values("config_template_id")
            .annotate(config_version_count=Count("config_template_id"))
            .order_by("config_template_id")  # 避免 ConfigTemplateVersion.Meta.ordering造成聚合计算错误
        )
        config_template_version_map = {
            config_version_count["config_template_id"]: config_version_count["config_version_count"]
            for config_version_count in config_version_counts
        }
        for config_template in config_templates:
            config_template_id = config_template["config_template_id"]
            relation_count = config_template_binding_count_map[config_template_id]
            config_template["relation_count"] = relation_count
            config_template["is_bound"] = bool(sum(relation_count.values()))
            config_template["has_version"] = bool(config_template_version_map.get(config_template_id, 0))
        return config_templates
