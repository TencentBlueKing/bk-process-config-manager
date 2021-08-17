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
from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.process.handlers.process import ProcessHandler

# CMDB API DATA

FIND_MODULE_BATCH = [
    {"default": 0, "bk_module_name": "测试模块-1", "bk_module_id": 4, "service_template_id": 1},
    {"default": 0, "bk_module_name": "测试模块-2", "bk_module_id": 5, "service_template_id": 1},
    {"default": 0, "bk_module_name": "测试模块-3", "bk_module_id": 6, "service_template_id": 2},
]

SEARCH_OBJECT_ATTRIBUTE_GROUP = {
    # 简化数据，后续有需要再扩充
    CMDBHandler.BK_HOST_OBJ_ID: [
        {
            "bk_property_id": "bk_host_name",
            "bk_property_name": "主机名称",
            "bk_property_group_name": "自动发现信息（需要安装agent）",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "operator",
            "bk_property_name": "主要维护人",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "objuser",
            "bk_obj_id": "host",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "bk_cloud_id",
            "bk_property_name": "云区域",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "foreignkey",
            "bk_obj_id": "host",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "bk_host_innerip",
            "bk_property_name": "内网IP",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "test_host",
            "bk_property_name": "主机自定义属性",
            "bk_property_group_name": "测试-自定义属性",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
            "bk_biz_id": 1,
        },
    ],
    CMDBHandler.BK_SET_OBJ_ID: [
        {
            "bk_property_id": "bk_service_status",
            "bk_property_name": "服务状态",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "enum",
            "bk_obj_id": "set",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "bk_set_env",
            "bk_property_name": "环境类型",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "enum",
            "bk_obj_id": "set",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "bk_set_name",
            "bk_property_name": "集群名",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "singlechar",
            "bk_obj_id": "set",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "test_set",
            "bk_property_name": "集群自定义属性",
            "bk_property_group_name": "测试-自定义属性",
            "bk_property_type": "singlechar",
            "bk_obj_id": "set",
            "bk_biz_id": 1,
        },
    ],
    CMDBHandler.BK_MODULE_OBJ_ID: [
        {
            "bk_property_id": "bk_module_name",
            "bk_property_name": "模块名",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "singlechar",
            "bk_obj_id": "module",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "bk_module_type",
            "bk_property_name": "模块类型",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "enum",
            "bk_obj_id": "module",
            "bk_biz_id": 0,
        },
        {
            "bk_property_id": "test_module",
            "bk_property_name": "模块自定义属性",
            "bk_property_group_name": "测试-自定义属性",
            "bk_property_type": "singlechar",
            "bk_obj_id": "module",
            "bk_biz_id": 1,
        },
    ],
    # 用于/api/{bk_biz_id}/cmdb/search_object_attribute/的测试
    CMDBHandler.BK_PROCESS_OBJ_ID: [
        {
            "creator": "cc_system",
            "bk_isapi": False,
            "bk_issystem": False,
            "bk_property_id": "bk_func_name",
            "id": 60,
            "unit": "",
            "description": "",
            "bk_property_group_name": "基础信息",
            "isreadonly": False,
            "last_time": "2020-10-28 11:45:59",
            "ispre": True,
            "option": "",
            "editable": True,
            "bk_obj_id": "process",
            "isonly": False,
            "bk_property_name": "进程名称",
            "placeholder": "程序的二进制名称</br> 比如zookeeper的二进制名称是java，则填java",
            "bk_biz_id": 0,
            "bk_property_type": "singlechar",
            "isrequired": True,
            "create_time": "2020-10-28 11:45:59",
            "bk_supplier_account": "0",
            "bk_property_index": 0,
            "bk_property_group": "default",
        }
    ],
}

PROCESS_INSTANCE_BASE = {
    "timeout": 10,
    "user": "root",
    "auto_start": None,
    "bk_start_check_secs": 1,
    "bk_supplier_account": "0",
    "description": "test cmdb proc",
    "work_path": "/data/home/tools",
    "bk_start_param_regex": "-c /tmp/config",
    "pid_file": "/data/home/tools/gamesvr.pid",
    "start_cmd": "sh /data/home/tools/start.sh",
    "stop_cmd": "sh /data/home/tools/stop.sh",
    "reload_cmd": "sh /data/home/tools/start.sh",
    "restart_cmd": "sh /data/home/tools/reload.sh",
    "face_stop_cmd": "",
    "last_time": "2020-12-21T15:35:10.192+08:00",
    "create_time": "2020-12-21T15:35:10.151+08:00",
    "bind_info": [{"ip": "127.0.0.1", "port": "3306", "protocol": "1", "enable": True, "row_id": 1}],
}

PROCESS_UPDATE_OR_CREATE_PARAMS = {
    "bk_process_name": "test_process-1",
    "description": "process update or create params",
    "bk_func_name": "test_process-1",
    "work_path": "/tmp",
    "user": "root",
    "proc_num": 1,
    "priority": 1,
    "timeout": 1,
    "start_cmd": "/tmp/start.sh",
    "stop_cmd": "/tmp/stop.sh",
    "restart_cmd": "/tmp/restart.sh",
    "face_stop_cmd": "/tmp/face_stop.sh",
    "reload_cmd": "/tmp/reload.sh",
    "pid_file": "/tmp/proc.pid",
    "bk_start_param_regex": "-c /tmp/config",
    "bind_info": [{"ip": "127.0.0.1", "port": "3306", "protocol": "1", "enable": True, "row_id": 1}],
    "bk_start_check_secs": 1,
}

LIST_PROCESS_RELATED_INFO = [
    {
        "set": {"bk_set_id": 2, "bk_set_env": "3", "bk_set_name": "测试集群-1"},
        "module": {"bk_module_name": "测试模块-1", "bk_module_id": 4},
        "host": {"bk_host_id": 1, "bk_cloud_id": 0, "bk_host_innerip": "127.0.0.1"},
        "service_instance": {"id": 1, "name": "127.0.0.1_test_service-1"},
        "process_template": {"id": 1},
        "process": {
            "bk_biz_id": MyTestCase.bk_biz_id,
            "bk_process_id": 1,
            "bk_func_name": "test_process-1",
            "bk_process_name": "test_process-1",
            "proc_num": 1,
            "priority": 1,
            **PROCESS_INSTANCE_BASE,
        },
    },
    {
        "set": {"bk_set_id": 3, "bk_set_env": "3", "bk_set_name": "测试集群-2"},
        "module": {"bk_module_name": "测试模块-3", "bk_module_id": 6},
        "host": {"bk_host_id": 3, "bk_cloud_id": 0, "bk_host_innerip": "127.0.0.3"},
        "service_instance": {"id": 3, "name": "127.0.0.3_test_service-2"},
        "process_template": {"id": 2},
        "process": {
            "bk_biz_id": MyTestCase.bk_biz_id,
            "bk_process_id": 3,
            "bk_func_name": "test_process-3",
            "bk_process_name": "test_process-3",
            "proc_num": 2,
            "priority": 1,
            **PROCESS_INSTANCE_BASE,
        },
    },
]

LIST_PROCESS_INSTANCE = [
    {
        "property": {
            "bk_biz_id": MyTestCase.bk_biz_id,
            "bk_process_id": 1,
            "bk_func_name": "test_process-1",
            "bk_process_name": "test_process-1",
            "proc_num": 1,
            "priority": 1,
            **PROCESS_INSTANCE_BASE,
        },
        "relation": {
            "bk_biz_id": MyTestCase.bk_biz_id,
            "process_template_id": 1,
            "bk_host_id": 1,
            "service_instance_id": 1,
            "bk_process_id": 1,
            "bk_supplier_account": "0",
        },
    },
    {
        "property": {
            "bk_biz_id": MyTestCase.bk_biz_id,
            "bk_process_id": 3,
            "bk_func_name": "test_process-3",
            "bk_process_name": "test_process-3",
            "proc_num": 2,
            "priority": 1,
            **PROCESS_INSTANCE_BASE,
        },
        "relation": {
            "bk_biz_id": MyTestCase.bk_biz_id,
            "process_template_id": 2,
            "bk_host_id": 3,
            "service_instance_id": 3,
            "bk_process_id": 3,
            "bk_supplier_account": "0",
        },
    },
]

LIST_PROC_TEMPLATE = [
    {
        "id": 1,
        "bk_biz_id": MyTestCase.bk_biz_id,
        "bk_process_name": "test_process-1",
        "service_template_id": 1,
        "property": ProcessHandler.parse_proc_template_params2cmdb_request_format(PROCESS_UPDATE_OR_CREATE_PARAMS),
        "modifier": "admin",
        "creator": "admin",
        "last_time": "2020-12-02T13:04:23.003Z",
        "create_time": "2020-11-13T06:14:36.628Z",
        "bk_supplier_account": "0",
    }
]

# INTERFACE MOCK DATA

BIZ_LIST_RESPONSE = [
    {"bk_biz_id": 1, "default": 0, "bk_biz_name": "蓝鲸", "permission": {"view_business": True}},
    {"bk_biz_id": 2, "default": 0, "bk_biz_name": "测试业务1", "permission": {"view_business": True}},
    {"bk_biz_id": 3, "default": 0, "bk_biz_name": "测试业务2", "permission": {"view_business": True}},
]

BIZ_TOPO_RESPONSE = [
    {
        "bk_inst_id": 1,
        "bk_inst_name": "蓝鲸",
        "bk_obj_id": "biz",
        "bk_obj_name": "biz",
        "host_count": 3,
        "child": [
            {
                "bk_inst_id": 2,
                "bk_inst_name": "测试集群-1",
                "bk_obj_id": "set",
                "bk_obj_name": "set",
                "host_count": 2,
                "child": [
                    {
                        "bk_inst_id": 4,
                        "bk_inst_name": "测试模块-1",
                        "bk_obj_id": "module",
                        "bk_obj_name": "module",
                        "child": [],
                        "service_template_id": 1,
                        "host_count": 1,
                    },
                    {
                        "bk_inst_id": 5,
                        "bk_inst_name": "测试模块-2",
                        "bk_obj_id": "module",
                        "bk_obj_name": "module",
                        "child": [],
                        "service_template_id": 1,
                        "host_count": 1,
                    },
                ],
            },
            {
                "bk_inst_id": 3,
                "bk_inst_name": "测试集群-2",
                "bk_obj_id": "set",
                "bk_obj_name": "set",
                "host_count": 1,
                "child": [
                    {
                        "bk_inst_id": 6,
                        "bk_inst_name": "测试模块-3",
                        "bk_obj_id": "module",
                        "bk_obj_name": "module",
                        "child": [],
                        "service_template_id": 2,
                        "host_count": 1,
                    }
                ],
            },
        ],
    }
]

SERVICE_TEMPLATE_RESPONSE = [
    {
        "bk_biz_id": 1,
        "id": 1,
        "name": "test_service-1",
        "service_category_id": 1,
        "creator": "admin",
        "modifier": "admin",
        "create_time": "2019-09-18T20:31:34.627+08:00",
        "last_time": "2019-09-18T20:31:34.627+08:00",
        "bk_supplier_account": "0",
    },
    {
        "bk_biz_id": 1,
        "id": 2,
        "name": "test_service-2",
        "service_category_id": 2,
        "creator": "admin",
        "modifier": "admin",
        "create_time": "2019-09-18T20:31:29.607+08:00",
        "last_time": "2019-09-18T20:31:29.607+08:00",
        "bk_supplier_account": "0",
    },
]
PROCESS_RELATED_INFO_REQUEST_BODY = {
    "set": {"bk_set_ids": []},
    "module": {"bk_module_ids": []},
    "service_instance": {"ids": []},
    "process_property_filter": {
        "condition": "OR",
        "rules": [
            {"field": "user", "operator": "equal", "value": ""},
            {"field": "work_path", "operator": "equal", "value": ""},
            {"field": "pid_file", "operator": "equal", "value": ""},
            {"field": "start_cmd", "operator": "equal", "value": ""},
            {"field": "stop_cmd", "operator": "equal", "value": ""},
            {"field": "priority", "operator": "equal", "value": ""},
        ],
    },
    "fields": [
        "bk_process_id",
        "bk_process_name",
        "bk_func_id",
        "bk_func_name",
        "user",
        "work_path",
        "start_cmd",
        "stop_cmd",
        "restart_cmd",
        "reload_cmd",
        "face_stop_cmd",
        "priority",
        "proc_num",
        "pid_file",
        "bk_start_check_secs",
        "bk_start_param_regex",
        "description",
    ],
    "page": {"start": 0, "limit": 10, "sort": "user,work_path,pid_file,start_cmd,stop_cmd,priority"},
}

PROCESS_RELATED_INFO_RESPONSE = {"count": len(LIST_PROCESS_RELATED_INFO), "info": LIST_PROCESS_RELATED_INFO}

SERVICE_INSTANCE_RESPONSE = [
    {
        "bk_biz_id": MyTestCase.bk_biz_id,
        "bk_module_id": 4,
        "name": "127.0.0.1.test_service-1",
        "creator": "admin",
        "labels": "None",
        "bk_host_id": 1,
        "last_time": "2020-12-16T14:13:40.887Z",
        "create_time": "2020-12-16T14:13:40.887Z",
        "bk_supplier_account": "0",
        "service_template_id": 1,
        "modifier": "admin",
        "id": 1,
    },
    {
        "bk_biz_id": MyTestCase.bk_biz_id,
        "bk_module_id": 5,
        "name": "127.0.0.2.test_service-1",
        "creator": "admin",
        "labels": "None",
        "bk_host_id": 2,
        "last_time": "2020-12-16T14:13:40.887Z",
        "create_time": "2020-12-16T14:13:40.887Z",
        "bk_supplier_account": "0",
        "service_template_id": 1,
        "modifier": "admin",
        "id": 2,
    },
    {
        "bk_biz_id": MyTestCase.bk_biz_id,
        "bk_module_id": 6,
        "name": "127.0.0.3_test_service-2",
        "creator": "admin",
        "labels": "None",
        "bk_host_id": 3,
        "last_time": "2020-12-16T14:13:40.887Z",
        "create_time": "2020-12-16T14:13:40.887Z",
        "bk_supplier_account": "0",
        "service_template_id": 2,
        "modifier": "admin",
        "id": 3,
    },
]

REQUEST_PROCESS_RELATED_INFO = {}

SET_LIST_REQUEST_BODY = {"bk_set_env": "3", "expression": "测试集群-[1-2]"}
SET_LIST_RESPONSE = [
    {"default": 0, "bk_set_env": "3", "bk_set_id": 2, "bk_set_name": "测试集群-1"},
    {"default": 0, "bk_set_env": "3", "bk_set_id": 3, "bk_set_name": "测试集群-2"},
]

MODULE_LIST_RESPONSE = [
    {"default": 0, "bk_module_id": 4, "bk_module_name": "测试模块-1", "set": {"bk_set_id": 2, "bk_set_name": "测试集群-1"}},
    {"default": 0, "bk_module_id": 5, "bk_module_name": "测试模块-2", "set": {"bk_set_id": 2, "bk_set_name": "测试集群-1"}},
    {"default": 0, "bk_module_id": 6, "bk_module_name": "测试模块-3", "set": {"bk_set_id": 3, "bk_set_name": "测试集群-2"}},
]

BIZ_GLOBAL_VAR_RESPONSE = {
    "global": [
        {
            "bk_property_id": "HELP",
            "bk_property_name": "【HELP】帮助",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "cc",
            "bk_property_name": "【业务拓扑对象】",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "this",
            "bk_property_name": "【当前实例对象】",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "LocalInstID",
            "bk_property_name": "主机进程实例ID",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "LocalInstID0",
            "bk_property_name": "主机进程实例ID（从0编号）",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "InstID",
            "bk_property_name": "实例ID",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "InstID0",
            "bk_property_name": "实例ID（从0编号）",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
        {
            "bk_property_id": "FuncID",
            "bk_property_name": "进程别名(旧)",
            "bk_property_group_name": "内置字段",
            "bk_property_type": "",
            "bk_obj_id": "global",
        },
    ],
    "host": [
        {
            "bk_property_id": "bk_host_name",
            "bk_property_name": "主机名称",
            "bk_property_group_name": "自动发现信息（需要安装agent）",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
        },
        {
            "bk_property_id": "HostName",
            "bk_property_name": "主机名称(旧)",
            "bk_property_group_name": "旧系统字段",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
        },
        {
            "bk_property_id": "test_host",
            "bk_property_name": "主机自定义属性",
            "bk_property_group_name": "测试-自定义属性",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
        },
        {
            "bk_property_id": "operator",
            "bk_property_name": "主要维护人",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "objuser",
            "bk_obj_id": "host",
        },
        {
            "bk_property_id": "bk_cloud_id",
            "bk_property_name": "云区域",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "foreignkey",
            "bk_obj_id": "host",
        },
        {
            "bk_property_id": "bk_host_innerip",
            "bk_property_name": "内网IP",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
        },
        {
            "bk_property_id": "InnerIP",
            "bk_property_name": "内网IP(旧)",
            "bk_property_group_name": "旧系统字段",
            "bk_property_type": "singlechar",
            "bk_obj_id": "host",
        },
    ],
    "set": [
        {
            "bk_property_id": "bk_service_status",
            "bk_property_name": "服务状态",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "enum",
            "bk_obj_id": "set",
        },
        {
            "bk_property_id": "SetServiceState",
            "bk_property_name": "服务状态(旧)",
            "bk_property_group_name": "旧系统字段",
            "bk_property_type": "enum",
            "bk_obj_id": "set",
        },
        {
            "bk_property_id": "bk_set_env",
            "bk_property_name": "环境类型",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "enum",
            "bk_obj_id": "set",
        },
        {
            "bk_property_id": "SetEnviType",
            "bk_property_name": "环境类型(旧)",
            "bk_property_group_name": "旧系统字段",
            "bk_property_type": "enum",
            "bk_obj_id": "set",
        },
        {
            "bk_property_id": "bk_set_name",
            "bk_property_name": "集群名",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "singlechar",
            "bk_obj_id": "set",
        },
        {
            "bk_property_id": "SetName",
            "bk_property_name": "集群名(旧)",
            "bk_property_group_name": "旧系统字段",
            "bk_property_type": "singlechar",
            "bk_obj_id": "set",
        },
        {
            "bk_property_id": "test_set",
            "bk_property_name": "集群自定义属性",
            "bk_property_group_name": "测试-自定义属性",
            "bk_property_type": "singlechar",
            "bk_obj_id": "set",
        },
    ],
    "module": [
        {
            "bk_property_id": "bk_module_name",
            "bk_property_name": "模块名",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "singlechar",
            "bk_obj_id": "module",
        },
        {
            "bk_property_id": "ModuleName",
            "bk_property_name": "模块名(旧)",
            "bk_property_group_name": "旧系统字段",
            "bk_property_type": "singlechar",
            "bk_obj_id": "module",
        },
        {
            "bk_property_id": "bk_module_type",
            "bk_property_name": "模块类型",
            "bk_property_group_name": "基础信息",
            "bk_property_type": "enum",
            "bk_obj_id": "module",
        },
        {
            "bk_property_id": "test_module",
            "bk_property_name": "模块自定义属性",
            "bk_property_group_name": "测试-自定义属性",
            "bk_property_type": "singlechar",
            "bk_obj_id": "module",
        },
    ],
}

BIZ_SEARCH_OBJECT_ATTRIBUTE_REQUEST_BODY = {"bk_obj_id": CMDBHandler.BK_PROCESS_OBJ_ID}
BIZ_SEARCH_OBJECT_ATTRIBUTE_RESPONSE = SEARCH_OBJECT_ATTRIBUTE_GROUP[
    BIZ_SEARCH_OBJECT_ATTRIBUTE_REQUEST_BODY["bk_obj_id"]
]
CHECK_SERVICE_TMPL_DIFF_REQUEST_BODY = {"service_template_id": 1}

LIST_SERVICE_TEMPLATE_DIFF = {
    "service_templates": [{"service_template_id": 1, "need_sync": True}, {"service_template_id": 2, "need_sync": False}]
}

CHECK_SERVICE_TEMPLATE_DIFFERENCE_RESPONSE = True

BATCH_CHECK_SERVICE_TEMPLATE_DIFFERENCE_RESPONSE = [{"1": True}, {"2": False}]
