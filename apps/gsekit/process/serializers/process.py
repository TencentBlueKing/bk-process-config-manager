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

from apps.exceptions import ValidationError
from apps.gsekit.process import mock_data
from apps.gsekit.utils.expression_utils.parse import BuildInChar
from apps.gsekit.utils.expression_utils.serializers import ExpresssionScopeSerializer, ScopeSerializer
from apps.utils.drf import PageSerializer, OrderingSerializer


class RecursiveField(serializers.Serializer):
    """指向自己递归"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ProcessInstanceRequestSerializer(serializers.Serializer):
    service_instance_id = serializers.IntegerField(help_text=_("服务实例ID"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_INSTANCE_REQUEST_BODY}


class ProcessInstanceResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_INSTANCE_RESPONSE}


class ProcessTemplateRequestSerializer(serializers.Serializer):
    service_template_id = serializers.IntegerField(help_text=_("服务模板ID"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_TEMPLATE_REQUEST_BODY}


class ProcessTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_TEMPLATE_RESPONSE}


class UpdateProcessInstanceRequestSerializer(serializers.Serializer):
    process_property = serializers.DictField(help_text=_("进程属性列表"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.UPDATE_PROCESS_INSTANCE_REQUEST_BODY}


class UpdateProcessInstanceResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.UPDATE_PROCESS_INSTANCE_RESPONSE}


class UpdateProcessTemplateRequestSerializer(serializers.Serializer):
    process_template_id = serializers.IntegerField(help_text=_("进程模板ID"))
    process_property = serializers.DictField(help_text=_("进程模板属性"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.UPDATE_PROCESS_TEMPLATE_REQUEST_BODY}


class UpdateProcessTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.UPDATE_PROCESS_TEMPLATE_RESPONSE}


class CreateProcessInstanceRequestSerializer(serializers.Serializer):
    service_instance_id = serializers.IntegerField(help_text=_("服务实例ID"))
    process_property = serializers.DictField(help_text=_("进程属性列表"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_PROCESS_INSTANCE_REQUEST_BODY}


class CreateProcessInstanceResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_PROCESS_INSTANCE_RESPONSE}


class CreateProcessTemplateRequestSerializer(serializers.Serializer):
    service_template_id = serializers.IntegerField(help_text=_("服务模板ID"))
    process_property = serializers.DictField(help_text=_("进程模板属性"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_PROCESS_TEMPLATE_REQUEST_BODY}


class CreateProcessTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_PROCESS_INSTANCE_RESPONSE}


class DeleteProcessInstanceRequestSerializer(serializers.Serializer):
    process_instance_ids = serializers.ListField(
        help_text=_("进程实例ID列表"), child=serializers.IntegerField(), min_length=1
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.DELETE_PROCESS_INSTANCE_REQUEST_BODY}


class DeleteProcessTemplateRequestSerializer(serializers.Serializer):
    process_template_ids = serializers.ListField(
        help_text=_("进程模板ID列表"), child=serializers.IntegerField(), min_length=1
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.DELETE_PROCESS_TEMPLATE_REQUEST_BODY}


class ProcessInstanceConfigRequestSerializer(serializers.Serializer):
    bk_process_ids = serializers.ListField(help_text=_("进程实例ID列表"), child=serializers.IntegerField(help_text=_("进程ID")))


class ProcessInstanceConfigResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_INSTANCE_CONFIG_RESPONSE}


class ProcessFilterBaseSerializer(serializers.Serializer):
    scope = ScopeSerializer(help_text=_("进程范围"), required=False)
    expression_scope = ExpresssionScopeSerializer(help_text=_("操作范围表达式, 和scope同时传入时, 优先使用scope"), required=False)

    def validate(self, data):
        if not ("scope" in data or "expression_scope" in data):
            raise ValidationError(_("scope, expression_scope required at least one."))
        return data


class ProcessStatusRequestSerializer(PageSerializer, OrderingSerializer, ProcessFilterBaseSerializer):
    bk_host_innerips = serializers.ListField(child=serializers.CharField(help_text=_("内网IP")), required=False)
    bk_cloud_ids = serializers.ListField(help_text=_("云区域ID列表"), required=False)
    process_status = serializers.IntegerField(help_text=_("进程状态"), required=False)
    searches = serializers.ListField(help_text=_("多模糊查询:支持内网IP及云区域名称"), child=serializers.CharField(), required=False)
    is_auto = serializers.BooleanField(help_text=_("托管状态"), required=False)
    is_auto_list = serializers.ListField(
        help_text=_("托管状态列表"), child=serializers.BooleanField(help_text=_("托管状态")), required=False
    )
    process_status_list = serializers.ListField(
        help_text=_("进程状态列表"), child=serializers.IntegerField(help_text=_("进程状态")), required=False
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_STATUS_REQUEST_BODY}


class ProcessStatusResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_STATUS_RESPONSE}


class OperateProcessRequestSerializer(ProcessFilterBaseSerializer):
    op_type = serializers.CharField(help_text=_("任务动作"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.OPERATE_PROCESS_REQUEST_BODY}


class OperateProcessResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.OPERATE_PROCESS_RESPONSE}


class ProcessInstanceSimpleRequestSerializer(serializers.Serializer):
    service_instance_ids = serializers.ListField(
        help_text=_("服务实例ID列表"), child=serializers.IntegerField(), required=False
    )
    expression = serializers.CharField(help_text=_("筛选表达式"), required=False, default=BuildInChar.ASTERISK)
    # TODO: 兼容原接口，后续前端变更后改用ProcessFilterBaseSerializer
    scope = ScopeSerializer(help_text=_("进程范围"), required=False)
    expression_scope = ExpresssionScopeSerializer(help_text=_("操作范围表达式, 和scope同时传入时, 优先使用scope"), required=False)

    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_INSTANCE_SIMPLE_REQUEST_BODY}


class ProcessInstanceSimpleResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_INSTANCE_SIMPLE_RESPONSE}
