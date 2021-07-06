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

from django.contrib import admin

from . import models


@admin.register(models.GsekitProcessToCCProcessTemplateMap)
class GsekitProcessToCCProcessTemplateMapAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.GsekitProcessToCCProcessTemplateMap._meta.get_fields()]
    search_fields = ["bk_biz_id"]
    list_filter = ["bk_biz_id"]


@admin.register(models.MigrationStatus)
class MigrationStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.MigrationStatus._meta.get_fields()]
    search_fields = ["bk_biz_id"]
    list_filter = ["migrate_obj", "bk_biz_id"]
