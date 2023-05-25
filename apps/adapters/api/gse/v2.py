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
import logging
import typing
from collections import Mapping

from . import base
from .v1 import GseV1ApiHelper

logger = logging.getLogger("app")


class GseV2ApiHelper(GseV1ApiHelper):
    def get_agent_id(self, host_info: typing.Union[base.InfoDict, typing.Dict]) -> str:

        if isinstance(host_info, Mapping):
            if "host" in host_info:
                return self.get_agent_id(host_info["host"])
            bk_agent_id: typing.Optional[str] = host_info.get("bk_agent_id")
        else:
            bk_agent_id: typing.Optional[int] = getattr(host_info, "bk_agent_id")
        if not bk_agent_id:
            return super(GseV2ApiHelper, self).get_agent_id(host_info)
        return bk_agent_id

    def preprocessing_proc_operate_info(
        self, host_info_list: base.InfoDictList, proc_operate_info: base.InfoDict
    ) -> base.InfoDict:
        proc_operate_info["agent_id_list"] = list({self.get_agent_id(host_info) for host_info in host_info_list})
        return proc_operate_info
