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

from apps.gsekit import constants
from apps.gsekit.cmdb.constants import BK_SET_ENV_CHOICES, BkSetEnv


class ScopeSerializer(serializers.Serializer):
    # TODO 前端联调后设置字段必填
    bk_set_env = serializers.ChoiceField(
        help_text=_("环境类型"), choices=BK_SET_ENV_CHOICES, required=False, default=BkSetEnv.FORMAL
    )
    bk_set_ids = serializers.ListField(help_text=_("集群ID列表"), child=serializers.IntegerField(), required=False)
    bk_module_ids = serializers.ListField(help_text=_("模块ID列表"), child=serializers.IntegerField(), required=False)
    bk_service_ids = serializers.ListField(help_text=_("服务实例ID列表"), child=serializers.IntegerField(), required=False)
    bk_process_names = serializers.ListField(help_text=_("进程别名列表"), child=serializers.CharField(), required=False)
    bk_process_ids = serializers.ListField(help_text=_("进程ID列表"), child=serializers.IntegerField(), required=False)


class ExpresssionScopeSerializer(serializers.Serializer):
    bk_set_env = serializers.ChoiceField(help_text=_("环境类型"), choices=BK_SET_ENV_CHOICES)
    bk_set_name = serializers.CharField(help_text=_("集群名称表达式"), required=False, default="*", allow_blank=True)
    bk_module_name = serializers.CharField(help_text=_("模块名称表达式"), required=False, default="*", allow_blank=True)
    service_instance_name = serializers.CharField(
        help_text=_("服务实例名称表达式"), required=False, default="*", allow_blank=True
    )
    bk_process_name = serializers.CharField(help_text=_("进程别名表达式"), required=False, default="*", allow_blank=True)
    bk_process_id = serializers.CharField(help_text=_("进程ID表达式"), required=False, default="*", allow_blank=True)

    def validate(self, attrs):
        attrs["bk_set_name"] = attrs.get("bk_set_name") or "*"
        attrs["bk_module_name"] = attrs.get("bk_module_name") or "*"
        attrs["service_instance_name"] = attrs.get("service_instance_name") or "*"
        attrs["bk_process_name"] = attrs.get("bk_process_name") or "*"
        attrs["bk_process_id"] = attrs.get("bk_process_id") or "*"
        return attrs


def gen_expression(expression_scope):
    expression_fields = ["bk_set_name", "bk_module_name", "service_instance_name", "bk_process_name", "bk_process_id"]
    return constants.EXPRESSION_SPLITTER.join([expression_scope[field] for field in expression_fields])
