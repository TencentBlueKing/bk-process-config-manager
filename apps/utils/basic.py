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
import hashlib
from datetime import datetime

from django.utils import timezone


def utc_strftime2local_strftime(
    utc_strftime: str, fmt: str = "%Y-%m-%d %H:%M:%S.%f", target_fmt: str = "%Y-%m-%d %H:%M:%S"
):
    utc_suffix = "+00:00"
    if utc_strftime.endswith(utc_suffix):
        utc_strftime = utc_strftime.replace(utc_suffix, "")
    utc_dt = datetime.strptime(utc_strftime, fmt)
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=timezone.get_current_timezone())
    return local_dt.strftime(target_fmt)


def filter_values(data: dict) -> dict:
    """
    用于过滤空值
    :param data: 存放各个映射关系的字典
    :return: 去掉None值的字典
    """

    ret = {}
    for obj in data:
        if data[obj] is not None:
            ret[obj] = data[obj]
    return ret


def suffix_slash(os_type, path):
    if os_type.lower() == "windows":
        if not path.endswith("\\"):
            path = path + "\\"
    else:
        if not path.endswith("/"):
            path = path + "/"
    return path


def md5(file_name):
    """内部实现的平台无关性计算MD5"""
    hash = hashlib.md5()
    try:
        with open(file_name, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                if not chunk:
                    break
                hash.update(chunk)
    except IOError:
        return "-1"

    return hash.hexdigest()


def distinct_dict_list(dict_list: list):
    """
    返回去重后字典列表，仅支持value为不可变对象的字典
    :param dict_list: 字典列表
    :return: 去重后的字典列表
    """
    return [dict(tupl) for tupl in set([tuple(sorted(item.items())) for item in dict_list])]
