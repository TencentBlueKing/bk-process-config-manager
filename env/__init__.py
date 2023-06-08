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
from .paas_version_diff import *  # noqa


__all__ = [
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
    "BKAPP_DOCS_URL",
    "BKAPP_STATIC_PROTOCOL_PREFIX",
    "BKPAAS_BK_DOMAIN",
]

# 文档地址
BKAPP_DOCS_URL = get_type_env(
    key="BKAPP_DOCS_URL", default="https://bk.tencent.com/docs/document/7.0/232/30348", _type=str
)

# 站点协议前缀，用于静态文件访问链接异常的场景
BKAPP_STATIC_PROTOCOL_PREFIX = get_type_env("BKAPP_STATIC_PROTOCOL_PREFIX", default="", _type=str)

# 蓝鲸主域名
BKPAAS_BK_DOMAIN = get_type_env("BKPAAS_BK_DOMAIN", default="", _type=str)
