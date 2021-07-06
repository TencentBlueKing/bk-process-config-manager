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
from django.utils.translation import ugettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.configfile import exceptions
from apps.gsekit.configfile.handlers.config_version import ConfigVersionHandler
from apps.gsekit.configfile.serializers import config_version as config_version_serializer
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import InstanceActionPermission, ViewBusinessPermission
from apps.utils.mako_utils.checker import check_mako_template_safety
from apps.utils.mako_utils.exceptions import ForbiddenMakoTemplateException
from apps.utils.mako_utils.visitor import MakoNodeVisitor
from apps.utils.models import model_to_dict

ConfigVersionViewTags = ["config_version"]


class ConfigVersionViews(APIViewSet):
    lookup_field = "config_version_id"

    def config_template_ids_getter(self, request):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        config_version_id = self.kwargs[lookup_url_kwarg]
        config_template_id = ConfigVersionHandler(config_version_id=config_version_id).data.config_template_id
        return [config_template_id]

    def get_instance_ids_getter(self, request):
        if self.action in ["clone", "update", "retrieve"]:
            return self.config_template_ids_getter(request)
        return None

    def get_permissions(self):

        if self.detail:
            return [
                InstanceActionPermission(
                    [ActionEnum.EDIT_CONFIG_TEMPLATE], ResourceEnum.CONFIG_TEMPLATE, self.get_instance_ids_getter
                ),
            ]

        return [ViewBusinessPermission()]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "update": config_version_serializer.UpdateConfigVersionRequestSerializer,
        }
        return action_serializer_map.get(self.action, serializers.Serializer)

    @swagger_auto_schema(
        operation_summary="创建配置模板版本（克隆）",
        tags=ConfigVersionViewTags,
        request_body=config_version_serializer.CreateConfigVersionRequestSerializer(),
        responses={status.HTTP_200_OK: config_version_serializer.CreateConfigVersionResponseSerializer()},
    )
    @action(
        methods=["POST"], detail=True, serializer_class=config_version_serializer.CreateConfigVersionRequestSerializer
    )
    def clone(self, request, config_version_id, *args, **kwargs):
        description = self.validated_data["description"]
        return Response(ConfigVersionHandler(config_version_id=config_version_id).clone(description))

    @swagger_auto_schema(
        operation_summary="编辑配置模板版本（草稿/保存）",
        tags=ConfigVersionViewTags,
        request_body=config_version_serializer.UpdateConfigVersionRequestSerializer(),
    )
    def update(self, request, config_version_id, *args, **kwargs):
        description = self.validated_data["description"]
        content = self.validated_data["content"]
        try:
            check_mako_template_safety(content, MakoNodeVisitor())
        except ForbiddenMakoTemplateException as mako_error:
            raise exceptions.ForbiddenMakoTemplateException(str(mako_error))
        is_draft = self.validated_data["is_draft"]
        is_active = self.validated_data["is_active"]
        file_format = self.validated_data.get("file_format")
        if "${HELP}" in content:
            raise exceptions.ForbiddenConfigContentException(err_msg=_("${HELP}变量仅在预览时提供帮助，保存配置时请不要包含"))
        return Response(
            ConfigVersionHandler(config_version_id=config_version_id).update(
                description, content, is_draft, is_active, file_format
            )
        )

    @swagger_auto_schema(
        operation_summary="获取配置模板详情", tags=ConfigVersionViewTags,
    )
    def retrieve(self, request, config_version_id, *args, **kwargs):
        return Response(model_to_dict(ConfigVersionHandler(config_version_id=config_version_id).data))

    @swagger_auto_schema(
        operation_summary="指定进程实例预览配置模板",
        tags=ConfigVersionViewTags,
        request_body=config_version_serializer.PreviewConfigRequestSerializer(),
        responses={status.HTTP_200_OK: config_version_serializer.PreviewConfigResponseSerializer()},
    )
    @action(detail=False, methods=["POST"], serializer_class=config_version_serializer.PreviewConfigRequestSerializer)
    def preview(self, request, bk_biz_id, *args, **kwargs):
        bk_process_id = self.validated_data["bk_process_id"]
        content = self.validated_data["content"]
        try:
            check_mako_template_safety(content, MakoNodeVisitor())
        except ForbiddenMakoTemplateException as mako_error:
            raise exceptions.ForbiddenMakoTemplateException(str(mako_error))
        process_info = ProcessHandler(bk_biz_id=bk_biz_id).process_info(bk_process_id=bk_process_id)
        CMDBHandler(bk_biz_id=bk_biz_id).cache_topo_tree_attr(bk_set_env=process_info["set"]["bk_set_env"])
        return Response(ConfigVersionHandler.render(bk_biz_id, process_info, content))
