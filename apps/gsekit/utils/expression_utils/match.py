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
import fnmatch
from typing import List

from django.utils.translation import ugettext_lazy as _

from apps.gsekit.utils.expression_utils.parse import parse_exp2unix_shell_style
from apps.gsekit.utils.expression_utils.exceptions import ExpressionSliceException

SLICE_PATTERN = re.compile(r"\[([-+]?\d+)?\s?:\s?([-+]?\d+)?]")


def str2num_or_none(num_str: str) -> int:
    try:
        num = int(num_str)
    except ValueError:
        num = None
    return num


def execute_slice(names: List, slice_expression: str) -> List[str]:
    slice_match_list = SLICE_PATTERN.findall(slice_expression)
    if len(slice_match_list) != 1:
        return names

    try:
        begin, end = str2num_or_none(slice_match_list[0][0]), str2num_or_none(slice_match_list[0][1])
        return names[begin:end]
    except Exception as err:
        raise ExpressionSliceException(
            _("表达式[{expression}]切片解析异常：{err}".format(expression=slice_expression, err=repr(err)))
        )


def match(name: str, expression: str) -> bool:
    """Test whether NAME matches EXPRESSION.

    Patterns are Unix shell style:

    *               matches everything
    ?               matches any single character
    [seq]           matches any character in seq
    [!seq]          matches any char not in seq

    Features different from fnmatch：

    [word1, word2]  matches any word in list
    [1-1000]        matches any number in range
    """
    # 将表达式中的枚举语法转化为若干Unix shell style的模式串
    exprs_unix_shell_style = parse_exp2unix_shell_style(expression)
    # name与任一模式串匹配成功即与expression匹配成功
    for expr in exprs_unix_shell_style:
        if fnmatch.fnmatch(name, expr):
            return True
    return False


def list_match(names: List[str], expression: str) -> List[str]:
    """Return the subset of the list NAMES that match EXPRESSION."""
    exprs_unix_shell_style = parse_exp2unix_shell_style(expression)
    filter_results = []
    for expr in exprs_unix_shell_style:
        filter_results.extend(fnmatch.filter(names, expr))
    filter_results = set(filter_results)
    # 保持筛选结果相对names有序
    return [name for name in names if name in filter_results]
