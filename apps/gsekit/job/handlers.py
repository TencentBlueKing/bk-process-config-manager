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
from collections import Counter
from itertools import groupby
from typing import Dict, List

from celery.task import task
from django.conf import settings
from django.db import transaction
from django.db.models import Count, QuerySet
from django.utils.translation import ugettext as _
from pipeline.eri.runtime import BambooDjangoRuntime

from apps.exceptions import AppBaseException
from apps.gsekit.adapters import channel_adapter
from apps.gsekit.job import exceptions
from apps.gsekit.job.models import (
    JOB_STATUS_CHOICES,
    Job,
    JobErrCode,
    JobStatus,
    JobTask,
)
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.utils.expression_utils.serializers import gen_expression
from apps.utils import APIModel
from apps.utils.basic import distinct_dict_list
from apps.utils.local import get_request
from apps.utils.models import model_to_dict, queryset_to_dict_list
from common.log import logger
from bamboo_engine import api


class JobHandlers(APIModel):
    def __init__(self, bk_biz_id, job_id=None):
        self.bk_biz_id = bk_biz_id
        self.job_id = job_id
        super().__init__()

    def _get_data(self) -> Job:
        try:
            job = Job.objects.get(bk_biz_id=self.bk_biz_id, id=self.job_id)
        except Job.DoesNotExist:
            logger.error("任务不存在, job_id={}".format(self.job_id))
            raise exceptions.JobDoseNotExistException()
        return job

    @property
    def data(self) -> Job:
        return super().data

    @staticmethod
    @task
    def create_job_task(job_id, extra_data):
        job = Job.objects.get(id=job_id)
        manager = channel_adapter.PIPELINE_MANAGER_FACTORY.get_manager(job)
        try:
            manager.create_job_task(extra_data=extra_data)
        except Exception as err:
            failed_reason = str(err)
            logger.exception("Failed to create job task: {err}".format(err=failed_reason))
            job.status = JobStatus.FAILED
            job.is_ready = True
            job.extra_data["failed_reason"] = failed_reason
            job.save(update_fields=["status", "is_ready", "extra_data"])

    def create_job(
        self,
        job_object: str,
        job_action: str,
        created_by: str,
        scope: Dict = None,
        expression_scope: Dict = None,
        extra_data: Dict = None,
    ) -> Dict:
        process_handler = ProcessHandler(self.bk_biz_id)
        if scope is None:
            scope_to_be_used = process_handler.expression_scope_to_scope(expression_scope)
            scope_to_be_used["is_expression"] = True
        else:
            scope_to_be_used = scope
            expression_scope = process_handler.scope_to_expression_scope(scope_to_be_used)

        # 记录expression，使用 . 分割用于前端展示，不使用 <-GSEKIT-> 分割(可读性较差)
        expression = gen_expression(expression_scope, splitter=".")

        # 记录调用方的app_code，用于运营统计
        bk_app_code = settings.APP_ID
        try:
            request = get_request()
        except AppBaseException:
            pass
        else:
            bk_app_code = request.META.get("HTTP_BK_APP_CODE", bk_app_code)

        job = Job.objects.create(
            bk_biz_id=self.bk_biz_id,
            expression=expression,
            expression_scope=expression_scope,
            scope=scope_to_be_used,
            job_object=job_object,
            job_action=job_action,
            created_by=created_by,
            bk_app_code=bk_app_code or settings.APP_ID,
        )
        self.create_job_task.delay(job.id, extra_data=extra_data)
        return {"job_id": job.id}

    @staticmethod
    def get_task_status_counter(job_task_queryset: QuerySet):
        status_counter = {job_status_tuple[0]: 0 for job_status_tuple in JOB_STATUS_CHOICES}
        status_counter.update(dict(Counter(job_task_queryset.values_list("status", flat=True))))
        return {"count": sum(status_counter.values()), "status_counter": status_counter}

    def get_job_task(self, page: int = 1, pagesize: int = None, conditions: Dict = None) -> Dict:
        if conditions is None:
            conditions = {}
        filter_conditions = {"job_id": self.data.id}
        key_filter_field_map = {
            "bk_set_ids": "bk_set_id__in",
            "bk_module_ids": "bk_module_id__in",
            "bk_process_ids": "bk_process_id__in",
            "bk_process_names": "bk_process_name__in",
            "statuses": "status__in",
        }
        for key, value_list in conditions.items():
            if not value_list and value_list != 0:
                continue
            if key in ["bk_set_ids", "bk_module_ids", "bk_process_ids", "bk_process_names"]:
                if key not in ["bk_process_names"]:
                    treated_value_list = [value for value in value_list if str(value).isdigit()]
                else:
                    treated_value_list = value_list
                obj_id = key.split("_")[1]
                filter_conditions[
                    f"extra_data__process_info__{obj_id}__{key_filter_field_map[key]}"
                ] = treated_value_list
            elif key in ["statuses"]:
                filter_conditions[f"{key_filter_field_map[key]}"] = value_list
            else:
                filter_conditions[key] = value_list
        job_task_queryset = JobTask.objects.filter(**filter_conditions)

        if pagesize is not None:
            job_task_page = job_task_queryset[pagesize * (page - 1) : pagesize * page]
        else:
            job_task_page = job_task_queryset
        return {
            "list": [model_to_dict(job_task) for job_task in job_task_page],
            **self.get_task_status_counter(job_task_queryset),
        }

    def job_task_statistics(self):
        """任务统计"""
        statistics = JobTask.objects.filter(job_id=self.job_id).values("err_code").annotate(count=Count("err_code"))
        err_code_msg_map = JobErrCode.all_err_code_msg_map()
        for stati in statistics:
            err_code = stati["err_code"]
            stati["message"] = err_code_msg_map.get(err_code, _("未知错误{err_code}").format(err_code=err_code))

        # 按指定顺序排序
        sort_order = [JobErrCode.PENDING, JobErrCode.RUNNING, JobErrCode.IGNORED]
        ordered_statistics = [stati for x in sort_order for stati in statistics if stati["err_code"] == x]
        ordered_statistics.extend([stati for stati in statistics if stati["err_code"] not in sort_order])
        return ordered_statistics

    def get_job_status(self, job_task_id_list: List[int] = None) -> Dict:
        if job_task_id_list is None:
            job_task_id_list = []
        return {
            "job_info": model_to_dict(self.data),
            "job_tasks": queryset_to_dict_list(JobTask.objects.filter(job_id=self.data.id, id__in=job_task_id_list)),
            **self.get_task_status_counter(JobTask.objects.filter(job_id=self.data.id)),
        }

    def retry(self, job_task_id_list: List = None):
        """重试失败的任务"""
        runtime = BambooDjangoRuntime()
        status_to_be_retry = [JobStatus.FAILED, JobStatus.PENDING]

        # 若未指定子任务重试，则重试所有子任务
        if not job_task_id_list:
            job_tasks = JobTask.objects.filter(job_id=self.job_id, status__in=status_to_be_retry)
        else:
            job_tasks = JobTask.objects.filter(id__in=job_task_id_list, status__in=status_to_be_retry)
        job_tasks = job_tasks.only("id", "pipeline_id")

        action_results = []
        with transaction.atomic():
            job = Job.objects.get(id=self.job_id)
            job.status = JobStatus.PENDING
            job.save(update_fields=["status"])
            job_tasks.update(status=JobStatus.PENDING, err_code=JobErrCode.PENDING)
            job_tasks_gby_pipeline_id = groupby(sorted(job_tasks, key=lambda t: t.pipeline_id), lambda x: x.pipeline_id)
            for pipeline_id, pipeline_job_tasks in job_tasks_gby_pipeline_id:
                # pipeline node id 为空 表示节点暂未执行，忽略
                if not pipeline_id:
                    continue
                job_task_ids = [job_task.id for job_task in pipeline_job_tasks]
                # 批量操作的流水线
                data = {key: data_input.value for key, data_input in runtime.get_data_inputs(pipeline_id).items()}
                data["job_task_ids"] = job_task_ids
                action_result = api.retry_node(runtime=runtime, node_id=pipeline_id, data=data)
                if not action_result.result:
                    raise exceptions.JobRetryException(message=action_result.message)
                action_results.append(action_result)
        return action_results

    def search_ip(self, status=None):
        """根据状态查询主机信息"""
        job_tasks = JobTask.objects.filter(job_id=self.job_id).only("extra_data")
        if status:
            job_tasks = job_tasks.filter(status=status)
        hosts = [job_task.extra_data["process_info"]["host"] for job_task in job_tasks]
        return distinct_dict_list(hosts)
