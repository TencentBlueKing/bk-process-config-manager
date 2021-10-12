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
from typing import Dict, Any, List

from bamboo_engine import api
from bamboo_engine.builder import builder, ServiceActivity, Var
from pipeline.eri.runtime import BambooDjangoRuntime

from apps.api import CCApi
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.job.exceptions import JobEmptyTaskException
from apps.gsekit.job.models import Job, JobTask, JobProcInstStatusStatistics
from apps.gsekit.pipeline_plugins.components.collections.base import ActivityType
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.process.models import ProcessInst, Process
from apps.utils.batch_request import batch_request


class BasePipelineManager(object):
    def __init__(self, job: Job):
        self.job = job

    def get_activity_manager(self):
        raise NotImplementedError

    @classmethod
    def mark_acts_tail_and_head(cls, activities: List[ServiceActivity]) -> None:
        if len(activities) == 1:
            activities[0].component.inputs.act_type = Var(type=Var.PLAIN, value=ActivityType.HEAD_TAIL)
            return
        activities[0].component.inputs.act_type = Var(type=Var.PLAIN, value=ActivityType.HEAD)
        activities[-1].component.inputs.act_type = Var(type=Var.PLAIN, value=ActivityType.TAIL)

    def create_pipeline(self, job_tasks) -> Dict[str, Any]:
        """创建pipeline，由子类实现，返回构建Pipeline的相关参数

        required:
            - pipeline_start: pipeline.builder.ServiceActivity Pipeline起始原子，用于构建pipeline tree
        optional:
            - global_pipeline_data: pipeline.builder.Data 全局流程数据上下文
            - more
        """

        raise NotImplementedError

    def generate_to_be_created_data(self, process_related_info, proc_inst_map, extra_data) -> Dict:
        """生成要创建的子任务"""
        to_be_created_job_tasks = []
        to_be_created_proc_inst_status_statistics = []
        bk_set_env = self.job.scope["bk_set_env"]
        for process_info in process_related_info:
            # 非指定环境类型集群的进程不操作
            if bk_set_env != process_info["set"]["bk_set_env"]:
                continue
            bk_process_id = process_info["process"]["bk_process_id"]
            for proc_inst in proc_inst_map[bk_process_id]:
                job_task_extra_data = copy.deepcopy(extra_data)
                job_task_extra_data["process_info"] = process_info
                job_task_extra_data["inst_id"] = proc_inst["inst_id"]
                job_task_extra_data["local_inst_id"] = proc_inst["local_inst_id"]
                job_task_extra_data["retryable"] = True
                job_task_extra_data["solutions"] = []
                to_be_created_job_tasks.append(
                    JobTask(
                        job_id=self.job.id,
                        bk_process_id=bk_process_id,
                        extra_data=job_task_extra_data,
                    )
                )
            if self.job.job_object in [Job.JobObject.PROCESS] and proc_inst_map[bk_process_id]:
                to_be_created_proc_inst_status_statistics.append(
                    JobProcInstStatusStatistics(
                        job_id=self.job.id,
                        bk_process_id=bk_process_id,
                        proc_inst_total_num=len(proc_inst_map[bk_process_id]),
                    )
                )
        return {
            "to_be_created_job_tasks": to_be_created_job_tasks,
            "to_be_created_proc_inst_status_statistics": to_be_created_proc_inst_status_statistics,
        }

    def create_job_task(self, extra_data=None):
        # 表达式筛选情况下bk_process_ids为空表示无进程，在list_process_related_info表示全选，需要兼容并提前返回
        if self.job.scope.get("is_expression") and not self.job.scope.get("bk_process_ids", []):
            raise JobEmptyTaskException()
        params = {
            "bk_biz_id": self.job.bk_biz_id,
            "set": {"bk_set_ids": self.job.scope.get("bk_set_ids") or []},
            "module": {"bk_module_ids": self.job.scope.get("bk_module_ids") or []},
            "service_instance": {"ids": self.job.scope.get("bk_service_ids") or []},
        }
        rules = []
        if self.job.scope.get("bk_process_names"):
            rules.append(
                {"field": "bk_process_name", "operator": "in", "value": self.job.scope.get("bk_process_names") or []}
            )

        if self.job.scope.get("bk_process_ids"):
            rules.append(
                {"field": "bk_process_id", "operator": "in", "value": self.job.scope.get("bk_process_ids") or []}
            )

        if rules:
            params["process_property_filter"] = {"condition": "AND", "rules": rules}
        process_related_info = batch_request(CCApi.list_process_related_info, params)
        CMDBHandler(bk_biz_id=self.job.bk_biz_id).cache_topo_tree_attr(self.job.scope["bk_set_env"])
        if extra_data is None:
            extra_data = {}

        bk_process_ids = [process_info["process"]["bk_process_id"] for process_info in process_related_info]
        proc_inst_map = defaultdict(list)
        if extra_data.get("extra_filter_conditions"):
            extra_filter_conditions = extra_data["extra_filter_conditions"]
            process_queryset = ProcessHandler(bk_biz_id=self.job.bk_biz_id).list(
                process_queryset=Process.objects.filter(bk_biz_id=self.job.bk_biz_id, bk_process_id__in=bk_process_ids),
                scope=self.job.scope,
                expression_scope=self.job.expression_scope,
                bk_cloud_ids=extra_filter_conditions.get("bk_cloud_ids"),
                bk_host_innerips=extra_filter_conditions.get("bk_host_innerips"),
                process_status_list=extra_filter_conditions.get("process_status_list"),
                is_auto_list=extra_filter_conditions.get("is_auto_list"),
            )
            bk_process_ids = process_queryset.values_list("bk_process_id", flat=True)
        for proc_inst in ProcessInst.objects.filter(bk_process_id__in=bk_process_ids).values(
            "bk_process_id", "inst_id", "local_inst_id", "process_status"
        ):
            proc_inst_map[proc_inst["bk_process_id"]].append(
                {"inst_id": proc_inst["inst_id"], "local_inst_id": proc_inst["local_inst_id"]}
            )

        to_be_created_job_data = self.generate_to_be_created_data(process_related_info, proc_inst_map, extra_data)

        to_be_created_proc_inst_status_statistics = to_be_created_job_data["to_be_created_proc_inst_status_statistics"]
        if to_be_created_proc_inst_status_statistics:
            JobProcInstStatusStatistics.objects.bulk_create(to_be_created_proc_inst_status_statistics)

        to_be_created_job_tasks = to_be_created_job_data["to_be_created_job_tasks"]
        # 无进程执行任务
        if not to_be_created_job_tasks:
            raise JobEmptyTaskException()
        JobTask.objects.bulk_create(to_be_created_job_tasks)

        job_tasks = JobTask.objects.filter(job_id=self.job.id)

        create_pipeline_params = self.create_pipeline(job_tasks)

        pipeline = builder.build_tree(
            create_pipeline_params["pipeline_start"], data=create_pipeline_params.get("global_pipeline_data")
        )

        self.job.set_pipeline_id(pipeline["id"])

        # 执行流程对象
        runtime = BambooDjangoRuntime()
        api.run_pipeline(runtime=runtime, pipeline=pipeline)
