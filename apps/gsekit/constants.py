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
import re
from django.utils.translation import ugettext_lazy as _
from enum import Enum


# 缓存过期时间
class CacheExpire(object):
    MIN = 60
    HOUR = 60 * 60
    DAY = 60 * 60 * 24

    # 频繁更新
    FREQUENT_UPDATE = 5 * MIN
    NEVER = None


JWT_CACHE_KEY = "APIGW_PUBLIC_KEY"

RE_WHITESPACE = re.compile("[\t\n\x0b\x0c\r ]")

PIPELINE_BATCH_SIZE = 200
ORM_BATCH_SIZE = 200

# 表达式分隔符
EXPRESSION_SPLITTER = "<-GSEKIT->"

# 任务执行系统类型,与作业平台语言执行参数一致
JOB_TASK_OS_TYPE = {"linux": 1, "win": 2}


class BkJobStatus(object):
    """
    作业步骤状态码:
    1.等待执行; 2.正在执行; 3.执行成功; 4.执行失败; 5.跳过; 6.忽略错误;
    7.等待用户; 8.强制终止; 9.状态异常; 10.强制终止中; 11.强制终止成功,13.确认终止
    这里只用到其中三个状态码
    """

    PENDING = 1
    RUNNING = 2
    SUCCEEDED = 3
    FAILED = 4


class BkJobErrorCode(object):
    NOT_RUNNING = -1

    BK_JOB_ERROR_CODE_MAP = {
        NOT_RUNNING: _("该IP未执行作业，请联系管理员排查问题"),
        1: _("Agent异常"),
        3: _("上次已成功"),
        5: _("等待执行"),
        7: _("正在执行"),
        9: _("执行成功"),
        11: _("任务失败"),
        12: _("任务下发失败"),
        13: _("任务超时"),
        15: _("任务日志错误"),
        101: _("脚本执行失败"),
        102: _("脚本执行超时"),
        103: _("脚本执行被终止"),
        104: _("脚本返回码非零"),
        117: _("Agent异常"),
        202: _("文件传输失败"),
        203: _("源文件不存在"),
        310: _("Agent异常"),
        311: _("用户名不存在"),
        320: _("文件获取失败"),
        321: _("文件超出限制"),
        329: _("文件传输错误"),
        399: _("任务执行出错"),
    }


class BkJobIpStatus(object):
    NOT_RUNNING = -1
    SUCCEEDED = 9

    BK_JOB_IP_STATUS_MAP = {
        NOT_RUNNING: _("该IP未执行作业，请联系管理员排查问题"),
        1: _("Agent异常"),
        5: _("等待执行"),
        7: _("正在执行"),
        SUCCEEDED: _("执行成功"),
        11: _("执行失败"),
        12: _("任务下发失败"),
        403: _("任务强制终止成功"),
        404: _("任务强制终止失败"),
    }


class TaskGranularity(object):
    BIZ = "BIZ"
    SET = "SET"
    MODULE = "MODULE"
    HOST = "HOST"

    TASK_GRANULARITY_NODE_KEY_FIELD_MAP = {
        BIZ: "bk_biz_id",
        SET: "bk_set_id",
        MODULE: "bk_module_id",
        HOST: "bk_host_id",
    }

    TASK_GRANULARITY_CHOICES = [BIZ, SET, MODULE, HOST]


class BkappRunEnvType(Enum):
    """APP运行环境"""

    CE = "ce"
    EE = "ee"


class TimeUnit:
    SECOND = 1
    MINUTE = SECOND * 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
