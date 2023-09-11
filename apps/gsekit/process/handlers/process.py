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
import copy
import json
import operator
import time
from collections import defaultdict
from functools import reduce
from itertools import groupby
from typing import List, Dict, Union

from django.db import transaction
from django.db.models import Q, QuerySet

from apps.api import CCApi, GseApi
from apps.gsekit import constants
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.configfile.models import ConfigTemplateBindingRelationship, ConfigTemplate
from apps.gsekit.pipeline_plugins.components.collections.gse import NAMESPACE, GseAutoType, GseDataErrorCode, GseOpType
from apps.gsekit.process import exceptions
from apps.gsekit.process.exceptions import (
    ProcessDoseNotExistException,
    DuplicateProcessInstException,
    ProcessNotMatchException,
)
from apps.gsekit.process.models import Process, ProcessInst
from apps.gsekit.utils.expression_utils import match
from apps.gsekit.utils.expression_utils.parse import parse_list2expr, BuildInChar
from apps.gsekit.utils.expression_utils.serializers import gen_expression
from apps.utils import APIModel
from apps.utils.batch_request import batch_request, request_multi_thread
from apps.utils.mako_utils.render import mako_render
from common.log import logger


class ProcessHandler(APIModel):
    def __init__(self, bk_biz_id: int, bk_process_id: int = None):
        super().__init__()
        self.bk_biz_id = int(bk_biz_id)
        self.bk_process_id = bk_process_id

    def _get_data(self) -> Process:
        try:
            process = Process.objects.get(bk_biz_id=self.bk_biz_id, bk_process_id=self.bk_process_id)
        except Process.DoesNotExist:
            logger.error("进程不存在, bk_process_id={}".format(self.bk_process_id))
            raise exceptions.ProcessDoseNotExistException(bk_process_id=self.bk_process_id)
        return process

    @property
    def data(self) -> Process:
        return super().data

    @staticmethod
    def process_expression_to_name(expression: str) -> Dict:
        """进程表达式转为名称"""

        expression_split_list = expression.split(constants.EXPRESSION_SPLITTER)
        return {
            "bk_set_name": expression_split_list[0],
            "bk_module_name": expression_split_list[1],
            "bk_service_name": expression_split_list[2],
            "bk_process_name": expression_split_list[3],
        }

    @classmethod
    def fill_topo_name_to_process(cls, process_list: List[Dict]) -> List[Dict]:
        if not process_list:
            return process_list
        bk_cloud_id_name_map = {
            cloud["bk_cloud_id"]: cloud["bk_cloud_name"]
            for cloud in CMDBHandler(bk_biz_id=process_list[0]["bk_biz_id"]).get_or_cache_bk_cloud_area()
        }
        for process in process_list:
            expression = process["expression"]
            names_dict = cls.process_expression_to_name(expression)
            process.update(names_dict)
            process["bk_cloud_name"] = bk_cloud_id_name_map.get(process["bk_cloud_id"])
        return process_list

    @staticmethod
    def fill_proc_inst_to_process(process_list: List[Dict]) -> List[Dict]:
        proc_inst_list = sorted(
            list(
                ProcessInst.objects.filter(bk_process_id__in=[proc["bk_process_id"] for proc in process_list]).values(
                    "bk_process_id", "local_inst_id", "inst_id", "process_status", "is_auto"
                )
            ),
            key=lambda proc_inst: proc_inst["bk_process_id"],
        )
        # 填充进程实例信息到进程状态列表中
        process_id_map = {proc["bk_process_id"]: proc for proc in process_list}
        for bk_process_id, proc_infos in groupby(proc_inst_list, lambda proc: proc["bk_process_id"]):
            process_id_map[bk_process_id]["proc_inst_infos"] = list(proc_infos)

        for proc in process_list:
            # 无实例的进程状态对象填充空列表
            proc["proc_inst_infos"] = proc.get("proc_inst_infos") or []
        return process_list

    @staticmethod
    def fill_config_template_binding_info_to_process(process_list: List[Dict]) -> List[Dict]:
        process_from_template_ids = [
            process["process_template_id"] for process in process_list if process["process_template_id"]
        ]
        process_normal_ids = [
            process["bk_process_id"] for process in process_list if not process["process_template_id"]
        ]

        # 查询相应的进程配置绑定关系
        conf_tmpl_relations = ConfigTemplateBindingRelationship.objects.filter(
            Q(
                process_object_id__in=process_from_template_ids,
                process_object_type=Process.ProcessObjectType.TEMPLATE,
            )
            | Q(
                process_object_id__in=process_normal_ids,
                process_object_type=Process.ProcessObjectType.INSTANCE,
            )
        ).values("config_template_id", "process_object_id", "process_object_type")

        # 按进程类别及id归类配置模板ID
        tmpl_id_group_by_obj_type_and_id = defaultdict(list)
        config_template_ids = set()
        for relation in conf_tmpl_relations:
            config_template_ids.add(relation["config_template_id"])
            tmpl_id_group_by_obj_type_and_id[
                f"{relation['process_object_type']}-{relation['process_object_id']}"
            ].append(relation["config_template_id"])

        # 批量获取配置模板
        conf_tmpls = ConfigTemplate.objects.filter(config_template_id__in=list(config_template_ids)).values(
            "config_template_id", "template_name", "file_name"
        )
        # 建立配置模板id与配置模板自身之间的映射关系
        conf_tmpl_id_map = {conf_tmpl["config_template_id"]: conf_tmpl for conf_tmpl in conf_tmpls}
        # 记录绑定关系中模板文件ID不存在的的情况
        to_be_deleted_conf_tmpl_ids = []
        for process in process_list:
            # 计算{process_object_type}-{process_object_id}
            if process["process_template_id"]:
                process_obj_type_id = f"{Process.ProcessObjectType.TEMPLATE}-" f"{process['process_template_id']}"
            else:
                process_obj_type_id = f"{Process.ProcessObjectType.INSTANCE}-{process['bk_process_id']}"

            # 获取当前进程下全部配置模板ID
            conf_tmpl_ids = tmpl_id_group_by_obj_type_and_id[process_obj_type_id]

            # 根据映射关系，填充config_templates
            # process["config_templates"] = [conf_tmpl_id_map[conf_tmpl_id] for conf_tmpl_id in conf_tmpl_ids]
            # TODO: 清理脏数据逻辑，后续删除
            process["config_templates"] = []
            for conf_tmpl_id in conf_tmpl_ids:
                if conf_tmpl_id in conf_tmpl_id_map:
                    process["config_templates"].append(conf_tmpl_id_map[conf_tmpl_id])
                    continue
                to_be_deleted_conf_tmpl_ids.append(conf_tmpl_id)

        # 删除脏数据
        if to_be_deleted_conf_tmpl_ids:
            ConfigTemplateBindingRelationship.objects.filter(
                config_template_id__in=to_be_deleted_conf_tmpl_ids
            ).delete()
        return process_list

    @classmethod
    def fill_extra_info_to_process(
        cls, process_list: List[Dict], topo_name: bool = False, bound_template: bool = False, proc_inst: bool = False
    ) -> List[Dict]:
        if topo_name:
            cls.fill_topo_name_to_process(process_list)
        if bound_template:
            cls.fill_config_template_binding_info_to_process(process_list)
        if proc_inst:
            cls.fill_proc_inst_to_process(process_list)
        return process_list

    @classmethod
    def parse_proc_template_params2cmdb_request_format(cls, process_property: Dict) -> Dict:
        """将进程模板操作参数转化为请求CMDB-API参数格式"""
        proc_template_cmdb_request_format = {}
        for key, value in process_property.items():
            # 前端传来的是字符串需要转换为int类型，否则ccapi会报错
            if key == "priority" and value is not None:
                value = int(value)

            proc_template_cmdb_request_format[key] = {"value": value, "as_default_value": value is not None}
            if key == "bind_info":
                bind_info_list = []
                for index, bind_info_value in enumerate(value):
                    bind_info = {
                        _key: {"value": _value, "as_default_value": _value is not None}
                        for _key, _value in bind_info_value.items()
                        if _key != "row_id"
                    }
                    if "row_id" in bind_info_value:
                        bind_info["row_id"] = bind_info_value["row_id"]
                    bind_info_list.append(bind_info)
                proc_template_cmdb_request_format[key] = {
                    "value": bind_info_list,
                    "as_default_value": bool(bind_info_list),
                }
        return proc_template_cmdb_request_format

    def scope_to_expression_scope(self, scope: Dict) -> Dict:
        """可DB筛选范围转化为表达式范围"""
        bk_process_names = scope.get("bk_process_names")
        bk_process_ids = scope.get("bk_process_ids")
        cmdb_handler = CMDBHandler(self.bk_biz_id)
        expression_scope = {}

        # 将筛选条件转化为表达式
        def parse_scope_field(nodes, ids, obj_prefix, expr_key):
            node_id_name_map = {node[f"{obj_prefix}_id"]: node[f"{obj_prefix}_name"] for node in nodes}
            expression_scope[expr_key] = (
                parse_list2expr([node_id_name_map[node_id] for node_id in ids if node_id in node_id_name_map])
                if ids
                else BuildInChar.ASTERISK
            )
            return ids or node_id_name_map.keys()

        set_ids_selected = parse_scope_field(
            nodes=cmdb_handler.set_list(scope["bk_set_env"]),
            ids=scope.get("bk_set_ids"),
            obj_prefix="bk_set",
            expr_key="bk_set_name",
        )
        module_ids_selected = parse_scope_field(
            nodes=cmdb_handler.module_list(bk_set_ids=set_ids_selected),
            ids=scope.get("bk_module_ids"),
            obj_prefix="bk_module",
            expr_key="bk_module_name",
        )
        parse_scope_field(
            nodes=cmdb_handler.fetch_service_instance_by_module_ids(module_ids_selected),
            ids=scope.get("bk_service_ids"),
            obj_prefix="service_instance",
            expr_key="service_instance_name",
        )
        expression_scope["bk_process_name"] = (
            parse_list2expr(bk_process_names) if bk_process_names else BuildInChar.ASTERISK
        )
        expression_scope["bk_process_id"] = parse_list2expr(bk_process_ids) if bk_process_ids else BuildInChar.ASTERISK
        expression_scope["bk_set_env"] = scope["bk_set_env"]
        return expression_scope

    def expression_scope_to_scope(self, expression_scope: Dict) -> Dict:
        """表达式范围转化为可DB筛选范围"""
        # 转化涉及输入表达式的修改，拷贝副本防止修改原表达式
        expression_scope = copy.deepcopy(expression_scope)

        candidate_processes = Process.objects.filter(
            bk_biz_id=self.bk_biz_id, bk_set_env=expression_scope["bk_set_env"]
        ).values("bk_process_id", "expression")

        expr_proc_id_map = {proc["expression"]: proc["bk_process_id"] for proc in candidate_processes}

        # 切片语法单独处理
        slice_expression = BuildInChar.ASTERISK
        if match.SLICE_PATTERN.match(expression_scope["bk_process_id"]):
            slice_expression = expression_scope["bk_process_id"]
            expression_scope["bk_process_id"] = BuildInChar.ASTERISK

        filter_exprs = match.list_match(list(expr_proc_id_map.keys()), gen_expression(expression_scope))
        bk_process_ids = [expr_proc_id_map[expr] for expr in filter_exprs]
        return {
            "bk_set_env": expression_scope["bk_set_env"],
            "bk_process_ids": match.execute_slice(bk_process_ids, slice_expression),
        }

    def list(
        self,
        process_queryset: QuerySet = None,
        scope: Dict = None,
        expression_scope: Dict = None,
        bk_cloud_ids: List[int] = None,
        bk_host_innerips: List[str] = None,
        process_status: int = None,
        searches: List[str] = None,
        is_auto: bool = None,
        process_status_list: List[str] = None,
        is_auto_list: List[bool] = None,
    ) -> QuerySet:
        # scope不为空情况下优先取，否则取表达式范围
        if scope is None:
            scope = self.expression_scope_to_scope(expression_scope)
            # scope对于空列表判定为全选，而表达式范围解析出进程列表为空表示无可选数据，此时返回空查询集
            if not scope["bk_process_ids"]:
                return Process.objects.none()
        bk_cloud_id__in = bk_cloud_ids
        bk_host_innerip__in = bk_host_innerips
        bk_set_env = scope.get("bk_set_env")
        bk_set_id__in = scope.get("bk_set_ids")
        bk_module_id__in = scope.get("bk_module_ids")
        service_instance_id__in = scope.get("bk_service_ids")
        bk_process_name__in = scope.get("bk_process_names")
        bk_process_id__in = scope.get("bk_process_ids")
        is_auto__in = is_auto_list
        process_status__in = process_status_list

        process_queryset = process_queryset or Process.objects.filter(bk_biz_id=self.bk_biz_id)
        bk_cloud_areas = CMDBHandler(self.bk_biz_id).get_or_cache_bk_cloud_area()
        # 多个模糊查询条件逻辑与叠加
        for search in searches or []:
            bk_cloud_ids_by_name_search = [
                cloud["bk_cloud_id"] for cloud in bk_cloud_areas if search in cloud["bk_cloud_name"]
            ]
            process_queryset = process_queryset.filter(
                Q(bk_host_innerip__contains=search) | Q(bk_cloud_id__in=bk_cloud_ids_by_name_search)
            )

        filter_condition = {}
        for filter_key in [
            "is_auto__in",
            "process_status__in",
            "bk_cloud_id__in",
            "bk_set_id__in",
            "bk_host_innerip__in",
            "bk_module_id__in",
            "bk_process_name__in",
            "service_instance_id__in",
            "bk_process_id__in",
            "process_status",
            "bk_set_env",
            "is_auto",
        ]:
            if locals()[filter_key] not in [None, []]:
                filter_condition.update({filter_key: locals()[filter_key]})

        return process_queryset.filter(**filter_condition)

    def process_instance(self, service_instance_id: int) -> List:
        """
        根据服务实例ID获取进程实例列表
        :param service_instance_id: 服务实例ID
        :return:
        """
        process_list = CCApi.list_process_instance(
            {"bk_biz_id": self.bk_biz_id, "service_instance_id": service_instance_id}
        )
        # 将relation中的process_template_id, bk_process_id提取到第一层级，便于填充配置信息
        for process in process_list:
            process["process_template_id"] = process["relation"]["process_template_id"]
            process["bk_process_id"] = process["relation"]["bk_process_id"]
        return self.fill_config_template_binding_info_to_process(process_list)

    def process_template(self, service_template_id: int) -> List:
        """
        根据服务模板ID获取进程模板列表
        :param service_template_id:
        :return:
        """
        process_template_list = batch_request(
            CCApi.list_proc_template, {"bk_biz_id": self.bk_biz_id, "service_template_id": service_template_id}
        )
        for process_template in process_template_list:
            # 把进程模板属性数据结构转为与进程实例结构一致
            process_template_property = process_template["property"]
            for key, value in process_template_property.items():
                process_template_property[key] = value.get("value")
                if key == "bind_info":
                    bind_info_list = []
                    for __, bind_info_value in enumerate(value.get("value") or []):
                        bind_info = {
                            _key: _value.get("value") for _key, _value in bind_info_value.items() if _key != "row_id"
                        }
                        bind_info["row_id"] = bind_info_value["row_id"]
                        bind_info_list.append(bind_info)
                    process_template_property[key] = bind_info_list
            process_template["bk_process_name"] = process_template_property["bk_process_name"]
            # 冗余process_template_id字段，方便填充配置文件信息
            process_template["process_template_id"] = process_template["id"]
        # 填充配置文件信息，并返回进程模板信息列表
        return self.fill_config_template_binding_info_to_process(process_template_list)

    def update_process_instance(self, process_property: Dict):
        return CCApi.update_process_instance({"bk_biz_id": self.bk_biz_id, "processes": [process_property]})

    def update_process_template(self, process_template_id: int, process_property: Dict):
        return CCApi.update_proc_template(
            {
                "bk_biz_id": self.bk_biz_id,
                "process_template_id": process_template_id,
                "process_property": self.parse_proc_template_params2cmdb_request_format(process_property),
            }
        )

    def create_process_instance(self, service_instance_id: int, process_property: Dict) -> List[int]:
        return CCApi.create_process_instance(
            {
                "bk_biz_id": self.bk_biz_id,
                "service_instance_id": service_instance_id,
                "processes": [{"process_info": process_property}],
            }
        )

    def create_process_template(self, service_template_id: int, process_property: Dict) -> List[int]:
        return CCApi.batch_create_proc_template(
            {
                "bk_biz_id": self.bk_biz_id,
                "service_template_id": service_template_id,
                "processes": [{"spec": self.parse_proc_template_params2cmdb_request_format(process_property)}],
            }
        )

    def delete_process_instance(self, process_instance_ids: List[int]):
        return CCApi.delete_process_instance(
            {"bk_biz_id": self.bk_biz_id, "process_instance_ids": process_instance_ids}
        )

    def delete_process_template(self, process_template_ids: List[int]):
        return CCApi.delete_proc_template({"bk_biz_id": self.bk_biz_id, "process_templates": process_template_ids})

    def get_module_id_service_template_id_map(self, process_list):
        # 获取模块下配置模板信息
        module_detail_list = CMDBHandler(bk_biz_id=self.bk_biz_id).find_obj_node_batch(
            CCApi.find_module_batch,
            [process["module"]["bk_module_id"] for process in process_list],
            fields=["service_template_id", "bk_module_id"],
        )
        module_id_service_template_id_map = {}
        for module_detail in module_detail_list:
            module_id_service_template_id_map[module_detail["bk_module_id"]] = module_detail.get("service_template_id")

        return module_id_service_template_id_map

    def sync_biz_process(self):
        """同步业务进程"""
        cmdb_handler = CMDBHandler(bk_biz_id=self.bk_biz_id)
        cmdb_handler.get_or_cache_bk_cloud_area(use_cache=False)

        exist_process_id_list = set(
            Process.objects.filter(bk_biz_id=self.bk_biz_id).values_list("bk_process_id", flat=True)
        )

        to_be_created_process = []
        to_be_deleted_process = []
        to_be_updated_process = []
        cmdb_process_id_list = []
        process_list = batch_request(CCApi.list_process_related_info, {"bk_biz_id": self.bk_biz_id})

        module_id_service_template_id_map = self.get_module_id_service_template_id_map(process_list)

        for process in process_list:
            bk_process_id = process["process"]["bk_process_id"]
            cmdb_process_id_list.append(bk_process_id)

            process_info = dict(
                bk_biz_id=self.bk_biz_id,
                bk_set_id=process["set"]["bk_set_id"],
                bk_set_env=process["set"]["bk_set_env"],
                bk_module_id=process["module"]["bk_module_id"],
                service_instance_id=process["service_instance"]["id"],
                service_template_id=module_id_service_template_id_map[process["module"]["bk_module_id"]],
                bk_process_id=bk_process_id,
                bk_host_innerip=process["host"]["bk_host_innerip"],
                bk_host_innerip_v6=process["host"].get("bk_host_innerip_v6"),
                bk_agent_id=process["host"].get("bk_agent_id"),
                bk_cloud_id=process["host"]["bk_cloud_id"],
                process_template_id=process["process_template"]["id"],
                bk_process_name=process["process"]["bk_process_name"],
                expression="{bk_set_name}{splitter}{bk_module_name}{splitter}"
                "{service_instance_name}{splitter}{bk_process_name}{splitter}{bk_process_id}".format(
                    bk_set_name=process["set"]["bk_set_name"],
                    bk_module_name=process["module"]["bk_module_name"],
                    service_instance_name=process["service_instance"]["name"],
                    bk_process_name=process["process"]["bk_process_name"],
                    bk_process_id=bk_process_id,
                    splitter=constants.EXPRESSION_SPLITTER,
                ),
            )

            if bk_process_id not in exist_process_id_list:
                to_be_created_process.append(Process(**process_info))
            else:
                to_be_updated_process.append(Process(**process_info))

        for process_id in exist_process_id_list:
            # 删除无需保存的进程
            if process_id not in cmdb_process_id_list:
                to_be_deleted_process.append(process_id)

        Process.objects.bulk_create(to_be_created_process, batch_size=constants.ORM_BATCH_SIZE)
        Process.objects.bulk_update(
            to_be_updated_process,
            fields=["bk_set_id", "bk_set_env", "bk_module_id", "bk_process_name", "expression"],
            batch_size=constants.ORM_BATCH_SIZE,
        )
        Process.objects.filter(bk_process_id__in=to_be_deleted_process).delete()

        logger.info(
            "[sync_biz_process] bk_biz_id: {bk_biz_id}, "
            "created_count: {created_count}, "
            "deleted_count:{deleted_count}".format(
                bk_biz_id=self.bk_biz_id,
                created_count=len(to_be_created_process),
                deleted_count=len(to_be_deleted_process),
            )
        )

        self.create_process_inst(process_list)

    def generate_process_inst_migrate_data(self, process_list: List) -> Dict:
        """计算准备好变更实例所需的数据"""

        local_inst_id_uniq_key_map = {}
        change_uniq_info_process_ids = set()
        # 本地缓存进程ID - 需保持一组进程实例唯一性信息 映射
        # 背景：模板进程修改需保存唯一性的信息（例如进程别名），存量的进程实例没有删除
        local_process_id_uniq_info_map: Dict[int, Dict[str, Union[str, int]]] = {}
        host_num_key_map: Dict[Union[int, ProcessInst]] = defaultdict(
            lambda: {"max_proc_num": ProcessInst.DEFAULT_PROC_NUM, "process": None}
        )
        # 本地数据中，模块下进程名对应最大的启动数量，用于判断模块下进程整体的 inst_id 和 local_inst_id 是否需要重建
        local_module_proc_name_map: Dict[Dict[Dict[int]]] = defaultdict(
            lambda: defaultdict(lambda: {"max_proc_num": ProcessInst.DEFAULT_PROC_NUM, "max_host_num": 0})
        )

        local_bk_process_ids = set()
        # 把进程按不同规则做映射，方便后续进行判断处理
        for local_process in ProcessInst.objects.filter(bk_biz_id=self.bk_biz_id):

            bk_module_id = local_process.bk_module_id
            bk_process_id = local_process.bk_process_id
            bk_process_name = local_process.bk_process_name

            # 构造缓存进程实例唯一性信息
            local_process_uniq_info = {"bk_process_name": bk_process_name, "bk_module_id": bk_module_id}

            if bk_process_id not in local_process_id_uniq_info_map:
                local_process_id_uniq_info_map[bk_process_id] = local_process_uniq_info
            else:
                # 同ID进程唯一性信息不一致，说明缓存有脏数据，记录进程ID后续重建全部实例
                if local_process_id_uniq_info_map[bk_process_id] != local_process_uniq_info:
                    change_uniq_info_process_ids.add(bk_process_id)
                    host_num_key_map.pop(local_process.bk_host_num_key, None)
                    # 进程实例需要重建，无需对脏数据执行下列计算，create_process_inst 在无记录下会对实例进行重建
                    continue

            local_inst_id_uniq_key_map[local_process.local_inst_id_uniq_key] = local_process
            host_num_key_map[local_process.bk_host_num_key] = {
                "max_proc_num": max(
                    host_num_key_map[local_process.bk_host_num_key]["max_proc_num"], local_process.proc_num
                ),
                "process": local_process,
            }
            local_module_proc_name_map[bk_module_id][bk_process_name] = {
                "max_proc_num": max(
                    local_module_proc_name_map[bk_module_id][bk_process_name]["max_proc_num"], local_process.proc_num
                ),
                "max_host_num": max(
                    local_module_proc_name_map[bk_module_id][bk_process_name]["max_host_num"], local_process.bk_host_num
                ),
            }
            local_bk_process_ids.add(bk_process_id)

        # 根据进程名分组获取进程名在模块下对应的进程数量的最大值
        cmdb_module_proc_name_map: Dict[Dict[Dict[Union[int, List]]]] = defaultdict(
            lambda: defaultdict(lambda: {"max_proc_num": ProcessInst.DEFAULT_PROC_NUM, "processes": []})
        )

        # CMDB实时业务进程ID列表
        cmdb_bk_process_ids = set()
        # 找到每个进程中最大的进程启动数量
        for cmdb_process in process_list:
            bk_module_id = cmdb_process["module"]["bk_module_id"]
            bk_process_id = cmdb_process["process"]["bk_process_id"]
            bk_process_name = cmdb_process["process"]["bk_process_name"]
            # 若CMDB进程未配置启动数量，则默认取 ProcessInst.DEFAULT_PROC_NUM
            cmdb_process["process"]["proc_num"] = cmdb_process["process"]["proc_num"] or ProcessInst.DEFAULT_PROC_NUM
            max_proc_num = max(
                cmdb_module_proc_name_map[bk_module_id][bk_process_name]["max_proc_num"],
                cmdb_process["process"]["proc_num"],
            )
            cmdb_module_proc_name_map[bk_module_id][bk_process_name]["max_proc_num"] = max_proc_num
            cmdb_module_proc_name_map[bk_module_id][bk_process_name]["processes"].append(cmdb_process)
            cmdb_bk_process_ids.add(cmdb_process["process"]["bk_process_id"])

            # 校验进程模板唯一性信息是否修改，如果修改需要重建该bk_process_id下的进程实例
            local_process_uniq_info = local_process_id_uniq_info_map.get(bk_process_id)

            if local_process_uniq_info != {"bk_process_name": bk_process_name, "bk_module_id": bk_module_id}:
                change_uniq_info_process_ids.add(bk_process_id)

        to_be_deleted_inst_condition = []
        # 计算无效进程ID并删除关联的进程实例
        # 无效进程ID：1. 存在于本地缓存但不存在于CMDB的进程ID 2. 唯一性字段变更（bk_process_name）
        invalid_bk_process_ids = (local_bk_process_ids - cmdb_bk_process_ids) | change_uniq_info_process_ids
        if invalid_bk_process_ids:
            to_be_deleted_inst_condition.append(Q(bk_process_id__in=invalid_bk_process_ids))

        return {
            "local_module_proc_name_map": local_module_proc_name_map,
            "local_inst_id_uniq_key_map": local_inst_id_uniq_key_map,
            "host_num_key_map": host_num_key_map,
            "cmdb_module_proc_name_map": cmdb_module_proc_name_map,
            "to_be_deleted_inst_condition": to_be_deleted_inst_condition,
        }

    def create_process_inst(self, process_list: List):
        """根据进程数量生成调整进程实例"""
        migrate_data = self.generate_process_inst_migrate_data(process_list)
        local_module_proc_name_map = migrate_data["local_module_proc_name_map"]
        local_inst_id_uniq_key_map = migrate_data["local_inst_id_uniq_key_map"]
        host_num_key_map = migrate_data["host_num_key_map"]
        cmdb_module_proc_name_map = migrate_data["cmdb_module_proc_name_map"]
        to_be_deleted_inst_condition = migrate_data["to_be_deleted_inst_condition"]

        # 根据进程启动数量创建进程实例，规则如下：
        # inst_id: 进程实例的作用域对应的实例 ID，从 1 开始顺序编号，不同服务器之间唯一
        # bk_host_num: 主机编号，从 1 开始顺序编号
        # max_proc_num: 当前拓扑结构下单机进程启动数最大值
        # local_inst_id: 同一服务器内从 1 开始顺序编号，同一服务器内唯一，不同服务器间不唯一
        # inst_id = (bk_host_num - 1) * max_proc_num + local_inst_id
        to_be_created_inst = []
        for bk_module_id, cmdb_process_name_map in cmdb_module_proc_name_map.items():
            for process_name, processes in cmdb_process_name_map.items():
                max_proc_num = processes["max_proc_num"]

                if max_proc_num != local_module_proc_name_map[bk_module_id][process_name]["max_proc_num"]:
                    # 若最大进程数量有调整，说明此进程的所有inst_id等需要重建
                    to_be_deleted_inst_condition.append(
                        Q(bk_module_id=bk_module_id, bk_biz_id=self.bk_biz_id, bk_process_name=process_name)
                    )
                    index = 0
                    for cmdb_process in processes["processes"]:
                        cmdb_proc_num = cmdb_process["process"]["proc_num"]
                        for local_inst_id in range(1, cmdb_proc_num + 1):
                            bk_host_num = index + 1
                            inst_id = (bk_host_num - 1) * max_proc_num + local_inst_id
                            local_inst_id_key = ProcessInst.LOCAL_INST_ID_UNIQ_KEY_TMPL.format(
                                bk_host_innerip=cmdb_process["host"]["bk_host_innerip"]
                                or cmdb_process["host"].get("bk_host_innerip_v6"),
                                bk_cloud_id=cmdb_process["host"]["bk_cloud_id"],
                                bk_process_name=process_name,
                                local_inst_id=local_inst_id,
                            )
                            to_be_created_inst.append(
                                ProcessInst(
                                    bk_biz_id=self.bk_biz_id,
                                    bk_host_num=bk_host_num,
                                    bk_module_id=cmdb_process["module"]["bk_module_id"],
                                    bk_host_innerip_v6=cmdb_process["host"].get("bk_host_innerip_v6"),
                                    bk_agent_id=cmdb_process["host"].get("bk_agent_id"),
                                    bk_cloud_id=cmdb_process["host"]["bk_cloud_id"],
                                    bk_process_id=cmdb_process["process"]["bk_process_id"],
                                    bk_process_name=cmdb_process["process"]["bk_process_name"],
                                    inst_id=inst_id,
                                    local_inst_id=local_inst_id,
                                    local_inst_id_uniq_key=local_inst_id_key,
                                    proc_num=cmdb_proc_num,
                                )
                            )
                        index += 1
                else:
                    # 若最大进程数量没有调整，继续判断进程中的进程数量是否有变更
                    max_host_num = local_module_proc_name_map[bk_module_id][process_name]["max_host_num"]
                    for cmdb_process in processes["processes"]:
                        bk_host_innerip = cmdb_process["host"]["bk_host_innerip"]
                        bk_host_innerip_v6 = cmdb_process["host"].get("bk_host_innerip_v6")
                        bk_agent_id = cmdb_process["host"].get("bk_agent_id")
                        bk_cloud_id = cmdb_process["host"]["bk_cloud_id"]
                        host_num_key = ProcessInst.BK_HOST_NUM_KEY_TMPL.format(
                            bk_host_innerip=bk_host_innerip or bk_host_innerip_v6,
                            bk_cloud_id=bk_cloud_id,
                            bk_process_name=process_name,
                        )

                        cmdb_proc_num = cmdb_process["process"]["proc_num"]

                        if host_num_key in host_num_key_map:
                            # host num 已存在，若proc_num有调整，则进行调整
                            local_process = host_num_key_map[host_num_key]["process"]
                            local_max_proc_num = host_num_key_map[host_num_key]["max_proc_num"]

                            # CMDB中增加进程数量
                            if cmdb_proc_num > local_max_proc_num:
                                for local_inst_id in range(1, cmdb_proc_num + 1):
                                    inst_id = (local_process.bk_host_num - 1) * max_proc_num + local_inst_id
                                    local_inst_id_key = ProcessInst.LOCAL_INST_ID_UNIQ_KEY_TMPL.format(
                                        bk_host_innerip=bk_host_innerip or bk_host_innerip_v6,
                                        bk_cloud_id=bk_cloud_id,
                                        bk_process_name=process_name,
                                        local_inst_id=local_inst_id,
                                    )
                                    if local_inst_id_key not in local_inst_id_uniq_key_map:
                                        to_be_created_inst.append(
                                            ProcessInst(
                                                bk_biz_id=self.bk_biz_id,
                                                bk_host_num=local_process.bk_host_num,
                                                bk_module_id=bk_module_id,
                                                bk_host_innerip=bk_host_innerip,
                                                bk_host_innerip_v6=bk_host_innerip_v6,
                                                bk_agent_id=bk_agent_id,
                                                bk_cloud_id=bk_cloud_id,
                                                bk_process_id=cmdb_process["process"]["bk_process_id"],
                                                bk_process_name=process_name,
                                                inst_id=inst_id,
                                                local_inst_id_uniq_key=local_inst_id_key,
                                                local_inst_id=local_inst_id,
                                                proc_num=cmdb_proc_num,
                                            )
                                        )

                            # CMDB中减少进程数量，多余的需要被删除
                            if cmdb_proc_num < local_max_proc_num:
                                to_be_deleted_inst_condition.append(
                                    Q(
                                        bk_module_id=bk_module_id,
                                        bk_host_innerip=bk_host_innerip,
                                        bk_host_innerip_v6=bk_host_innerip_v6,
                                        bk_agent_id=bk_agent_id,
                                        bk_cloud_id=bk_cloud_id,
                                        bk_process_name=process_name,
                                        local_inst_id__gt=cmdb_proc_num,
                                        local_inst_id__lte=local_max_proc_num,
                                    )
                                )
                        else:
                            # host num 不存在，从 max_host_num 开始新增
                            for local_inst_id in range(1, cmdb_proc_num + 1):
                                bk_host_num = max_host_num + 1
                                inst_id = (bk_host_num - 1) * max_proc_num + local_inst_id
                                local_inst_id_key = ProcessInst.LOCAL_INST_ID_UNIQ_KEY_TMPL.format(
                                    bk_host_innerip=bk_host_innerip or bk_host_innerip_v6,
                                    bk_cloud_id=bk_cloud_id,
                                    bk_process_name=process_name,
                                    local_inst_id=local_inst_id,
                                )
                                to_be_created_inst.append(
                                    ProcessInst(
                                        bk_biz_id=self.bk_biz_id,
                                        bk_host_num=bk_host_num,
                                        bk_module_id=bk_module_id,
                                        bk_host_innerip=bk_host_innerip,
                                        bk_host_innerip_v6=bk_host_innerip_v6,
                                        bk_agent_id=bk_agent_id,
                                        bk_cloud_id=bk_cloud_id,
                                        bk_process_id=cmdb_process["process"]["bk_process_id"],
                                        bk_process_name=process_name,
                                        inst_id=inst_id,
                                        local_inst_id_uniq_key=local_inst_id_key,
                                        local_inst_id=local_inst_id,
                                        proc_num=cmdb_proc_num,
                                    )
                                )
                        max_host_num += 1

        # 检查待创建实例中不符合唯一键的项
        uniq_key_set = set()
        duplicate_proc_instances = set()
        for inst in to_be_created_inst:
            if inst.local_inst_id_uniq_key in uniq_key_set:
                duplicate_proc_instances.add(inst.local_inst_id_uniq_key)
                continue
            uniq_key_set.add(inst.local_inst_id_uniq_key)

        # 存在重复进程实例
        if duplicate_proc_instances:
            raise DuplicateProcessInstException(uniq_key=duplicate_proc_instances)

        with transaction.atomic():
            if to_be_deleted_inst_condition:
                ProcessInst.objects.filter(reduce(operator.or_, to_be_deleted_inst_condition)).delete()
            ProcessInst.objects.bulk_create(to_be_created_inst, batch_size=constants.ORM_BATCH_SIZE)

    def sync_proc_status_to_db(self, proc_status_infos=None):
        """
        同步业务进程状态
        :return:
        """
        # 不传proc_status_infos默认拉取sync_proc_status接口数据，该接口有5min状态延迟
        if not proc_status_infos:
            proc_status_infos = batch_request(
                GseApi.sync_proc_status,
                {"meta": {"namespace": NAMESPACE.format(bk_biz_id=self.bk_biz_id)}},
                get_data=lambda x: x["proc_infos"],
            )
            # 对于gse，0,2都是终止状态
            for proc_status_info in proc_status_infos:
                if proc_status_info["status"] == Process.ProcessStatus.UNREGISTERED:
                    proc_status_info["status"] = Process.ProcessStatus.TERMINATED
                # 统一is_auto字段
                proc_status_info["is_auto"] = proc_status_info["isauto"]
                proc_status_info["inst_uniq_key"] = (
                    f"{proc_status_info['host']['ip']}-{proc_status_info['host']['bk_cloud_id']}-"
                    f"{'-'.join(proc_status_info['meta']['name'].rsplit('_', 1))}"
                )

        cmdb_proc_id_status_map = {}
        cmdb_proc_id_is_auto_map = {}
        all_bk_process_ids = []
        for cmdb_proc in Process.objects.filter(bk_biz_id=self.bk_biz_id).values(
            "process_status", "bk_process_id", "is_auto"
        ):
            cmdb_proc_id_status_map[cmdb_proc["bk_process_id"]] = cmdb_proc["process_status"]
            cmdb_proc_id_is_auto_map[cmdb_proc["bk_process_id"]] = cmdb_proc["is_auto"]
            all_bk_process_ids.append(cmdb_proc["bk_process_id"])

        bk_process_ids_exists_inst = set()
        inst_uniq_key_proc_id_map = {}
        inst_uniq_key_is_auto_map = {}
        inst_uniq_key_group_by_inst_status = defaultdict(list)
        for proc_inst in ProcessInst.objects.filter(bk_biz_id=self.bk_biz_id).values(
            "local_inst_id_uniq_key", "process_status", "bk_process_id", "is_auto"
        ):
            inst_uniq_key_proc_id_map[proc_inst["local_inst_id_uniq_key"]] = proc_inst["bk_process_id"]
            inst_uniq_key_is_auto_map[proc_inst["local_inst_id_uniq_key"]] = proc_inst["is_auto"]
            inst_uniq_key_group_by_inst_status[proc_inst["process_status"]].append(proc_inst["local_inst_id_uniq_key"])
            bk_process_ids_exists_inst.add(proc_inst["bk_process_id"])

        effective_uniq_keys = []
        all_terminated_uniq_keys = []
        proc_status_infos.sort(key=lambda proc_status: proc_status["status"])
        proc_status_info_group_by_status = groupby(proc_status_infos, lambda proc_status: proc_status["status"])
        # 只会有两个状态，RUNNING or TERMINATED
        for status, proc_status_info_list in proc_status_info_group_by_status:
            inst_uniq_keys_in_db = [proc_status_info["inst_uniq_key"] for proc_status_info in proc_status_info_list]
            # sync_proc_status非即时接口，需要过滤掉不在DB的数据
            inst_uniq_keys_in_db = [
                uniq_key for uniq_key in inst_uniq_keys_in_db if uniq_key in inst_uniq_key_proc_id_map
            ]
            effective_uniq_keys.extend(inst_uniq_keys_in_db)
            # 全部uniq_keys与某状态下原先的进程实例uniq_keys取差集，获得需要更新状态的进程实例
            to_be_updated_proc_inst_status_uniq_keys = set(inst_uniq_keys_in_db) - set(
                inst_uniq_key_group_by_inst_status[status]
            )
            ProcessInst.objects.filter(local_inst_id_uniq_key__in=to_be_updated_proc_inst_status_uniq_keys).update(
                process_status=status
            )

            if status == Process.ProcessStatus.TERMINATED:
                all_terminated_uniq_keys = inst_uniq_keys_in_db

        # 获得所有状态为TERMINATED的进程后，可以反推汇总状态，同步规则如下：
        # 1. 进程下任意实例终止，汇总状态为TERMINATED 2. 进程下无实例，汇总状态为TERMINATED
        # 3. 排除掉1. 2. 两种情况，其他的进程状态都为RUNNING
        all_terminated_proc_ids = set()
        to_be_updated_terminated_proc_ids = set()
        for uniq_key in all_terminated_uniq_keys:
            bk_process_id = inst_uniq_key_proc_id_map[uniq_key]
            # 统计所有存在终止进程实例的进程ID
            all_terminated_proc_ids.add(bk_process_id)
            # 与已有进程状态对比，统计需要变更汇总状态的进程ID
            if cmdb_proc_id_status_map[bk_process_id] != Process.ProcessStatus.TERMINATED:
                to_be_updated_terminated_proc_ids.add(bk_process_id)

        # CMDB进程下无进程实例 or 任一实例为未运行，进程汇总状态为TERMINATED，其余情况都是RUNNING
        all_without_inst_proc_ids = set(all_bk_process_ids) - bk_process_ids_exists_inst
        Process.objects.filter(bk_process_id__in=all_without_inst_proc_ids | to_be_updated_terminated_proc_ids).update(
            process_status=Process.ProcessStatus.TERMINATED
        )

        # 计算出gse.sync_proc_status查询不到的
        proc_without_status_ids = set(
            [
                bk_process_id
                for uniq_key, bk_process_id in inst_uniq_key_proc_id_map.items()
                if uniq_key not in effective_uniq_keys
            ]
        )
        # 计算出进程汇总状态为RUNNING的进程ID
        all_running_proc_ids = (
            set(all_bk_process_ids) - all_terminated_proc_ids - all_without_inst_proc_ids - proc_without_status_ids
        )
        to_be_updated_running_proc_ids = set()
        for bk_process_id in all_running_proc_ids:
            # 计算需要变更为RUNNING的进程ID
            if cmdb_proc_id_status_map[bk_process_id] != Process.ProcessStatus.RUNNING:
                to_be_updated_running_proc_ids.add(bk_process_id)
        Process.objects.filter(bk_process_id__in=to_be_updated_running_proc_ids).update(
            process_status=Process.ProcessStatus.RUNNING
        )

        effective_uniq_keys = set(effective_uniq_keys)
        all_noauto_proc_ids = set()
        to_be_updated_auto_field_uniq_keys = []
        to_be_updated_noauto_proc_ids = set()
        # 更新托管状态
        for proc_status_info in proc_status_infos:
            uniq_key = proc_status_info["inst_uniq_key"]
            if uniq_key not in effective_uniq_keys:
                continue

            bk_process_id = inst_uniq_key_proc_id_map[uniq_key]

            if not proc_status_info["is_auto"]:
                all_noauto_proc_ids.add(bk_process_id)

            if proc_status_info["is_auto"] != inst_uniq_key_is_auto_map[uniq_key]:
                to_be_updated_auto_field_uniq_keys.append(uniq_key)
                if not proc_status_info["is_auto"] and cmdb_proc_id_is_auto_map[bk_process_id]:
                    to_be_updated_noauto_proc_ids.add(bk_process_id)

        # 更新进程实例状态
        ProcessInst.objects.filter(local_inst_id_uniq_key__in=to_be_updated_auto_field_uniq_keys).update(
            is_auto=Q(is_auto=False)
        )

        bk_process_ids_without_inst = set(all_bk_process_ids) - bk_process_ids_exists_inst
        # 更新进程为未托管状态： 1. 变更为未托管的进程实例 2.不存在实例的进程
        Process.objects.filter(bk_process_id__in=(to_be_updated_noauto_proc_ids | bk_process_ids_without_inst)).update(
            is_auto=False
        )

        # 计算出gse.sync_proc_status查询不到的
        bk_process_ids_no_found = set(
            [
                bk_process_id
                for uniq_key, bk_process_id in inst_uniq_key_proc_id_map.items()
                if uniq_key not in effective_uniq_keys
            ]
        )

        all_auto_proc_ids = (
            set(all_bk_process_ids) - bk_process_ids_no_found - bk_process_ids_without_inst - all_noauto_proc_ids
        )
        to_be_updated_auto_proc_ids = [
            proc_id for proc_id in all_auto_proc_ids if not cmdb_proc_id_is_auto_map[proc_id]
        ]
        Process.objects.filter(bk_process_id__in=to_be_updated_auto_proc_ids).update(is_auto=True)

    @staticmethod
    def get_proc_inst_status_infos(proc_inst_infos, _request=None) -> List[Dict]:
        base_params = {"_request": _request} if _request else {}
        proc_operate_req_slice = []
        meta_key_uniq_key_map = {}
        for proc_inst_info in proc_inst_infos:
            host_info = proc_inst_info["host_info"]
            process_info = proc_inst_info["process_info"]
            set_info = proc_inst_info["set_info"]
            module_info = proc_inst_info["module_info"]
            inst_id = proc_inst_info["inst_id"]
            local_inst_id = proc_inst_info["local_inst_id"]
            context = {
                "inst_id": inst_id,
                "inst_id_0": inst_id - 1,
                "local_inst_id": local_inst_id,
                "local_inst_id0": local_inst_id - 1,
                "bk_set_name": set_info["bk_set_name"],
                "bk_module_name": module_info["bk_module_name"],
                "bk_process_name": process_info["bk_process_name"],
                # 兼容老版本字段
                "InstID": inst_id,
                "InstID0": inst_id - 1,
                "LocalInstID": local_inst_id,
                "LocalInstID0": local_inst_id - 1,
                "SetName": set_info["bk_set_name"],
                "ModuleName": module_info["bk_module_name"],
                "FuncID": process_info["bk_process_name"],
            }
            namespace = NAMESPACE.format(bk_biz_id=process_info["bk_biz_id"])
            uniq_key = ProcessInst.LOCAL_INST_ID_UNIQ_KEY_TMPL.format(
                bk_host_innerip=host_info["bk_host_innerip"] or host_info.get("bk_host_innerip_v6"),
                bk_cloud_id=host_info["bk_cloud_id"],
                bk_process_name=process_info["bk_process_name"],
                local_inst_id=local_inst_id,
            )
            meta_key = (
                f"{host_info['bk_cloud_id']}:{host_info['bk_host_innerip']}:"
                f"{namespace}:{process_info['bk_process_name']}_{local_inst_id}"
            )

            meta_key_uniq_key_map[meta_key] = uniq_key
            proc_operate_req_slice.append(
                {
                    "meta": {
                        "namespace": namespace,
                        "name": f"{process_info['bk_process_name']}_{local_inst_id}",
                        "labels": {
                            "bk_process_name": process_info["bk_process_name"],
                            "bk_process_id": process_info["bk_process_id"],
                        },
                    },
                    "op_type": GseOpType.CHECK,
                    "hosts": [{"ip": host_info["bk_host_innerip"], "bk_cloud_id": host_info["bk_cloud_id"]}],
                    "spec": {
                        "identity": {
                            "index_key": "",
                            "proc_name": process_info["bk_func_name"],
                            "setup_path": mako_render(process_info["work_path"] or "", context),
                            "pid_path": mako_render(process_info["pid_file"] or "", context),
                            "user": process_info["user"],
                        },
                        "control": {
                            "start_cmd": mako_render(process_info["start_cmd"] or "", context),
                            "stop_cmd": mako_render(process_info["stop_cmd"] or "", context),
                            "restart_cmd": mako_render(process_info["restart_cmd"] or "", context),
                            "reload_cmd": mako_render(process_info["reload_cmd"] or "", context),
                            "kill_cmd": mako_render(process_info["face_stop_cmd"] or "", context),
                        },
                        "alive_monitor_policy": {
                            "auto_type": GseAutoType.RESIDENT,
                            # 缺省取gse接口设定的默认值
                            "start_check_secs": process_info.get("bk_start_check_secs", 5),
                            "op_timeout": process_info.get("timeout"),
                        },
                    },
                }
            )

        gse_task_id = GseApi.operate_proc_multi({"proc_operate_req": proc_operate_req_slice, **base_params})["task_id"]

        proc_inst_status_infos = []
        uniq_keys_recorded = set()
        poll_time, interval, timeout = 0, 1.5, 60
        while True:
            try:
                gse_api_result = GseApi.get_proc_operate_result({"task_id": gse_task_id, **base_params})
            except Exception as error:
                logger.error(
                    "[sync_biz_process_status | get_proc_inst_status_infos] "
                    "gse_task_id: {gse_task_id}, error: {error}".format(gse_task_id=gse_task_id, error=str(error))
                )
                poll_time += 2 * interval
                if poll_time > timeout:
                    break
                time.sleep(interval)
                continue

            for meta_key, task_result in gse_api_result.items():
                if meta_key_uniq_key_map[meta_key] in uniq_keys_recorded:
                    continue
                if task_result.get("error_code") == GseDataErrorCode.SUCCESS:
                    gse_ip_proc_info = json.loads(task_result["content"])
                    proc_inst_status_infos.append(
                        {
                            "is_auto": gse_ip_proc_info["process"][0]["instance"][0].get("isAuto", False),
                            "status": (
                                Process.ProcessStatus.RUNNING
                                if gse_ip_proc_info["process"][0]["instance"][0].get("pid", -1) > 0
                                else Process.ProcessStatus.TERMINATED
                            ),
                            "inst_uniq_key": meta_key_uniq_key_map[meta_key],
                        }
                    )
                    uniq_keys_recorded.add(meta_key_uniq_key_map[meta_key])
                elif task_result.get("error_code") != GseDataErrorCode.RUNNING:
                    uniq_keys_recorded.add(meta_key_uniq_key_map[meta_key])

            if any([len(uniq_keys_recorded) == len(gse_api_result.keys()), poll_time > timeout]):
                break
            time.sleep(interval)
            poll_time += interval

        if len(proc_inst_status_infos) != len(proc_inst_infos):
            # TODO: 是否拉起异步任务重试
            total_uniq_keys = set(meta_key_uniq_key_map.values())
            success_uniq_keys = set([info["inst_uniq_key"] for info in proc_inst_status_infos])
            logger.error(
                "[sync_biz_process_status | get_proc_inst_status_infos] gse_task_id: {gse_task_id}, "
                "check_number: {check_number}, failed_uniq_keys: {uniq_keys_failed}, "
                "timeout: {uniq_keys_timeout}".format(
                    gse_task_id=gse_task_id,
                    check_number=len(total_uniq_keys),
                    uniq_keys_failed=uniq_keys_recorded - success_uniq_keys,
                    uniq_keys_timeout=total_uniq_keys - uniq_keys_recorded,
                )
            )
        else:
            logger.info(
                "[sync_biz_process_status | get_proc_inst_status_infos] gse_task_id: {gse_task_id}, "
                "poll_time: {poll_time}s, check_number: {check_number}".format(
                    gse_task_id=gse_task_id, poll_time=poll_time, check_number=len(proc_inst_status_infos)
                )
            )
        return proc_inst_status_infos

    def sync_biz_process_status(self):

        begin_time = time.time()

        process_related_infos = batch_request(CCApi.list_process_related_info, {"bk_biz_id": self.bk_biz_id})
        bk_process_ids = [process_info["process"]["bk_process_id"] for process_info in process_related_infos]
        proc_inst_map = defaultdict(list)
        for proc_inst in ProcessInst.objects.filter(bk_process_id__in=bk_process_ids).values(
            "bk_process_id", "inst_id", "local_inst_id", "process_status"
        ):
            proc_inst_map[proc_inst["bk_process_id"]].append(
                {"inst_id": proc_inst["inst_id"], "local_inst_id": proc_inst["local_inst_id"]}
            )

        proc_inst_infos = []
        for process_related_info in process_related_infos:
            bk_process_id = process_related_info["process"]["bk_process_id"]
            for proc_inst in proc_inst_map[bk_process_id]:
                proc_inst_infos.append(
                    {
                        "host_info": process_related_info["host"],
                        "process_info": process_related_info["process"],
                        "set_info": process_related_info["set"],
                        "module_info": process_related_info["module"],
                        "inst_id": proc_inst["inst_id"],
                        "local_inst_id": proc_inst["local_inst_id"],
                    }
                )

        # 片起始位置，分片大小
        limit = 1000
        params_list = [
            dict(proc_inst_infos=proc_inst_infos[start : start + limit])
            for start in range(0, len(proc_inst_infos), limit)
        ]
        proc_status_infos = request_multi_thread(
            self.get_proc_inst_status_infos, params_list, get_data=lambda x: x, get_request_target=lambda x: x
        )

        # 更新进程实例状态并汇总到Process
        self.sync_proc_status_to_db(proc_status_infos)

        cost_time = time.time() - begin_time
        logger.info("[sync_proc_status] cost: {cost_time}s".format(cost_time=cost_time))
        return {"cost_time": cost_time}

    def process_instance_simple(
        self,
        scope: Dict = None,
        expression_scope: Dict = None,
        service_instance_ids: List = None,
        expression: str = BuildInChar.ASTERISK,
    ) -> List:
        """根据服务实例ID获取进程实例列表"""
        # TODO: 兼容原接口逻辑, 前端改动后删除
        if service_instance_ids is not None:
            process_queryset = self.list(scope={"bk_service_ids": service_instance_ids})
            processes = process_queryset.values("bk_process_id", "bk_process_name")
            return [process for process in processes if match.match(process["bk_process_name"], expression)]
        return list(
            self.list(scope=scope, expression_scope=expression_scope).values("bk_process_name", "bk_process_id")
        )

    def process_info(self, bk_process_id):

        process_list = (
            CCApi.list_process_related_info(
                {
                    "bk_biz_id": self.bk_biz_id,
                    "page": {"start": 0, "limit": 1},
                    "process_property_filter": {
                        "condition": "AND",
                        "rules": [{"field": "bk_process_id", "operator": "equal", "value": bk_process_id}],
                    },
                }
            ).get("info")
            or []
        )
        if not process_list:
            raise ProcessDoseNotExistException(bk_process_id=bk_process_id)
        process = process_list[0]
        cc_process_id = process["process"]["bk_process_id"]
        if cc_process_id != bk_process_id:
            # 当 CCApi.list_process_related_info 接口变更或不符合预期时，可能触发此异常，请确认接口参数和返回，
            # 若有疑问请联系 CMDB 排查
            raise ProcessNotMatchException(user_bk_process_id=bk_process_id, cc_bk_process_id=cc_process_id)
        return process_list[0]
