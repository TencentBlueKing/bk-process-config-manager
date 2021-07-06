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
import datetime
import time

import pytz
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

# 默认时间戳乘数
DEFAULT_MULTIPLICATOR = 1

SHOW_TZ = False
FMT_LENGTH = None if SHOW_TZ else 16


def timeformat_to_timestamp(timeformat, time_multiplicator=DEFAULT_MULTIPLICATOR):
    """
    时间格式 -> 时间戳
    :param timeformat:
    :param time_multiplicator: 时间倍数
    :return:
    """
    if not timeformat:
        return None
    if type(timeformat) in [str]:
        # 时间字符串转时间戳
        timestamp = int(time.mktime(time.strptime(timeformat, "%Y-%m-%d %H:%M:%S")))
    else:
        # type(timeformat) is datetime
        # datetime 转时间戳
        timestamp = int(timeformat.strftime("%s"))
    return int(timestamp * time_multiplicator)


def datetime_to_timestamp(datetime):
    time_str = str(datetime.astimezone(pytz.timezone(get_dataapi_tz())))[:19]
    # time_str = datetime.strftime("%Y-%m-%d %H:%M:%S")
    return timeformat_to_timestamp(time_str)


def timestamp_to_datetime(from_timestamp, time_multiplicator=DEFAULT_MULTIPLICATOR):
    """
    timestamp -> aware datetime
    """
    utc_tz = pytz.timezone("UTC")
    utc_dt = utc_tz.localize(datetime.datetime.utcfromtimestamp(int(from_timestamp) / time_multiplicator))
    return utc_dt


def format_datetime(o_datetime):
    """
    格式化日志对象展示格式

    @param {datetime} o_dateitime
    """
    return o_datetime.strftime("%Y-%m-%d %H:%M:%S%z")


def get_dataapi_tz():
    """
    获取当前dataapi系统的时区
    """
    return settings.DATAAPI_TIME_ZONE


def get_delta_time():
    """
    获取app时间与dataapi时间差
    """
    sys_offset = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime("%z")
    dataapi_offset = datetime.datetime.now(pytz.timezone(settings.DATAAPI_TIME_ZONE)).strftime("%z")
    return (int(dataapi_offset) - int(sys_offset)) / 100 * 3600


def get_pizza_timestamp():
    return time.time() + get_delta_time()


def get_active_timezone_offset():
    """
    获取当前用户时区偏移量
    """
    time_zone = str(timezone.get_current_timezone())
    offset = datetime.datetime.now(pytz.timezone(time_zone)).strftime("%z")
    return offset


def strftime_local(aware_time, fmt="%Y-%m-%d %H:%M:%S"):
    """
    格式化aware_time为本地时间
    """
    if not aware_time:
        # 当时间字段允许为NULL时，直接返回None
        return None
    if timezone.is_aware(aware_time):
        # translate to time in local timezone
        aware_time = timezone.localtime(aware_time)
    return aware_time.strftime(fmt)


def localtime_to_timezone(d_time, to_zone):
    """
    将时间字符串根据源时区转为用户时区
    @param {datetime} d_time 时间
    @param {String} to_zone 时区
    """
    zone = pytz.timezone(to_zone)
    return d_time.astimezone(zone)


class SelfDRFDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if not value:
            return None
        return strftime_local(value)


def time_to_string(_time):
    """
    传入一个标准时间，返回其字符串形式
    :param _time: 时间
    :return: 时间字符串
    """
    return _time.strftime("%Y-%m-%d %H:%M:%S")


def date_to_string(_data):
    """
    传入一个标准日期，返回其字符串形式
    :param _data: 日期
    :return: 日期字符串
    """
    return _data.strftime("%Y-%m-%d")


def string_to_time(t_str):
    """
    传入一个字符串，返回其标准时间格式
    :param t_str: 时间字符串
    :return: 时间
    """
    return datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")


def string_to_date(d_str):
    """
    传入一个字符串，返回其标准日期格式
    :param d_str: 日期字符串
    :return: 日期
    """
    return datetime.datetime.strptime(d_str, "%Y-%m-%d")
