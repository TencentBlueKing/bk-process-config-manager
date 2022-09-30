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
import copy
from collections import defaultdict
from functools import reduce
from typing import Dict, List

from django.db import transaction
from django.db.models import QuerySet

from apps.gsekit.configfile.models import (
    ConfigInstance,
    ConfigTemplateBindingRelationship,
)
from apps.gsekit.constants import PIPELINE_BATCH_SIZE
from apps.gsekit.job.exceptions import NotSupportedJobActionException
from apps.gsekit.job.models import Job, JobTask
from apps.gsekit.process.models import Process
from pipeline import builder

from .base import BasePipelineManager


class ConfigFilePipelineManager(BasePipelineManager):
    def get_activity_manager(self):
        from apps.gsekit.adapters import channel_adapter

        action_manager_map = {
            Job.JobAction.GENERATE: channel_adapter.BulkGenerateConfigActivityManager,
            Job.JobAction.RELEASE: channel_adapter.ReleaseConfigActivityManager,
            Job.JobAction.DIFF: channel_adapter.BulkDiffConfigActivityManager,
        }
        job_action = self.job.job_action
        try:
            return action_manager_map[job_action]
        except KeyError:
            raise NotSupportedJobActionException(job_action=job_action)

    def generate_to_be_created_data(self, process_related_info, proc_inst_map, extra_data) -> Dict:
        """生成要创建的子任务"""
        config_template_ids = extra_data.get("config_template_ids") or []
        config_template_relation_mapping = ConfigTemplateBindingRelationship.get_config_template_relation_mapping(
            config_template_ids
        )
        config_version_ids_map = extra_data.get("config_version_ids_map") or []
        template_id_version_ids_map = {
            mapping["config_template_id"]: mapping.get("config_version_ids") or [] for mapping in config_version_ids_map
        }
        if config_version_ids_map:
            # 生成配置时，需过滤掉非最新配置版本
            config_template_process_mapping = ConfigInstance.get_config_template_latest_version_process_mapping(
                config_version_ids_map
            )
        else:
            config_template_process_mapping = {}
        to_be_created_job_tasks = []

        bk_set_env = self.job.scope["bk_set_env"]
        process_id__config_tmpl_ids_map: Dict[int, List[int]] = defaultdict(list)
        for process_info in process_related_info:
            # 非指定环境类型集群的进程不操作
            if bk_set_env != process_info["set"]["bk_set_env"]:
                continue
            bk_process_id = process_info["process"]["bk_process_id"]
            process_template_id = process_info["process_template"]["id"]

            # 用于标记是否指定配置模板
            is_config_specified: bool = False
            for config_template_id in config_template_ids:
                is_config_specified = True

                if not (
                    bk_process_id
                    in config_template_relation_mapping[config_template_id][Process.ProcessObjectType.INSTANCE]
                    or process_template_id
                    in config_template_relation_mapping[config_template_id][Process.ProcessObjectType.TEMPLATE]
                ):
                    # 指定了配置模板，且进程未绑定配置模板，则不创建任务
                    continue

                # 没有指定版本，视为已选择最新版本
                if not template_id_version_ids_map.get(config_template_id):
                    process_id__config_tmpl_ids_map[bk_process_id].append(config_template_id)
                    continue

                # 指定配置模板版本，需要判断进程是否具有该版本的实例
                if bk_process_id in config_template_process_mapping.get(config_template_id, []):
                    process_id__config_tmpl_ids_map[bk_process_id].append(config_template_id)
                    continue

            # 获取进程实例关联的配置模板 ID 列表
            related_config_template_ids: List[int] = process_id__config_tmpl_ids_map[bk_process_id]

            # 指定配置的情况下，如果配置关联检查不合法，跳过该进程的任务创建
            if is_config_specified and not related_config_template_ids:
                continue

            for proc_inst in proc_inst_map[bk_process_id]:

                job_task_extra_data = copy.deepcopy(extra_data)
                job_task_extra_data["process_info"] = process_info
                job_task_extra_data["inst_id"] = proc_inst["inst_id"]
                job_task_extra_data["local_inst_id"] = proc_inst["local_inst_id"]
                # 将配置模板绑定关系写入到进程所关联的任务实例，用于后置过滤
                job_task_extra_data["related_config_info"] = {
                    "is_config_specified": is_config_specified,
                    "related_config_template_ids": related_config_template_ids,
                }
                job_task_extra_data["config_instances"] = []
                to_be_created_job_tasks.append(
                    JobTask(
                        job_id=self.job.id,
                        bk_process_id=bk_process_id,
                        extra_data=job_task_extra_data,
                    )
                )

        return {
            "to_be_created_job_tasks": to_be_created_job_tasks,
            "to_be_created_proc_inst_status_statistics": [],
        }

    def create_pipeline(self, job_tasks: QuerySet) -> Dict:
        """
        根据优先级生成不同的执行顺序的并行网关，组成pipeline
                   StartEvent
                       |
                 ParallelGateway
                       |
            -----------------------
            |          |          |
         gen_conf   gen_conf   gen_conf
            |          |          |
        push_repo  push_repo  push_repo
            |          |          |
           ...        ...        ...
            |          |          |
            ----------------------
                       |
                 ConvergeGateway
                       |
                    EndEvent
        """

        activity_manager = self.get_activity_manager()
        sub_processes = []
        with transaction.atomic():
            job_task_ids = [job_task.id for job_task in job_tasks]
            job_task_len = len(job_task_ids)
            start = 0
            # 分批创建pipeline，提高执行效率
            while start < job_task_len:
                activities = activity_manager(
                    job=self.job, job_task_ids=job_task_ids[start : start + PIPELINE_BATCH_SIZE]
                ).bulk_generate_activities()["activities"]
                self.mark_acts_tail_and_head(activities)

                activities_start_event = activities[0]
                # 串联 activities
                reduce(lambda l, r: l.extend(r), [act for act in activities if act])
                sub_processes.append(activities_start_event)
                start = start + PIPELINE_BATCH_SIZE

        start_event = builder.EmptyStartEvent()
        parallel_gw = builder.ParallelGateway()
        converge_gw = builder.ConvergeGateway()
        end_event = builder.EmptyEndEvent()
        start_event.extend(parallel_gw).connect(*sub_processes).to(parallel_gw).converge(converge_gw).extend(end_event)

        return {"pipeline_start": start_event, "global_pipeline_data": None}
