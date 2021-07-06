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
import json

import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.gsekit.meta import serializers as meta_serializer
from apps.gsekit.meta.handlers import MetaHandler
from apps.gsekit.meta.models import GlobalSettings

MetaViewTags = ["meta"]


class MetaViewSet(APIViewSet):
    @swagger_auto_schema(
        operation_summary="footer内容", tags=MetaViewTags,
    )
    @action(detail=False, methods=["GET"])
    def footer(self, request, *args, **kwargs):
        return Response(GlobalSettings.footer())

    @swagger_auto_schema(
        operation_summary="获取所有用户", tags=MetaViewTags,
    )
    @action(detail=False, methods=["GET"])
    def users(self, request, *args, **kwargs):
        return Response(MetaHandler.list_users(request))

    @swagger_auto_schema(
        operation_summary="获取用户信息",
        tags=MetaViewTags,
        responses={status.HTTP_200_OK: meta_serializer.GetUserInfoResponseSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def get_user_info(self, request, *args, **kwargs):
        return Response(MetaHandler.get_user_info(request))

    @swagger_auto_schema(
        operation_summary="任务历史过滤选项", tags=MetaViewTags,
    )
    @action(detail=False, methods=["GET"])
    def job_filter_choices(self, request, *args, **kwargs):
        return Response(MetaHandler.get_job_filter_choices())

    @swagger_auto_schema(
        operation_summary="进程状态过滤项",
        tags=MetaViewTags,
        responses={status.HTTP_200_OK: meta_serializer.ProcessFilterChoicesResponseSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def process_filter_choices(self, request, bk_biz_id, *args, **kwargs):
        return Response(MetaHandler.get_process_filter_choices(bk_biz_id))

    @swagger_auto_schema(
        operation_summary="任务详细过滤选项",
        tags=MetaViewTags,
        query_serializer=meta_serializer.JobTaskFilterChoicesRequestSerializer(),
        responses={status.HTTP_200_OK: meta_serializer.JobTaskFilterChoicesResponseSerializer()},
    )
    @action(detail=False, methods=["GET"], serializer_class=meta_serializer.JobTaskFilterChoicesRequestSerializer)
    def job_task_filter_choices(self, request, *args, **kwargs):
        job_id = self.validated_data["job_id"]
        return Response(MetaHandler.get_job_task_filter_choices(job_id))

    @swagger_auto_schema(
        operation_summary="全局", tags=MetaViewTags,
    )
    @action(detail=False, methods=["GET"])
    def variables(self, request, *args, **kwargs):
        return Response(MetaHandler.get_job_filter_choices())

    @swagger_auto_schema(
        operation_summary="获取老数据", tags=MetaViewTags,
    )
    @action(detail=False, methods=["GET"])
    def get_old_data(self, request, *args, **kwargs):
        old_gsekit_url = "apps.***.com/ieod-bkapp-gsekit-prod"  # 内部版金枪鱼地址
        biz_list = requests.get(
            url="http://{old_gsekit_url}/base/all_business/".format(old_gsekit_url=old_gsekit_url),
            cookies=request.COOKIES,
        )
        biz_list = json.loads(biz_list.text)
        for biz in biz_list:
            config_file_list = requests.get(
                url="http://{old_gsekit_url}/api/{biz}/3/config_file/".format(
                    old_gsekit_url=old_gsekit_url, biz=biz["cc_id"]
                ),
                cookies=request.COOKIES,
            )
            config_file_list = json.loads(config_file_list.text).get("objects") or []

            if not config_file_list:
                continue

            with open("/tmp/gsekit_config_files.txt", "a+") as file:
                file.write("[{}]{}".format(biz["cc_id"], biz["cc_name"]))
                file.write(json.dumps(config_file_list, indent=2))
                file.write("=" * 20)

        return Response()

    @swagger_auto_schema(
        operation_summary="表达式匹配",
        tags=MetaViewTags,
        request_body=meta_serializer.ExpressionMatchRequestSerializer(),
        responses={status.HTTP_200_OK: meta_serializer.ExpressionMatchResponseSerializer()},
    )
    @action(methods=["POST"], detail=False, serializer_class=meta_serializer.ExpressionMatchRequestSerializer)
    def expression_match(self, request, *args, **kwargs):
        expression = self.validated_data["expression"]
        candidates = self.validated_data["candidates"]
        return Response(MetaHandler().expression_match(expression, candidates))
