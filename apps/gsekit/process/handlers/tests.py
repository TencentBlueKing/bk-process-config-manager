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
import random
from typing import List, Dict

from mock import patch

from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.process import models as proc_models
from apps.gsekit.cmdb.views.tests import CmdbMockClient
from apps.gsekit.cmdb import mock_data as cmdb_mock_data
from apps.gsekit.process.handlers.process import ProcessHandler


class TestProcessHandler(MyTestCase):
    cmdb_mock_client = CmdbMockClient.get_cmdb_mock_client_inst()
    CC_API_MOCK_PATH = "apps.gsekit.process.handlers.process.CCApi"

    def setUp(self) -> None:
        super(TestProcessHandler, self).setUp()
        patch(self.CC_API_MOCK_PATH, self.cmdb_mock_client).start()

    @staticmethod
    def cal_proc_inst_num(proc_related_infos: List[Dict]) -> int:
        inst_total_num = 0
        for proc_related_info in proc_related_infos:
            inst_total_num += proc_related_info["process"]["proc_num"]
        return inst_total_num

    def test_sync_biz_process(self):
        proc_models.Process.objects.all().delete()
        ProcessHandler(bk_biz_id=self.bk_biz_id).sync_biz_process()
        all_process_ids = list(proc_models.Process.objects.all().values_list("bk_process_id", flat=True))
        self.assertEqual(len(all_process_ids), len(cmdb_mock_data.LIST_PROCESS_RELATED_INFO))
        self.assertEqual(
            proc_models.ProcessInst.objects.all().count(),
            self.cal_proc_inst_num(cmdb_mock_data.LIST_PROCESS_RELATED_INFO),
        )

        # 随机删除一些数据，验证同步鲁棒性
        random.shuffle(all_process_ids)

        del_proc_ids = all_process_ids[0 : random.randint(1, len(all_process_ids))]
        proc_models.Process.objects.filter(bk_process_id__in=del_proc_ids).delete()
        proc_models.ProcessInst.objects.filter(bk_process_id__in=del_proc_ids).delete()

        ProcessHandler(bk_biz_id=self.bk_biz_id).sync_biz_process()
        self.assertEqual(proc_models.Process.objects.all().count(), len(cmdb_mock_data.LIST_PROCESS_RELATED_INFO))
        self.assertEqual(
            proc_models.ProcessInst.objects.all().count(),
            self.cal_proc_inst_num(cmdb_mock_data.LIST_PROCESS_RELATED_INFO),
        )
