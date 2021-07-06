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

import ast
from typing import List

from mako import parsetree
from mako.ast import PythonFragment
from mako.exceptions import MakoException
from mako.lexer import Lexer

from .exceptions import ForbiddenMakoTemplateException


def parse_template_nodes(nodes: List[parsetree.Node], node_visitor: ast.NodeVisitor):
    """
    解析mako模板节点，逐个节点解析抽象语法树并检查安全性
    :param nodes: mako模板节点列表
    :param node_visitor: 节点访问类，用于遍历AST节点
    """
    for node in nodes:
        if isinstance(node, (parsetree.Code, parsetree.Expression)):
            code = node.text
        elif isinstance(node, parsetree.ControlLine):
            if node.isend:
                continue
            code = PythonFragment(node.text).code
        elif isinstance(node, (parsetree.Text, parsetree.TextTag, parsetree.Comment)):
            continue
        else:
            raise ForbiddenMakoTemplateException("不支持[{}]节点".format(node.__class__.__name__))
        ast_node = ast.parse(code.strip(), "<unknown>", "exec")
        for _node in ast.walk(ast_node):
            node_visitor.visit(_node)
        if hasattr(node, "nodes"):
            parse_template_nodes(node.nodes, node_visitor)


def check_mako_template_safety(text: str, node_visitor: ast.NodeVisitor) -> bool:
    """
    检查mako模板是否安全，若不安全直接抛出异常，安全则返回True
    :param text: mako模板内容
    :param node_visitor: 节点访问器，用于遍历AST节点
    """
    text = clean_mako_content(text)
    try:
        lexer_template = Lexer(text).parse()
    except MakoException as mako_error:
        raise ForbiddenMakoTemplateException("mako解析失败, {err_msg}".format(err_msg=mako_error))
    parse_template_nodes(lexer_template.nodes, node_visitor)
    return True


def clean_mako_content(content):
    # 替换 制表符 为 4个空格
    content = content.replace("\t", " " * 4)
    return content
