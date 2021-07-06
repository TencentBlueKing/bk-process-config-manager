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
from functools import reduce
from itertools import chain, groupby
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet

from apps.gsekit.adapters.base.pipeline_managers.configfile import ConfigFilePipelineManager
from apps.gsekit.constants import PIPELINE_BATCH_SIZE
from bamboo_engine import builder
from bamboo_engine.builder import Data


class BscpReleaseConfigFilePipelineManager(ConfigFilePipelineManager):
    def create_pipeline(self, job_tasks: QuerySet) -> Dict:
        """
        BSCP下发配置时需特殊处理，按一定的规则做分组汇聚
        """

        activity_manager = self.get_activity_manager()
        start_event = builder.EmptyStartEvent()
        # 声明一个Pipeline全局数据上下文
        global_pipeline_data = Data()
        current_node = start_event
        with transaction.atomic():

            # 按照进程模板进行分组
            ordered_process_template_job_tasks = job_tasks.exclude(extra_data__process_info__process_template__id=0)
            grouped_process_template_job_tasks = groupby(
                ordered_process_template_job_tasks, lambda x: x.extra_data["process_info"]["process_template"]["id"]
            )
            # 按照进程实例进行分组
            ordered_process_inst_job_tasks = job_tasks.filter(extra_data__process_info__process_template__id=0)
            grouped_process_inst_job_tasks = groupby(
                ordered_process_inst_job_tasks, lambda x: x.extra_data["process_info"]["process"]["bk_process_id"]
            )
            # 根据进程模板分组构建并行网关
            group_sub_processes = []

            for process_template_id, process_template_job_tasks in chain(
                grouped_process_template_job_tasks, grouped_process_inst_job_tasks
            ):

                job_task_ids = []
                for job_task in process_template_job_tasks:
                    job_task_ids.append(job_task.id)

                # 分批创建pipeline，提高执行效率
                job_task_len = len(job_task_ids)
                start = 0
                batch_sub_processes = []
                while start < job_task_len:
                    create_sub_process_params = activity_manager(
                        job=self.job, job_task=job_task, job_task_ids=job_task_ids[start : start + PIPELINE_BATCH_SIZE]
                    ).generate_activities(global_pipeline_data)
                    activities = create_sub_process_params["activities"]
                    # 标记头部及尾部原子
                    self.mark_acts_tail_and_head(activities)
                    activities_start_event = activities[0]
                    # 串联 activities
                    reduce(lambda l, r: l.extend(r), [act for act in activities if act])
                    batch_sub_processes.append(activities_start_event)
                    start = start + PIPELINE_BATCH_SIZE

                group_parallel_gw = builder.ParallelGateway()
                group_converge_gw = builder.ConvergeGateway()
                group_parallel_gw.connect(*batch_sub_processes).to(group_parallel_gw).converge(group_converge_gw)
                group_sub_processes.append(group_parallel_gw)

            parallel_gw = builder.ParallelGateway()
            converge_gw = builder.ConvergeGateway()
            current_node = (
                current_node.extend(parallel_gw).connect(*group_sub_processes).to(parallel_gw).converge(converge_gw)
            )

        current_node.extend(builder.EmptyEndEvent())
        return {"pipeline_start": start_event, "global_pipeline_data": global_pipeline_data}
