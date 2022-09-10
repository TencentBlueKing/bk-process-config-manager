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

from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _

from apps.gsekit.job import mock_data
from apps.utils.drf import PageSerializer
from apps.gsekit.job.models import Job, JOB_STATUS_CHOICES
from apps.gsekit.utils.expression_utils.serializers import ExpresssionScopeSerializer, ScopeSerializer


class CreateJobRequestSerializer(serializers.Serializer):
    job_object = serializers.ChoiceField(help_text=_("操作对象"), choices=Job.JOB_OBJECT_CHOICES)
    job_action = serializers.ChoiceField(help_text=_("操作动作"), choices=Job.JOB_ACTION_CHOICES)

    scope = ScopeSerializer(help_text=_("进程范围"), required=False)
    expression_scope = ExpresssionScopeSerializer(help_text=_("操作范围表达式, 和scope同时传入时, 优先使用scope"), required=False)
    extra_data = serializers.DictField(help_text=_("其它参数"), required=False)


class JobTaskResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.JOB_TASK_RESPONSE}


class JobTaskRequestSerializer(PageSerializer):
    # 提高鲁棒性，使用 CharField 代替 IntegerField
    bk_set_ids = serializers.ListField(
        help_text=_("集群ID列表"), child=serializers.CharField(help_text=_("集群ID")), required=False
    )
    bk_module_ids = serializers.ListField(
        help_text=_("模块ID列表"), child=serializers.CharField(help_text=_("模块ID")), required=False
    )
    bk_process_ids = serializers.ListField(
        help_text=_("进程ID列表"), child=serializers.CharField(help_text=_("进程ID")), required=False
    )
    bk_process_names = serializers.ListField(
        help_text=_("进程别名列表"), child=serializers.CharField(help_text=_("进程别名")), required=False
    )
    statuses = serializers.ListField(
        help_text=_("任务状态列表"),
        child=serializers.ChoiceField(help_text=_("任务状态"), choices=JOB_STATUS_CHOICES),
        required=False,
    )
    err_code = serializers.IntegerField(help_text=_("错误码"), required=False)

    class Meta:
        swagger_schema_fields = {"example": mock_data.JOB_TASK_REQUEST}


class JobStatusResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.JOB_STATUS_RESPONSE}


class RetryRequestSerializer(serializers.Serializer):
    job_task_id_list = serializers.ListField(help_text=_("任务ID列表"), required=False)


class SearchIpRequestSerializer(serializers.Serializer):
    status = serializers.CharField(help_text=_("任务状态"), required=False)
