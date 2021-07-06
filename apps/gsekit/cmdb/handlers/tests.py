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

from apps.gsekit.cmdb.constants import BkSetEnv
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.utils.test_utils.tests import patch_get_request


class TestProcessHandler(TestCase):
    """
    测试进程相关的接口
    """

    BK_BIZ_ID = 2

    @patch_get_request
    def test_cache_topo_name(self):
        CMDBHandler(bk_biz_id=self.BK_BIZ_ID).cache_topo_name()

    @patch_get_request
    def test_cache_topo_tree_attr(self):
        CMDBHandler(bk_biz_id=self.BK_BIZ_ID).cache_topo_tree_attr(BkSetEnv.FORMAL)
