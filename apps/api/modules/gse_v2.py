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
from ..domains import GSE_APIGATEWAY_ROOT_V2


class _GseV2Api(BaseApi):
    MODULE = _("管控平台 V2")

    def __init__(self):
        self.operate_proc_multi = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "api/v2/proc/operate_proc_multi/",
            module=self.MODULE,
            description="批量进程操作",
        )
        self.get_proc_operate_result = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "api/v2/proc/get_proc_operate_result_v2/",
            module=self.MODULE,
            description="查询进程操作结果",
        )
        self.get_proc_status = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "api/v2/proc/get_proc_status_v2/",
            module=self.MODULE,
            description="查询进程状态信息",
        )
