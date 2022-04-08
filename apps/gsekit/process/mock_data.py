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
from apps.gsekit import constants
from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.cmdb import mock_data as cmdb_mock_data
from apps.gsekit.process.handlers.process import ProcessHandler


PROCESS_INSTANCE_REQUEST_BODY = {"service_instance_id": 1}
PROCESS_INSTANCE_RESPONSE = [
    {
        "config_templates": [
            {"config_template_id": 1, "template_name": "测试专用配置模板2", "file_name": "test.conf"},
            {"config_template_id": 2, "template_name": "测试专用配置模板1", "file_name": "test.conf"},
            {"config_template_id": 3, "template_name": "测试专用配置模板0", "file_name": "test.conf"},
        ],
        "process_template_id": 1,
        "bk_process_id": 1,
        **cmdb_mock_data.LIST_PROCESS_INSTANCE[0],
    }
]


UPDATE_PROCESS_INSTANCE_REQUEST_BODY = {
    "process_property": {**cmdb_mock_data.PROCESS_UPDATE_OR_CREATE_PARAMS, "bk_process_id": 1}
}
UPDATE_PROCESS_INSTANCE_RESPONSE = [1]


UPDATE_PROCESS_TEMPLATE_REQUEST_BODY = {
    "process_template_id": 1,
    "process_property": cmdb_mock_data.PROCESS_UPDATE_OR_CREATE_PARAMS,
}
UPDATE_PROCESS_TEMPLATE_RESPONSE = {
    "bk_biz_id": MyTestCase.bk_biz_id,
    "modifier": "admin",
    "creator": "admin",
    "last_time": "2021-01-07T16:08:13.910172751+08:00",
    "bk_process_name": cmdb_mock_data.PROCESS_UPDATE_OR_CREATE_PARAMS["bk_process_name"],
    "create_time": "2020-12-16T14:11:11.282Z",
    "bk_supplier_account": "0",
    "service_template_id": 1,
    "id": UPDATE_PROCESS_TEMPLATE_REQUEST_BODY["process_template_id"],
    "property": ProcessHandler.parse_proc_template_params2cmdb_request_format(
        cmdb_mock_data.PROCESS_UPDATE_OR_CREATE_PARAMS
    ),
}


CREATE_PROCESS_INSTANCE_REQUEST_BODY = {
    "service_instance_id": 1,
    "process_property": cmdb_mock_data.PROCESS_UPDATE_OR_CREATE_PARAMS,
}
CREATE_PROCESS_INSTANCE_RESPONSE = [1]
CREATE_PROCESS_TEMPLATE_REQUEST_BODY = {
    "service_template_id": 1,
    "process_property": cmdb_mock_data.PROCESS_UPDATE_OR_CREATE_PARAMS,
}


DELETE_PROCESS_INSTANCE_REQUEST_BODY = {"process_instance_ids": [1, 2]}
DELETE_PROCESS_TEMPLATE_REQUEST_BODY = {"process_template_ids": [3, 4]}


PROCESS_INSTANCE_CONFIG_RESPONSE = [
    {
        "bk_process_id": 43,
        "config_templates": [
            {"config_template_id": 102, "template_name": "mysql.ini", "file_name": "mysql"},
            {"config_template_id": 103, "template_name": "mysql_safe.ini", "file_name": "mysql_2"},
        ],
    }
]


PROCESS_TEMPLATE_REQUEST_BODY = {"service_template_id": 1}
PROCESS_TEMPLATE_RESPONSE = [
    {
        **cmdb_mock_data.LIST_PROC_TEMPLATE[0],
        "process_template_id": cmdb_mock_data.LIST_PROC_TEMPLATE[0]["id"],
        "config_templates": [
            {"config_template_id": 1, "template_name": "测试专用配置模板2", "file_name": "test.conf"},
            {"config_template_id": 2, "template_name": "测试专用配置模板1", "file_name": "test.conf"},
            {"config_template_id": 3, "template_name": "测试专用配置模板0", "file_name": "test.conf"},
        ],
    }
]


PROCESS_STATUS_REQUEST_BODY = {
    "scope": {
        "bk_set_env": "3",
        "bk_set_ids": [],
        "bk_module_ids": [],
        "bk_service_ids": [],
        "bk_process_names": [],
        "bk_process_ids": [],
    },
    "bk_host_innerips": [],
    "process_status": 2,
    "is_auto": False,
    "searches": [],
    "page": 1,
    "pagesize": 10,
    "expression_scope": {
        "bk_set_env": "3",
        "bk_set_name": "[管控平台, PaaS平台]",
        "bk_module_name": "*",
        "service_instance_name": "*",
        "bk_process_name": "*",
        "bk_process_id": "4[6, 8, 9]",
    },
    "fields": [],
}
PROCESS_STATUS_RESPONSE = {
    "count": 2,
    "list": [
        {
            "bk_biz_id": 1,
            "expression": "测试集群-1{splitter}测试模块-1{splitter}127.0.0.1_test_service-1{splitter}"
            "test_process-1{splitter}1".format(splitter=constants.EXPRESSION_SPLITTER),
            "bk_host_innerip": "127.0.0.1",
            "bk_cloud_id": 0,
            "bk_set_env": "3",
            "bk_set_id": 2,
            "bk_module_id": 4,
            "service_template_id": 1,
            "service_instance_id": 1,
            "bk_process_name": "test_process-1",
            "bk_process_id": 1,
            "process_template_id": 1,
            "process_status": 2,
            "is_auto": False,
            "bk_set_name": "测试集群-1",
            "bk_module_name": "测试模块-1",
            "bk_service_name": "127.0.0.1_test_service-1",
            "bk_cloud_name": "default area",
            "config_templates": [
                {"template_name": "测试专用配置模板2", "file_name": "test.conf"},
                {"template_name": "测试专用配置模板1", "file_name": "test.conf"},
                {"template_name": "测试专用配置模板0", "file_name": "test.conf"},
            ],
            "proc_inst_infos": [
                {"bk_process_id": 1, "local_inst_id": 1, "inst_id": 1, "process_status": 2, "is_auto": False}
            ],
        },
        {
            "bk_biz_id": 1,
            "expression": "测试集群-2{splitter}测试模块-3{splitter}127.0.0.3_test_service-2{splitter}"
            "test_process-3{splitter}3".format(splitter=constants.EXPRESSION_SPLITTER),
            "bk_host_innerip": "127.0.0.3",
            "bk_cloud_id": 0,
            "bk_set_env": "3",
            "bk_set_id": 3,
            "bk_module_id": 6,
            "service_template_id": 2,
            "service_instance_id": 3,
            "bk_process_name": "test_process-3",
            "bk_process_id": 3,
            "process_template_id": 2,
            "process_status": 2,
            "is_auto": False,
            "bk_set_name": "测试集群-2",
            "bk_module_name": "测试模块-3",
            "bk_service_name": "127.0.0.3_test_service-2",
            "bk_cloud_name": "default area",
            "config_templates": [],
            "proc_inst_infos": [
                {"bk_process_id": 3, "local_inst_id": 1, "inst_id": 1, "process_status": 2, "is_auto": False},
                {"bk_process_id": 3, "local_inst_id": 2, "inst_id": 2, "process_status": 2, "is_auto": False},
            ],
        },
    ],
}


OPERATE_PROCESS_REQUEST_BODY = {
    "op_type": "start",
    "scope": {
        "bk_set_env": "3",
        "bk_set_ids": [],
        "bk_module_ids": [],
        "bk_service_ids": [],
        "bk_process_names": [],
        "bk_process_ids": [],
    },
    "expression_scope": {
        "bk_set_env": "3",
        "bk_set_name": "[管控平台, PaaS平台]",
        "bk_module_name": "*",
        "service_instance_name": "*",
        "bk_process_name": "*",
        "bk_process_id": "4[6, 8, 9]",
    },
}
OPERATE_PROCESS_RESPONSE = {"job_id": 1}


PROCESS_INSTANCE_SIMPLE_REQUEST_BODY = {"service_instance_ids": [1, 3]}
PROCESS_INSTANCE_SIMPLE_RESPONSE = [
    {"bk_process_id": 1, "bk_process_name": "test_process-1"},
    {"bk_process_id": 3, "bk_process_name": "test_process-3"},
]
