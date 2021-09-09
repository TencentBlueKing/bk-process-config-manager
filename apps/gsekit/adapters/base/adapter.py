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
from typing import Dict, Any, List

from apps.gsekit.adapters.base.pipeline_managers import ManagerFactory
from apps.gsekit.configfile.models import ConfigTemplate, ConfigTemplateBindingRelationship
from apps.gsekit.job.models import Job, JobTask
from apps.gsekit.pipeline_plugins.components.collections.configfile import (
    GenerateConfigComponent,
    BulkGenerateConfigComponent,
    BulkPushConfigComponent,
    BulkBackupConfigComponent
)
from apps.gsekit.pipeline_plugins.components.collections.gse import (
    GseOperateProcessComponent,
    GseOpType,
    GseCheckProcessComponent,
    BulkGseOperateProcessComponent,
    BulkGseCheckProcessComponent,
)
from bamboo_engine.builder import ServiceActivity, Var, Data, NodeOutput


class BaseActivityManager(object):
    def __init__(self, job: Job, job_task: JobTask, *args, **kwargs):
        self.job = job
        self.job_task = job_task

    def generate_activities(self, global_pipeline_data: Data = None) -> Dict[str, Any]:
        """生成Pipeline执行流程步骤原子，返回构建子流程的相关参数

        :param global_pipeline_data: 全局流程数据上下文

        required:
            - activities: List[pipeline.builder.ServiceActivity] 流程步骤原子列表
        optional:
            - sub_process_data: pipeline.builder.Data 子流程数据上下文
            - ...

        子流程无法重试任务,建议用 job_task_id / act_id 唯一标识数据后通过global_pipeline_data实现原子数据交互
        """
        raise NotImplementedError


class BulkBaseActivityManager(object):
    def __init__(self, job: Job, job_task_ids: List[int], *args, **kwargs):
        self.job = job
        self.job_task_ids = job_task_ids

    def bulk_generate_activities(self, global_pipeline_data: Data = None) -> Dict[str, Any]:
        raise NotImplementedError


class BaseChannelAdapters(object):
    """通道适配器，用于扩展BSCP、TCM等"""

    PIPELINE_MANAGER_FACTORY = ManagerFactory

    def do_preparation(self, bk_biz_id: int):
        """
        使用适配器的前置工作
        :param bk_biz_id: 业务ID
        :return:
        """
        pass

    def post_create_config_template(self, config_template: ConfigTemplate):
        pass

    def post_update_config_template(self, config_template: ConfigTemplate):
        pass

    def post_create_config_template_relation(self, relation: ConfigTemplateBindingRelationship):
        pass

    def post_update_config_template_relation(self, relation: ConfigTemplateBindingRelationship):
        pass

    def post_delete_config_template_relation(self, relation: ConfigTemplateBindingRelationship):
        pass

    class GenerateConfigActivityManager(BaseActivityManager):
        def generate_activities(self, global_pipeline_data: Data = None) -> Dict:
            return {
                "activities": [self.generate_config()],
                "sub_process_data": None,
            }

        def generate_config(self):
            act = ServiceActivity(component_code=GenerateConfigComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.job.created_by)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

    class OperateProcessActivityManager(BaseActivityManager):
        def __init__(self, job: Job, job_task: JobTask, *args, **kwargs):
            self.job = job
            self.job_task = job_task
            self.op_type = kwargs["op_type"]
            super().__init__(job, job_task, *args, **kwargs)

        def generate_activities(self, global_pipeline_data: Data = None) -> Dict[str, Any]:
            proc_op_act = self.operate_process()
            check_status_act = self.check_status()

            # 全局具有多个重复流程，通过全局上下文交互变量需要用job_task_id唯一标识变量
            proc_op_act_status_output_name = "${" + f"job_task_id_{self.job_task.id}_last_proc_op_status" + "}"
            # proc_op_act的进程操作状态传入check_status_act
            check_status_act.component.inputs["last_proc_op_status"] = Var(
                type=Var.SPLICE, value=proc_op_act_status_output_name
            )
            global_pipeline_data.inputs[proc_op_act_status_output_name] = NodeOutput(
                type=Var.SPLICE, source_act=proc_op_act.id, source_key="proc_op_status", value=""
            )
            return {"activities": [proc_op_act, check_status_act], "sub_process_data": None}

        def operate_process(self):
            """进程操作原子"""
            act = ServiceActivity(component_code=GseOperateProcessComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            act.component.inputs.op_type = Var(type=Var.PLAIN, value=self.op_type)
            return act

        def check_status(self):
            """查询进程状态，更新写入DB"""
            act = ServiceActivity(component_code=GseCheckProcessComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task.id)
            act.component.inputs.op_type = Var(type=Var.PLAIN, value=GseOpType.CHECK)
            return act

    class BulkOperateProcessActivityManager(BulkBaseActivityManager):
        def __init__(self, job: Job, job_task_ids, *args, **kwargs):
            self.job = job
            self.job_task_ids = job_task_ids
            self.op_type = kwargs["op_type"]
            super().__init__(job, job_task_ids, *args, **kwargs)

        def bulk_generate_activities(self, global_pipeline_data: Data = None) -> Dict[str, Any]:
            proc_op_act = self.bulk_operate_process()
            check_status_act = self.bulk_check_status()

            # 全局具有多个重复流程，通过全局上下文交互变量需要用 proc_op_act.id 唯一标识变量
            proc_op_act_status_output_name = "${" + f"job_id_{proc_op_act.id}_last_proc_op_status_map" + "}"
            # proc_op_act的进程操作状态传入check_status_act
            check_status_act.component.inputs["last_proc_op_status_map"] = Var(
                type=Var.SPLICE, value=proc_op_act_status_output_name
            )
            global_pipeline_data.inputs[proc_op_act_status_output_name] = NodeOutput(
                type=Var.SPLICE, source_act=proc_op_act.id, source_key="proc_op_status_map", value=""
            )
            return {"activities": [proc_op_act, check_status_act], "sub_process_data": None}

        def bulk_operate_process(self):
            """批量进程操作原子"""
            act = ServiceActivity(component_code=BulkGseOperateProcessComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.op_type = Var(type=Var.PLAIN, value=self.op_type)
            return act

        def bulk_check_status(self):
            """批量查询进程状态，更新写入DB"""
            act = ServiceActivity(component_code=BulkGseCheckProcessComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.op_type = Var(type=Var.PLAIN, value=GseOpType.CHECK)
            return act

    class BulkGenerateConfigActivityManager(BulkBaseActivityManager):
        def bulk_generate_activities(self, global_pipeline_data: Data = None) -> Dict:
            return {
                "activities": [self.bulk_generate_config()],
                "sub_process_data": None,
            }

        def bulk_generate_config(self):
            act = ServiceActivity(component_code=BulkGenerateConfigComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.job.created_by)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

    class ReleaseConfigActivityManager(BulkBaseActivityManager):
        def bulk_generate_activities(self, global_pipeline_data: Data = None) -> Dict:
            return {
                "activities": [self.bulk_backup_config(), self.bulk_release_config()],
                "sub_process_data": None,
            }

        def bulk_release_config(self):
            act = ServiceActivity(component_code=BulkPushConfigComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.job.created_by)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act

        def bulk_backup_config(self):
            act = ServiceActivity(component_code=BulkBackupConfigComponent.code)
            act.component.inputs.job_task_id = Var(type=Var.PLAIN, value=self.job_task_ids[0])
            act.component.inputs.job_task_ids = Var(type=Var.PLAIN, value=self.job_task_ids)
            act.component.inputs.bk_username = Var(type=Var.PLAIN, value=self.job.created_by)
            act.component.inputs.bk_biz_id = Var(type=Var.PLAIN, value=self.job.bk_biz_id)
            return act
