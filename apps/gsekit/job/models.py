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
from collections import defaultdict
from typing import List, Dict

from django.conf import settings
from django.db import models
from django.db.models import QuerySet, Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import AppBaseException
from apps.gsekit.configfile.exceptions import ProcessDoseNotBindTemplate
from apps.gsekit.configfile.models import ConfigTemplateBindingRelationship, ConfigInstance
from apps.gsekit.process.models import Process

logger = logging.getLogger("app")


class JobErrCode(object):
    SUCCEEDED = 0
    PENDING = 1
    RUNNING = 2
    FAILED = 3
    IGNORED = 4
    # 其它非预期错误
    OTHER = -1

    @classmethod
    def all_err_code_msg_map(cls):
        """
        错误码由以上几个状态错误码加上 父类为 AppBaseException 的所有错误码
        """
        err_map = {
            cls.PENDING: _("等待执行"),
            cls.RUNNING: _("正在执行"),
            cls.SUCCEEDED: _("执行成功"),
            cls.FAILED: _("执行失败"),
            cls.IGNORED: _("已忽略"),
            cls.OTHER: _("其它错误"),
        }
        err_map.update(AppBaseException.get_err_code_msg_map())
        # 补充 GSE 接口细分错误码
        from apps.gsekit.pipeline_plugins.components.collections.gse import GSE_OP_ERROR_CODE_MSG_MAP

        err_map.update(GSE_OP_ERROR_CODE_MSG_MAP)
        return err_map


class JobStatus(object):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    IGNORED = "ignored"

    @classmethod
    def get_status_err_code(cls, status: str):
        status_err_code_map = {
            cls.PENDING: JobErrCode.PENDING,
            cls.RUNNING: JobErrCode.RUNNING,
            cls.SUCCEEDED: JobErrCode.SUCCEEDED,
            cls.FAILED: JobErrCode.FAILED,
            cls.IGNORED: JobErrCode.IGNORED,
        }
        # 不存在状态对应错误码的则认为是失败
        return status_err_code_map.get(status, JobErrCode.OTHER)


JOB_STATUS_CHOICES = (
    (JobStatus.PENDING, _("等待执行")),
    (JobStatus.RUNNING, _("正在执行")),
    (JobStatus.SUCCEEDED, _("执行成功")),
    (JobStatus.FAILED, _("执行失败")),
    (JobStatus.IGNORED, _("已忽略")),
)


class Job(models.Model):
    class JobObject(object):
        CONFIGFILE = "configfile"
        PROCESS = "process"

    JOB_OBJECT_CHOICES = (
        (JobObject.CONFIGFILE, _("配置文件")),
        (JobObject.PROCESS, _("进程")),
    )

    class JobAction(object):
        GENERATE = "generate"
        RELEASE = "release"
        START = "start"
        STOP = "stop"
        RESTART = "restart"
        RELOAD = "reload"
        FORCE_STOP = "force_stop"
        SET_AUTO = "set_auto"
        UNSET_AUTO = "unset_auto"

    JOB_ACTION_CHOICES = (
        (JobAction.GENERATE, _("生成")),
        (JobAction.RELEASE, _("下发")),
        (JobAction.START, _("启动")),
        (JobAction.STOP, _("停止")),
        (JobAction.RESTART, _("重启")),
        (JobAction.RELOAD, _("重载")),
        (JobAction.FORCE_STOP, _("强制停止")),
        (JobAction.SET_AUTO, _("托管")),
        (JobAction.UNSET_AUTO, _("取消托管")),
    )

    bk_biz_id = models.IntegerField(_("业务ID"), db_index=True)
    expression = models.TextField(_("实例表达式"), null=True)
    scope = models.JSONField(_("范围"))
    expression_scope = models.JSONField(_("表达式范围"), default=dict)
    job_object = models.CharField(_("任务对象"), max_length=16, db_index=True, choices=JOB_OBJECT_CHOICES)
    job_action = models.CharField(_("动作"), max_length=16, db_index=True, choices=JOB_ACTION_CHOICES)
    status = models.CharField(
        _("任务状态"), max_length=16, db_index=True, choices=JOB_STATUS_CHOICES, default=JobStatus.PENDING
    )
    created_by = models.CharField(_("执行账户"), max_length=64, db_index=True)
    is_ready = models.BooleanField(_("是否已准备(子任务是否全部创建完成)"), default=False)
    start_time = models.DateTimeField(_("开始时间"), auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(_("结束时间"), null=True)
    pipeline_id = models.CharField(_("PIPELINE ID"), max_length=33, db_index=True)
    extra_data = models.JSONField(_("额外数据"), default=dict)

    bk_app_code = models.CharField(_("蓝鲸应用ID"), max_length=32, default=settings.APP_CODE)

    def set_pipeline_id(self, pipeline_id: str):
        """设置任务的pipeline id"""
        self.pipeline_id = pipeline_id
        self.is_ready = True
        self.status = JobStatus.RUNNING
        self.save(update_fields=["pipeline_id", "is_ready", "status"])

    class Meta:
        ordering = ("-id",)
        verbose_name = _("任务历史")
        verbose_name_plural = _("任务历史")


class JobTask(models.Model):
    job_id = models.IntegerField(_("任务ID"), db_index=True)
    bk_process_id = models.IntegerField(_("进程ID"), db_index=True)
    status = models.CharField(
        _("任务状态"), max_length=16, db_index=True, choices=JOB_STATUS_CHOICES, default=JobStatus.PENDING
    )
    err_code = models.IntegerField(_("错误码"), db_index=True, default=JobErrCode.PENDING)
    start_time = models.DateTimeField(_("开始时间"), auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(_("结束时间"), null=True)
    pipeline_id = models.CharField(_("PIPELINE ID"), max_length=33, db_index=True)
    extra_data = models.JSONField(_("额外数据"), default=dict)

    def set_status(self, status, extra_data=None):
        if extra_data is None:
            extra_data = {}
        self.err_code = JobStatus.get_status_err_code(status)
        if status == JobStatus.FAILED:
            logger.exception(extra_data)
            # 优先取已设置的错误码
            self.err_code = extra_data.get("err_code") or self.extra_data.get("err_code") or self.err_code

        self.status = status
        if status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            self.end_time = timezone.now()

        if extra_data:
            if "retryable" not in extra_data:
                extra_data["retryable"] = True
            # 把错误码单独存储，便于分类检索，已忽略的合成一个错误
            if extra_data.get("err_code") and status != JobStatus.IGNORED:
                self.err_code = extra_data.get("err_code")
            self.extra_data.update(extra_data)

        self.save()

    def set_extra_data(self, extra_data):
        if "retryable" not in extra_data:
            extra_data["retryable"] = True
        self.extra_data.update(extra_data)
        self.save(update_fields=["extra_data"])

    def set_pipeline_id(self, pipeline_id: str):
        """设置任务的pipeline id，注意批量设置时需使用 with transaction.atomic()"""
        self.pipeline_id = pipeline_id
        self.save(update_fields=["pipeline_id"])

    def get_job_task_config_template_ids(self) -> List[int]:
        """查询任务绑定的配置模板"""
        config_template_ids = self.extra_data.get("config_template_ids", [])

        if not config_template_ids:
            config_template_ids = self.get_process_binding_config_template_ids()
        return config_template_ids

    def get_job_task_config_instance_ids(self):

        # 优先取前面原子缓存的config_instances
        config_instance_ids = [config_inst["id"] for config_inst in self.extra_data.get("config_instances", [])]

        if not config_instance_ids:
            config_template_ids = self.get_job_task_config_template_ids()
            config_instance_ids = ConfigInstance.objects.filter(
                config_template_id__in=config_template_ids,
                bk_process_id=self.bk_process_id,
                inst_id=self.extra_data["inst_id"],
                is_latest=True,
            ).values_list("id", flat=True)
            if not config_instance_ids:
                extra_data = {
                    "failed_reason": str(ProcessDoseNotBindTemplate().message),
                    "err_code": ProcessDoseNotBindTemplate().code,
                }
                self.set_status(JobStatus.FAILED, extra_data=extra_data)
        return list(set(config_instance_ids))

    def get_process_binding_config_template_ids(self):
        process_info = self.extra_data["process_info"]
        bk_process_id = process_info["process"]["bk_process_id"]
        process_template_id = process_info["process_template"].get("id") or 0
        return ConfigTemplateBindingRelationship.get_process_binding_config_template_ids(
            bk_process_id, process_template_id
        )

    @classmethod
    def get_job_tasks_config_template_ids_map(cls, job_tasks: QuerySet) -> Dict:
        bk_process_ids = []
        process_template_ids = []
        for job_task in job_tasks:
            process_template_id = job_task.extra_data["process_info"]["process_template"].get("id")
            if process_template_id:
                process_template_ids.append(process_template_id)
            else:
                bk_process_ids.append(job_task.extra_data["process_info"]["process"]["bk_process_id"])

        relations = ConfigTemplateBindingRelationship.objects.filter(
            Q(process_object_type=Process.ProcessObjectType.INSTANCE, process_object_id__in=bk_process_ids)
            | Q(process_object_type=Process.ProcessObjectType.TEMPLATE, process_object_id__in=process_template_ids)
        )
        job_task_config_template_ids_map = defaultdict(list)
        for job_task in job_tasks:
            for relation in relations:
                process_template_id = job_task.extra_data["process_info"]["process_template"].get("id")
                bk_process_id = job_task.extra_data["process_info"]["process"]["bk_process_id"]

                if (
                    relation.process_object_type == Process.ProcessObjectType.TEMPLATE
                    and process_template_id == relation.process_object_id
                ) or (
                    relation.process_object_type == Process.ProcessObjectType.INSTANCE
                    and bk_process_id == relation.process_object_id
                ):
                    job_task_config_template_ids_map[job_task.id].append(relation.config_template_id)

        return job_task_config_template_ids_map

    class Meta:
        verbose_name = _("任务详情")
        verbose_name_plural = _("任务详情")


class JobProcInstStatusStatistics(models.Model):
    job_id = models.IntegerField(_("任务ID"), db_index=True)
    bk_process_id = models.IntegerField(_("进程ID"), db_index=True)
    proc_inst_total_num = models.IntegerField(_("进程实例数量"))
    proc_inst_terminated_num = models.IntegerField(_("进程终止数量"), default=0)
    proc_inst_running_num = models.IntegerField(_("进程运行数量"), default=0)
    proc_inst_auto_num = models.IntegerField(_("进程托管数量"), default=0)
    proc_inst_noauto_num = models.IntegerField(_("进程未托管数量"), default=0)

    class Meta:
        verbose_name = _("任务进程实例状态统计")
        verbose_name_plural = _("任务进程实例状态统计")
