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
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import ModelViewSet
from apps.gsekit.job import serializers as job_serializers
from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import Job
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import ViewBusinessPermission, InstanceActionPermission
from apps.utils.drf import GeneralOrderingFilter
from common.log import logger

JobViewTags = ["job"]


class JobViews(ModelViewSet):
    model = Job
    filter_backends = (DjangoFilterBackend, GeneralOrderingFilter)
    ordering_fields = ["start_time", "end_time"]
    filterset_fields = {
        "id": ["exact", "in"],
        "job_object": ["exact", "in"],
        "job_action": ["exact", "in"],
        "created_by": ["exact", "in"],
        "status": ["exact", "in"],
        "start_time": ["gte", "lte"],
    }

    # 去除ModelViewSet中的put patch delete等方法，不允许编辑删除作业
    http_method_names = ["get", "head", "post"]

    def get_queryset(self):
        return self.model.objects.filter(bk_biz_id=self.kwargs.get("bk_biz_id"))

    def get_permissions(self):
        if self.action == "create":
            job_object = self.request.data["job_object"]
            job_action = self.request.data["job_action"]
            if job_object == Job.JobObject.PROCESS:
                return [InstanceActionPermission([ActionEnum.MANAGE_PROCESS], ResourceEnum.BUSINESS)]
            if job_object == Job.JobObject.CONFIGFILE:
                if job_action in [Job.JobAction.GENERATE, Job.JobAction.RELEASE]:
                    return [InstanceActionPermission([ActionEnum.OPERATE_CONFIG], ResourceEnum.BUSINESS)]
        elif self.action == self.retry.__name__:
            try:
                job_obj: Job = Job.objects.get(id=self.kwargs["pk"])
            except KeyError:
                logger.exception(f"api[{self.retry.__name__}]: cannot get pk")
                return [ViewBusinessPermission()]
            except Job.DoesNotExist:
                logger.exception(f"api[{self.retry.__name__}]: Job(id -> {self.kwargs['pk']}) does not exist")
                return [ViewBusinessPermission()]

            if job_obj.job_object == Job.JobObject.PROCESS:
                return [InstanceActionPermission([ActionEnum.MANAGE_PROCESS], ResourceEnum.BUSINESS)]
            if job_obj.job_object == Job.JobObject.CONFIGFILE:
                if job_obj.job_action in [Job.JobAction.GENERATE, Job.JobAction.RELEASE]:
                    return [InstanceActionPermission([ActionEnum.OPERATE_CONFIG], ResourceEnum.BUSINESS)]
        return [ViewBusinessPermission()]

    @swagger_auto_schema(operation_summary="任务列表", tags=JobViewTags)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="任务详情", tags=JobViewTags)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="创建任务", tags=JobViewTags, request_body=job_serializers.CreateJobRequestSerializer()
    )
    def create(self, request, bk_biz_id, *args, **kwargs):
        self.serializer_class = job_serializers.CreateJobRequestSerializer
        return Response(
            JobHandlers(bk_biz_id=bk_biz_id).create_job(
                job_object=self.validated_data["job_object"],
                job_action=self.validated_data["job_action"],
                created_by=request.user.username,
                scope=self.validated_data.get("scope"),
                expression_scope=self.validated_data.get("expression_scope"),
                extra_data=self.validated_data.get("extra_data"),
            )
        )

    @swagger_auto_schema(
        operation_summary="任务详情列表",
        tags=JobViewTags,
        request_body=job_serializers.JobTaskRequestSerializer(),
        responses={status.HTTP_200_OK: job_serializers.JobTaskResponseSerializer()},
    )
    @action(methods=["POST"], detail=True, serializer_class=job_serializers.JobTaskRequestSerializer)
    def job_task(self, request, *args, **kwargs):
        conditions = self.validated_data
        page = conditions.pop("page")
        pagesize = conditions.pop("pagesize")
        return Response(
            JobHandlers(bk_biz_id=kwargs.get("bk_biz_id"), job_id=kwargs["pk"]).get_job_task(page, pagesize, conditions)
        )

    @swagger_auto_schema(
        operation_summary="任务详情统计（按错误码）",
        tags=JobViewTags,
        responses={status.HTTP_200_OK: job_serializers.JobTaskResponseSerializer()},
    )
    @action(methods=["GET"], detail=True)
    def job_task_statistics(self, request, *args, **kwargs):
        return Response(JobHandlers(bk_biz_id=kwargs.get("bk_biz_id"), job_id=kwargs["pk"]).job_task_statistics())

    @swagger_auto_schema(
        operation_summary="任务状态查询",
        tags=JobViewTags,
        responses={status.HTTP_200_OK: job_serializers.JobTaskResponseSerializer()},
    )
    @action(methods=["POST"], detail=True, serializer_class=job_serializers.RetryRequestSerializer)
    def job_status(self, request, *args, **kwargs):
        job_task_id_list = self.validated_data.get("job_task_id_list") or []
        return Response(
            JobHandlers(bk_biz_id=kwargs.get("bk_biz_id"), job_id=kwargs["pk"]).get_job_status(job_task_id_list)
        )

    @swagger_auto_schema(operation_summary="重试", tags=JobViewTags)
    @action(detail=True, methods=["POST"], serializer_class=job_serializers.RetryRequestSerializer)
    def retry(self, request, *args, **kwargs):
        job_task_id_list = self.validated_data.get("job_task_id_list") or []
        JobHandlers(bk_biz_id=kwargs["bk_biz_id"], job_id=kwargs["pk"]).retry(job_task_id_list)
        return Response()

    @swagger_auto_schema(
        operation_summary="查询任务IP", tags=JobViewTags, query_serializer=job_serializers.SearchIpRequestSerializer()
    )
    @action(detail=True, methods=["GET"], serializer_class=job_serializers.SearchIpRequestSerializer)
    def search_ip(self, request, *args, **kwargs):
        job_status = self.validated_data.get("status")
        ips = JobHandlers(bk_biz_id=kwargs["bk_biz_id"], job_id=kwargs["pk"]).search_ip(job_status)
        return Response(ips)
