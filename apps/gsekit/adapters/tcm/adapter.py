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
from apps.gsekit.configfile.models import ConfigTemplate
from ..base.adapter import BaseChannelAdapters


class TcmAdapter(BaseChannelAdapters):
    """TCM适配器"""

    def do_preparation(self, bk_biz_id: int):
        self.create_app()
        self.generate_host_xml()

    def post_create_config_template(self, config_template: ConfigTemplate):
        pass

    def post_update_config_template(self, config_template: ConfigTemplate):
        pass

    def create_app(self):
        """创建TCP业务"""

    def generate_host_xml(self):
        """创建TCM 主机 XML"""

    def generate_proc_xml(self):
        """创建TCM 进程 XML"""

    def generate_proc_deploy_xml(self):
        """创建TCM 进程部署 XML"""

    def generate_bus_relation_xml(self):
        """创建TCM 进程间通信 XML"""
