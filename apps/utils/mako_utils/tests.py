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

from django.test import TestCase

from .exceptions import ForbiddenMakoTemplateException
from .visitor import MakoNodeVisitor
from .checker import check_mako_template_safety


class TestMakoUtils(TestCase):
    def test_mako(self, hack_mako: str = "<% import os%>", expect_safe: bool = False):
        print(hack_mako)
        if expect_safe:
            assert check_mako_template_safety(hack_mako, MakoNodeVisitor())
        else:
            with self.assertRaises(ForbiddenMakoTemplateException):
                check_mako_template_safety(hack_mako, MakoNodeVisitor())

    def test_private_bases(self):
        self.test_mako(
            '${"".__class__.__bases__[0].__subclasses__()[91].__init__.__globals__["__builtins__"]'
            '["eval"]("__import__(\\"os\\").system(\\"whoami\\")")}'
        )

    def test_private_mro(self):
        self.test_mako('${"".__class__.__mro__[-1].__subclasses__()[127].__init__.__globals__["system"]("whoami")}')

    def test_getattr(self):
        self.test_mako('${getattr("", dir(0)[0][0] + dir(0)[0][0] + "class" + dir(0)[0][0]+ dir(0)[0][0])}')

    def test_import(self):
        self.test_mako('${__import__("os").system("whoami")}')

    def test_only_import(self):
        self.test_mako("<% import os %>")

    def test_import_2(self):
        self.test_mako("${import os}")

    def test_builtin_open(self):
        self.test_mako("""<% with open("/tmp/hack", "w+") as f:f.write("hack")%>""")

    def test_builtin_eval(self):
        self.test_mako("""<% eval("__import__('os').system('whoami')") %>""")

    def test_sys(self):
        self.test_mako("""<% import sys %>${sys.modules['os'].system("whoami")}""")

    def test_def_tag(self):
        self.test_mako("""<%def name="hack(a=__import__('os').system('whoami'))"></%def>""")

    def test_gi_frame(self):
        self.test_mako("""<% g=(a for a in ()) %>${g.gi_frame.f_builtins["__import__"]("os").system("whoami")}""")

    def test_json_codecs(self):
        self.test_mako("""<% import json %> ${json.codecs.builtins.exec('import os; os.system("whoami")')}""")

    def test_syntax_error(self):
        self.test_mako("""${<% with open("/tmp/hack", "w+") as f:f.write("hack")%>}""")

    def test_mako_context(self):
        self.test_mako(
            """<% import datetime; i = context["globals"]()["__builtins__"]["__import__"];
         g=context["globals"]()["__builtins__"]["getattr"]; o_s=i("os"); %> ${g(o_s, "environ")}"""
        )

    def test_mako_self(self):
        self.test_mako("""<% self.module.runtime.compat %>""")

    def test_mako_compat(self):
        self.test_mako(
            """<% compat = self.module.runtime.compat; octal = compat.octal;%>
             ${octal(\"0 or sys.modules['subprocess'].check_output(['uname', '-a'])\")}"""
        )

    def test_mako_capture(self):
        self.test_mako(
            """<% ctx = capture.args[0]; ret = ctx[\"eval\"]('exec(\"import subprocess as sub_process\")
             or sub_process.check_output([\"ps\", \"-ef\"])');  %> ${ret}"""
        )

    def test_re(self):
        self.test_mako(
            """
            <%
            import re
            re.compile("")
            re.findall("")
            re.match("", "")
            re.split("", "")
            %>
            """,
            expect_safe=True,
        )

    def test_json(self):
        self.test_mako(
            """
            <%
            import json
            json.loads("[]")
            json.dumps([])
            %>
            """,
            expect_safe=True,
        )
