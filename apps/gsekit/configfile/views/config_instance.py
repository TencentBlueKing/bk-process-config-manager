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
from typing import Callable, Union, List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.gsekit.configfile.handlers.config_instance import ConfigInstanceHandler
from apps.gsekit.configfile.serializers import config_instance as config_instance_serializer
from apps.iam.handlers.drf import ViewBusinessPermission

ConfigInstanceViewTags = ["config_instance"]


class ConfigInstanceViews(APIViewSet):
    lookup_field = "config_instance_id"

    def config_template_ids_getter(self, request) -> List[int]:
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        config_instance_id = self.kwargs[lookup_url_kwarg]
        config_template_id = ConfigInstanceHandler(config_instance_id=config_instance_id).data.config_template_id
        return [config_template_id]

    def get_instance_ids_getter(self) -> Union[Callable, None]:
        if self.action == "retrieve":
            return self.config_template_ids_getter
        elif self.action == "latest_config_instance":
            return lambda request: [self.validated_data["config_template_id"]]
        elif self.action == "list_config_instances":
            return
        return None

    def get_permissions(self):
        # TODO 待确认是否需要细粒度控制配置实例的查看权限
        # if self.action in ["retrieve", "latest_config_instance", "list_config_instances"]:
        #     return [
        #         InstanceActionPermission([ActionEnum.EDIT_CONFIG_TEMPLATE], ResourceEnum.CONFIG_TEMPLATE),
        #         self.get_instance_ids_getter,
        #     ]
        return [ViewBusinessPermission()]

    def get_serializer_class(self, *args, **kwargs):
        action_serializer_map = {}
        return action_serializer_map.get(self.action, serializers.Serializer)

    @swagger_auto_schema(
        operation_summary="指定进程和配置模板查询配置实例",
        tags=ConfigInstanceViewTags,
        query_serializer=config_instance_serializer.LatestConfigInstanceRequestSerializer(),
        responses={status.HTTP_200_OK: config_instance_serializer.LatestConfigInstanceResponseSerializer()},
    )
    @action(
        methods=["GET"], detail=False, serializer_class=config_instance_serializer.LatestConfigInstanceRequestSerializer
    )
    def latest_config_instance(self, request, *args, **kwargs):
        bk_process_id = self.validated_data["bk_process_id"]
        config_template_id = self.validated_data["config_template_id"]
        inst_id = self.validated_data.get("inst_id")
        return Response(ConfigInstanceHandler.latest_config_instance(bk_process_id, config_template_id, inst_id))

    @swagger_auto_schema(
        operation_summary="查询配置实例",
        tags=ConfigInstanceViewTags,
        responses={status.HTTP_200_OK: config_instance_serializer.RetrieveConfigInstancResponseSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        config_instance_id = kwargs["config_instance_id"]
        return Response(ConfigInstanceHandler(config_instance_id=config_instance_id).retrieve())

    @swagger_auto_schema(
        operation_summary="查询配置实例生成列表",
        tags=ConfigInstanceViewTags,
        request_body=config_instance_serializer.ListConfigInstancesRequestSerializer(),
        responses={status.HTTP_200_OK: config_instance_serializer.LatestConfigInstanceResponseSerializer()},
    )
    @action(
        methods=["POST"], detail=False, serializer_class=config_instance_serializer.ListConfigInstancesRequestSerializer
    )
    def list_config_instances(self, request, bk_biz_id, *args, **kwargs):
        scope = self.validated_data.get("scope")
        expression_scope = self.validated_data.get("expression_scope")
        process_status = self.validated_data.get("process_status")
        is_auto = self.validated_data.get("is_auto")
        config_template_id = self.validated_data.get("config_template_id")
        config_version_ids = self.validated_data.get("config_version_ids")
        filter_released = self.validated_data.get("filter_released")
        return Response(
            ConfigInstanceHandler.list(
                bk_biz_id,
                scope=scope,
                expression_scope=expression_scope,
                process_status=process_status,
                is_auto=is_auto,
                config_template_id=config_template_id,
                config_version_ids=config_version_ids,
                filter_released=filter_released,
            )
        )
