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
from rest_framework import status

from apps.generic import APIViewSet

from . import handlers, permission, serializers

GRAY_VIEW_TAGS = ["gray"]


class GrayViewSet(APIViewSet):
    URL_BASE_NAME = "gray"
    permission_classes = (permission.GrayPermission,)

    @swagger_auto_schema(
        operation_summary="GSE 2.0灰度",
        tags=GRAY_VIEW_TAGS,
    )
    @action(detail=False, methods=["POST"], serializer_class=serializers.GraySerializer)
    def build(self, request):
        return Response(handlers.GrayHandler.build(self.validated_data))

    @swagger_auto_schema(
        operation_summary="GSE 2.0灰度回滚",
        tags=GRAY_VIEW_TAGS,
    )
    @action(detail=False, methods=["POST"], serializer_class=serializers.GraySerializer)
    def rollback(self, request):
        return Response(handlers.GrayHandler.rollback(self.validated_data))

    @swagger_auto_schema(
        operation_summary="获取GSE 2.0灰度信息",
        tags=GRAY_VIEW_TAGS,
        responses={status.HTTP_200_OK: serializers.GraySerializer},
    )
    @action(detail=False, methods=["GET"])
    def info(self, request):
        return Response({"bk_biz_ids": handlers.GrayHandler.list_biz_ids()})
