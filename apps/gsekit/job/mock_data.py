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

JOB_TASK_REQUEST = {
    "page": 1,
    "pagesize": 10,
    "bk_set_ids": [5],
    "bk_module_ids": [],
    "bk_process_ids": [],
    "statuses": ["failed", "running", "succeeded"],
}

JOB_TASK_RESPONSE = [
    {
        "bk_set_name": "集群名称",
        "bk_module_name": "模块名称",
        "service_instance_name": "服务实例名称",
        "bk_process_name": "进程别名",
        "bk_func_id": "功能ID",
        "bk_process_id": "",
        "start_time": "2020-10-16 03:58:47",
        "end_time": "2020-10-16 04:58:47",
        "status": "running",
        "extra_data": "",
    }
]


JOB_STATUS_RESPONSE = {
    "job_info": {
        "id": 158,
        "bk_biz_id": 2,
        "expression": "*.*.*.*.*",
        "scope": {
            "bk_set_id_list": [],
            "bk_func_id_list": [],
            "bk_module_id_list": [],
            "bk_process_id_list": [],
            "bk_service_id_list": [],
        },
        "job_object": "process",
        "job_action": "start",
        "status": "failed",
        "created_by": "admin",
        "is_ready": True,
        "start_time": "2020-11-16T11:22:42.214195Z",
        "end_time": "2020-11-16T11:22:50.766235Z",
        "pipeline_id": "b7116a7514c13319b816e9d76688ccf6",
    },
    "job_tasks": [{"id": 403, "status": "failed", "extra_data__failed_reason": "process is running"}],
}
