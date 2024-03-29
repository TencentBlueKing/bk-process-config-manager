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

from django.apps import AppConfig
from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

"""
API 统一调用模块，使用方式，举例
>>> from apps.api import CCApi
>>> CCApi.search_business({})
"""


def new_api_module(module_name, api_name, module_dir="modules"):
    mod = "apps.api.{modules}.{mod}.{api}".format(modules=module_dir, mod=module_name, api=api_name)
    return import_string(mod)()


# 对请求模块设置懒加载机制，避免项目启动出现循环引用，或者 model 提前加载

# 蓝鲸平台模块域名
CCApi = SimpleLazyObject(lambda: new_api_module("cc", "_CCApi"))
JobApi = SimpleLazyObject(lambda: new_api_module("job", "_JobApi"))
GseApi = SimpleLazyObject(lambda: new_api_module("gse", "_GseApi"))
GseV2Api = SimpleLazyObject(lambda: new_api_module("gse_v2", "_GseV2Api"))
BscpApi = SimpleLazyObject(lambda: new_api_module("bscp", "_BscpApi"))
EsbApi = SimpleLazyObject(lambda: new_api_module("esb", "_ESBApi"))
UserManageApi = SimpleLazyObject(lambda: new_api_module("usermanage", "_UserManageApi"))
# 节点管理
# NodeApi = SimpleLazyObject(lambda: new_api_module("bk_node", "_BKNodeApi"))
CmsiApi = SimpleLazyObject(lambda: new_api_module("cmsi", "_CmsiApi"))

__all__ = ["CCApi", "JobApi", "GseApi", "GseV2Api", "EsbApi", "BscpApi", "UserManageApi", "CmsiApi"]


class ApiConfig(AppConfig):
    name = "apps.api"
    verbose_name = "ESB_API"

    def ready(self):
        pass


default_app_config = "apps.api.ApiConfig"
