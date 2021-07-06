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
from mock import patch

from apps.utils.test_utils import tools
from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.cmdb.views.tests import CmdbMockClient
from apps.gsekit.process import models as process_models
from apps.gsekit.process.views.process import ProcessViews
from apps.gsekit.process.handlers.process import ProcessHandler
from apps.gsekit.process import mock_data as process_mock_data
from apps.gsekit.configfile.models import ConfigTemplateBindingRelationship
from apps.gsekit.configfile.views.tests import BscpMockClient


class TestProcessView(MyTestCase):
    """
    测试进程相关的接口
    """

    swagger_test_view = ProcessViews
    fields_exempt = MyTestCase.fields_exempt + ["config_template_id"]
    actions_exempt = MyTestCase.actions_exempt + ["operate_process", "sync_process_status"]

    cmdb_mock_client = CmdbMockClient.get_cmdb_mock_client_inst()

    CC_API_MOCK_PATH = "apps.gsekit.process.handlers.process.CCApi"
    BSCP_API_MOCK_PATH = "apps.gsekit.adapters.bscp.adapter.BscpApi"

    BSCP_MOCK_CLIENT = BscpMockClient(create_app_return={"app_id": "test_app"}, update_config_return=None)
    CMDB_MOCK_CLIENT = CmdbMockClient.get_cmdb_mock_client_inst()

    @classmethod
    def setUpTestData(cls):
        """TestCase实例生成时调用一次, 可DB回滚
        该hook比setUpClass先执行，需要考虑mock相关顺序
        """
        super().setUpTestData()
        patch(cls.CC_API_MOCK_PATH, cls.cmdb_mock_client).start()
        patch(cls.BSCP_API_MOCK_PATH, cls.BSCP_MOCK_CLIENT).start()
        ProcessHandler(bk_biz_id=cls.bk_biz_id).sync_biz_process()

        # 创建绑定关系
        config_templates = tools.init_config_template(3)
        relation_to_be_created = []
        for config_template in config_templates:
            relation_to_be_created.append(
                ConfigTemplateBindingRelationship(
                    bk_biz_id=cls.bk_biz_id,
                    config_template_id=config_template["config_template_id"],
                    process_object_type=process_models.Process.ProcessObjectType.TEMPLATE,
                    process_object_id=process_mock_data.PROCESS_TEMPLATE_RESPONSE[0]["id"],
                )
            )
        ConfigTemplateBindingRelationship.objects.bulk_create(relation_to_be_created)

    def setUp(self) -> None:
        super(TestProcessView, self).setUp()
