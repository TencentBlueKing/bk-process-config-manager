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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.gsekit.configfile import mock_data
from apps.gsekit.configfile.models import ConfigTemplate
from apps.gsekit.process.models import Process
from apps.gsekit.process.serializers.process import ProcessFilterBaseSerializer
from apps.utils.drf import OrderingSerializer, PageSerializer


class ListConfigTemplateRequestSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_CONFIG_TEMPLATE_REQUEST_BODY}


class ListConfigTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_CONFIG_TEMPLATE_RESPONSE}


class CreateConfigTemplateRequestSerializer(serializers.Serializer):
    template_name = serializers.CharField(help_text=_("模板名称"))
    file_name = serializers.CharField(help_text=_("文件名称"))
    abs_path = serializers.CharField(help_text=_("文件绝对路径"))
    owner = serializers.CharField(help_text=_("文件所有者"))
    group = serializers.CharField(help_text=_("文件归属群组"))
    filemode = serializers.CharField(help_text=_("文件权限"))
    line_separator = serializers.CharField(help_text=_("换行符格式"))

    def validate(self, attrs):
        attrs["abs_path"] = os.path.normpath(attrs["abs_path"])
        return attrs

    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_CONFIG_TEMPLATE_REQUEST_BODY}


class CreateConfigTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_CONFIG_TEMPLATE_RESPONSE}


class RetrieveConfigTemplateRequestSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.RETRIEVE_CONFIG_TEMPLATE_REQUEST_BODY}


class RetrieveConfigTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.RETRIEVE_CONFIG_TEMPLATE_RESPONSE}


class UpdateConfigTemplateRequestSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if attrs.get("abs_path"):
            attrs["abs_path"] = os.path.normpath(attrs["abs_path"])
        return attrs

    class Meta:
        model = ConfigTemplate
        fields = ["template_name", "file_name", "abs_path", "owner", "group", "filemode", "line_separator"]
        swagger_schema_fields = {"example": mock_data.UPDATE_CONFIG_TEMPLATE_REQUEST_BODY}


class UpdateConfigTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.UPDATE_CONFIG_TEMPLATE_RESPONSE}


class DeleteConfigTemplateRequestSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.DELETE_CONFIG_TEMPLATE_REQUEST_BODY}


class ListConfigTemplateVersionRequestSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_CONFIG_TEMPLATE_VERSION_REQUEST_BODY}


class ListConfigTemplateVersionResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_CONFIG_TEMPLATE_VERSION_RESPONSE}


class CreateConfigTemplateVersionRequestSerializer(serializers.Serializer):
    description = serializers.CharField(help_text=_("版本描述"))
    content = serializers.CharField(help_text=_("配置版本内容"), allow_blank=True, trim_whitespace=False)
    file_format = serializers.CharField(help_text=_("文件格式"))
    is_active = serializers.BooleanField(help_text=_("是否保存上线"), required=False, default=False)

    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY}


class CreateConfigTemplateVersionResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.CREATE_CONFIG_TEMPLATE_VERSION_RESPONSE}


class ListBindingRelationshipResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_BINDING_RELATIONSHIP_RESPONSE}


class ProcessObjectSerializer(serializers.Serializer):
    process_object_type = serializers.ChoiceField(help_text=_("进程对象类型"), choices=Process.PROCESS_OBJECT_TYPE_CHOICE)
    process_object_id = serializers.IntegerField(help_text=_("进程对象ID"))


class BindTemplateToProcessRequestSerializer(serializers.Serializer):
    config_template_id = serializers.IntegerField(help_text=_("配置模板ID"), required=False)
    process_object_list = serializers.ListField(
        help_text=_("进程对象列表"), child=ProcessObjectSerializer(help_text=_("进程对象")), allow_empty=True
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.BIND_TEMPLATE_TO_PROCESS_REQUEST_BODY}


class BindTemplateToProcessResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.BIND_TEMPLATE_TO_PROCESS_RESPONSE}


class BindProcessToTemplateRequestSerializer(ProcessObjectSerializer):
    config_template_id_list = serializers.ListField(
        help_text=_("配置模板ID列表"), child=serializers.IntegerField(help_text=_("配置模板ID")), allow_empty=True
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.BIND_PROCESS_TO_TEMPLATE_REQUEST_BODY}


class BindProcessToTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.BIND_PROCESS_TO_TEMPLATE_RESPONSE}


class GenerateConfigRequestSerializer(ProcessFilterBaseSerializer):
    config_template_id = serializers.IntegerField(help_text=_("配置模板ID"), required=False)
    config_version_ids = serializers.ListField(help_text=_("配置模板版本ID列表"), required=False)

    class Meta:
        swagger_schema_fields = {"example": mock_data.GENERATE_CONFIG_REQUEST_BODY}


class SyncGenerateConfigRequestSerializer(serializers.Serializer):
    bk_process_id = serializers.IntegerField(help_text=_("进程ID"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.SYNC_GENERATE_CONFIG_REQUEST_BODY}


class ListGeneratedConfigResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_GENERATED_CONFIG_RESPONSE}


class ReleaseConfigRequestSerializer(ProcessFilterBaseSerializer):
    config_template_id = serializers.IntegerField(help_text=_("配置模板ID"), required=False)
    config_version_ids = serializers.ListField(help_text=_("配置模板版本ID列表"), required=False)

    class Meta:
        swagger_schema_fields = {"example": mock_data.RELEASE_CONFIG_REQUEST_BODY}


class ReleaseConfigResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.RELEASE_CONFIG_RESPONSE}


class ListConfigTemplateV2RequestSerializer(PageSerializer, OrderingSerializer):
    binding_config_template_ids = serializers.ListField(
        help_text=_("配置模板ID列表"), required=False, child=serializers.IntegerField()
    )

    class Meta:
        swagger_schema_fields = {"example": mock_data.LIST_CONFIG_TEMPLATE_V2_REQUEST_BODY}
