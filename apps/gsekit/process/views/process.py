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

from apps.generic import APIViewSet
from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import Job
from apps.gsekit.process.models import Process
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.process.serializers import process as process_serializer
from apps.iam import ActionEnum, ResourceEnum
from apps.iam.handlers.drf import InstanceActionPermission, ViewBusinessPermission
from apps.utils.models import queryset_to_dict_list
from apps.utils.drf import GeneralOrderingFilter

ProcessViewTags = ["process"]


class ProcessViews(APIViewSet):
    model = Process
    filter_backends = (GeneralOrderingFilter,)
    # TODO: 服务实例名称、配置文件数、云区域名称作为非DB字段，排序待开发
    ordering_fields = ["id", "bk_set_id", "bk_module_id", "bk_process_name", "bk_process_id", "bk_host_innerip"]

    def get_queryset(self):
        return self.model.objects.filter(bk_biz_id=self.kwargs["bk_biz_id"])

    def get_permissions(self):
        if self.action in ["operate_process"]:
            return [InstanceActionPermission([ActionEnum.MANAGE_PROCESS], ResourceEnum.BUSINESS)]
        return [ViewBusinessPermission()]

    @swagger_auto_schema(
        operation_summary="进程状态列表",
        tags=ProcessViewTags,
        request_body=process_serializer.ProcessStatusRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.ProcessStatusResponseSerializer()},
    )
    @action(methods=["POST"], detail=False, serializer_class=process_serializer.ProcessStatusRequestSerializer)
    def process_status(self, request, bk_biz_id, *args, **kwargs):
        # TODO: 逻辑无关筛选字段通过FilterSet筛选
        queryset = ProcessHandler(bk_biz_id=bk_biz_id).list(
            process_queryset=self.filter_queryset(self.get_queryset()),
            scope=self.validated_data.get("scope"),
            expression_scope=self.validated_data.get("expression_scope"),
            bk_cloud_ids=self.validated_data.get("bk_cloud_ids"),
            process_status=self.validated_data.get("process_status"),
            is_auto=self.validated_data.get("is_auto"),
            searches=self.validated_data.get("searches"),
            bk_host_innerips=self.validated_data.get("bk_host_innerips"),
            process_status_list=self.validated_data.get("process_status_list"),
            is_auto_list=self.validated_data.get("is_auto_list"),
        )
        process_list = queryset_to_dict_list(self.paginate_queryset(queryset))
        return Response(
            {
                "count": queryset.count(),
                "list": ProcessHandler.fill_extra_info_to_process(
                    process_list, topo_name=True, bound_template=True, proc_inst=True
                ),
            }
        )

    @swagger_auto_schema(
        operation_summary="进程操作",
        tags=ProcessViewTags,
        responses={status.HTTP_200_OK: process_serializer.OperateProcessResponseSerializer()},
    )
    @action(methods=["POST"], detail=False, serializer_class=process_serializer.OperateProcessRequestSerializer)
    def operate_process(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            JobHandlers(bk_biz_id=bk_biz_id).create_job(
                job_object=Job.JobObject.PROCESS,
                job_action=self.validated_data["op_type"],
                created_by=request.user.username,
                scope=self.validated_data.get("scope"),
                expression_scope=self.validated_data.get("expression_scope"),
            )
        )

    @swagger_auto_schema(
        operation_summary="根据服务模板查询进程模板列表",
        tags=ProcessViewTags,
        query_serializer=process_serializer.ProcessTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.ProcessTemplateResponseSerializer()},
    )
    @action(detail=False, methods=["GET"], serializer_class=process_serializer.ProcessTemplateRequestSerializer)
    def process_template(self, request, bk_biz_id, *args, **kwargs):
        service_template_id = self.validated_data["service_template_id"]
        return Response(ProcessHandler(bk_biz_id=bk_biz_id).process_template(service_template_id))

    @swagger_auto_schema(
        operation_summary="根据服务实例查询进程实例列表",
        tags=ProcessViewTags,
        query_serializer=process_serializer.ProcessInstanceRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.ProcessInstanceResponseSerializer()},
    )
    @action(detail=False, methods=["GET"], serializer_class=process_serializer.ProcessInstanceRequestSerializer)
    def process_instance(self, request, bk_biz_id, *args, **kwargs):
        service_instance_id = self.validated_data["service_instance_id"]
        return Response(ProcessHandler(bk_biz_id=bk_biz_id).process_instance(service_instance_id))

    @swagger_auto_schema(
        operation_summary="更新进程实例",
        tags=ProcessViewTags,
        request_body=process_serializer.UpdateProcessInstanceRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.UpdateProcessInstanceResponseSerializer()},
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.UpdateProcessInstanceRequestSerializer)
    def update_process_instance(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).update_process_instance(self.validated_data["process_property"])
        )

    @swagger_auto_schema(
        operation_summary="更新进程模板",
        tags=ProcessViewTags,
        request_body=process_serializer.UpdateProcessTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.UpdateProcessTemplateResponseSerializer()},
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.UpdateProcessTemplateRequestSerializer)
    def update_process_template(self, request, bk_biz_id, *args, **kwargs):
        process_template_id = self.validated_data["process_template_id"]
        process_property = self.validated_data["process_property"]
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).update_process_template(process_template_id, process_property)
        )

    @swagger_auto_schema(
        operation_summary="创建进程实例",
        tags=ProcessViewTags,
        request_body=process_serializer.CreateProcessInstanceRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.CreateProcessInstanceResponseSerializer()},
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.CreateProcessInstanceRequestSerializer)
    def create_process_instance(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).create_process_instance(
                service_instance_id=self.validated_data["service_instance_id"],
                process_property=self.validated_data["process_property"],
            )
        )

    @swagger_auto_schema(
        operation_summary="创建进程模板",
        tags=ProcessViewTags,
        request_body=process_serializer.CreateProcessTemplateRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.CreateProcessTemplateResponseSerializer()},
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.CreateProcessTemplateRequestSerializer)
    def create_process_template(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).create_process_template(
                service_template_id=self.validated_data["service_template_id"],
                process_property=self.validated_data["process_property"],
            )
        )

    @swagger_auto_schema(
        operation_summary="删除进程实例",
        tags=ProcessViewTags,
        request_body=process_serializer.DeleteProcessInstanceRequestSerializer(),
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.DeleteProcessInstanceRequestSerializer)
    def delete_process_instance(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).delete_process_instance(
                process_instance_ids=self.validated_data["process_instance_ids"],
            )
        )

    @swagger_auto_schema(
        operation_summary="删除进程模板",
        tags=ProcessViewTags,
        request_body=process_serializer.DeleteProcessTemplateRequestSerializer(),
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.DeleteProcessTemplateRequestSerializer)
    def delete_process_template(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).delete_process_template(
                process_template_ids=self.validated_data["process_template_ids"],
            )
        )

    @swagger_auto_schema(
        operation_summary="刷新业务进程缓存", tags=ProcessViewTags,
    )
    @action(detail=False, methods=["POST"])
    def flush_process(self, request, bk_biz_id, *args, **kwargs):
        return Response(ProcessHandler(bk_biz_id=bk_biz_id).sync_biz_process())

    @swagger_auto_schema(
        operation_summary="同步进程状态", tags=ProcessViewTags,
    )
    @action(detail=False, methods=["POST"])
    def sync_process_status(self, request, bk_biz_id, *args, **kwargs):
        return Response(ProcessHandler(bk_biz_id=bk_biz_id).sync_biz_process_status())

    @swagger_auto_schema(
        operation_summary="根据服务实例ID列表获取进程实例列表概要信息",
        tags=ProcessViewTags,
        request_body=process_serializer.ProcessInstanceSimpleRequestSerializer(),
        responses={status.HTTP_200_OK: process_serializer.ProcessInstanceSimpleResponseSerializer()},
    )
    @action(detail=False, methods=["POST"], serializer_class=process_serializer.ProcessInstanceSimpleRequestSerializer)
    def process_instance_simple(self, request, bk_biz_id, *args, **kwargs):
        return Response(
            ProcessHandler(bk_biz_id=bk_biz_id).process_instance_simple(
                scope=self.validated_data.get("scope"),
                expression_scope=self.validated_data.get("expression_scope"),
                service_instance_ids=self.validated_data.get("service_instance_ids"),
                expression=self.validated_data.get("expression"),
            )
        )
