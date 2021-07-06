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
import os

from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.process.models import Process

LIST_CONFIG_TEMPLATE_REQUEST_BODY = {}

LIST_CONFIG_TEMPLATE_RESPONSE = {
    "count": 3,
    "list": [
        {
            "abs_path": "/tmp/",
            "bk_biz_id": MyTestCase.bk_biz_id,
            "config_template_id": 3,
            "created_at": "2020-12-30 15:14:37+0800",
            "created_by": "admin",
            "file_name": "test.conf",
            "filemode": "0777",
            "group": "root",
            "has_version": False,
            "is_bound": False,
            "line_separator": "CRLF",
            "owner": "root",
            "permission": {"delete_config_template": True, "edit_config_template": True},
            "relation_count": {"INSTANCE": 0, "TEMPLATE": 0},
            "template_name": "测试专用配置模板2",
            "updated_at": "2020-12-30 15:14:37+0800",
            "updated_by": "admin",
        },
        {
            "abs_path": "/tmp/",
            "bk_biz_id": MyTestCase.bk_biz_id,
            "config_template_id": 2,
            "created_at": "2020-12-30 15:14:37+0800",
            "created_by": "admin",
            "file_name": "test.conf",
            "filemode": "0777",
            "group": "root",
            "has_version": False,
            "is_bound": False,
            "line_separator": "CRLF",
            "owner": "root",
            "permission": {"delete_config_template": True, "edit_config_template": True},
            "relation_count": {"INSTANCE": 0, "TEMPLATE": 0},
            "template_name": "测试专用配置模板1",
            "updated_at": "2020-12-30 15:14:37+0800",
            "updated_by": "admin",
        },
        {
            "abs_path": "/tmp/",
            "bk_biz_id": MyTestCase.bk_biz_id,
            "config_template_id": 1,
            "created_at": "2020-12-30 15:14:37+0800",
            "created_by": "admin",
            "file_name": "test.conf",
            "filemode": "0777",
            "group": "root",
            "has_version": True,
            "is_bound": False,
            "line_separator": "CRLF",
            "owner": "root",
            "permission": {"delete_config_template": True, "edit_config_template": True},
            "relation_count": {"INSTANCE": 0, "TEMPLATE": 0},
            "template_name": "测试专用配置模板0",
            "updated_at": "2020-12-30 15:14:37+0800",
            "updated_by": "admin",
        },
    ],
}

CREATE_CONFIG_TEMPLATE_REQUEST_BODY = {
    "template_name": "测试专用配置模板4",
    "file_name": "test.conf",
    "abs_path": "/tmp/",
    "owner": "root",
    "group": "root",
    "filemode": "0777",
    "line_separator": "CRLF",
}

CREATE_CONFIG_TEMPLATE_RESPONSE = {
    "abs_path": os.path.normpath("/tmp/"),
    "bk_biz_id": "1",
    "config_template_id": 4,
    "created_at": "2020-12-30 07:23:01.940249+00:00",
    "created_by": "admin",
    "file_name": "test.conf",
    "filemode": "0777",
    "group": "root",
    "line_separator": "CRLF",
    "owner": "root",
    "template_name": "测试专用配置模板4",
    "updated_at": "2020-12-30 07:23:01.940249+00:00",
    "updated_by": "admin",
}

RETRIEVE_CONFIG_TEMPLATE_REQUEST_BODY = {"config_template_id": 1}

RETRIEVE_CONFIG_TEMPLATE_RESPONSE = {
    "abs_path": "/tmp/",
    "bk_biz_id": MyTestCase.bk_biz_id,
    "config_template_id": 1,
    "created_at": "2020-12-30 07:31:04.013814+00:00",
    "created_by": "admin",
    "file_name": "test.conf",
    "filemode": "0777",
    "group": "root",
    "has_version": True,
    "is_bound": False,
    "line_separator": "CRLF",
    "owner": "root",
    "permission": {"delete_config_template": True, "edit_config_template": True},
    "relation_count": {"INSTANCE": 0, "TEMPLATE": 0},
    "template_name": "测试专用配置模板0",
    "updated_at": "2020-12-30 07:31:04.013814+00:00",
    "updated_by": "admin",
}

UPDATE_CONFIG_TEMPLATE_REQUEST_BODY = {
    "template_name": "测试专用配置模板-update",
    "file_name": "update.conf",
    "abs_path": "/tmp/update/",
    "owner": "update",
    "group": "update",
    "filemode": "0666",
    "line_separator": "CRLF",
}

UPDATE_CONFIG_TEMPLATE_RESPONSE = {
    "abs_path": os.path.normpath("/tmp/update/"),
    "file_name": "update.conf",
    "filemode": "0666",
    "group": "update",
    "line_separator": "CRLF",
    "owner": "update",
    "template_name": "测试专用配置模板-update",
}

DELETE_CONFIG_TEMPLATE_REQUEST_BODY = {"config_template_id": 1}

LIST_CONFIG_TEMPLATE_VERSION_REQUEST_BODY = {
    "config_template_id": 1,
}
LIST_BINDING_RELATIONSHIP_RESPONSE = [
    {
        "id": 19,
        "created_at": "2020-10-16T03:55:06.088669Z",
        "created_by": "admin",
        "updated_at": "2020-10-16T03:55:06.088669Z",
        "updated_by": "admin",
        "config_template_id": 1,
        "process_object_type": "INSTANCE",
        "process_object_id": 2000000839,
        "process_object_info": {
            "bk_set_name": "集群",
            "bk_module_name": "Mok1",
            "bk_service_name": "bk_service_name",
            "bk_process_name": "beat",
        },
    },
    {
        "id": 20,
        "created_at": "2020-10-16T03:55:06.088669Z",
        "created_by": "admin",
        "updated_at": "2020-10-16T03:55:06.088669Z",
        "updated_by": "admin",
        "config_template_id": 1,
        "process_object_type": "TEMPLATE",
        "process_object_id": 2000000053,
        "process_object_info": {"process_object_name": "agent", "service_template_name": "s_agent"},
    },
]

CREATE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY = {
    "description": "版本描述",
    "content": "草稿内容\n${HELP}",
    "file_format": "python",
    "is_active": False,
}
CREATE_CONFIG_TEMPLATE_VERSION_RESPONSE = {
    "config_template_id": 1,
    "config_version_id": 3,
    "content": "草稿内容\n${HELP}",
    "created_at": "2020-12-30 08:44:57.875424+00:00",
    "created_by": "admin",
    "description": "版本描述",
    "file_format": "python",
    "is_active": False,
    "is_draft": True,
    "updated_at": "2020-12-30 08:44:57.875424+00:00",
    "updated_by": "admin",
}

LIST_CONFIG_TEMPLATE_VERSION_RESPONSE = [
    {
        "config_template_id": 1,
        "config_version_id": 2,
        "content": "草稿内容\n${HELP}",
        "created_at": "2020-12-30 09:25:12.634796+00:00",
        "created_by": "admin",
        "description": "版本描述1",
        "file_format": "python",
        "is_active": True,
        "is_draft": False,
        "updated_at": "2020-12-30 09:25:12.634796+00:00",
        "updated_by": "admin",
    },
    {
        "config_template_id": 1,
        "config_version_id": 1,
        "content": "草稿内容\n${HELP}",
        "created_at": "2020-12-30 09:25:12.634796+00:00",
        "created_by": "admin",
        "description": "版本描述",
        "file_format": "python",
        "is_active": True,
        "is_draft": False,
        "updated_at": "2020-12-30 09:25:12.634796+00:00",
        "updated_by": "admin",
    },
]

BIND_TEMPLATE_TO_PROCESS_REQUEST_BODY = {
    "process_object_list": [
        {"process_object_type": "INSTANCE", "process_object_id": 1},
        {"process_object_type": "TEMPLATE", "process_object_id": 2},
    ]
}
BIND_TEMPLATE_TO_PROCESS_RESPONSE = {"deleted_relations_count": 0, "created_relations_count": 2}

BIND_PROCESS_TO_TEMPLATE_REQUEST_BODY = {
    "config_template_id_list": [1, 2, 3],
    "process_object_type": Process.ProcessObjectType.INSTANCE,
    "process_object_id": 1,
}
BIND_PROCESS_TO_TEMPLATE_RESPONSE = {"deleted_relations_count": 0, "created_relations_count": 3}

CLONE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY = {
    "description": "2020新的活动(版本描述)",
}

CLONE_CONFIG_TEMPLATE_VERSION_RESPONSE = {
    "config_version_id": 104,
    "content": '{"config": "test"}',
}

UPDATE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY = {
    "description": "2020新的活动(版本描述)",
    "content": "${HELP}",
    "is_draft": False,
    "is_active": True,
    "file_format": "yaml",
}

PREVIEW_CONFIG_REQUEST_BODY = {
    "content": "${HELP}",
    "bk_process_id": 1,
}

PREVIEW_CONFIG_RESPONSE = '{"config": "new_config"}'

BIND_TO_PROCESS_REQUEST_BODY = {
    "config_template_id_list": [1, 2, 3],
    "bk_process_id_list": [1, 2, 3],
    "process_template_id_list": [4, 5, 6],
}

GENERATE_CONFIG_REQUEST_BODY = {
    "config_template_id": None,
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

SYNC_GENERATE_CONFIG_REQUEST_BODY = {"bk_process_id": 1}

LIST_GENERATED_CONFIG_RESPONSE = [
    {
        "bk_set_id": 1,
        "bk_set_name": "广东一区",
        "bk_module_id": 2,
        "bk_module_name": "gameserver",
        "bk_service_id": 3,
        "bk_service_name": "服务实例名称",
        "bk_func_id": 4,
        "bk_func_name": "功能名称",
        "bk_process_id": 5,
        "bk_process_name": "进程名称",
        "bk_inner_ip": "127.0.0.1",
        "status": "success",
        "config_instance_id": 1,
    }
]

RELEASE_CONFIG_REQUEST_BODY = {
    "scope": {"bk_set_ids": [], "bk_module_ids": [], "bk_service_ids": [], "bk_func_ids": [], "bk_process_ids": []},
    "expression_scope": {
        "bk_set_env": "3",
        "bk_set_name": "[管控平台, PaaS平台]",
        "bk_module_name": "*",
        "service_instance_name": "*",
        "bk_process_name": "*",
        "bk_process_id": "4[6, 8, 9]",
    },
}

RELEASE_CONFIG_RESPONSE = {"job_id": 1}

LATEST_CONFIG_INSTANCE_REQUEST_BODY = {"bk_process_id": 1, "config_template_id": 1, "inst_id": 1}

LATEST_CONFIG_INSTANCE_RESPONSE = {
    "generated_config": {"content": "渲染后的配置文件内容", "created_at": "2020-09-08 16:43:33"},
    "released_config": {"content": "已下发的配置文件内容", "created_at": "2020-09-07 12:32:33"},
    "is_latest": False,
}

LIST_CONFIG_INSTANCES_RESPONSE_BODY = [
    {
        "status": "success",
        "config_template": {"config_template_id": 2, "template_name": "模块名2", "file_name": "nginx.conf"},
        "id": 5,
        "bk_biz_id": 2,
        "expression": "管控平台.gse_agent.127.0.0.1_gse_agent.gse_agent.46",
        "bk_host_innerip": "127.0.0.1",
        "bk_cloud_id": 0,
        "bk_set_id": 5,
        "bk_module_id": 21,
        "service_template_id": None,
        "service_instance_id": 5,
        "bk_func_id": "1",
        "bk_process_id": 46,
        "process_template_id": 26,
        "process_status": 0,
        "is_auto": False,
        "bk_set_name": "管控平台",
        "bk_module_name": "gse_agent",
        "bk_service_name": "gse_agent.127.0.0.1_gse_agent",
        "bk_process_name": "gse_agent",
        "bk_cloud_name": "default area",
        "created_at": "2020-11-18T04:04:51.786957Z",
    }
]

LIST_CONFIG_INSTANCES_REQUEST_BODY = {
    "scope": {
        "bk_set_env": "3",
        "bk_set_ids": [],
        "bk_module_ids": [],
        "bk_service_ids": [],
        "bk_process_names": [],
        "bk_process_ids": [],
    },
    "process_status": 0,
    "is_auto": True,
    "expression_scope": {
        "bk_set_env": "3",
        "bk_set_name": "[管控平台, PaaS平台]",
        "bk_module_name": "*",
        "service_instance_name": "*",
        "bk_process_name": "*",
        "bk_process_id": "4[6, 8, 9]",
    },
    "config_template_id": None,
    "config_version_ids": [],
}

RETRIEVE_CONFIG_INSTANCE_RESPONSE_BODY = {
    "id": 36,
    "config_version_id": 1,
    "config_template_id": 1,
    "bk_process_id": 49,
    "content": "test: 2020-11-18 12:04:51.963281",
    "is_latest": True,
    "sha256": "5e6479f42b84869c0d60584510868ef2de26e7502055691e87b2b601beec96ec",
    "expression": "TODO",
    "created_at": "2020-11-18T04:04:51.965915Z",
    "created_by": "admin",
}

MOCK_DATA = {"mock": "data"}

LIST_CONFIG_TEMPLATE_V2_REQUEST_BODY = {"page": 1, "pagesize": 10, "binding_config_template_ids": []}
