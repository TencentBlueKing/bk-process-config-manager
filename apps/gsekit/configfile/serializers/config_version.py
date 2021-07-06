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
from apps.gsekit.configfile import mock_data


class CreateConfigVersionRequestSerializer(serializers.Serializer):
    description = serializers.CharField(help_text=_("配置模板版本描述"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.CLONE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY}


class CreateConfigVersionResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.CLONE_CONFIG_TEMPLATE_VERSION_RESPONSE}


class UpdateConfigVersionRequestSerializer(serializers.Serializer):
    description = serializers.CharField(help_text=_("描述"))
    content = serializers.CharField(help_text=_("配置版本内容"), allow_blank=True, trim_whitespace=False)
    is_draft = serializers.BooleanField(help_text=_("是否草稿"))
    is_active = serializers.BooleanField(help_text=_("是否上线"))
    file_format = serializers.CharField(help_text=_("文件风格"), required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        if attrs["is_draft"] == attrs["is_active"]:
            raise ValidationError(_("不允许同时保存为草稿和可用状态"))
        return attrs

    class Meta:
        swagger_schema_fields = {"example": mock_data.UPDATE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY}


class PreviewConfigRequestSerializer(serializers.Serializer):
    content = serializers.CharField(help_text=_("配置版本内容"), allow_blank=True, trim_whitespace=False)
    bk_process_id = serializers.IntegerField(help_text=_("进程实例ID"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.PREVIEW_CONFIG_REQUEST_BODY}


class PreviewConfigResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PREVIEW_CONFIG_RESPONSE}
