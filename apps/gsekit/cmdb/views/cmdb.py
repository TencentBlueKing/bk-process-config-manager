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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api import CCApi
from apps.generic import APIViewSet
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.cmdb.serializers import cmdb as cmdb_serializer
from apps.iam.handlers.drf import ViewBusinessPermission

CMDBViewTags = ["cmdb"]


class CMDBViews(APIViewSet):
    def get_permissions(self):
        if self.action in [None, "biz_list"]:
            return []
        return [ViewBusinessPermission()]

    @swagger_auto_schema(
        operation_summary="查询用户有权限的业务",
        tags=CMDBViewTags,
        responses={status.HTTP_200_OK: cmdb_serializer.ListBizResponseSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def biz_list(self, request, *args, **kwargs):
        return Response(CMDBHandler.biz_list(request.user))

    @swagger_auto_schema(
        operation_summary="根据业务查询拓扑",
        tags=CMDBViewTags,
        responses={status.HTTP_200_OK: cmdb_serializer.BizTopoResponseSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def biz_topo(self, request, bk_biz_id, *args, **kwargs):
        return Response(CMDBHandler(bk_biz_id).biz_topo())

    @swagger_auto_schema(
        operation_summary="根据业务查询服务模板列表",
        tags=CMDBViewTags,
        responses={status.HTTP_200_OK: cmdb_serializer.ServiceTemplateResponseSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def service_template(self, request, bk_biz_id, *args, **kwargs):
        return Response(CMDBHandler(bk_biz_id).service_template())

    @swagger_auto_schema(
        operation_summary="根据模块查询服务实例列表",
        tags=CMDBViewTags,
        request_body=cmdb_serializer.ServiceInstanceRequestSerializer(),
        responses={status.HTTP_200_OK: cmdb_serializer.ServiceInstanceResponseSerializer()},
    )
    @action(
        detail=False, methods=["POST"], serializer_class=cmdb_serializer.ServiceInstanceRequestSerializer,
    )
    def service_instance(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            CMDBHandler(bk_biz_id).fetch_service_instance_by_module_ids(
                bk_module_ids=self.validated_data.get("bk_module_ids") or None,
                expression=self.validated_data["expression"],
                with_proc_count=self.validated_data["with_proc_count"],
            )
        )

    @swagger_auto_schema(
        operation_summary="查询进程实例的相关信息",
        tags=CMDBViewTags,
        request_body=cmdb_serializer.ProcessRelatedInfoRequestSerializer,
    )
    @action(detail=False, methods=["POST"])
    def list_process_related_info(self, request, bk_biz_id, *args, **kwargs):
        params = {"bk_biz_id": bk_biz_id}
        params.update(request.data)
        return Response(CCApi.list_process_related_info(params))

    @swagger_auto_schema(
        operation_summary="根据业务获取集群列表",
        tags=CMDBViewTags,
        query_serializer=cmdb_serializer.ListSetRequestSerializer(),
        responses={status.HTTP_200_OK: cmdb_serializer.ListSetResponseSerializer()},
    )
    @action(
        detail=False, methods=["GET"], serializer_class=cmdb_serializer.ListSetRequestSerializer,
    )
    def set_list(self, request, bk_biz_id, *args, **kwargs):
        bk_set_env = self.validated_data["bk_set_env"]
        expression = self.validated_data["expression"]
        return Response(CMDBHandler(bk_biz_id).set_list(bk_set_env, expression))

    @swagger_auto_schema(
        operation_summary="根据业务获取模块列表",
        tags=CMDBViewTags,
        request_body=cmdb_serializer.ListModuleRequestSerializer(),
        responses={status.HTTP_200_OK: cmdb_serializer.ListModuleResponseSerializer()},
    )
    @action(
        detail=False, methods=["POST"], serializer_class=cmdb_serializer.ListModuleRequestSerializer,
    )
    def module_list(self, request, bk_biz_id, *args, **kwargs):
        bk_set_ids = self.validated_data.get("bk_set_ids")
        bk_set_env = self.validated_data.get("bk_set_env")
        expression = self.validated_data["expression"]
        return Response(CMDBHandler(bk_biz_id).module_list(bk_set_ids or None, bk_set_env, expression))

    @swagger_auto_schema(
        operation_summary="获取业务变量",
        tags=CMDBViewTags,
        responses={status.HTTP_200_OK: cmdb_serializer.BizGlobalVarResponseSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def biz_global_variables(self, request, bk_biz_id, *args, **kwargs):
        return Response(CMDBHandler(bk_biz_id).biz_global_variables())

    @swagger_auto_schema(
        operation_summary="查询对象模型属性",
        tags=CMDBViewTags,
        query_serializer=cmdb_serializer.BizSearchObjectAttributeRequestSerializer(),
        responses={status.HTTP_200_OK: cmdb_serializer.BizSearchObjectAttributeResponseSerializer()},
    )
    @action(detail=False, methods=["GET"], serializer_class=cmdb_serializer.BizSearchObjectAttributeRequestSerializer)
    def search_object_attribute(self, request, bk_biz_id, *args, **kwargs):
        bk_obj_id = self.validated_data["bk_obj_id"]
        return Response(CMDBHandler(bk_biz_id).search_object_attribute(bk_obj_id))

    @swagger_auto_schema(
        operation_summary="查询服务模板是否需要同步",
        tags=CMDBViewTags,
        query_serializer=cmdb_serializer.CheckServiceTemplateDifferenceRequestSerializer(),
    )
    @action(
        detail=False, methods=["GET"], serializer_class=cmdb_serializer.CheckServiceTemplateDifferenceRequestSerializer
    )
    def check_service_template_difference(self, request, bk_biz_id, *args, **kwargs):
        service_template_id = self.validated_data["service_template_id"]
        has_difference = (
            CMDBHandler(bk_biz_id)
            .check_service_template_difference(service_template_id)
            .get(service_template_id, False)
        )
        return Response(has_difference)

    @swagger_auto_schema(
        operation_summary="批量查询服务模板是否需要同步", tags=CMDBViewTags,
    )
    @action(detail=False, methods=["GET"])
    def batch_check_service_template_difference(self, request, bk_biz_id, *args, **kwargs):
        return Response(CMDBHandler(bk_biz_id).batch_check_service_template_difference())
