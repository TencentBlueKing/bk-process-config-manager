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
import datetime

from blueapps.account.conf import ConfFixture
from django.conf import settings
from django.utils.translation import ugettext as _
from apps.gsekit import constants

"""
context_processor for common(setting)

除setting外的其他context_processor内容，均采用组件的方式(string)
"""
WEB_TITLE_MAP = {
    "ieod": _("{app_name} | 腾讯蓝鲸智云").format(app_name=settings.APP_NAME),
    "open": _("{app_name} | 腾讯蓝鲸智云").format(app_name=settings.APP_NAME),
}


def get_docs_center_url():
    docs_suffix = "markdown/进程配置管理/产品白皮书/Introduce/Overview.md"
    if settings.BK_DOCS_CENTER_HOST:
        docs_prefix = settings.BK_DOCS_CENTER_HOST
        return f"{docs_prefix}/{docs_suffix}"

    if settings.BKAPP_RUN_ENV == constants.BkappRunEnvType.CE.value:
        docs_prefix = "https://bk.tencent.com/docs"
    else:
        docs_prefix = f"{settings.BK_PAAS_HOST}/o/bk_docs_center"
    return f"{docs_prefix}/{docs_suffix}"


def mysetting(request):
    return {
        "gettext": _,
        "_": _,
        "LANGUAGES": settings.LANGUAGES,
        # 基础信息
        "RUN_MODE": settings.RUN_MODE,
        "ENVIRONMENT": settings.ENVIRONMENT,
        "APP_CODE": settings.APP_CODE,
        "APP_NAME": settings.APP_NAME,
        "SITE_URL": settings.SITE_URL,
        "BKAPP_DOCS_URL": settings.BKAPP_DOCS_URL,
        "AJAX_URL_PREFIX": settings.SITE_URL,
        # 远程静态资源url
        "REMOTE_STATIC_URL": settings.REMOTE_STATIC_URL,
        # 静态资源
        "STATIC_URL": settings.STATIC_URL,
        "BK_STATIC_URL": f"{settings.BKAPP_STATIC_PROTOCOL_PREFIX}{settings.STATIC_URL}dist",
        "STATIC_VERSION": settings.STATIC_VERSION,
        # 登录跳转链接
        "LOGIN_URL": ConfFixture.LOGIN_URL,
        "LOGIN_SERVICE_URL": ConfFixture.LOGIN_URL,
        # 当前页面，主要为了login_required做跳转用
        "APP_PATH": request.get_full_path(),
        "NOW": datetime.datetime.now(),
        "RUN_VER": settings.RUN_VER,
        "TITLE": WEB_TITLE_MAP.get(settings.RUN_VER),
        "USERNAME": request.user.username,
        "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
        # 第三方系统配置
        "CMDB_URL": settings.BK_CC_HOST,
        "TAM_AEGIS_KEY": settings.TAM_AEGIS_KEY,
        "TAM_AEGIS_URL": settings.TAM_AEGIS_URL,
        # 导航栏开源社区地址
        "BKAPP_NAV_OPEN_SOURCE_URL": settings.BKAPP_NAV_OPEN_SOURCE_URL,
        # 导航栏技术支持地址
        "BKAPP_NAV_HELPER_URL": settings.BKAPP_NAV_HELPER_URL,
        "BK_DOCS_CENTER_URL": get_docs_center_url(),
        "BKAPP_RUN_ENV": settings.BKAPP_RUN_ENV,
    }
