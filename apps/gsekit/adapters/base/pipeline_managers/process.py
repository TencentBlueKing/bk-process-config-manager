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
from itertools import groupby
from typing import Dict, Any

from django.db import transaction
from django.db.models import QuerySet

from apps.gsekit.job.exceptions import NotSupportedJobActionException
from apps.gsekit.job.models import Job
from apps.gsekit.pipeline_plugins.components.collections.gse import GseOpType
from common.log import logger
from bamboo_engine import builder
from bamboo_engine.builder import Data
from .base import BasePipelineManager


class ProcessPipelineManager(BasePipelineManager):
    def get_activity_manager(self):
        from apps.gsekit.adapters import channel_adapter

        return channel_adapter.BulkOperateProcessActivityManager

    def create_pipeline(self, job_tasks: QuerySet) -> Dict[str, Any]:
        """
        根据优先级生成不同的执行顺序的并行网关，组成pipeline
                 StartEvent
                     |
               ParallelGateway
                     |
            -------------------
            |        |        |
          prio=1   prio=1   prio=1
            |        |        |
          check    check    check
            |        |        |
            -------------------
                     |
               ConvergeGateway
                     |
               ParallelGateway
                     |
            -------------------
            |        |        |
          prio=2   prio=2   prio=2
            |        |        |
          check    check    check
            |        |        |
            -------------------
                     |
               ConvergeGateway
                     |
                  EndEvent
        """
        activity_manager = self.get_activity_manager()
        start_event = builder.EmptyStartEvent()
        # 声明一个Pipeline全局数据上下文
        global_pipeline_data = Data()
        current_node = start_event
        op_type = self.get_op_type()

        if self.get_op_type_order():
            order_by_key = "-extra_data__process_info__process__priority"
        else:
            order_by_key = "extra_data__process_info__process__priority"

        with transaction.atomic():
            # 按照priority优先级进行分组
            ordered_job_tasks = job_tasks.order_by(order_by_key)

            # 托管/取消托管 时，无需区分优先级，将优先级都设为一样
            if self.job.job_action in [Job.JobAction.SET_AUTO, Job.JobAction.UNSET_AUTO]:
                for job_task in ordered_job_tasks:
                    job_task.extra_data["process_info"]["process"]["priority"] = 0

            grouped_job_tasks = groupby(
                ordered_job_tasks, lambda x: x.extra_data["process_info"]["process"]["priority"]
            )

            # 根据分组按优先级顺序执行进程操作
            for priority, priority_job_tasks in grouped_job_tasks:
                logger.info(f"creating pipeline with priority[{priority}]")

                job_task_ids = [job_task.id for job_task in priority_job_tasks]
                activities = activity_manager(
                    job=self.job, job_task_ids=job_task_ids, op_type=op_type
                ).bulk_generate_activities(global_pipeline_data)["activities"]
                self.mark_acts_tail_and_head(activities)
                # 串联 activities
                for act in activities:
                    if not act:
                        continue
                    current_node = current_node.extend(act)

        current_node.extend(builder.EmptyEndEvent())
        return {"pipeline_start": start_event, "global_pipeline_data": global_pipeline_data}

    def get_op_type(self) -> int:
        job_action_op_type_map = {
            Job.JobAction.START: GseOpType.START,
            Job.JobAction.STOP: GseOpType.STOP,
            Job.JobAction.RELOAD: GseOpType.RELOAD,
            Job.JobAction.RESTART: GseOpType.RESTART,
            Job.JobAction.FORCE_STOP: GseOpType.FORCE_STOP,
            Job.JobAction.SET_AUTO: GseOpType.SET_AUTO,
            Job.JobAction.UNSET_AUTO: GseOpType.UNSET_AUTO,
        }
        job_action = self.job.job_action
        try:
            return job_action_op_type_map[job_action]
        except KeyError:
            raise NotSupportedJobActionException(job_action=job_action)

    def get_op_type_order(self) -> bool:
        """操作顺序"""
        # 停止和重启按优先级逆序执行，其它按正序执行
        job_action_op_type_map = {
            Job.JobAction.STOP: True,
            Job.JobAction.RESTART: True,
        }
        return job_action_op_type_map.get(self.job.job_action, False)
