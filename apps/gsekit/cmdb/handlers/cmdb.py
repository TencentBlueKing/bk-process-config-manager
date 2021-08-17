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
from collections import defaultdict
from itertools import groupby
from typing import Dict, List, Set, Any
from xml.dom.minidom import Document, Element

from blueapps.account.models import User
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from lxml import etree

from apps.api import CCApi
from apps.gsekit import constants as gsetkit_const
from apps.gsekit.cmdb import constants
from apps.gsekit.constants import EXPRESSION_SPLITTER
from apps.gsekit.process.models import Process
from apps.gsekit.utils.expression_utils import match
from apps.gsekit.utils.expression_utils.parse import BuildInChar
from apps.iam import Permission, ActionEnum
from apps.utils.basic import distinct_dict_list
from apps.utils.batch_request import batch_request, request_multi_thread

# extend xpath function
from apps.utils.local import get_request


def tokenize(context, string, split_token):
    if type(string) is list:
        string = string[0]
    return string.split(split_token)


def contains(context, s_list, s_sub):
    return s_sub in s_list


ns = etree.FunctionNamespace(None)
ns["lcontains"] = contains
ns["tokenize"] = tokenize


class CMDBHandler(object):
    CACHE_KEY_TEMPLATE = "{bk_obj_id}_{bk_inst_id}_name"
    CACHE_GLOBAL_VAR_TEMPLATE = "gsekit:cmdb:biz:{bk_biz_id}:global_variables"
    CACHE_TOPO_ATTR_TEMPLATE = "gsekit:cmdb:biz:{bk_biz_id}:topo_tree_attributes"
    CACHE_CLOUD_TEMPLATE = "gsekit:cmdb:biz:{bk_biz_id}:clouds"
    BK_BIZ_OBJ_ID = "biz"
    BK_SET_OBJ_ID = "set"
    BK_MODULE_OBJ_ID = "module"
    BK_HOST_OBJ_ID = "host"
    BK_SERVICE_OBJ_ID = "service"
    BK_PROCESS_OBJ_ID = "process"
    BK_FUNC_OBJ_ID = "func"
    BK_HOST_IP_OBJ_ID = "host_ip"
    BK_CLOUD_OBJ_ID = "cloud"
    BK_GLOBAL_OBJ_ID = "global"

    BK_OBJ_ID_CHOICES = (
        (BK_BIZ_OBJ_ID, _("业务")),
        (BK_SET_OBJ_ID, _("集群")),
        (BK_MODULE_OBJ_ID, _("模块")),
        (BK_HOST_OBJ_ID, _("主机")),
        (BK_PROCESS_OBJ_ID, _("进程")),
    )

    # 内置常用字段
    BK_SYSTEM_COMMON_ATTRIBUTE = {
        BK_SET_OBJ_ID: [
            "bk_set_name",
            "bk_set_env",
            "bk_service_status",
            "bk_world_id",
            "bk_platform",
            "bk_system",
            "bk_chn_name",
            "bk_category",
        ],
        BK_MODULE_OBJ_ID: ["bk_module_name", "bk_module_type"],
        BK_HOST_OBJ_ID: ["bk_host_innerip", "bk_host_name", "operator", "bk_cloud_id"],
    }

    def __init__(self, bk_biz_id: int = None):
        super().__init__()
        self.bk_biz_id = int(bk_biz_id)

    @staticmethod
    def biz_list(user: User) -> List:
        """当前用户有权限的业务列表"""
        all_biz_list = CCApi.search_business({"fields": ["bk_biz_id", "bk_biz_name"]}, use_admin=True).get("info") or []
        allowed_biz_list = Permission(user.username).filter_business_list_by_action(
            ActionEnum.VIEW_BUSINESS, all_biz_list
        )
        allowed_biz_id_list = {biz["bk_biz_id"] for biz in allowed_biz_list}
        for biz in all_biz_list:
            biz["permission"] = {ActionEnum.VIEW_BUSINESS.id: biz["bk_biz_id"] in allowed_biz_id_list}

        return all_biz_list

    @staticmethod
    def map_cc3_field_to_cc1(new_field_name: str) -> str:
        """
        映射CC3.0的字段 到 CC1.0的字段，兼容老的字段
        :param new_field_name: CC3.0的新字段名
        :return: old_field_name: CC1.0的老字段名
        """
        field_name_mapping = {
            # set
            "bk_set_name": "SetName",
            "bk_set_env": "SetEnviType",
            "bk_world_id": "SetWorldID",
            "bk_platform": "Platform",
            "bk_system": "System",
            "bk_chn_name": "SetChnName",
            "bk_service_status": "SetServiceState",
            "bk_set_id": "SetID",
            "bk_category": "SetCategory",
            # module
            "bk_module_name": "ModuleName",
            "bk_module_id": "ModuleID",
            # host
            "bk_host_innerip": "InnerIP",
            "bk_host_name": "HostName",
        }
        old_field_name = field_name_mapping.get(new_field_name, new_field_name)
        return old_field_name

    @staticmethod
    def relations_group_by(relations: List[Dict], key: str, get_data=lambda relation: relation) -> Dict[int, List[Any]]:
        relations_group_by_key = groupby(
            sorted(relations, key=lambda relation: relation[key]), lambda relation: relation[key]
        )
        key_relations_map = {
            key: [get_data(relation) for relation in sub_relations] for key, sub_relations in relations_group_by_key
        }
        return key_relations_map

    def set_attr_to_xml_element(self, xml_element: Element, attr_dict: Dict, topo_variables: List):
        if attr_dict is None:
            return
        for attr_key, attr_value in attr_dict.items():
            if not isinstance(attr_value, (list, tuple, dict)):
                # attr_value 需都转为字符串
                xml_element.setAttribute(attr_key, "%s" % attr_value)
                # 设置老字段
                old_field_name = self.map_cc3_field_to_cc1(attr_key)
                xml_element.setAttribute(old_field_name, "%s" % attr_value)

        for var in topo_variables:
            # CMDB部分字段连key都没有，这里默认填充为空字符串
            attr_key = self.map_cc3_field_to_cc1(var["bk_property_id"])
            xml_element_keys = xml_element.attributes.keys()
            if attr_key not in xml_element_keys:
                xml_element.setAttribute(attr_key, "")

    def get_or_cache_bk_cloud_area(self, use_cache: bool = True):
        """缓存云区域
        该方法目前置于process.sync_biz_process下定时更新缓存(use_cache=False)
        """
        cloud_areas = cache.get(self.CACHE_CLOUD_TEMPLATE.format(bk_biz_id=self.bk_biz_id)) if use_cache else None
        if cloud_areas:
            return cloud_areas

        cloud_areas = [
            {"bk_cloud_id": cloud["bk_cloud_id"], "bk_cloud_name": cloud["bk_cloud_name"]}
            for cloud in batch_request(CCApi.search_cloud_area, {})
        ]
        # 缓存云区域信息
        cache.set(
            self.CACHE_CLOUD_TEMPLATE.format(bk_biz_id=self.bk_biz_id), cloud_areas, gsetkit_const.CacheExpire.HOUR
        )
        return cloud_areas

    def cache_topo_tree_attr(self, bk_set_env: str):
        """缓存业务拓扑树属性"""
        biz_global_variables = self.biz_global_variables()
        topo_tree_info = CCApi.find_biz_tree_brief_info(
            {
                "bk_biz_id": self.bk_biz_id,
                "set_fields": [prop["bk_property_id"] for prop in biz_global_variables[self.BK_SET_OBJ_ID]],
                "module_fields": [prop["bk_property_id"] for prop in biz_global_variables[self.BK_MODULE_OBJ_ID]],
                "host_fields": [prop["bk_property_id"] for prop in biz_global_variables[self.BK_HOST_OBJ_ID]],
            }
        )

        # 由于大型 JSON 处理速度较慢，转为 XML 处理

        doc = Document()
        app = doc.createElement("Application")
        doc.appendChild(app)

        # 遍历集群
        for bk_set in topo_tree_info:
            if bk_set is None:
                continue

            # 判断集群环境是否匹配并设置集群属性
            bk_set_attr = bk_set["set"]
            cc_bk_set_env = bk_set_attr["bk_set_env"]
            if cc_bk_set_env is None:
                # CMDB 获取的 bk_set_env 可能是None，但process得到的bk_set_env是空字符串，此处进行兼容
                cc_bk_set_env = ""
            if cc_bk_set_env != bk_set_env:
                continue
            xml_set = doc.createElement("Set")
            self.set_attr_to_xml_element(xml_set, bk_set_attr, biz_global_variables[self.BK_SET_OBJ_ID])

            # 遍历模块并设置模块属性
            for bk_module in bk_set.get("modules") or []:
                if bk_module is None:
                    continue
                xml_module = doc.createElement("Module")
                self.set_attr_to_xml_element(
                    xml_module, bk_module["module"], biz_global_variables[self.BK_MODULE_OBJ_ID]
                )

                # 遍历主机并设置属性
                for bk_host in bk_module.get("hosts") or []:
                    if bk_host is None:
                        continue
                    xml_host = doc.createElement("Host")
                    self.set_attr_to_xml_element(xml_host, bk_host, biz_global_variables[self.BK_HOST_OBJ_ID])

                    xml_module.appendChild(xml_host)

                xml_set.appendChild(xml_module)

            app.appendChild(xml_set)

        # TODO 考虑换redis缓存，或者大业务的情况进行压缩缓存
        doc = doc.toxml("utf-8")
        cache.set(
            self.CACHE_TOPO_ATTR_TEMPLATE.format(bk_biz_id=self.bk_biz_id),
            doc,
            gsetkit_const.CacheExpire.HOUR,
        )
        return doc

    def list_target_obj_node_from_topo(self, topo: List[Dict], node_list: List, target_obj_id: str):
        """
        从业务拓扑中获取所有模块
        :param topo: 业务拓扑树
        :param node_list: 模块列表，用于递归，首次递归需传入空列表
        :param target_obj_id: 预期获得的节点类型
        :return:
        """
        for node in topo:
            if node.get("bk_obj_id") == target_obj_id:
                node_list.append(node)
                continue
            self.list_target_obj_node_from_topo(node.get("child", []), node_list, target_obj_id)

    def find_obj_node_batch(
        self, api_func, bk_ids: List, ids_param_key: str = "bk_ids", limit: int = 500, **kwargs
    ) -> List:
        """
        批量获取节点属性信息
        :param api_func: api调用函数
        :param bk_ids: 节点id列表
        :param ids_param_key: 接口id列表键名
        :param limit: 接口id列表一次请求最大限制
        :param kwargs: 额外接口参数
        """
        get_data = kwargs.pop("get_data", lambda x: x)
        base_params = {"bk_biz_id": self.bk_biz_id, **kwargs}
        inst_ids_list = []
        for index in range(int(len(bk_ids) / limit) + 1):
            inst_ids_list.append(bk_ids[index * limit : (index + 1) * limit])
        return request_multi_thread(
            func=api_func,
            params_list=[
                {"params": {ids_param_key: inst_ids, **base_params}} for inst_ids in inst_ids_list if inst_ids
            ],
            get_data=get_data,
        )

    def get_bk_inst_id_map(
        self, topo: Dict, id_map: Dict, key_obj_id: str, value_obj_id: str, parent_inst_id: int = None
    ):
        """
        从拓扑树获取两个节点对象的归属关系，key_obj_id要求层级比value_obj_id低
        :param topo: 拓扑树
        :param id_map: ID映射表，用于递归，首次递归需传入空字典
        :param key_obj_id: 作为key的对象ID，如module
        :param value_obj_id: 作为value的对象ID，如set
        :param parent_inst_id: 父节点实例ID，为value_obj_id所对应的实例ID
        :return:
        {
            100(module_id): 1(set_id),
            101(module_id): 2(set_id)
        }
        """
        for node in topo:
            bk_obj_id = node.get("bk_obj_id")
            if bk_obj_id == key_obj_id:
                id_map[node["bk_inst_id"]] = parent_inst_id
                continue
            if bk_obj_id == value_obj_id:
                parent_inst_id = node["bk_inst_id"]
            self.get_bk_inst_id_map(node.get("child", []), id_map, key_obj_id, value_obj_id, parent_inst_id)

    def fill_object_num_to_topo(
        self, topo: List[Dict], module_id_obj_ids_maps: List[Dict[int, iter]], count_names: List[str]
    ) -> Dict[str, Set[int]]:
        """在拓扑树中填充数量：同级节点可能共用object，在此采取从模块开始，回溯求上一层级去重列表再统计object数"""
        count_name_total_obj_ids_map = defaultdict(set)
        for node in topo:
            count_name_obj_ids_map = defaultdict(set)
            if node.get("bk_obj_id") == self.BK_MODULE_OBJ_ID:
                for index, module_id_obj_ids_map in enumerate(module_id_obj_ids_maps):
                    count_name_obj_ids_map[count_names[index]] = set(
                        module_id_obj_ids_map.get(node["bk_inst_id"], set())
                    )
            else:
                count_name_obj_ids_map = self.fill_object_num_to_topo(
                    node.get("child", []), module_id_obj_ids_maps, count_names
                )
            for count_name, proj_ids in count_name_obj_ids_map.items():
                node[count_name] = len(proj_ids)
                count_name_total_obj_ids_map[count_name] = (
                    count_name_total_obj_ids_map[count_name] | count_name_obj_ids_map[count_name]
                )
        return count_name_total_obj_ids_map

    def fill_service_template_id_to_topo(self, topo: List[Dict]):
        """
        在拓扑树中填入服务模板ID
        :param topo: 业务拓扑树
        :return:
        """

        def fill_service_template_id_recursion(topo_nodes: List[Dict]):
            for node in topo_nodes:
                if node.get("bk_obj_id") == self.BK_MODULE_OBJ_ID:
                    node["service_template_id"] = module_id_service_template_id_map[node["bk_inst_id"]]
                    continue
                fill_service_template_id_recursion(node.get("child", []))

        # 获取topo下所有的module节点
        module_list = []
        self.list_target_obj_node_from_topo(topo, module_list, self.BK_MODULE_OBJ_ID)
        module_id_list = list(set([module["bk_inst_id"] for module in module_list]))

        # 需要额外信息，通过find_module_batch接口批量获取模块信息
        module_detail_list = self.find_obj_node_batch(
            CCApi.find_module_batch, module_id_list, fields=["service_template_id", "bk_module_id"]
        )
        module_id_service_template_id_map = {}
        for module_detail in module_detail_list:
            module_id_service_template_id_map[module_detail["bk_module_id"]] = module_detail.get("service_template_id")

        fill_service_template_id_recursion(topo)

    def biz_topo(self) -> Dict:
        """业务拓扑，并补充service_template_id，用于识别是否服务模板创建的模块"""
        topo = CCApi.search_biz_inst_topo({"bk_biz_id": self.bk_biz_id})

        self.fill_service_template_id_to_topo(topo)

        # 获取模块ID与主机ID列表映射关系
        host_topo_relations = batch_request(
            func=CCApi.find_host_topo_relation, params={"bk_biz_id": self.bk_biz_id}, get_data=lambda x: x["data"]
        )
        module_id_host_ids_map = self.relations_group_by(
            host_topo_relations, "bk_module_id", lambda relation: relation["bk_host_id"]
        )

        # 获取模块ID与进程ID列表映射关系
        module_process_relations = list(
            Process.objects.filter(bk_biz_id=self.bk_biz_id).values("bk_module_id", "bk_process_id")
        )
        module_id_process_ids_map = self.relations_group_by(
            module_process_relations, "bk_module_id", lambda relation: relation["bk_process_id"]
        )

        # 向拓扑节点填充主机数量
        self.fill_object_num_to_topo(
            topo, [module_id_host_ids_map, module_id_process_ids_map], ["host_count", "process_count"]
        )
        return topo

    def service_template(self) -> List:
        """服务模板列表"""
        return batch_request(CCApi.list_service_template, {"bk_biz_id": self.bk_biz_id})

    def process_template(self, service_template_id: int = None, process_template_ids: List[int] = None) -> List:
        """进程模板列表"""
        if service_template_id is not None:
            return (
                CCApi.list_proc_template(
                    {
                        "bk_biz_id": int(self.bk_biz_id),
                        "service_template_id": int(service_template_id),
                        "process_template_ids": process_template_ids or [],
                    }
                ).get("info")
                or []
            )

        if not process_template_ids:
            return []
        return self.find_obj_node_batch(
            CCApi.list_proc_template,
            process_template_ids,
            ids_param_key="process_template_ids",
            limit=200,
            get_data=lambda x: x["info"],
        )

    def service_instance(self, bk_module_id: int) -> List[Dict]:
        """根据模块ID获取服务实例列表
        :param bk_module_id: 模块ID
        :return:
        """
        return batch_request(CCApi.list_service_instance, {"bk_biz_id": self.bk_biz_id, "bk_module_id": bk_module_id})

    def cache_topo_name(self, topo: List[Dict] = None):
        if topo is None:
            topo = self.biz_topo()
        for node in topo:
            topo_cache_name = self.CACHE_KEY_TEMPLATE.format(bk_obj_id=node["bk_obj_id"], bk_inst_id=node["bk_inst_id"])
            cache.set(topo_cache_name, node["bk_inst_name"], None)
            self.cache_topo_name(node.get("child") or [])

    def set_list(self, bk_set_env: str, expression: str = BuildInChar.ASTERISK) -> List:
        """根据集群环境获取集群信息列表"""
        search_set_kwargs = {"bk_biz_id": self.bk_biz_id, "fields": ["bk_set_id", "bk_set_name", "bk_set_env"]}
        if bk_set_env != constants.BkSetEnv.ALL:
            search_set_kwargs["condition"] = {"bk_set_env": bk_set_env}
        sets = batch_request(CCApi.search_set, search_set_kwargs)
        return [set_node for set_node in sets if match.match(set_node["bk_set_name"], expression)]

    def module_list(
        self, bk_set_ids: List, bk_set_env: str = constants.BkSetEnv.ALL, expression: str = BuildInChar.ASTERISK
    ) -> List:
        """获取集群ID列表下所有模块
        :param bk_set_ids: 集群ID列表，为None时全部拉取
        :param expression: 表达式
        :param bk_set_env: 环境类型
        """
        if bk_set_ids == list():
            return []

        # 获取业务下全部的集群
        set_list = []
        self.list_target_obj_node_from_topo(
            CCApi.search_biz_inst_topo({"bk_biz_id": self.bk_biz_id}), set_list, self.BK_SET_OBJ_ID
        )
        if bk_set_env != constants.BkSetEnv.ALL:
            # 过滤非指定环境类型下的集群
            sets_in_env_ids = [set_node["bk_set_id"] for set_node in self.set_list(bk_set_env=bk_set_env)]
            bk_set_ids = list(set(bk_set_ids) & set(sets_in_env_ids)) if bk_set_ids else sets_in_env_ids

        # 非空情况下筛选指定ID下的集群节点
        if bk_set_ids is not None:
            set_list = [set_node for set_node in set_list if set_node["bk_inst_id"] in bk_set_ids]

        module_id_list = []
        module_id_set_map = {}
        for set_node in set_list:
            set_simple_info = {"bk_set_name": set_node["bk_inst_name"], "bk_set_id": set_node["bk_inst_id"]}
            for module_node in set_node.get("child", []):
                # 过滤名称不匹配的模块
                if not match.match(module_node["bk_inst_name"], expression):
                    continue
                # 聚合集群节点下模块ID并建立模块ID-集群信息映射
                module_id_set_map[module_node["bk_inst_id"]] = set_simple_info
                module_id_list.append(module_node["bk_inst_id"])

        module_id_list = list(set(module_id_list))

        # 通过find_module_batch接口批量获取模块信息，后续可能需要module的其他信息，故不直接从拓扑节点获取module信息
        modules = self.find_obj_node_batch(
            CCApi.find_module_batch, module_id_list, fields=["bk_module_name", "bk_module_id"]
        )
        # 填充模块对应的集群信息
        for module in modules:
            module["set"] = module_id_set_map[module["bk_module_id"]]
        return modules

    def fetch_service_instance_by_module_ids(
        self,
        bk_module_ids: List,
        expression: str = BuildInChar.ASTERISK,
        with_proc_count: bool = False,
    ) -> List[Dict]:
        """获取模块列表下所有服务实例列表
        :param bk_module_ids: 模块ID列表，为None时拉取全部
        :param expression: 表达式
        :param with_proc_count: 是否携带进程数量信息
        """
        # 为空拉取全部服务实例
        if bk_module_ids is None:
            module_list = []
            self.list_target_obj_node_from_topo(
                CCApi.search_biz_inst_topo({"bk_biz_id": self.bk_biz_id}), module_list, self.BK_MODULE_OBJ_ID
            )
            bk_module_ids = list(set([module["bk_inst_id"] for module in module_list]))

        processes = Process.objects.filter(bk_module_id__in=bk_module_ids).values(
            "service_instance_id", "expression", "bk_process_id"
        )

        # CMDB接口 list_service_instance 无法用批量模块id拉取，该方法存在性能问题，因此直接读取缓存数据
        service_insts_filtered = distinct_dict_list(
            [
                {
                    "service_instance_id": process["service_instance_id"],
                    "service_instance_name": process["expression"].split(EXPRESSION_SPLITTER)[2],
                }
                for process in processes
                if match.match(process["expression"].split(EXPRESSION_SPLITTER)[2], expression)
            ]
        )

        # 如不需要携带进程数量直接返回，减少DB查询耗时
        if not with_proc_count:
            return service_insts_filtered

        # 获取服务实例与进程的关系
        service_id_proc_ids_map = self.relations_group_by(
            processes, "service_instance_id", lambda relation: relation["bk_process_id"]
        )

        # 填充进程数量信息
        for inst in service_insts_filtered:
            inst["process_count"] = len(service_id_proc_ids_map.get(inst["service_instance_id"], []))
        return service_insts_filtered

    def append_legacy_global_variables(self, global_variables: List) -> None:
        """旧系统使用的全局变量"""
        for var in global_variables:
            bk_property_id = var["bk_property_id"]
            legacy_field = self.map_cc3_field_to_cc1(bk_property_id)
            if bk_property_id == legacy_field:
                # 无需映射的字段
                continue
            legacy_var = copy.deepcopy(var)
            legacy_var.update(
                {
                    "bk_property_id": legacy_field,
                    "bk_property_name": "{bk_property_name}{suffix}".format(
                        bk_property_name=var["bk_property_name"], suffix=_("(旧)")
                    ),
                    "bk_property_group_name": _("旧系统字段"),
                    "bk_biz_id": self.bk_biz_id,
                }
            )
            global_variables.append(legacy_var)

        # 内置系统变量
        builtin_global_variables = [
            {"bk_property_id": "FuncID", "bk_property_name": _("进程别名(旧)")},
            {"bk_property_id": "InstID", "bk_property_name": _("实例ID")},
            {"bk_property_id": "InstID0", "bk_property_name": _("实例ID（从0编号）")},
            {"bk_property_id": "LocalInstID", "bk_property_name": _("主机进程实例ID")},
            {"bk_property_id": "LocalInstID0", "bk_property_name": _("主机进程实例ID（从0编号）")},
            {"bk_property_id": "this", "bk_property_name": _("【当前实例对象】")},
            {"bk_property_id": "cc", "bk_property_name": _("【业务拓扑对象】")},
            {"bk_property_id": "HELP", "bk_property_name": _("【HELP】帮助")},
        ]
        for var in builtin_global_variables:
            global_variables.append(
                {
                    "bk_property_id": var["bk_property_id"],
                    "bk_property_name": var["bk_property_name"],
                    "bk_property_group_name": _("内置字段"),
                    "bk_property_type": "",
                    "bk_obj_id": self.BK_GLOBAL_OBJ_ID,
                    "bk_biz_id": self.bk_biz_id,
                }
            )

    def biz_global_variables(self):
        # 尝试从缓存获取业务模型属性
        biz_global_variables_cache = cache.get(CMDBHandler.CACHE_GLOBAL_VAR_TEMPLATE.format(bk_biz_id=self.bk_biz_id))
        if biz_global_variables_cache:
            return biz_global_variables_cache

        bk_obj_ids = [CMDBHandler.BK_SET_OBJ_ID, CMDBHandler.BK_MODULE_OBJ_ID, CMDBHandler.BK_HOST_OBJ_ID]
        all_object_attribute = request_multi_thread(
            func=CCApi.search_object_attribute,
            params_list=[{"params": {"bk_biz_id": self.bk_biz_id, "bk_obj_id": bk_obj_id}} for bk_obj_id in bk_obj_ids],
            get_data=lambda x: x,
        )
        self.append_legacy_global_variables(all_object_attribute)
        all_object_attribute = [
            {
                "bk_property_id": obj_attribute["bk_property_id"],
                "bk_property_name": obj_attribute["bk_property_name"],
                "bk_property_group_name": obj_attribute.get("bk_property_group_name"),
                "bk_property_type": obj_attribute.get("bk_property_type"),
                "bk_obj_id": obj_attribute["bk_obj_id"],
            }
            # 筛选自定义属性，自定义属性bk_biz_id为0
            for obj_attribute in all_object_attribute
            if any(
                [
                    obj_attribute["bk_biz_id"] != 0,
                    obj_attribute["bk_property_id"]
                    in CMDBHandler.BK_SYSTEM_COMMON_ATTRIBUTE.get(obj_attribute["bk_obj_id"], []),
                ]
            )
        ]
        # 排序
        all_object_attribute = sorted(all_object_attribute, key=lambda attr: attr["bk_property_name"])

        # 分组
        attributes_group_by_obj = defaultdict(list)
        for obj_attribute in all_object_attribute:
            attributes_group_by_obj[obj_attribute["bk_obj_id"]].append(obj_attribute)

        cache.set(
            CMDBHandler.CACHE_GLOBAL_VAR_TEMPLATE.format(bk_biz_id=self.bk_biz_id),
            attributes_group_by_obj,
            gsetkit_const.CacheExpire.FREQUENT_UPDATE,
        )
        return attributes_group_by_obj

    def search_object_attribute(self, bk_obj_id: str):
        return CCApi.search_object_attribute({"bk_biz_id": self.bk_biz_id, "bk_obj_id": bk_obj_id})

    def list_module_by_service_template_id(self, service_template_id, _request=None):
        return batch_request(
            CCApi.search_module,
            {
                "bk_biz_id": self.bk_biz_id,
                "fields": ["bk_module_id"],
                "condition": {"service_template_id": service_template_id},
                "_request": _request,
            },
        )

    def check_service_template_difference(self, service_template_id: int, _request=None) -> Dict:
        """检查服务模板是否有变更"""
        differences = CCApi.list_service_template_difference(
            {
                "service_template_ids": [service_template_id],
                "bk_biz_id": self.bk_biz_id,
                "is_partial": True,
                "_request": _request,
            }
        )
        for diff in differences.get("service_templates") or []:
            if diff["service_template_id"] == service_template_id and diff["need_sync"]:
                return {service_template_id: True}
        return {service_template_id: False}

    def batch_check_service_template_difference(self) -> Dict:
        """检查服务模板是否有变更"""
        service_template_ids = [service_template["id"] for service_template in self.service_template()]
        results = request_multi_thread(
            self.check_service_template_difference,
            params_list=[
                {"service_template_id": service_template_id, "_request": get_request()}
                for service_template_id in service_template_ids
            ],
            get_data=lambda x: [x],
        )
        return results
