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
from collections import defaultdict

from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.gsekit.job.models import Job
from apps.gsekit.operations import serializers
from apps.gsekit.operations.handlers import OperationsHandler
from apps.gsekit.operations.models import VisitCount

OperationsViewTags = ["operations"]


class OperationsViewSet(APIViewSet):
    """
    运营数据统计
    """

    @swagger_auto_schema(operation_summary="任务统计（使用ORM自定义统计）", tags=OperationsViewTags)
    @action(methods=["POST"], detail=False, serializer_class=serializers.JobCountStatisticsRequestSerializer)
    def job_count_statistics_with_orm(self, request, *args, **kwargs):
        filter_conditions = self.validated_data["filter_conditions"]
        exclude_conditions = self.validated_data["exclude_conditions"]
        group_by = self.validated_data["group_by"]
        return Response(
            OperationsHandler.job_count_statistics_with_orm(filter_conditions, exclude_conditions, group_by)
        )

    @swagger_auto_schema(operation_summary="用户访问统计（使用ORM自定义统计）", tags=OperationsViewTags)
    @action(methods=["POST"], detail=False, serializer_class=serializers.VisitCountStatisticsRequestSerializer)
    def visit_count_statistics_with_orm(self, request, *args, **kwargs):
        filter_conditions = self.validated_data["filter_conditions"]
        exclude_conditions = self.validated_data["exclude_conditions"]
        group_by = self.validated_data["group_by"]
        return Response(
            OperationsHandler.visit_count_statistics_with_orm(filter_conditions, exclude_conditions, group_by)
        )

    @swagger_auto_schema(operation_summary="用户访问", tags=OperationsViewTags)
    @action(methods=["POST"], detail=False, serializer_class=serializers.VisitRequestSerializer)
    def visit(self, request, *args, **kwargs):
        bk_username = request.user.username
        bk_biz_id = self.validated_data["bk_biz_id"]
        return Response(VisitCount.visit(bk_username, bk_biz_id))

    @swagger_auto_schema(operation_summary="运用统计-频次统计", tags=OperationsViewTags)
    @action(methods=["POST"], detail=False, serializer_class=serializers.FrequencyStatisticsRequestSerializer)
    def frequency_statistics(self, request, *args, **kwargs):
        query_params = self.validated_data
        group_by = query_params["group_by"]
        statistics = (
            Job.objects.filter(start_time__gte=query_params["start_time"], start_time__lte=query_params["end_time"])
            .extra(select={"date": "DATE(start_time)"})
            .values(group_by, "date")
            .annotate(count=Count("*"))
            .order_by("date")
        )

        # 按日期得到当天最大的值
        date_max_count = defaultdict(dict)
        for static in statistics:
            if static["count"] > date_max_count[str(static["date"])].get("count", 0):
                date_max_count[str(static["date"])] = {"count": static["count"], group_by: static[group_by]}
        return Response(
            [
                {"date": date, "count": static["count"], group_by: static[group_by]}
                for date, static in date_max_count.items()
            ]
        )

    @swagger_auto_schema(operation_summary="运用统计-趋势统计", tags=OperationsViewTags)
    @action(methods=["POST"], detail=False, serializer_class=serializers.TrendStatisticsRequestSerializer)
    def trend_statistics(self, request, *args, **kwargs):
        query_params = self.validated_data
        job_action = query_params.get("job_action")
        job_object = query_params.get("job_object")
        filter_conditions = {}
        if job_action:
            filter_conditions["job_action"] = job_action
        if job_object:
            filter_conditions["job_object"] = job_object
        statistics = (
            Job.objects.filter(
                start_time__gte=query_params["start_time"],
                start_time__lte=query_params["end_time"],
                **filter_conditions
            )
            .extra(select={"date": "DATE(start_time)"})
            .values("date")
            .annotate(count=Count("*"))
            .order_by("date")
        )
        return Response(statistics)
