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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.gsekit.meta import mock_data


class GetUserInfoResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.GET_USER_INFO_RESPONSE}


class JobTaskFilterChoicesRequestSerializer(serializers.Serializer):
    job_id = serializers.IntegerField(help_text=_("任务ID"))


class JobTaskFilterChoicesResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.JOB_TASK_FILTER_CHOICES_RESPONSE}


class ProcessFilterChoicesResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_FILTER_CHOICES_RESPONSE}


class ExpressionMatchRequestSerializer(serializers.Serializer):
    expression = serializers.CharField(help_text=_("表达式"))
    candidates = serializers.ListField(help_text=_("待筛选字符串"), child=serializers.CharField(), required=False, default=[])

    class Meta:
        swagger_schema_fields = {"example": mock_data.EXPRESSION_MATCH_REQUEST}


class ExpressionMatchResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.EXPRESSION_MATCH_RESPONSE}
