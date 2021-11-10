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
from typing import List

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.gsekit.process.models import Process


class BaseSolutionMaker(object):
    """解决方案制作器"""

    ACTION = ""
    LINK_HIGHLIGHT = ""

    def __init__(self, action: str = None, link_highlight: str = None):
        if action is None:
            action = self.ACTION
        self.action = action

        if link_highlight is None:
            link_highlight = self.LINK_HIGHLIGHT
        self.link_highlight = link_highlight

    def generate_html(self, link: str, site_url: str = "") -> str:
        """生成可点击的html"""
        return _(
            '<span>点击跳转到</span><a href="{link}" target="_blank">[{highlight}]</a>，' "请您进行 <b>[{action}]</b> 操作"
        ).format(highlight=self.link_highlight, link=f"{site_url}/{link}", action=self.action)

    def make(self) -> List:
        """得出解决方案"""
        raise NotImplementedError


class SyncCmdbSvcTmplSolutionMakerMaker(BaseSolutionMaker):

    ACTION = _("锁定进程模板信息并同步")
    LINK_HIGHLIGHT = _("配置平台-服务模板")

    def __init__(self, bk_biz_id: int, process_template_id: int):
        self.bk_biz_id = bk_biz_id
        self.process_template_id = process_template_id
        super().__init__()

    def make(self) -> List:
        link = f"/#/business/{self.bk_biz_id}/service/"
        process = Process.objects.filter(process_template_id=self.process_template_id).first()
        if process:
            link += f"operational/template/{process.service_template_id}?_f=1&tab=config"
        else:
            link += "template"
        return [{"html": self.generate_html(site_url=settings.BK_CC_HOST, link=link)}]


class SyncProcessSolutionMaker(BaseSolutionMaker):
    ACTION = _("同步CMDB进程配置")
    LINK_HIGHLIGHT = _("进程状态")

    def __init__(self):
        super().__init__()

    def make(self):
        return [{"html": self.generate_html(link="process-manage/status")}]


class BindTemplateSolutionMaker(BaseSolutionMaker):
    def __init__(self, service_instance_id: int, process_template_id: int, bk_process_id: int):
        self.service_instance_id = service_instance_id
        self.process_template_id = process_template_id
        self.bk_process_id = bk_process_id
        super().__init__()

    def make(self):
        return (
            EditProcessSolutionMaker(
                service_instance_id=self.service_instance_id,
                process_template_id=self.process_template_id,
                bk_process_id=self.bk_process_id,
            ).make()
            + EditTemplateSolutionMaker().make()
        )


class EditProcessSolutionMaker(BaseSolutionMaker):
    ACTION = _("配置文件")
    LINK_HIGHLIGHT = _("进程属性")

    def __init__(self, service_instance_id: int, process_template_id: int, bk_process_id: int, action: str = None):
        self.service_instance_id = service_instance_id
        self.process_template_id = process_template_id
        self.bk_process_id = bk_process_id
        super().__init__(action=action)

    def make(self):
        link = "process-attr"
        if self.process_template_id:
            process = Process.objects.filter(process_template_id=self.process_template_id).first()
            if process:
                link = f"process-attr/template?template={process.service_template_id}"
        return [{"html": self.generate_html(link=link)}]


class EditTemplateSolutionMaker(BaseSolutionMaker):
    ACTION = _("关联进程")
    LINK_HIGHLIGHT = _("配置文件")

    def __init__(self):
        super().__init__()

    def make(self):
        return [{"html": self.generate_html(link="config-file/template/")}]
