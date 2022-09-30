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


class PipelineBaseException(AppBaseException):
    MODULE_CODE = ErrorCode.PIPELINE_CODE
    MESSAGE = _("Pipeline模块异常")


class PipelineTimeoutException(PipelineBaseException):
    ERROR_CODE = "001"
    MESSAGE = _("执行超时")
    MESSAGE_TPL = _("执行超时，有两种异常可能：" "<div><span>1.</span> 脚本执行时间过长 </div>" "<div><span>2.</span> 脚本未正常退出 </div>")


class GseApiException(PipelineBaseException):
    ERROR_CODE = "002"
    MESSAGE = _("GSE接口错误")


class GsePriorityException(PipelineBaseException):
    ERROR_CODE = "003"
    MESSAGE = _("进程优先级提前错误")


class JobApiException(PipelineBaseException):
    ERROR_CODE = "004"
    MESSAGE = _("作业平台接口错误")


class ConfigInstanceDoseNotExistException(PipelineBaseException):
    ERROR_CODE = "005"
    MESSAGE = _("配置实例不存在")


class ConfigSnapshotDoseNotExistException(PipelineBaseException):
    ERROR_CODE = "006"
    MESSAGE = _("现网配置不存在")


class ConfigChangeException(PipelineBaseException):
    ERROR_CODE = "007"
    MESSAGE = _("现网配置异常")
