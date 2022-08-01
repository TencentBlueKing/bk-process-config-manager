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


GET_USER_INFO_RESPONSE = {"id": 1, "username": "admin", "timestamp": 1606129919.619032}

JOB_TASK_FILTER_CHOICES_RESPONSE = {
    "set": [{"id": 1, "name": "set"}],
    "module": [{"id": 1, "name": "module"}],
    "process": [{"id": 1, "name": "process"}],
    "status_choices": [
        {"id": "pending", "name": "等待中"},
        {"id": "running", "name": "执行中"},
        {"id": "succeeded", "name": "执行成功"},
        {"id": "failed", "name": "执行失败"},
    ],
}

PROCESS_FILTER_CHOICES_RESPONSE = {
    "bk_cloud_id_choices": [{"id": 0, "name": "default area"}],
    "process_status_choices": [{"id": 0, "name": "未注册"}, {"id": 1, "name": "运行中"}, {"id": 2, "name": "已终止"}],
    "is_auto_choices": [{"id": False, "name": "未托管"}, {"id": True, "name": "已托管"}],
}

EXPRESSION_MATCH_REQUEST = {
    "expression": "string[1-100].[集群1, 集群2].server.word[a-z]-[1.1, 1.2]*",
    "candidates": ["string1.集群1.server.worda-1.1.111", "string100.集群2.server.worda-1.2A"],
}

EXPRESSION_MATCH_RESPONSE = {
    "exps_with_unix_shell_style": [
        "string[1-9].集群1.server.word[a-z]-1.1*",
        "string[1-9][0-9].集群2.server.word[a-z]-1.1*",
        "string100.集群2.server.word[a-z]-1.1*",
        "string100.集群1.server.word[a-z]-1.1*",
        "string[1-9].集群2.server.word[a-z]-1.1*",
        "string100.集群2.server.word[a-z]-1.2*",
        "string[1-9].集群2.server.word[a-z]-1.2*",
        "string[1-9][0-9].集群1.server.word[a-z]-1.2*",
        "string[1-9][0-9].集群2.server.word[a-z]-1.2*",
        "string100.集群1.server.word[a-z]-1.2*",
        "string[1-9][0-9].集群1.server.word[a-z]-1.1*",
        "string[1-9].集群1.server.word[a-z]-1.2*",
    ],
    "filter_results": ["string1.集群1.server.worda-1.1.111", "string100.集群2.server.worda-1.2A"],
}

ACCESS_OVERVIEW_RESPONSE = {"is_access": True, "process": True, "configfile": True}
