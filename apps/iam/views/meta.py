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
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.iam import Permission
from apps.iam.serializers import IamActionResourceRequestSerializer

IamMetaViewTags = ["iam_meta"]


class MetaViewSet(APIViewSet):
    # 权限豁免
    permission_classes = ()

    @swagger_auto_schema(operation_summary="获取系统权限中心信息", tags=IamMetaViewTags)
    @action(methods=["GET"], detail=False)
    def get_system_info(self, request, *args, **kwargs):
        result = Permission().get_system_info()
        return Response(result)

    @swagger_auto_schema(operation_summary="检查当前用户对该动作是否有权限", tags=IamMetaViewTags)
    @action(detail=False, methods=["POST"], serializer_class=IamActionResourceRequestSerializer)
    def check_allowed(self, request, *args, **kwargs):
        action_ids = self.validated_data.get("action_ids", [])
        resources = self.validated_data.get("resources", [])

        result = []
        client = Permission()
        resources = client.batch_make_resource(resources)
        for action_id in action_ids:
            is_allowed = client.is_allowed(action_id, resources)
            result.append({"action_id": action_id, "is_allowed": is_allowed})

        return Response(result)

    @swagger_auto_schema(operation_summary="获取权限申请数据", tags=IamMetaViewTags)
    @action(detail=False, methods=["POST"], serializer_class=IamActionResourceRequestSerializer)
    def get_apply_data(self, request, *args, **kwargs):
        action_ids = self.validated_data.get("action_ids", [])
        resources = self.validated_data.get("resources", [])
        client = Permission()
        resources = client.batch_make_resource(resources)
        apply_data, apply_url = client.get_apply_data(action_ids, resources)
        return Response({"apply_data": apply_data, "apply_url": apply_url})
