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


class BscpErrorCode(object):
    BSCP_OBJ_ALREADY_EXIST = 4003005
    PROC_ATTR_ALREADY_EXIST = 4004003
    CFG_DOSE_NOT_EXIST = 4004007


class BscpBaseException(AppBaseException):
    MODULE_CODE = ErrorCode.BSCP
    MESSAGE = _("BSCP块异常")


class BscpConfigDoseNotExistException(BscpBaseException):
    ERROR_CODE = "001"
    MESSAGE = _("BSCP配置不存在")


class ReleaseConfigException(BscpBaseException):
    ERROR_CODE = "002"
    MESSAGE = _("BSCP下发配置失败")
    MESSAGE_TPL = _("BSCP下发配置失败, error_msg: [{error_msg}]")


class BscpConfigCommitException(BscpBaseException):
    ERROR_CODE = "003"
    MESSAGE = _("BSCP配置提交异常")


class BscpCreateProcAttrException(BscpBaseException):
    ERROR_CODE = "004"
    MESSAGE = _("BSCP创建进程属性异常")


class BscpAgentOfflineException(BscpBaseException):
    ERROR_CODE = "005"
    MESSAGE = _("BSCP AGENT已离线，请尝试重装AGENT或联系管理员处理")
