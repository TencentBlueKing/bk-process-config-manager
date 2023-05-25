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
import typing

from . import base


class GseV1ApiHelper(base.GseApiBaseHelper):
    def get_agent_id(self, host_info: typing.Union[base.InfoDict, typing.Dict]) -> str:
        return f"{host_info['bk_cloud_id']}:{host_info['bk_host_innerip']}"

    def preprocessing_proc_operate_info(
        self, host_info_list: base.InfoDictList, proc_operate_info: base.InfoDict
    ) -> base.InfoDict:
        proc_operate_info["hosts"] = [
            {"ip": host_info["bk_host_innerip"], "bk_cloud_id": host_info["bk_cloud_id"]}
            for host_info in host_info_list
        ]
        return proc_operate_info

    def _operate_proc_multi(self, proc_operate_req: base.InfoDictList, **options) -> str:
        return self.gse_api_obj.operate_proc_multi({"proc_operate_req": proc_operate_req, "no_request": True})[
            "task_id"
        ]

    def get_proc_operate_result(self, task_id: str) -> base.InfoDict:
        return self.gse_api_obj.get_proc_operate_result({"task_id": task_id, "no_request": True}, raw=True)
