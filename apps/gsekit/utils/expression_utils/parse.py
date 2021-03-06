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
from typing import List, Tuple, Union

from django.utils.translation import ugettext_lazy as _

from common.log import logger
from apps.gsekit.utils.expression_utils.range2re import range2re
from apps.gsekit.utils.expression_utils.exceptions import (
    ExpressionSyntaxException,
    ExpressionBaseException,
    ExpressionParseException,
)


class MatchType:
    WORD = 0
    RANGE = 1
    WORD_LIST = 2
    BUILD_IN_ENUM = 3
    BUILD_IN_EXCLUDE = 4


class BuildInChar:
    COMMA = ","
    HYPHEN = "-"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    # 通配符
    ASTERISK = "*"
    EXCLAMATION = "!"


def parse_list2expr(value_list: List) -> str:
    deduplicated = set(value_list)
    if len(deduplicated) == 1:
        return str(list(deduplicated)[0])
    return "[" + ",".join([str(value) for value in compressed_list(deduplicated)]) + "]"


def compressed_list(value_list: iter) -> List[str]:
    deduplicated = set([str(value) for value in value_list])
    number_values = sorted([value for value in deduplicated if value.isdecimal()])
    no_number_values = deduplicated - set(number_values)

    left, right = 0, 0
    str_range_set = set()
    while right < len(number_values) - 1:
        if int(number_values[right]) + 1 == int(number_values[right + 1]):
            right = right + 1
        else:
            str_range_set.add(number_values[left] if left == right else f"{number_values[left]}-{number_values[right]}")
            left, right = right + 1, right + 1
    if len(number_values) != 0:
        str_range_set.add(number_values[left] if left == right else f"{number_values[left]}-{number_values[right]}")
    return list(str_range_set | no_number_values)


def expand_list_element(nested_list: Union[List[List], str]) -> List[str]:
    """将嵌套数组元素全部展开为一维数组"""
    expand_str_list = []
    for child in nested_list:
        if isinstance(child, list):
            expand_str_list.extend(expand_list_element(child))
        else:
            expand_str_list.append(child)
    if isinstance(nested_list, str):
        return [nested_list]
    return expand_str_list


def get_range_scope(range_expression: str) -> Tuple[str, str]:
    range_list = range_expression.split(BuildInChar.HYPHEN)
    return range_list[0], range_list[1]


def is_range_format(expression: str) -> bool:
    """判断表达式是否为范围表达式"""
    range_list = expression.split(BuildInChar.HYPHEN)
    if len(range_list) != 2:
        return False
    return True


def is_single_alpha_range(range_expression: str) -> bool:
    """判断表达式是否为单字符范围"""
    begin, end = get_range_scope(range_expression)
    if begin.islower() != end.islower():
        return False
    if len(begin) == 1 and len(end) == 1 and begin.isalpha() and end.isalpha() and ord(begin) < ord(end):
        return True
    return False


def is_number_range(range_expression: str) -> bool:
    """判断表达式是否为数字范围"""
    begin, end = get_range_scope(range_expression)
    if begin.isdecimal() and end.isdecimal() and int(begin) < int(end):
        return True
    return False


def get_match_type(expression: str) -> int:
    """获取表达式类型"""
    if expression.startswith(BuildInChar.LEFT_BRACKET) and expression.endswith(BuildInChar.RIGHT_BRACKET):
        return MatchType.BUILD_IN_ENUM
    elif expression.startswith(BuildInChar.EXCLAMATION):
        return MatchType.BUILD_IN_EXCLUDE
    elif BuildInChar.COMMA in expression:
        return MatchType.WORD_LIST
    elif BuildInChar.HYPHEN in expression:
        if is_range_format(expression):
            if is_single_alpha_range(expression) or is_number_range(expression):
                return MatchType.RANGE
        return MatchType.WORD
    else:
        return MatchType.WORD


def parse_enum_expression(enum_expression: str) -> List:
    """解析枚举表达式，获取枚举值"""
    match_status_func = {
        MatchType.WORD: lambda x: [x],
        MatchType.BUILD_IN_ENUM: lambda x: [x],
        MatchType.BUILD_IN_EXCLUDE: lambda x: f"[{x}]",
        MatchType.WORD_LIST: parse_word_list_expression,
        MatchType.RANGE: parse_range_expression,
    }
    match_type = get_match_type(enum_expression)
    sub_expressions = match_status_func[match_type](enum_expression)
    if match_type in [MatchType.WORD, MatchType.BUILD_IN_ENUM, MatchType.BUILD_IN_EXCLUDE]:
        return match_status_func[match_type](enum_expression)
    return [parse_enum_expression(sub_expression) for sub_expression in sub_expressions]


def parse_word_list_expression(word_list_expression: str) -> List[str]:
    elements = word_list_expression.split(BuildInChar.COMMA)
    return [element.strip() for element in elements]


def parse_range_expression(range_expression: str) -> List[str]:
    if is_single_alpha_range(range_expression):
        return [f"[{range_expression}]"]
    if is_number_range(range_expression):
        begin, end = get_range_scope(range_expression)
        return range2re(int(begin), int(end))
    raise ExpressionSyntaxException(_("范围表达式解析错误: {range_expression}").format(range_expression=range_expression))


def parse_exp2unix_shell_style_main(expression: str) -> List[str]:
    """将表达式解析为若干unix shell风格的匹配式"""
    expressions_parsed = [""]
    last_enum_end = -1
    enum_begin = expression.find(BuildInChar.LEFT_BRACKET)
    # 预处理枚举[...]
    while enum_begin != -1:
        enum_end = expression.find(BuildInChar.RIGHT_BRACKET, enum_begin)
        if enum_end == -1:
            raise ExpressionSyntaxException(
                _("枚举表达式缺少`]`: {error_expression}").format(error_expression=expression[enum_begin:])
            )
        enum_expression = expression[enum_begin : enum_end + 1]
        # 展开枚举值
        enum_value_list = expand_list_element(parse_enum_expression(enum_expression[1:-1]))
        # 枚举值添加到前缀末尾
        sub_expressions_parsed = [
            f"{expression[last_enum_end + 1: enum_begin]}{enum_value}" for enum_value in enum_value_list
        ]
        # 与现有解析表达式叠加
        expressions_parsed = [
            f"{exp_prefix}{sub_exp}" for exp_prefix in expressions_parsed for sub_exp in sub_expressions_parsed
        ]

        last_enum_end = enum_end
        enum_begin = expression.find(BuildInChar.LEFT_BRACKET, enum_end)
    expressions_parsed = [f"{exp_prefix}{expression[last_enum_end + 1:]}" for exp_prefix in expressions_parsed]
    return expressions_parsed


def parse_exp2unix_shell_style(expression: str) -> List[str]:
    try:
        return list(set(parse_exp2unix_shell_style_main(expression)))
    except ExpressionBaseException:
        raise
    except Exception as err:
        msg = _("表达式[{expression}]解析异常：{err}".format(expression=expression, err=repr(err)))
        logger.error(msg)
        raise ExpressionParseException(msg) from err
