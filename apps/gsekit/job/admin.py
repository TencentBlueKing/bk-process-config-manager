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


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "bk_biz_id",
        "expression_scope",
        "job_object",
        "job_action",
        "status",
        "created_by",
        "start_time",
        "end_time",
        "bk_app_code",
    ]
    search_fields = ["bk_biz_id", "created_by", "pipeline_id"]
    list_filter = ["job_object", "job_action", "status", "is_ready", "bk_app_code"]
    list_editable = ["status"]


@admin.register(models.JobTask)
class JobTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "job_id", "bk_process_id", "status", "err_code", "start_time", "end_time", "pipeline_id"]
    search_fields = ["job_id", "pipeline_id"]
    list_filter = ["status", "err_code"]
    list_editable = ["status"]
