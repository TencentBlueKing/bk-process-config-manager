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
from apps.utils.env import get_type_env

from .. import constants

# 差异化赋值后的统一命名 settings
__all__ = [
    "BKAPP_RUN_ENV",
    # PaaS 部署环境，标准化为 stag / dev
    "ENVIRONMENT",
    # esb 访问地址
    "BK_COMPONENT_API_URL",
    # 权限中心 SaaS 地址
    "BK_IAM_SAAS_HOST",
    # 提供给权限中心的资源回调地址
    "BK_IAM_RESOURCE_API_HOST",
    # SaaS 访问地址
    "BK_SAAS_HOST",
]

# PaaS 版本
BKPAAS_MAJOR_VERSION = get_type_env(key="BKPAAS_MAJOR_VERSION", default=constants.BkPaaSVersion.V2.value, _type=int)
# 是否为 PaaS V3 容器化部署版本
BKAPP_IS_V3_CONTAINER = get_type_env(key="BKAPP_IS_V3_CONTAINER", default=False, _type=bool)

# 运行环境，ce / ee / ieod, 默认为 ce
BKAPP_RUN_ENV = get_type_env(key="BKAPP_RUN_ENV", default="ce", _type=str)

if BKPAAS_MAJOR_VERSION == constants.BkPaaSVersion.V3.value:
    if BKAPP_IS_V3_CONTAINER:
        from .paas_v3_container import *  # noqa
    else:
        from .paas_v3 import *  # noqa
else:
    from .paas_v2 import *  # noqa
