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
from bamboo_engine import states
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.gsekit import constants
from apps.gsekit.job.models import Job, JobStatus, JobTask, JobErrCode
from apps.gsekit.pipeline_plugins.exceptions import GsePriorityException
from apps.gsekit.utils.notification_maker import JobNotificationMaker, ContentType, MsgType


def pipeline_end_handler(sender, root_pipeline_id, **kwargs):
    """pipeline结束信号处理"""
    # 设置 Job 和 JobTask 的状态
    Job.objects.filter(pipeline_id=root_pipeline_id).update(status=JobStatus.SUCCEEDED, end_time=timezone.now())
    job = Job.objects.get(pipeline_id=root_pipeline_id)
    JobTask.objects.filter(job_id=job.id, err_code__in=(JobErrCode.PENDING, JobErrCode.RUNNING)).update(
        err_code=JobErrCode.SUCCEEDED
    )
    # 发送邮件
    JobNotificationMaker(
        job=Job.objects.get(pipeline_id=root_pipeline_id), content_type=ContentType.HTML, msg_type=MsgType.MAIL
    ).send()


def activity_failed_handler(pipeline_id, pipeline_activity_id, *args, **kwargs):
    """activity失败信号处理"""
    with transaction.atomic():
        job = Job.objects.get(pipeline_id=pipeline_id)
        job.status = JobStatus.FAILED
        job.end_time = timezone.now()
        job.save(update_fields=["status", "end_time"])

        # 优先级前置的进程操作已失败
        if job.job_object == Job.JobObject.PROCESS:
            from apps.gsekit.adapters.base.pipeline_managers import ProcessPipelineManager

            job_task = JobTask.objects.filter(job_id=job.id, pipeline_id=pipeline_activity_id).first()
            if job_task is None:
                return

            priority = job_task.extra_data["process_info"]["process"]["priority"] or 0
            bk_func_name = job_task.extra_data["process_info"]["process"]["bk_func_name"]
            bk_process_name = job_task.extra_data["process_info"]["process"]["bk_process_name"]
            if ProcessPipelineManager(job=job).get_op_type_order():
                conditions = {"extra_data__process_info__process__priority__lt": priority}
                failed_reason = _(
                    "优先级等于[{priority}]的进程({bk_func_name}-{bk_process_name})操作已失败，优先级小于此的进程操作不会被继续执行"
                ).format(priority=priority, bk_func_name=bk_func_name, bk_process_name=bk_process_name)
            else:
                conditions = {"extra_data__process_info__process__priority__gt": priority}
                failed_reason = _(
                    "优先级等于[{priority}]的进程({bk_func_name}-{bk_process_name})操作已失败，优先级大于此的进程操作不会被继续执行"
                ).format(priority=priority, bk_func_name=bk_func_name, bk_process_name=bk_process_name)

            process_task_aggregate_node_key_field = constants.TaskGranularity.TASK_GRANULARITY_NODE_KEY_FIELD_MAP[
                job.task_granularity
            ]
            if job_task.extra_data.get("topo_level_info"):
                conditions[
                    f"extra_data__topo_level_info__{process_task_aggregate_node_key_field}"
                ] = job_task.extra_data["topo_level_info"][process_task_aggregate_node_key_field]

            with transaction.atomic():
                for job_task in JobTask.objects.filter(job_id=job.id, status=JobStatus.PENDING, **conditions):
                    job_task.set_status(
                        JobStatus.FAILED,
                        extra_data={"failed_reason": failed_reason, "err_code": GsePriorityException().code},
                    )

    JobNotificationMaker(
        job=Job.objects.get(pipeline_id=pipeline_id), content_type=ContentType.HTML, msg_type=MsgType.MAIL
    ).send()


def bamboo_engine_eri_post_set_state_handler(node_id, to_state, version, root_id, parent_id, loop, **kwargs):
    # 适配bamboo_engine信号
    if to_state == states.FAILED:
        activity_failed_handler(root_id, node_id)
    elif to_state == states.FINISHED and node_id == root_id:
        pipeline_end_handler(None, root_id)
