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
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import ErrorCode, AppBaseException


class JobBaseException(AppBaseException):
    MODULE_CODE = ErrorCode.JOB_CODE
    MESSAGE = _("任务模块异常")


class NotSupportedJobObjectException(JobBaseException):
    ERROR_CODE = "001"
    MESSAGE = _("不支持的任务对象")
    MESSAGE_TPL = _("不支持的任务对象: [{job_object}]")


class NotSupportedJobActionException(JobBaseException):
    ERROR_CODE = "002"
    MESSAGE = _("不支持的任务动作")
    MESSAGE_TPL = _("不支持的任务动作: [{job_action}]")


class JobTaskNotReadyException(JobBaseException):
    ERROR_CODE = "003"
    MESSAGE = _("任务未准备好，请稍后再试")


class JobActionManagerNotCompletedException(JobBaseException):
    ERROR_CODE = "004"
    MESSAGE = _("任务动作管理器未定义")


class JobDoseNotExistException(JobBaseException):
    ERROR_CODE = "005"
    MESSAGE = _("作业不存在")


class JobTaskNotExistException(JobBaseException):
    ERROR_CODE = "006"
    MESSAGE = _("任务不存在")


class JobEmptyTaskException(JobBaseException):
    ERROR_CODE = "007"
    MESSAGE = _("启动任务数为0，请确认是否已同步进程或绑定配置文件")


class JobRetryException(JobBaseException):
    ERROR_CODE = "008"
    MESSAGE = _("任务重试失败")
    MESSAGE_TPL = _("任务重试失败: [{message}]")
