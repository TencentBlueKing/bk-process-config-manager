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

from apps.gsekit.cmdb import mock_data, constants
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.utils.expression_utils.parse import BuildInChar


class RecursiveField(serializers.Serializer):
    """指向自己递归"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ListBizResponseSerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(help_text=_("业务ID"))
    bk_biz_name = serializers.CharField(help_text=_("业务名称"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.BIZ_LIST_RESPONSE}


class BizTopoResponseSerializer(serializers.Serializer):
    bk_inst_id = serializers.IntegerField(help_text=_("实例ID"))
    bk_inst_name = serializers.CharField(help_text=_("实例名称"))
    bk_obj_id = serializers.CharField(help_text=_("对象ID"))
    bk_obj_name = serializers.CharField(help_text=_("对象名称"))
    service_template_id = serializers.IntegerField(help_text=_("服务模板ID"))
    child = RecursiveField(help_text=_("拓扑子树"), many=True)

    class Meta:
        swagger_schema_fields = {"example": mock_data.BIZ_TOPO_RESPONSE}


class ServiceTemplateResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.SERVICE_TEMPLATE_RESPONSE}


class ServiceInstanceRequestSerializer(serializers.Serializer):
    bk_module_ids = serializers.ListField(help_text=_("模块ID列表"), child=serializers.IntegerField(), required=False)
    expression = serializers.CharField(help_text=_("筛选表达式"), required=False, default=BuildInChar.ASTERISK)
    with_proc_count = serializers.BooleanField(help_text=_("是否包含进程数量信息"), required=False, default=False)


class ProcessRelatedInfoRequestSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_RELATED_INFO_REQUEST_BODY}


class ProcessRelatedInfoResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.PROCESS_RELATED_INFO_RESPONSE}


class ServiceInstanceResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.SERVICE_INSTANCE_RESPONSE}


class ListSetRequestSerializer(serializers.Serializer):
    bk_set_env = serializers.ChoiceField(help_text=_("环境类型"), choices=constants.BK_SET_ENV_CHOICES)
    expression = serializers.CharField(help_text=_("筛选表达式"), required=False, default=BuildInChar.ASTERISK)

    class Meta:
        swagger_schema_fields = {"example": mock_data.SET_LIST_REQUEST_BODY}


class ListSetResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.SET_LIST_RESPONSE}


class ListModuleRequestSerializer(serializers.Serializer):
    bk_set_env = serializers.ChoiceField(
        help_text=_("环境类型"), choices=constants.BK_SET_ENV_CHOICES, default=constants.BkSetEnv.ALL, required=False
    )
    bk_set_ids = serializers.ListField(help_text=_("集群ID列表"), child=serializers.IntegerField(), required=False)
    expression = serializers.CharField(help_text=_("筛选表达式"), required=False, default=BuildInChar.ASTERISK)


class ListModuleResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.MODULE_LIST_RESPONSE}


class BizGlobalVarResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.BIZ_GLOBAL_VAR_RESPONSE}


class BizSearchObjectAttributeRequestSerializer(serializers.Serializer):
    bk_obj_id = serializers.ChoiceField(help_text=_("模型ID"), choices=CMDBHandler.BK_OBJ_ID_CHOICES)

    class Meta:
        swagger_schema_fields = {"example": mock_data.BIZ_SEARCH_OBJECT_ATTRIBUTE_REQUEST_BODY}


class BizSearchObjectAttributeResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.BIZ_SEARCH_OBJECT_ATTRIBUTE_RESPONSE}


class CheckServiceTemplateDifferenceRequestSerializer(serializers.Serializer):
    service_template_id = serializers.IntegerField(help_text=_("服务模板ID"))

    class Meta:
        swagger_schema_fields = {"example": mock_data.CHECK_SERVICE_TMPL_DIFF_REQUEST_BODY}


class CheckServiceTemplateDifferenceResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.CHECK_SERVICE_TEMPLATE_DIFFERENCE_RESPONSE}


class BatchCheckServiceTemplateDifferenceRequestSerializer(serializers.Serializer):
    service_template_ids = serializers.ListField(help_text=_("服务模板ID列表"))


class BatchCheckServiceTemplateDifferenceResponseSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"example": mock_data.BATCH_CHECK_SERVICE_TEMPLATE_DIFFERENCE_RESPONSE}
