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
from django.conf.urls import url
from django.urls import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from apps.gsekit import home
from apps.gsekit.cmdb.views import cmdb
from apps.gsekit.configfile.views import config_template, config_version, config_instance
from apps.gsekit.job.views import JobViews
from apps.gsekit.meta import views as meta_view
from apps.gsekit.operations import views as operations_view
from apps.gsekit.migrate.views import MigrateViewSet
from apps.gsekit.process.views import process
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

biz_router = routers.DefaultRouter(trailing_slash=True)
biz_router.register(r"process", process.ProcessViews, basename="process")
biz_router.register(r"config_template", config_template.ConfigTemplateViews, basename="config_template")
biz_router.register(r"config_version", config_version.ConfigVersionViews, basename="config_version")

biz_router.register(r"config_instance", config_instance.ConfigInstanceViews, basename="config_instance")

biz_router.register(r"cmdb", cmdb.CMDBViews, basename="cmdb")
biz_router.register(r"job", JobViews, basename="job")
biz_router.register(r"meta", meta_view.MetaViewSet, basename="meta")
biz_router.register(r"migrate", MigrateViewSet, basename="migrate")

none_biz_router = routers.DefaultRouter(trailing_slash=True)
none_biz_router.register(r"meta", operations_view.OperationsViewSet, basename="operations")

urlpatterns = [
    url(r"^$", home.index),
    url(r"^metrics/?$", home.metrics),
    url(r"api/(?P<bk_biz_id>\d+)/", include(biz_router.urls)),
    url(r"^", include(none_biz_router.urls)),
    url(r"^", home.index),
]

if settings.ENVIRONMENT not in ["production", "prod"]:
    schema_view = get_schema_view(
        openapi.Info(
            title=_("{app_name} API").format(app_name=settings.APP_NAME),
            default_version="v1",
            description=_(
                "{app_name} 是腾讯蓝鲸智云推出的一个专注于进程和配置文件管理的 SaaS 工具。\n"
                "GitHub 开源，欢迎共建：https://github.com/TencentBlueKing/bk-process-config-manager"
            ).format(app_name=settings.APP_NAME),
        ),
        public=True,
        permission_classes=(permissions.IsAdminUser,),
    )
    swagger_format_view = schema_view.without_ui(cache_timeout=0)
    setattr(swagger_format_view, "login_exempt", True)
    urlpatterns += [
        url(r"^swagger(?P<format>\.json|\.yaml)$", swagger_format_view, name="schema-json"),
        url(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        url(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
