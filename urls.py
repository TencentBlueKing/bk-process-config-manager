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

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # 出于安全考虑，默认屏蔽admin访问路径。
    # 开启前请修改路径随机内容，降低被猜测命中几率，提升安全性
    url(r"^admin_gsekit/?", admin.site.urls),
    url(r"^account/", include("blueapps.account.urls")),
    url(r"^api/iam/", include("apps.iam.urls")),
    url(r"^api/core/", include("apps.core.urls")),
    url(r"^", include("apps.gsekit.urls")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
]
