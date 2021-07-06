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
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.generic import APIViewSet
from apps.gsekit.migrate.handlers import MigrateHandlers

"""
一次性迁移工具，用于把数据从金枪鱼迁移过来
"""

MigrateViewTags = ["migrate"]


class MigrateIamRequestSerializer(serializers.Serializer):
    perm_gainer = serializers.CharField(help_text="权限获得者，不填则默认是配置模板创建者", required=False)

    class Meta:
        swagger_schema_fields = {"example": {"perm_gainer": "权限获得者，不填则默认是配置模板创建者"}}


class MigrateViewSet(APIViewSet):
    def get_permissions(self):
        # return [ViewBusinessPermission()]
        return []

    @swagger_auto_schema(
        operation_summary="迁移进程信息预览", tags=MigrateViewTags,
    )
    @action(methods=["GET"], detail=False)
    def migrate_process_preview(self, request, bk_biz_id, *args, **kwargs):
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).diff_biz_process())

    @swagger_auto_schema(
        operation_summary="迁移进程信息预览（可读版）", tags=MigrateViewTags,
    )
    @action(methods=["GET"], detail=False)
    def migrate_process_preview_brief(self, request, bk_biz_id, *args, **kwargs):
        processes = MigrateHandlers(bk_biz_id=bk_biz_id, request=request).diff_biz_process()
        return Response(
            [
                {
                    "action": "【不迁移的runshell】",
                    "processes": [f'{runshell_proc["FuncName"]}' for runshell_proc in processes["runshell_processes"]],
                },
                {
                    "action": "【新增的进程模板】",
                    "processes": [
                        f'将在【{service_template["ModuleName"]}】模块（服务模板）下新增'
                        f'【{proc_tmpl["ProcName"]}-{proc_tmpl["FuncName"]}-{proc_tmpl["FuncID"]}】进程模板'
                        for service_template in processes["service_template_list"]
                        for proc_tmpl in service_template["module_process_difference"][
                            "to_be_created_process_templates"
                        ]
                    ],
                },
            ]
        )

    @swagger_auto_schema(
        operation_summary="迁移进程信息", tags=MigrateViewTags,
    )
    @action(methods=["POST"], detail=False)
    def migrate_process(self, request, bk_biz_id, *args, **kwargs):
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).migrate_process())

    @swagger_auto_schema(
        operation_summary="迁移配置模板预览", tags=MigrateViewTags,
    )
    @action(methods=["GET"], detail=False)
    def migrate_config_template_preview(self, request, bk_biz_id, *args, **kwargs):
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).migrate_config_file_preview())

    @swagger_auto_schema(
        operation_summary="迁移配置模板", tags=MigrateViewTags,
    )
    @action(methods=["POST"], detail=False)
    def migrate_config_template(self, request, bk_biz_id, *args, **kwargs):
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).migrate_config_file())

    @swagger_auto_schema(
        operation_summary="迁移绑定关系", tags=MigrateViewTags,
    )
    @action(methods=["POST"], detail=False)
    def migrate_binding_relation(self, request, bk_biz_id, *args, **kwargs):
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).migrate_binding_relation())

    @swagger_auto_schema(
        operation_summary="迁移进程实例", tags=MigrateViewTags,
    )
    @action(methods=["POST"], detail=False)
    def migrate_process_instance(self, request, bk_biz_id, *args, **kwargs):
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).migrate_process_instance())

    @swagger_auto_schema(
        operation_summary="迁移权限", tags=MigrateViewTags,
    )
    @action(methods=["POST"], detail=False, serializer_class=MigrateIamRequestSerializer)
    def migrate_iam(self, request, bk_biz_id, *args, **kwargs):
        perm_gainer = self.validated_data.get("perm_gainer")
        return Response(MigrateHandlers(bk_biz_id=bk_biz_id, request=request).migrate_iam(perm_gainer=perm_gainer))
