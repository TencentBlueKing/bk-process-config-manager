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
import sys

from django.conf import settings

from apps.utils import build_auth_args
from apps.utils.local import get_request


def _clean_auth_info_uin(auth_info):
    if "uin" in auth_info:
        # 混合云uin去掉第一位
        if auth_info["uin"].startswith("o"):
            auth_info["uin"] = auth_info["uin"][1:]
    return auth_info


def update_bkdata_auth_info(params):
    """
    更新参数中的数据平台鉴权信息
    """
    if settings.FEATURE_TOGGLE.get("bkdata_token_auth", "off") == "on":
        # 如果使用 bkdata token 鉴权，需要设置鉴权方式，如果是用户鉴权，直接沿用原来的用户
        params["bkdata_authentication_method"] = params.get("bkdata_authentication_method") or "token"
        params["bkdata_data_token"] = settings.BKDATA_DATA_TOKEN
    else:
        # 如果是用户授权，设置为admin超级管理员
        params["bkdata_authentication_method"] = "user"
        params["bk_username"] = "admin"
        params["operator"] = "admin"
    return params


IS_BACKEND = False
for argv in sys.argv:
    if "celery" in argv:
        IS_BACKEND = True
        break
    if "manage.py" in argv and "runserver" not in sys.argv:
        IS_BACKEND = True


# 后台任务 & 测试任务调用 ESB 接口不需要用户权限控制
if IS_BACKEND:

    def add_esb_info_before_request(params):
        params["bk_app_code"] = settings.APP_CODE
        params["bk_app_secret"] = settings.SECRET_KEY

        if "bk_username" not in params:
            params["bk_username"] = "admin"

        params.pop("_request", None)
        return params


# 正常 WEB 请求所使用的函数
else:

    def add_esb_info_before_request(params):
        """
        通过 params 参数控制是否检查 request

        @param {Boolean} [params.no_request] 是否需要带上 request 标识
        """
        # 规范后的参数
        params["bk_app_code"] = settings.APP_CODE
        params["bk_app_secret"] = settings.SECRET_KEY

        if "no_request" in params and params["no_request"]:
            params["bk_username"] = "admin"
        else:
            # _request，用于并发请求的场景
            _request = params.get("_request")
            req = _request or get_request()
            auth_info = build_auth_args(_request)
            params.update(auth_info)

            bk_username = req.user.bk_username if hasattr(req.user, "bk_username") else req.user.username
            params["bk_username"] = bk_username

        params.pop("_request", None)
        return params
