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

import os
from typing import Any

from apps.utils.string import str2bool


def get_type_env(key: str, default: Any = None, _type: type = str, exempt_empty_str: bool = False) -> Any:
    """
    获取环境变量并转为目标类型
    :param key: 变量名
    :param default: 默认值，若获取不到环境变量会默认使用该值
    :param _type: 环境变量需要转换的类型，不会转 default
    :param exempt_empty_str: 是否豁免空串
    :return:
    """
    value = os.getenv(key) or default
    if value == default:
        return value

    # 豁免空串
    if isinstance(value, str) and not value and exempt_empty_str:
        return value

    if _type == bool:
        return str2bool(value)

    try:
        value = _type(value)
    except TypeError:
        raise TypeError(f"can not convert env value -> {value} to type -> {_type}")

    return value
