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
from functools import reduce
from typing import Dict, Any, Optional, Union, List
from collections import defaultdict

from django.db import transaction
from django.db.models import QuerySet

from apps.gsekit.job.exceptions import NotSupportedJobActionException
from apps.gsekit.job.models import Job, JobTask
from apps.gsekit.meta.models import GlobalSettings
from apps.gsekit.pipeline_plugins.components.collections.gse import GseOpType
from common.log import logger
from bamboo_engine import builder
from bamboo_engine.builder import Data, ServiceActivity
from .base import BasePipelineManager


class ProcessPipelineManager(BasePipelineManager):

    process_task_aggregate_info: Dict[str, str] = None

    def __init__(self, job: Job):
        super().__init__(job)

        self.process_task_aggregate_info: Dict[str, str] = GlobalSettings.process_task_aggregate_info(
            bk_biz_id=self.job.bk_biz_id
        )
        job.task_granularity = self.process_task_aggregate_info["task_granularity"]
        job.save()

    def get_activity_manager(self):
        from apps.gsekit.adapters import channel_adapter

        return channel_adapter.BulkOperateProcessActivityManager

    def create_pipeline(self, job_tasks: QuerySet[JobTask]) -> Dict[str, Any]:
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
        # 声明一个Pipeline全局数据上下文
        global_pipeline_data = Data()
        op_type = self.get_op_type()

        if self.get_op_type_order():
            weights = -1
        else:
            weights = 1

        job_tasks_gby_node_key: Dict[Optional[Union[str, int]], List[JobTask]] = defaultdict(list)
        for job_task in job_tasks:
            aggregate_node_key: Optional[Union[str, int]] = job_task.extra_data["topo_level_info"].get(
                self.process_task_aggregate_info["node_key_field"]
            )
            job_tasks_gby_node_key[aggregate_node_key].append(job_task)

        sub_processes = []
        with transaction.atomic():
            for job_tasks_under_node_key in job_tasks_gby_node_key.values():
                # 按照 priority 优先级进行分组
                ordered_job_tasks = sorted(
                    job_tasks_under_node_key,
                    key=lambda x: weights * x.extra_data["process_info"]["process"]["priority"],
                )

                # 托管/取消托管 时，无需区分优先级，将优先级都设为一样
                if self.job.job_action in [Job.JobAction.SET_AUTO, Job.JobAction.UNSET_AUTO]:
                    for job_task in ordered_job_tasks:
                        job_task.extra_data["process_info"]["process"]["priority"] = 0

                ordered_activities: List[ServiceActivity] = []
                # 根据分组按优先级顺序执行进程操作
                grouped_job_tasks = groupby(
                    ordered_job_tasks, lambda x: x.extra_data["process_info"]["process"]["priority"]
                )
                for priority, priority_job_tasks in grouped_job_tasks:
                    logger.info(f"creating pipeline with priority[{priority}]")
                    job_task_ids = [job_task.id for job_task in priority_job_tasks]
                    activities: List[ServiceActivity] = activity_manager(
                        job=self.job, job_task_ids=job_task_ids, op_type=op_type
                    ).bulk_generate_activities(global_pipeline_data)["activities"]
                    self.mark_acts_tail_and_head(activities)
                    ordered_activities.extend(list(filter(None, activities)))

                # 串联 activities
                reduce(lambda l, r: l.extend(r), ordered_activities)
                sub_processes.append(ordered_activities[0])

        start_event = builder.EmptyStartEvent()
        parallel_gw = builder.ParallelGateway()
        converge_gw = builder.ConvergeGateway()
        end_event = builder.EmptyEndEvent()
        start_event.extend(parallel_gw).connect(*sub_processes).to(parallel_gw).converge(converge_gw).extend(end_event)
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
