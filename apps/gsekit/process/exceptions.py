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


class ProcessBaseException(AppBaseException):
    MODULE_CODE = ErrorCode.PROCESS_CODE
    MESSAGE = _("进程模块异常")


class ProcessDoseNotExistException(ProcessBaseException):
    ERROR_CODE = "001"
    MESSAGE = _("进程不存在")
    MESSAGE_TPL = _("进程不存在: bk_process_id[{bk_process_id}]")


class ProcessAttrIsNotConfiguredException(ProcessBaseException):
    ERROR_CODE = "002"
    MESSAGE = _("未配置该操作对应的进程属性")
    MESSAGE_TPL = _("进程【{process_name}】未配置进程属性【{process_attr}】。【注意】此任务为操作时配置的快照【无法直接重试】，请配置后新建任务进行操作")


class ProcessInstDoseNotExistException(ProcessBaseException):
    ERROR_CODE = "003"
    MESSAGE = _("进程未生成进程实例，请进行同步操作")


class GenerateProcessObjException(ProcessBaseException):
    ERROR_CODE = "004"
    MESSAGE = _("构造进程对象失败，请检查参数")


class DuplicateProcessInstException(ProcessBaseException):
    ERROR_CODE = "005"
    MESSAGE = _("进程实例重复")
    MESSAGE_TPL = _("进程实例重复: {uniq_key}，请删除或合并对应实例")


class ProcessNotMatchException(ProcessBaseException):
    ERROR_CODE = "006"
    MESSAGE = _("查询进程不匹配")
    MESSAGE_TPL = _("查询进程不匹配: {user_bk_process_id} vs {cc_bk_process_id}")
