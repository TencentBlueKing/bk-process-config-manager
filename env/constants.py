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

from enum import Enum
from typing import Dict
from django.utils.translation import ugettext_lazy as _

from apps.utils.enum import EnhanceEnum


class BkPaaSVersion(EnhanceEnum):
    V2 = 2
    V3 = 3

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {cls.V2: "V2", cls.V3: _("V3具备容器及二进制配置差异")}


class GseVersion(EnhanceEnum):
    V1 = "V1"
    V2 = "V2"

    @classmethod
    def _get_member__alias_map(cls) -> Dict[Enum, str]:
        return {cls.V1: "V1", cls.V2: "V2"}
