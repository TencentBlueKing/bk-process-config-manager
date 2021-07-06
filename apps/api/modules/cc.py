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

from django.utils.translation import ugettext_lazy as _

from ..base import BaseApi, DataAPI
from ..domains import CC_APIGATEWAY_ROOT

MOCK_LIST_PROCESS_RELATED_INFO_RETURN = {
    "result": True,
    "code": 0,
    "message": "success",
    "data": {
        "count": 2,
        "info": [
            {
                "set": {"bk_set_id": 10, "bk_set_name": "广东一区"},
                "module": {"bk_module_id": 11, "bk_module_name": "gameserver"},
                "host": {"bk_host_innerip": "127.0.0.1", "bk_host_id": 18, "bk_cloud_id": 16},
                "service_instance": {"id": 1008, "name": "127.0.0.1_gameserver_9080"},
                "process_template": {"id": 456},
                "process": {
                    "bk_func_id": "",
                    "bk_func_name": "java",
                    "bk_process_id": 2000000839,
                    "bk_process_name": "job_java",
                    "work_path": "/data/bkee",
                },
            },
            {
                "set": {"bk_set_id": 10, "bk_set_name": "广东一区"},
                "module": {"bk_module_id": 11, "bk_module_name": "gameserver"},
                "host": {"bk_host_innerip": "127.0.0.1", "bk_host_id": 18, "bk_cloud_id": 16},
                "service_instance": {"id": 1008, "name": "127.0.0.1_gameserver_9080"},
                "process_template": {"id": 456},
                "process": {
                    "bk_func_id": "",
                    "bk_func_name": "java",
                    "bk_process_id": 123,
                    "bk_process_name": "job_java",
                    "work_path": "/data/bkee",
                    "process_template_id": 2000000053,
                },
            },
        ],
    },
}


def list_process_related_info_after(response_data):
    # 过滤掉bk_set_id为0的数据
    response_data["data"]["info"] = list(
        filter(lambda x: x["set"]["bk_set_id"] != 0, response_data["data"]["info"] or [])
    )
    return response_data


class _CCApi(BaseApi):
    MODULE = _("配置平台")

    def __init__(self):
        self.search_business = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "search_business/", module=self.MODULE, description="查询业务列表",
        )
        self.search_cloud_area = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "search_cloud_area/", module=self.MODULE, description="查询云区域",
        )
        self.search_biz_inst_topo = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "search_biz_inst_topo/", module=self.MODULE, description="查询业务实例拓扑",
        )
        self.find_module_batch = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "find_module_batch/", module=self.MODULE, description="批量获取模块详情",
        )
        self.list_service_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "list_service_template/",
            module=self.MODULE,
            description="查询服务模板列表",
        )
        self.list_service_instance = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "list_service_instance/",
            module=self.MODULE,
            description="查询服务实例列表",
        )
        self.list_process_instance = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "list_process_instance/",
            module=self.MODULE,
            description="查询进程实例列表",
        )
        self.list_proc_template = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "list_proc_template/", module=self.MODULE, description="查询进程模板信息",
        )
        self.batch_create_proc_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "batch_create_proc_template/",
            module=self.MODULE,
            description="批量创建进程模板",
        )
        self.update_process_instance = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "update_process_instance/",
            module=self.MODULE,
            description="批量更新进程信息",
        )
        self.update_proc_template = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "update_proc_template/", module=self.MODULE, description="更新进程模板信息",
        )
        self.list_process_related_info = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "list_process_related_info/",
            module=self.MODULE,
            after_request=list_process_related_info_after,
            description="根据规则批量查询进程实例信息",
        )
        self.find_set_batch = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "find_set_batch/", module=self.MODULE, description="批量获取指定业务下集群",
        )
        self.search_set = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "search_set/", module=self.MODULE, description="查询集群",
        )
        self.search_module = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "search_module/", module=self.MODULE, description="查询模块",
        )
        self.search_object_attribute = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "search_object_attribute/",
            module=self.MODULE,
            description="查询对象模型属性",
        )
        self.find_biz_tree_brief_info = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "find_biz_tree_brief_info/",
            module=self.MODULE,
            description="查询业务topo树的简要信息",
        )
        self.create_process_instance = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "create_process_instance/",
            module=self.MODULE,
            description="创建进程实例",
        )
        self.batch_create_proc_template = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "batch_create_proc_template/",
            module=self.MODULE,
            description="批量创建进程模板",
        )
        self.find_host_topo_relation = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "find_host_topo_relation/",
            module=self.MODULE,
            description="获取主机与拓扑的关系",
        )
        self.delete_process_instance = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "delete_process_instance/",
            module=self.MODULE,
            description="删除进程实例",
        )
        self.delete_proc_template = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "delete_proc_template/", module=self.MODULE, description="删除进程模板",
        )
        self.list_service_template_difference = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT + "list_service_template_difference/",
            module=self.MODULE,
            description="列出服务模版和服务实例之间的差异",
        )
        self.resource_watch = DataAPI(
            method="POST", url=CC_APIGATEWAY_ROOT + "resource_watch/", module=self.MODULE, description="监听资源变化事件",
        )
