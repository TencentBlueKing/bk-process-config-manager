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
from apps.gsekit import constants
from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.utils.expression_utils import parse, range2re, match, exceptions, serializers


class TestParse(MyTestCase):
    def test_parse_list2expr(self):
        # 测试去重后单元素返回元素本身
        self.assertDataStructure(
            result_data=parse.parse_list2expr(value_list=["module", "module"]), expected_data="module", value_eq=True
        )
        value_list = ["module1", "module2"]
        self.assertDataStructure(
            result_data=parse.parse_list2expr(value_list=value_list),
            expected_data="[" + ",".join([str(value) for value in set(value_list)]) + "]",
            value_eq=True,
        )

    def test_expand_list_element(self):
        self.assertDataStructure(
            result_data=parse.expand_list_element(nested_list=[["1", "2"], "3", "4", [["5"], ["6"]]]),
            expected_data=["1", "2", "3", "4", "5", "6"],
            value_eq=True,
        )

    def test_get_range_scope(self):
        range_tuple = ("1", "99")
        self.assertDataStructure(
            result_data=parse.get_range_scope(range_expression=parse.BuildInChar.HYPHEN.join(range_tuple)),
            expected_data=range_tuple,
            value_eq=True,
        )

    def test_is_range_format(self):
        self.assertTrue(parse.is_range_format(expression="1-100"))
        self.assertFalse(parse.is_range_format(expression="1-100-1009"))

    def test_is_single_alpha_range(self):
        # 规则：字符大小写相符、单字符、ascii值升序
        self.assertTrue(parse.is_single_alpha_range(range_expression="a-z"))
        self.assertTrue(parse.is_single_alpha_range(range_expression="A-Z"))

        self.assertFalse(parse.is_single_alpha_range(range_expression="z-a"))
        self.assertFalse(parse.is_single_alpha_range(range_expression="1-9"))

    def test_is_number_range(self):
        self.assertTrue(parse.is_number_range(range_expression="1-100"))
        self.assertFalse(parse.is_number_range(range_expression="9-1"))

    def test_get_match_type(self):
        # 以中括号包围的字符串为BUILD_IN_ENUM类型
        self.assertEqual(parse.get_match_type(expression="[1, 2, 3]"), parse.MatchType.BUILD_IN_ENUM)
        # 以逗号分隔的多关键字字符串为WORD_LIST类型
        self.assertEqual(parse.get_match_type(expression="1, 2, 3"), parse.MatchType.WORD_LIST)

        # 存在`-`时，除单字母枚举及整数返回枚举，其他视为WORD
        self.assertEqual(parse.get_match_type(expression="1-100"), parse.MatchType.RANGE)
        self.assertEqual(parse.get_match_type(expression="a-z"), parse.MatchType.RANGE)
        self.assertEqual(parse.get_match_type(expression="z-a"), parse.MatchType.WORD)

    def test_parse_word_list_expression(self):
        self.assertDataStructure(
            result_data=parse.parse_word_list_expression("module1, module2, 3,4"),
            expected_data=["module1", "module2", "3", "4"],
            value_eq=True,
        )

    def test_parse_range_expression(self):
        self.assertDataStructure(
            result_data=parse.parse_range_expression("a-z"), expected_data=["[a-z]"], value_eq=True
        )
        # 对于整数范围枚举，会转化为正则
        self.assertDataStructure(
            result_data=parse.parse_range_expression("1-100"),
            expected_data=["[1-9]", "[1-9][0-9]", "100"],
            value_eq=True,
        )
        self.assertRaises(exceptions.ExpressionSyntaxException, parse.parse_range_expression, range_expression="z-a")

    def test_parse_enum_expression(self):
        self.assertDataStructure(
            result_data=parse.parse_enum_expression("a-z, 1-100, 1-9"),
            expected_data=[[["[a-z]"]], [["[1-9]"], ["[1-9][0-9]"], ["100"]], [["[1-9]"]]],
            value_eq=True,
        )

    def test_parse_exp2unix_shell_style_main(self):
        self.assertDataStructure(
            result_data=parse.parse_exp2unix_shell_style_main(expression="module[1-3].proc[a-c].[1-100]"),
            expected_data=[
                "module[1-3].proc[a-c].[1-9][0-9]",
                "module[1-3].proc[a-c].100",
                "module[1-3].proc[a-c].[1-9]",
            ],
            value_eq=True,
        )
        self.assertDataStructure(
            result_data=parse.parse_exp2unix_shell_style_main(expression="[!9]"), expected_data=["[!9]"], value_eq=True
        )
        self.assertRaises(exceptions.ExpressionSyntaxException, parse.parse_exp2unix_shell_style, expression="[....")

    def test_parse_exp2unix_shell_style(self):
        # 测试结果去重
        self.assertDataStructure(
            result_data=parse.parse_exp2unix_shell_style(expression="module[1-3, 1-3].proc[a-c].[1-100]"),
            expected_data=[
                "module[1-3].proc[a-c].[1-9][0-9]",
                "module[1-3].proc[a-c].100",
                "module[1-3].proc[a-c].[1-9]",
            ],
            value_eq=True,
        )


class TestRange2Re(MyTestCase):
    def test_get_upper_range(self):
        self.assertDataStructure(result_data=range2re.get_upper_range(100), expected_data=(100, 999), value_eq=True)
        self.assertDataStructure(result_data=range2re.get_upper_range(1880), expected_data=(1880, 1899), value_eq=True)

    def test_get_lower_range(self):
        self.assertDataStructure(result_data=range2re.get_lower_range(15), expected_data=(10, 15), value_eq=True)
        self.assertDataStructure(result_data=range2re.get_lower_range(199), expected_data=(0, 199), value_eq=True)

    def test_split_range_left(self):
        self.assertDataStructure(
            result_data=range2re.split_range_left(1, 100), expected_data=[(1, 9), (10, 99)], value_eq=True
        )
        self.assertDataStructure(
            result_data=range2re.split_range_left(1, 105), expected_data=[(1, 9), (10, 99), (100, 999)], value_eq=True
        )

    def test_split_range_right(self):
        self.assertDataStructure(
            result_data=range2re.split_range_right(1, 100), expected_data=[(0, 99), (100, 100)], value_eq=True
        )
        self.assertDataStructure(
            result_data=range2re.split_range_right(1, 105), expected_data=[(0, 99), (100, 105)], value_eq=True
        )

    def test_range2re(self):
        self.assertDataStructure(
            result_data=range2re.range2re(1, 100), expected_data=["[1-9]", "[1-9][0-9]", "100"], value_eq=True
        )
        self.assertDataStructure(
            result_data=range2re.range2re(1, 105), expected_data=["[1-9]", "[1-9][0-9]", "10[0-5]"], value_eq=True
        )


class TestMatch(MyTestCase):
    def test_match(self):
        self.assertTrue(match.match("module-a.proc1.99", "module-[a-c].proc[1-10].[1-9999]"))
        self.assertFalse(match.match("module-a.proc1.99", "module-[!a].proc[1-10].[1-9999]"))

    def test_list_match(self):
        self.assertDataStructure(
            result_data=match.list_match(
                names=[
                    "module-a.proc1.10",
                    "module-b.proc2.20",
                    "module-c.proc3.30",
                    "module-d.proc4.40",
                    "module-e.proc5.50",
                ],
                expression="module-[a-d].proc[!2].[10-19, 30-39]",
            ),
            expected_data=["module-a.proc1.10", "module-c.proc3.30"],
            value_eq=True,
        )

    def test_list_match_service_name_contain_process_name(self):
        expression_a = "set{splitter}*{splitter}127.0.0.1_proc_name{splitter}127{splitter}50".format(
            splitter=constants.EXPRESSION_SPLITTER
        )
        expression_b = "set{splitter}*{splitter}127.0.0.1_proc_name{splitter}12{splitter}50".format(
            splitter=constants.EXPRESSION_SPLITTER
        )

        self.assertDataStructure(
            result_data=match.list_match(
                names=[expression_a, expression_b],
                expression="*{splitter}*{splitter}*{splitter}127{splitter}*".format(
                    splitter=constants.EXPRESSION_SPLITTER
                ),
            ),
            expected_data=[expression_a],
            value_eq=True,
        )


class TestSerializers(MyTestCase):
    def test_gen_expression(self):
        expression_scope = {
            "bk_set_env": "3",
            "bk_set_name": "set",
            "bk_module_name": "*",
            "service_instance_name": "127.0.0.1_proc_name",
            "bk_process_name": "*",
            "bk_process_id": "50",
        }
        self.assertDataStructure(
            serializers.gen_expression(expression_scope),
            "set{splitter}*{splitter}127.0.0.1_proc_name{splitter}*{splitter}50".format(
                splitter=constants.EXPRESSION_SPLITTER
            ),
            value_eq=True,
        )
