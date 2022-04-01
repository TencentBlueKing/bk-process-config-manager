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


@admin.register(models.ConfigTemplate)
class ConfigTemplatesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ConfigTemplate._meta.get_fields()]
    search_fields = ["bk_biz_id", "template_name", "file_name", "abs_path", "created_by"]
    list_filter = ["bk_biz_id", "owner", "group", "filemode", "line_separator"]


@admin.register(models.ConfigTemplateVersion)
class ConfigTemplateVersionAdmin(admin.ModelAdmin):
    list_display = ["config_version_id", "config_template_id", "description", "is_draft", "is_active", "file_format"]
    search_fields = ["config_version_id", "config_template_id", "description"]
    list_filter = ["is_draft", "is_active", "file_format"]


@admin.register(models.ConfigInstance)
class ConfigInstanceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ConfigInstance._meta.get_fields()]
    search_fields = ["config_template_id", "bk_process_id", "name", "path", "sha256"]
    list_filter = ["is_latest", "is_released"]


@admin.register(models.ConfigTemplateBindingRelationship)
class ConfigTemplateBindingRelationshipAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ConfigTemplateBindingRelationship._meta.get_fields()]
    search_fields = [
        "config_template_id",
    ]
    list_filter = ["process_object_type"]
