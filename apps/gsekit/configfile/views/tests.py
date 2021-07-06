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
import json
import copy
import uuid
import random
import pprint
from typing import Dict

from mock import patch, MagicMock
from django.test import TestCase, override_settings

from apps.utils.test_utils import tools
from apps.iam.tests import PermissionMock
from apps.gsekit.cmdb.views.tests import CmdbMockClient
from apps.gsekit.configfile import mock_data as configfile_mock_data
from apps.utils.test_utils.tests import OVERRIDE_MIDDLEWARE, MyTestCase
from apps.gsekit.configfile.views.config_template import ConfigTemplateViews
from apps.gsekit.configfile.models import ConfigTemplate, ConfigTemplateVersion


class BscpMockClient:
    def __init__(self, create_app_return=None, update_config_return=None):
        self.create_app = MagicMock(return_value=create_app_return)
        self.create_config = MagicMock(side_effect=lambda *args, **kwargs: {"cfg_id": uuid.uuid4()})
        self.update_config = MagicMock(return_value=update_config_return)


class TestConfigTemplateView(MyTestCase):
    """
    测试配置模板相关的接口
    """

    swagger_test_view = ConfigTemplateViews

    path_params = {**MyTestCase.path_params, "config_template_id": 1}

    fields_exempt = MyTestCase.fields_exempt + ["config_template_id", "config_version_id"]
    actions_exempt = ["generate_config", "list_binding_relationship", "release_config", "sync_generate_config"]

    INIT_CREATE_NUM = 3

    BSCP_MOCK_CLIENT = BscpMockClient(create_app_return={"app_id": "test_app"}, update_config_return=None)
    CMDB_MOCK_CLIENT = CmdbMockClient.get_cmdb_mock_client_inst()

    PERMISSION_MOCK_PATH = "apps.iam.handlers.drf.Permission"
    CC_API_MOCK_PATH = "apps.gsekit.cmdb.handlers.cmdb.CCApi"
    BSCP_API_MOCK_PATH = "apps.gsekit.adapters.bscp.adapter.BscpApi"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        tools.init_config_template(cls.INIT_CREATE_NUM)
        cls.bulk_create_config_versions(
            config_template_id=cls.path_params["config_template_id"],
            create_num=2,
            base_create_params={
                "description": "版本描述",
                "content": "草稿内容\n${HELP}",
                "file_format": "python",
                "is_active": True,
            },
        )

    @classmethod
    def setUpClass(cls):
        super(TestConfigTemplateView, cls).setUpClass()

        # TODO Permission贯穿各个模块的鉴权，后续可以把通用部分提到MyTestCase
        patch(cls.PERMISSION_MOCK_PATH, PermissionMock).start()
        patch(cls.BSCP_API_MOCK_PATH, cls.BSCP_MOCK_CLIENT).start()
        patch(cls.CC_API_MOCK_PATH, cls.CMDB_MOCK_CLIENT).start()

    def setUp(self) -> None:
        super().setUp()

        self.assertEqual(ConfigTemplate.objects.all().count(), self.INIT_CREATE_NUM)

    def random_config_template_id(self):
        ids = list(ConfigTemplate.objects.all().values_list("config_template_id", flat=True))
        self.assertFalse(len(ids) == 0)
        return ids[random.randint(0, len(ids) - 1)]

    @staticmethod
    def bulk_create_config_versions(config_template_id: int, create_num: int, base_create_params: Dict) -> None:
        config_versions_to_be_created = []
        for index in range(create_num):
            create_params = copy.deepcopy(base_create_params)
            if index != 0:
                create_params["description"] = f"{create_params['description']}{index}"
            create_params["is_draft"] = not create_params["is_active"]
            create_params["config_template_id"] = config_template_id
            config_versions_to_be_created.append(ConfigTemplateVersion(**create_params))
        ConfigTemplateVersion.objects.bulk_create(config_versions_to_be_created)


class TestConfigVersionView(TestCase):
    """
    测试配置模板版本相关接口
    """

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_retrieve_config_version(self):
        config_version_id = TestConfigTemplateView().test_create_config_template()["config_version_id"]
        res = self.client.get(path=f"/api/config_version/{config_version_id}/")
        pprint.pprint(res.data)
        assert res.status_code == 200
        assert res.data["result"]

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_update_config_version(self):
        config_version_id = TestConfigTemplateView().test_create_config_template()["config_version_id"]
        res = self.client.put(
            content_type="application/json",
            path=f"/api/config_version/{config_version_id}/",
            data=json.dumps(configfile_mock_data.UPDATE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY),
        )
        pprint.pprint(res.data)
        assert res.status_code == 200
        assert res.data["result"]
        return res.data["data"]

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_clone(self):
        config_version_id = self.test_update_config_version()["config_version_id"]
        res = self.client.post(
            content_type="application/json",
            path=f"/api/config_version/{config_version_id}/clone/",
            data=json.dumps(configfile_mock_data.CLONE_CONFIG_TEMPLATE_VERSION_REQUEST_BODY),
        )
        pprint.pprint(res.data)
        assert res.status_code == 200
        assert res.data["result"]
        return res.data["data"]

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_preview(self):
        res = self.client.post(
            content_type="application/json",
            path="/api/config_version/preview/",
            data=json.dumps(configfile_mock_data.PREVIEW_CONFIG_REQUEST_BODY),
        )
        pprint.pprint(res.data)
        assert res.status_code == 200
        assert res.data["result"]
        return res.data["data"]


class TestConfigInstanceView(TestCase):
    BK_BIZ_ID = 2

    @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
    def test_list_config(self):
        res = self.client.post(
            content_type="application/json",
            path="/api/{}/config_instance/list_config/".format(self.BK_BIZ_ID),
            data=json.dumps(configfile_mock_data.LIST_CONFIG_INSTANCES_REQUEST_BODY),
        )
        pprint.pprint(res.data)
        assert res.status_code == 200
        assert res.data["result"]
        return res.data["data"]
