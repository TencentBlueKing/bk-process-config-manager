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
from django.db import transaction, IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import ModelViewSet
from apps.gsekit.configfile import models as config_models
from apps.gsekit.configfile.exceptions import DuplicateTemplateNameException
from apps.gsekit.configfile.handlers.config_template import ConfigTemplateHandler
from apps.gsekit.configfile.serializers import config_template as config_template_serializer
from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import Job
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import (
    ViewBusinessPermission,
    BusinessActionPermission,
    InstanceActionPermission,
    insert_permission_field,
    grant_creator_action,
)
from apps.utils.drf import GeneralSearchFilter, GeneralOrderingFilter
from apps.utils.models import queryset_to_dict_list

ConfigTemplateViewTags = ["config_template"]


class ConfigTemplateViews(ModelViewSet):
    model = config_models.ConfigTemplate
    filter_backends = (GeneralSearchFilter, GeneralOrderingFilter)
    search_fields = ["template_name", "file_name"]
    ordering_fields = ["config_template_id", "template_name", "file_name", "abs_path", "updated_at"]
    lookup_field = "config_template_id"

    def get_queryset(self):
        return self.model.objects.filter(bk_biz_id=self.kwargs["bk_biz_id"])

    def perform_destroy(self, instance):
        """删除配置模板前，需要清理配置模板关联数据"""
        with transaction.atomic():
            config_models.ConfigTemplateBindingRelationship.objects.filter(
                config_template_id=instance.config_template_id
            ).delete()
            super().perform_destroy(instance)

    def get_permissions(self):
        if self.action == "create":
            return [BusinessActionPermission([ActionEnum.CREATE_CONFIG_TEMPLATE])]
        elif self.action in ["update", "partial_update"]:
            return [InstanceActionPermission([ActionEnum.EDIT_CONFIG_TEMPLATE], ResourceEnum.CONFIG_TEMPLATE)]
        elif self.action == "destroy":
            return [InstanceActionPermission([ActionEnum.DELETE_CONFIG_TEMPLATE], ResourceEnum.CONFIG_TEMPLATE)]
        elif self.action in ["generate_config", "sync_generate_config", "release_config"]:
            return [InstanceActionPermission([ActionEnum.OPERATE_CONFIG], ResourceEnum.BUSINESS)]
        return [ViewBusinessPermission()]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {
            "create": config_template_serializer.CreateConfigTemplateRequestSerializer,
            "update": config_template_serializer.UpdateConfigTemplateRequestSerializer,
            "partial_update": config_template_serializer.UpdateConfigTemplateRequestSerializer,
        }
        serializer_class = action_serializer_map.get(self.action)
        if not serializer_class:
            serializer_class = super().get_serializer_class(*args, **kwargs)
        return serializer_class

    @swagger_auto_schema(
        operation_summary="获取配置模板列表",
        tags=ConfigTemplateViewTags,
        query_serializer=config_template_serializer.ListConfigTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.ListConfigTemplateResponseSerializer()},
    )
    @insert_permission_field(
        id_field=lambda d: d["config_template_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.EDIT_CONFIG_TEMPLATE, ActionEnum.DELETE_CONFIG_TEMPLATE],
        resource_meta=ResourceEnum.CONFIG_TEMPLATE,
    )
    def list(self, request, bk_biz_id, *args, **kwargs):
        response = super().list(request, bk_biz_id, *args, **kwargs)
        response.data["list"] = ConfigTemplateHandler.fill_with_is_bound(response.data["list"])
        return response

    @swagger_auto_schema(
        operation_summary="创建配置模板",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.CreateConfigTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.CreateConfigTemplateResponseSerializer()},
    )
    @grant_creator_action(
        id_field=lambda d: d["config_template_id"],
        name_field=lambda d: d["template_name"],
        resource_meta=ResourceEnum.CONFIG_TEMPLATE,
    )
    def create(self, request, bk_biz_id, *args, **kwargs):
        return Response(ConfigTemplateHandler.create_config_template(bk_biz_id=bk_biz_id, **self.validated_data))

    @swagger_auto_schema(
        operation_summary="获取配置模板详情",
        tags=ConfigTemplateViewTags,
        query_serializer=config_template_serializer.RetrieveConfigTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.RetrieveConfigTemplateResponseSerializer()},
    )
    @insert_permission_field(
        id_field=lambda d: d["config_template_id"],
        actions=[ActionEnum.EDIT_CONFIG_TEMPLATE, ActionEnum.DELETE_CONFIG_TEMPLATE],
        resource_meta=ResourceEnum.CONFIG_TEMPLATE,
        many=False,
    )
    def retrieve(self, request, bk_biz_id, config_template_id, *args, **kwargs):
        return Response(
            ConfigTemplateHandler(config_template_id=config_template_id, bk_biz_id=bk_biz_id).retrieve_config_template()
        )

    @swagger_auto_schema(
        operation_summary="更新配置模板",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.UpdateConfigTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.UpdateConfigTemplateResponseSerializer()},
    )
    def update(self, request, config_template_id, *args, **kwargs):
        try:
            return super().update(request, config_template_id, *args, **kwargs)
        except IntegrityError:
            raise DuplicateTemplateNameException(template_name=self.validated_data.get("template_name"))

    @swagger_auto_schema(
        operation_summary="更新配置模板",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.UpdateConfigTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.UpdateConfigTemplateResponseSerializer()},
    )
    def partial_update(self, request, config_template_id, *args, **kwargs):
        try:
            return super().partial_update(request, config_template_id, *args, **kwargs)
        except IntegrityError:
            raise DuplicateTemplateNameException(template_name=self.validated_data.get("template_name"))

    @swagger_auto_schema(operation_summary="删除配置模板", tags=ConfigTemplateViewTags)
    def destroy(self, request, config_template_id, *args, **kwargs):
        return super().destroy(self, request, config_template_id, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="获取配置模板版本列表",
        tags=ConfigTemplateViewTags,
        query_serializer=config_template_serializer.ListConfigTemplateVersionRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.ListConfigTemplateVersionResponseSerializer()},
    )
    @action(methods=["GET"], detail=True)
    def list_version(self, request, bk_biz_id, config_template_id, *args, **kwargs):
        return Response(
            ConfigTemplateHandler(bk_biz_id=bk_biz_id, config_template_id=config_template_id).list_config_version()
        )

    @swagger_auto_schema(
        operation_summary="创建配置版本",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.CreateConfigTemplateVersionRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.CreateConfigTemplateVersionResponseSerializer()},
    )
    @action(
        methods=["POST"],
        detail=True,
        serializer_class=config_template_serializer.CreateConfigTemplateVersionRequestSerializer,
    )
    def create_config_version(self, request, bk_biz_id, config_template_id, *args, **kwargs):
        description = self.validated_data["description"]
        content = self.validated_data["content"]
        file_format = self.validated_data["file_format"]
        is_active = self.validated_data.get("is_active")
        return Response(
            ConfigTemplateHandler(bk_biz_id=bk_biz_id, config_template_id=config_template_id).create_config_version(
                description, content, file_format, is_active
            )
        )

    @swagger_auto_schema(
        operation_summary="配置文件模板绑定关系",
        tags=ConfigTemplateViewTags,
        responses={status.HTTP_200_OK: config_template_serializer.ListBindingRelationshipResponseSerializer()},
    )
    @action(methods=["GET"], detail=True)
    def list_binding_relationship(self, request, bk_biz_id, config_template_id, *args, **kwargs):
        return Response(
            ConfigTemplateHandler(
                bk_biz_id=bk_biz_id, config_template_id=config_template_id
            ).list_binding_relationship()
        )

    @swagger_auto_schema(
        operation_summary="配置模板绑定到进程",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.BindTemplateToProcessRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.BindTemplateToProcessResponseSerializer()},
    )
    @action(
        detail=True,
        methods=["POST"],
        serializer_class=config_template_serializer.BindTemplateToProcessRequestSerializer,
    )
    def bind_template_to_process(self, request, bk_biz_id, config_template_id, *args, **kwargs):
        process_object_list = self.validated_data["process_object_list"]
        return Response(
            ConfigTemplateHandler(bk_biz_id=bk_biz_id, config_template_id=config_template_id).bind_template_to_process(
                process_object_list
            )
        )

    @swagger_auto_schema(
        operation_summary="配置进程到配置模板",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.BindProcessToTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.BindProcessToTemplateResponseSerializer()},
    )
    @action(
        detail=False,
        methods=["POST"],
        serializer_class=config_template_serializer.BindProcessToTemplateRequestSerializer,
    )
    def bind_process_to_template(self, request, bk_biz_id, *args, **kwargs):
        config_template_id_list = self.validated_data["config_template_id_list"]
        process_object_type = self.validated_data["process_object_type"]
        process_object_id = self.validated_data["process_object_id"]
        return Response(
            ConfigTemplateHandler(bk_biz_id=bk_biz_id).bind_process_to_template(
                process_object_type, process_object_id, config_template_id_list
            )
        )

    @swagger_auto_schema(
        operation_summary="异步生成配置",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.GenerateConfigRequestSerializer,
    )
    @action(detail=False, methods=["POST"], serializer_class=config_template_serializer.GenerateConfigRequestSerializer)
    def generate_config(self, request, bk_biz_id, *args, **kwargs):
        config_template_id = self.validated_data.get("config_template_id")
        config_version_ids = self.validated_data.get("config_version_ids", [])
        scope = self.validated_data.get("scope")
        expression_scope = self.validated_data.get("expression_scope")
        extra_filter_conditions = {
            "bk_host_innerips": self.validated_data.get("bk_host_innerips"),
            "bk_cloud_ids": self.validated_data.get("bk_cloud_ids"),
            "is_auto_list": self.validated_data.get("is_auto_list"),
            "process_status_list": self.validated_data.get("process_status_list"),
        }
        return Response(
            ConfigTemplateHandler.generate_config(
                bk_biz_id,
                config_template_id,
                scope,
                expression_scope,
                config_version_ids=config_version_ids,
                extra_filter_conditions=extra_filter_conditions,
            )
        )

    @swagger_auto_schema(operation_summary="同步生成配置", tags=ConfigTemplateViewTags)
    @action(
        detail=True, methods=["POST"], serializer_class=config_template_serializer.SyncGenerateConfigRequestSerializer
    )
    def sync_generate_config(self, request, bk_biz_id, config_template_id, *args, **kwargs):
        bk_process_id = self.validated_data["bk_process_id"]
        return Response(
            ConfigTemplateHandler(bk_biz_id=bk_biz_id, config_template_id=config_template_id).sync_generate_config(
                bk_biz_id, bk_process_id
            )
        )

    @swagger_auto_schema(
        operation_summary="配置下发",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.ReleaseConfigRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.ReleaseConfigResponseSerializer()},
    )
    @action(methods=["POST"], detail=False, serializer_class=config_template_serializer.ReleaseConfigRequestSerializer)
    def release_config(self, request, bk_biz_id, *args, **kwargs):
        config_template_id = self.validated_data.get("config_template_id")
        config_version_ids = self.validated_data.get("config_version_ids", [])
        return Response(
            JobHandlers(bk_biz_id=bk_biz_id).create_job(
                job_object=Job.JobObject.CONFIGFILE,
                job_action=Job.JobAction.RELEASE,
                created_by=request.user.username,
                scope=self.validated_data.get("scope"),
                expression_scope=self.validated_data.get("expression_scope"),
                extra_data={
                    "config_template_ids": [config_template_id],
                    "config_version_ids_map": [
                        {"config_template_id": config_template_id, "config_version_ids": config_version_ids}
                    ],
                    "extra_filter_conditions": {
                        "bk_host_innerips": self.validated_data.get("bk_host_innerips"),
                        "bk_cloud_ids": self.validated_data.get("bk_cloud_ids"),
                        "is_auto_list": self.validated_data.get("is_auto_list"),
                        "process_status_list": self.validated_data.get("process_status_list"),
                    },
                }
                if config_template_id
                else None,
            )
        )

    @swagger_auto_schema(
        operation_summary="现网配置对比",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.ReleaseConfigRequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.ReleaseConfigResponseSerializer()},
    )
    @action(methods=["POST"], detail=False, serializer_class=config_template_serializer.ReleaseConfigRequestSerializer)
    def diff_config(self, request, bk_biz_id, *args, **kwargs):
        config_template_id = self.validated_data.get("config_template_id")
        config_version_ids = self.validated_data.get("config_version_ids", [])
        return Response(
            JobHandlers(bk_biz_id=bk_biz_id).create_job(
                job_object=Job.JobObject.CONFIGFILE,
                job_action=Job.JobAction.DIFF,
                created_by=request.user.username,
                scope=self.validated_data.get("scope"),
                expression_scope=self.validated_data.get("expression_scope"),
                extra_data={
                    "config_template_ids": [config_template_id],
                    "config_version_ids_map": [
                        {"config_template_id": config_template_id, "config_version_ids": config_version_ids}
                    ],
                    "extra_filter_conditions": {
                        "bk_host_innerips": self.validated_data.get("bk_host_innerips"),
                        "bk_cloud_ids": self.validated_data.get("bk_cloud_ids"),
                        "is_auto_list": self.validated_data.get("is_auto_list"),
                        "process_status_list": self.validated_data.get("process_status_list"),
                    },
                }
                if config_template_id
                else None,
            )
        )

    @swagger_auto_schema(
        operation_summary="获取配置模板列表",
        tags=ConfigTemplateViewTags,
        request_body=config_template_serializer.ListConfigTemplateV2RequestSerializer(),
        responses={status.HTTP_200_OK: config_template_serializer.ListConfigTemplateResponseSerializer()},
    )
    @insert_permission_field(
        id_field=lambda d: d["config_template_id"],
        data_field=lambda d: d["list"],
        actions=[ActionEnum.EDIT_CONFIG_TEMPLATE, ActionEnum.DELETE_CONFIG_TEMPLATE],
        resource_meta=ResourceEnum.CONFIG_TEMPLATE,
    )
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=config_template_serializer.ListConfigTemplateV2RequestSerializer,
    )
    def config_templates_list(self, request, bk_biz_id, *args, **kwargs):
        paginated_params = self.pagination_class.get_paginated_params(request)
        page = paginated_params[self.pagination_class.page_query_param]
        page_size = paginated_params[self.pagination_class.page_size_query_param]
        original_page_start = page_size * (page - 1) + 1
        original_page_end = page * page_size

        queryset = self.filter_queryset(self.get_queryset())

        binding_config_template_ids = self.validated_data.get("binding_config_template_ids")
        # 配置文件可返回整页
        if not binding_config_template_ids or len(binding_config_template_ids) < original_page_start:
            if not binding_config_template_ids:
                config_template_list = queryset_to_dict_list(self.paginate_queryset(queryset))
            else:
                start = original_page_start - len(binding_config_template_ids) - 1
                end = original_page_end - len(binding_config_template_ids)
                config_template_list = queryset_to_dict_list(
                    queryset.exclude(config_template_id__in=binding_config_template_ids)[start:end]
                )
            return Response(
                {"count": queryset.count(), "list": ConfigTemplateHandler.fill_with_is_bound(config_template_list)}
            )

        binding_page_start = original_page_start
        binding_page_end = min(len(binding_config_template_ids), original_page_end)
        binding_config_templates = queryset_to_dict_list(
            queryset.filter(
                config_template_id__in=binding_config_template_ids[binding_page_start - 1 : binding_page_end]
            )
        )
        # 绑定配置文件可覆盖整页时，直接返回
        if len(binding_config_template_ids) > original_page_end:
            return Response(
                {"count": queryset.count(), "list": ConfigTemplateHandler.fill_with_is_bound(binding_config_templates)}
            )

        # 绑定配置文件不足一页，通过非绑定配置文件补齐
        config_template_list = binding_config_templates + queryset_to_dict_list(
            queryset.exclude(config_template_id__in=binding_config_template_ids)[
                : page_size - len(binding_config_templates)
            ]
        )
        return Response(
            {"count": queryset.count(), "list": ConfigTemplateHandler.fill_with_is_bound(config_template_list)}
        )
