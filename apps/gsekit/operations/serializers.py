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
from django.utils.timezone import get_current_timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.gsekit.job.models import Job


class CountStatisticsOrmRequestSerializer(serializers.Serializer):
    filter_conditions = serializers.DictField(help_text=_("筛选条件"))
    exclude_conditions = serializers.DictField(help_text=_("排除条件"))
    group_by = serializers.ListField(help_text=_("分组字段"))


class JobCountStatisticsRequestSerializer(CountStatisticsOrmRequestSerializer):
    class Meta:
        swagger_schema_fields = {
            "example": {
                "filter_conditions": {},
                "exclude_conditions": {},
                "group_by": ["created_by", "bk_biz_id", "job_object", "job_action", "status", "bk_app_code"],
            }
        }


class VisitCountStatisticsRequestSerializer(CountStatisticsOrmRequestSerializer):
    class Meta:
        swagger_schema_fields = {
            "example": {
                "filter_conditions": {"bk_biz_id": 2},
                "exclude_conditions": {},
                "group_by": ["bk_username", "bk_biz_id"],
            }
        }


class VisitRequestSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(help_text=_("业务ID"))

    class Meta:
        swagger_schema_fields = {"example": {"bk_biz_id": 2}}


class FrequencyStatisticsRequestSerializer(serializers.Serializer):

    start_time = serializers.DateTimeField(help_text=_("开始时间"), default_timezone=get_current_timezone())
    end_time = serializers.DateTimeField(help_text=_("结束时间"), default_timezone=get_current_timezone())
    group_by = serializers.CharField(help_text=_("分组字段"))

    class Meta:
        swagger_schema_fields = {
            "example": {"start_time": "2021-01-01 00:00:00", "end_time": "2021-12-31 23:59:59", "group_by": "bk_biz_id"}
        }


class TrendStatisticsRequestSerializer(serializers.Serializer):

    start_time = serializers.DateTimeField(help_text=_("开始时间"), default_timezone=get_current_timezone())
    end_time = serializers.DateTimeField(help_text=_("结束时间"), default_timezone=get_current_timezone())
    job_object = serializers.ChoiceField(help_text=_("操作对象"), choices=Job.JOB_OBJECT_CHOICES, required=False)
    job_action = serializers.ChoiceField(help_text=_("操作动作"), choices=Job.JOB_ACTION_CHOICES, required=False)

    class Meta:
        swagger_schema_fields = {
            "example": {
                "start_time": "2021-01-01 00:00:00",
                "end_time": "2021-12-31 23:59:59",
                "job_action": "start",
                "job_object": "process",
            }
        }
