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
import logging
import traceback
from typing import Dict

from django.db.models import QuerySet
from django.utils.translation import ugettext as _

from apps.exceptions import AppBaseException
from apps.gsekit.configfile import exceptions as configfile_exceptions
from apps.gsekit.job import models as job_models, exceptions as job_exceptions
from apps.gsekit.meta.models import GlobalSettings
from apps.gsekit.pipeline_plugins.exceptions import PipelineTimeoutException
from apps.gsekit.process import exceptions as process_exceptions
from apps.gsekit.utils import solution_maker
from pipeline.core.data.base import DataObject
from pipeline.core.flow.activity import Service

logger = logging.getLogger("celery")

# 轮询间隔
POLLING_INTERVAL = 3
JOB_POLLING_INTERVAL = 5
GSE_POLLING_INTERVAL = 2


class ActivityType:
    HEAD = 0
    TAIL = 1
    HEAD_TAIL = 2


class JobTaskBaseService(Service):
    def judge_act_head_and_set_running(self, data: DataObject, job_task: job_models.JobTask) -> None:
        act_type = data.get_one_of_inputs("act_type")
        if act_type in [ActivityType.HEAD, ActivityType.HEAD_TAIL]:
            job_task.set_status(job_models.JobStatus.RUNNING)
        logger.info(
            "job_task[{job_task_id}] begin at act[{act_name}]".format(
                job_task_id=job_task.id, act_name=self.__class__.__name__
            )
        )

    def judge_act_tail_and_set_succeeded(self, data: DataObject, job_task: job_models.JobTask) -> None:
        act_type = data.get_one_of_inputs("act_type")
        if act_type in [ActivityType.TAIL, ActivityType.HEAD_TAIL]:
            job_task.set_status(job_models.JobStatus.SUCCEEDED)
        logger.info(
            "job_task[{job_task_id}] succeeded at act[{act_name}]".format(
                job_task_id=job_task.id, act_name=self.__class__.__name__
            )
        )

    @classmethod
    def return_data(cls, result: bool, job_extra_data: Dict = None, is_finished: bool = False, **kwargs) -> Dict:
        """
        原子执行调度统一返回
        :param result: 执行结果
        :param job_extra_data:
        :param is_finished: 是否结束调度，对schedule有效，result=False时默认为结束，缺省时is_finished=False
        :param kwargs:
        """
        return {"result": result, "extra_data": job_extra_data, "is_finished": is_finished}

    def run(self, service_func, job_task, **kwargs):
        logger.info(
            "act[{act_name}], job_task[{job_task_id}] {func_name} begin.".format(
                act_name=self.__class__.__name__,
                job_task_id=job_task.id,
                func_name=service_func.__name__,
            )
        )
        try:
            run_return = service_func(**kwargs)
            if not run_return["result"]:
                job_task.set_status(job_models.JobStatus.FAILED, extra_data=run_return.get("extra_data"))
            # 正常执行状态下需要更新extra_data
            elif run_return.get("extra_data"):
                job_task.set_extra_data(extra_data=run_return["extra_data"])
        except Exception as error:
            logger.error(traceback.format_exc())
            extra_data = self.exception_handler(error, job_task)
            job_task.set_status(job_models.JobStatus.FAILED, extra_data=extra_data)
            return {"result": False}

        logger.info(
            "act[{act_name}], job_task[{job_task_id}] {func_name} success: {run_return}".format(
                act_name=self.__class__.__name__,
                job_task_id=job_task.id,
                func_name=service_func.__name__,
                run_return=run_return,
            )
        )
        return run_return

    def exception_handler(self, error: Exception, job_task: job_models.JobTask):
        """异常处理器"""
        extra_data = {"failed_reason": _("系统异常，请联系管理员:{error}").format(error=error), "retryable": True, "solutions": []}
        process_info = job_task.extra_data["process_info"]
        has_solution = True
        if isinstance(error, process_exceptions.ProcessAttrIsNotConfiguredException):
            edit_process_solutions = solution_maker.EditProcessSolutionMaker(
                process_info["service_instance"]["id"],
                process_info["process_template"]["id"],
                process_info["process"]["bk_process_id"],
                action=_("编辑进程属性"),
            ).make()
            sync_cmdb_svc_tmpl_solutions = solution_maker.SyncCmdbSvcTmplSolutionMakerMaker(
                bk_biz_id=process_info["process"]["bk_biz_id"],
                process_template_id=process_info["process_template"]["id"],
            ).make()
            extra_data.update(retryable=False, solutions=edit_process_solutions + sync_cmdb_svc_tmpl_solutions)
        elif isinstance(error, configfile_exceptions.ProcessDoseNotBindTemplate):
            extra_data.update(
                solutions=solution_maker.BindTemplateSolutionMaker(
                    process_info["service_instance"]["id"],
                    process_info["process_template"]["id"],
                    process_info["process"]["bk_process_id"],
                ).make(),
            )
        else:
            has_solution = False

        if has_solution:
            extra_data["failed_reason"] = _("系统异常：{error}。请先参照下方的解决方案处理，若有疑问请联系管理员").format(error=error)
        else:
            extra_data["failed_reason"] = _("系统异常：{error}。请联系管理员处理").format(error=error)
        extra_data["err_code"] = getattr(error, "code", AppBaseException().code)

        return extra_data

    def execute(self, data, parent_data):
        job_task_id = data.get_one_of_inputs("job_task_id")
        try:
            job_task = job_models.JobTask.objects.get(id=job_task_id)
        except job_models.JobTask.DoesNotExist:
            message = _("JobTask[{job_task_id}] not exist".format(job_task_id=job_task_id))
            logger.error(message)
            raise job_exceptions.JobDoseNotExistException(message)

        # 写入pipeline id
        job_task.pipeline_id = self.id

        # 起始原子初始化JobTask为RUNNING
        self.judge_act_head_and_set_running(data, job_task)

        data.inputs.job_task = job_task
        execute_return = self.run(self._execute, job_task, data=data, parent_data=parent_data)

        if not execute_return["result"]:
            return False

        # 需要执行调度且调度未提前结束，初始化轮询总时长
        if self.need_schedule() and not self.is_schedule_finished():
            data.outputs.polling_time = 0
            return True

        # 无需执行调度并且是最后一个原子执行成功, 标识结束
        self.judge_act_tail_and_set_succeeded(data, job_task)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        job_task = data.get_one_of_inputs("job_task")
        schedule_return = self.run(
            self._schedule, job_task, data=data, parent_data=parent_data, callback_data=callback_data
        )

        # 执行错误，返回失败并结束调度
        if not schedule_return["result"]:
            self.finish_schedule()
            return False

        elif schedule_return.get("is_finished", False):
            # 调度成功结束且为最后一个原子，更新JobTask为SUCCEEDED
            self.judge_act_tail_and_set_succeeded(data, job_task)
            self.finish_schedule()
            return True

        # 校验轮询是否超时
        polling_time = data.get_one_of_outputs("polling_time")
        if polling_time + POLLING_INTERVAL > GlobalSettings.pipeline_polling_timeout():
            error = PipelineTimeoutException()
            job_task.set_status(
                job_models.JobStatus.FAILED, extra_data={"failed_reason": error.message, "err_code": error.code}
            )
            self.finish_schedule()
            return False

        data.outputs.polling_time = polling_time + POLLING_INTERVAL
        return True

    def _execute(self, data, parent_data) -> Dict:
        raise NotImplementedError

    def _schedule(self, data, parent_data, callback_data=None) -> Dict:
        return {"result": True, "is_finished": True}

    def inputs_format(self):
        return [
            Service.InputItem(name="job_task_id", key="job_task_id", required=True),
            Service.InputItem(name="job_task", key="job_task", required=True),
            Service.InputItem(name="act_type", key="act_type", required=False),
        ]

    def outputs_format(self):
        return (
            [Service.OutputItem(name="proc_op_status", key="proc_op_status", type="int")]
            if self.need_schedule()
            else []
        )


class MultiJobTaskBaseService(JobTaskBaseService):
    """
    批量JobTask处理，用于多JobTask汇聚，由其中一个执行的场景
    """

    def judge_act_head_and_set_running(self, data: DataObject, job_tasks: QuerySet) -> None:
        act_type = data.get_one_of_inputs("act_type")
        if act_type in [ActivityType.HEAD, ActivityType.HEAD_TAIL]:
            job_tasks.update(status=job_models.JobStatus.RUNNING)
        logger.info(
            "job_task[{job_tasks}] begin at act[{act_name}]".format(
                job_tasks=job_tasks, act_name=self.__class__.__name__
            )
        )

    def judge_act_tail_and_set_succeeded(self, data: DataObject, job_tasks: QuerySet) -> None:
        act_type = data.get_one_of_inputs("act_type")
        if act_type in [ActivityType.TAIL, ActivityType.HEAD_TAIL]:
            job_tasks.filter(status__in=[job_models.JobStatus.PENDING, job_models.JobStatus.RUNNING]).update(
                status=job_models.JobStatus.SUCCEEDED
            )
        logger.info(
            "job_task[{job_tasks}] succeeded at act[{act_name}]".format(
                job_tasks=job_tasks, act_name=self.__class__.__name__
            )
        )

    @classmethod
    def return_data(cls, result: bool, job_extra_data_map: Dict = None, is_finished: bool = False, **kwargs) -> Dict:
        """
        原子执行调度统一返回
        :param result: 执行结果
        :param job_extra_data_map:
        :param is_finished: 是否结束调度，对schedule有效，result=False时默认为结束，缺省时is_finished=False
        :param kwargs:
        """
        return {"result": result, "extra_data": job_extra_data_map, "is_finished": is_finished}

    def run(self, service_func, job_tasks, **kwargs):
        logger.info(
            "act[{act_name}], job_task[{job_tasks}] {func_name} begin.".format(
                act_name=self.__class__.__name__,
                job_tasks=job_tasks,
                func_name=service_func.__name__,
            )
        )
        try:
            run_return = service_func(**kwargs) or {"result": False}
            # reload job tasks
            job_tasks = job_tasks.all()
            extra_data_map = run_return.get("extra_data_map", {})
            if not run_return["result"]:
                for job_task in job_tasks:
                    if job_task.status in [job_models.JobStatus.SUCCEEDED, job_models.JobStatus.IGNORED]:
                        continue
                    job_task.set_status(job_models.JobStatus.FAILED, extra_data=extra_data_map.get(job_task.id))
            # 正常执行状态下需要更新extra_data
            elif extra_data_map:
                for job_task in job_tasks:
                    job_task.set_extra_data(extra_data=extra_data_map.get(job_task.id))
        except Exception as error:
            logger.error(traceback.format_exc())
            for job_task in job_tasks:

                # 已有状态的任务直接跳过
                if job_task.status not in [job_models.JobStatus.RUNNING, job_models.JobStatus.PENDING]:
                    continue

                extra_data = self.exception_handler(error, job_task)
                job_task.set_status(job_models.JobStatus.FAILED, extra_data=extra_data)
            return {"result": False}

        logger.info(
            "act[{act_name}], job_task[{job_tasks}] {func_name} success: {run_return}".format(
                act_name=self.__class__.__name__,
                job_tasks=job_tasks,
                func_name=service_func.__name__,
                run_return=run_return,
            )
        )
        return run_return

    def execute(self, data, parent_data):
        job_task_id = data.get_one_of_inputs("job_task_id")
        try:
            job_task = job_models.JobTask.objects.get(id=job_task_id)
        except job_models.JobTask.DoesNotExist:
            message = _("JobTask[{job_task_id}] not exist".format(job_task_id=job_task_id))
            logger.error(message)
            raise job_exceptions.JobDoseNotExistException(message)

        job_task_ids = data.get_one_of_inputs("job_task_ids")
        job_tasks = job_models.JobTask.objects.filter(id__in=job_task_ids)
        # 写入pipeline id
        job_tasks.update(pipeline_id=self.id)

        # 起始原子初始化JobTask为RUNNING
        self.judge_act_head_and_set_running(data, job_tasks)

        data.inputs.job_task = job_task
        data.inputs.job_tasks = list(job_tasks)
        execute_return = self.run(self._execute, job_tasks, data=data, parent_data=parent_data)

        if not execute_return["result"]:
            return False

        # 需要执行调度，初始化轮询总时长
        if self.need_schedule() and not self.is_schedule_finished():
            data.outputs.polling_time = 0
            return True

        # 无需执行调度并且是最后一个原子执行成功, 标识结束
        self.judge_act_tail_and_set_succeeded(data, job_tasks)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        job_task_ids = data.get_one_of_inputs("job_task_ids")
        job_tasks = job_models.JobTask.objects.filter(id__in=job_task_ids)
        schedule_return = self.run(
            self._schedule, job_tasks, data=data, parent_data=parent_data, callback_data=callback_data
        )

        # 执行错误，返回失败并结束调度
        if not schedule_return["result"]:
            self.finish_schedule()
            return False

        elif schedule_return.get("is_finished", False):
            # 调度成功结束且为最后一个原子，更新JobTask为SUCCEEDED
            self.judge_act_tail_and_set_succeeded(data, job_tasks)
            self.finish_schedule()
            return True

        # 校验轮询是否超时
        polling_time = data.get_one_of_outputs("polling_time")
        if polling_time + POLLING_INTERVAL > GlobalSettings.pipeline_polling_timeout():
            for job_task in job_tasks.filter(status=job_models.JobStatus.RUNNING):
                error = PipelineTimeoutException()
                job_task.set_status(
                    job_models.JobStatus.FAILED, extra_data={"failed_reason": error.message, "err_code": error.code}
                )
            self.finish_schedule()
            return False

        data.outputs.polling_time = polling_time + POLLING_INTERVAL
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name="job_task_id", key="job_task_id", required=True),
            Service.InputItem(name="job_task", key="job_task", required=True),
            Service.InputItem(name="job_task_ids", key="job_task_ids", required=True),
            Service.InputItem(name="act_type", key="act_type", required=False),
        ]

    def outputs_format(self):
        return []
