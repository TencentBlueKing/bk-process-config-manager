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

import os

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2019 Tencent BlueKing. All Rights Reserved."
__all__ = ["celery_app", "RUN_VER", "BK_URL", "BASE_DIR"]

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app
from django.utils.translation import ugettext_lazy as _

# app 基本信息


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            ('Environment variable "{}" not found, you must set this variable to run this application.').format(key)
        )
    return value


# SaaS运行版本，如非必要请勿修改
RUN_VER = os.environ.get("BKPAAS_ENGINE_REGION", "open")
# 兼容 V3 取值差异
if RUN_VER == "default":
    RUN_VER = "open"

APP_ID = APP_CODE = os.environ.get("APP_ID", "bk_gsekit")
APP_TOKEN = SECRET_KEY = os.environ.get("APP_TOKEN", "28b7b410-c7b7-4537-9a65-8ce55738170e")

# 蓝鲸平台URL
BK_URL = os.getenv("BKPAAS_URL", None)  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GSEKit 对于外部用户来说理解成本比较高，于是通过 RUN_ENV 区分内外部应用名称
APP_NAME = (_("进程配置管理"), _("GSEKit"))[RUN_VER == "ieod"]
