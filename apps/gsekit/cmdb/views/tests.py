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
from typing import List, Dict
from collections import defaultdict

from mock import patch, MagicMock

from apps.utils.test_utils.tests import MyTestCase
from apps.iam.tests import PermissionMock
from apps.gsekit.cmdb.views.cmdb import CMDBViews
from apps.gsekit.cmdb import mock_data as cmdb_mock_data
from apps.gsekit.process import mock_data as proc_mock_data


class CmdbMockClient:
    def find_module_batch_side_effect(self, *args, **kwargs) -> List[Dict]:
        fields = kwargs.get("params", {}).get("fields")
        if not fields:
            return self.find_module_batch_return
        fields.append("default")
        module_list = []
        for module_info in self.find_module_batch_return:
            module_list.append({field: value for field, value in module_info.items() if field in fields})
        return module_list

    def search_object_attribute_side_effect(self, *args, **kwargs) -> List[Dict]:
        bk_obj_id = kwargs.get("params", {}).get("bk_obj_id")
        if bk_obj_id:
            return self.search_object_attribute_group[bk_obj_id]

        # 用于/api/{bk_biz_id}/cmdb/search_object_attribute/的测试
        bk_obj_id = args[0].get("bk_obj_id")
        return self.search_object_attribute_group[bk_obj_id]

    def list_proc_template_side_effect(self, *args, **kwargs) -> Dict:
        service_template_id = args[0].get("service_template_id")
        proc_template_group_by_service_template_id = defaultdict(list)
        for proc_template in self.list_proc_template_return:
            proc_template_group_by_service_template_id[proc_template["service_template_id"]].append(proc_template)
        return {
            "count": len(proc_template_group_by_service_template_id[service_template_id]),
            "info": proc_template_group_by_service_template_id[service_template_id],
        }

    def list_process_instance_side_effect(self, *args, **kwargs):
        service_instance_id = args[0].get("service_instance_id")
        proc_inst_group_by_service_instance_id = defaultdict(list)
        for proc_inst in self.list_process_instance_return:
            proc_inst_group_by_service_instance_id[proc_inst["relation"]["service_instance_id"]].append(proc_inst)
        return proc_inst_group_by_service_instance_id[service_instance_id]

    def __init__(
        self,
        search_business_return=None,
        search_biz_inst_topo_return=None,
        search_set_return=None,
        find_module_batch_return=None,
        list_service_template_return=None,
        create_process_instance_return=None,
        batch_create_proc_template_return=None,
        delete_process_instance_return=None,
        delete_proc_template_return=None,
        update_process_instance_return=None,
        update_proc_template_return=None,
        list_process_related_info_return=None,
        # side effect
        search_object_attribute_group=None,
        list_proc_template_return=None,
        list_process_instance_return=None,
    ):
        self.find_module_batch_return = find_module_batch_return
        self.list_proc_template_return = list_proc_template_return
        self.list_process_instance_return = list_process_instance_return
        self.search_object_attribute_group = search_object_attribute_group

        self.find_module_batch = MagicMock(side_effect=self.find_module_batch_side_effect)
        self.list_proc_template = MagicMock(side_effect=self.list_proc_template_side_effect)
        self.list_process_instance = MagicMock(side_effect=self.list_process_instance_side_effect)
        self.search_object_attribute = MagicMock(side_effect=self.search_object_attribute_side_effect)

        self.search_business = MagicMock(return_value=search_business_return)
        self.search_biz_inst_topo = MagicMock(return_value=search_biz_inst_topo_return)
        self.search_set = MagicMock(return_value=search_set_return)
        self.list_service_template = MagicMock(return_value=list_service_template_return)
        self.create_process_instance = MagicMock(return_value=create_process_instance_return)
        self.batch_create_proc_template = MagicMock(return_value=batch_create_proc_template_return)
        self.delete_process_instance = MagicMock(return_value=delete_process_instance_return)
        self.delete_proc_template = MagicMock(return_value=delete_proc_template_return)
        self.update_process_instance = MagicMock(return_value=update_process_instance_return)
        self.update_proc_template = MagicMock(return_value=update_proc_template_return)
        self.list_process_related_info = MagicMock(return_value=list_process_related_info_return)

    @staticmethod
    def get_cmdb_mock_client_inst(
        search_business_data: List = cmdb_mock_data.BIZ_LIST_RESPONSE,
        search_biz_inst_topo_data: List = cmdb_mock_data.BIZ_TOPO_RESPONSE,
        search_set_data: List = cmdb_mock_data.SET_LIST_RESPONSE,
        find_module_batch_data: List = cmdb_mock_data.FIND_MODULE_BATCH,
        list_service_template_data: List = cmdb_mock_data.SERVICE_TEMPLATE_RESPONSE,
        create_process_instance_data: List = proc_mock_data.CREATE_PROCESS_INSTANCE_RESPONSE,
        batch_create_proc_template_data: List = proc_mock_data.CREATE_PROCESS_INSTANCE_RESPONSE,
        update_process_instance_data: List = proc_mock_data.UPDATE_PROCESS_INSTANCE_RESPONSE,
        update_proc_template_data: List = proc_mock_data.UPDATE_PROCESS_TEMPLATE_RESPONSE,
        list_process_related_info_data: List = cmdb_mock_data.LIST_PROCESS_RELATED_INFO,
        # side effect
        list_proc_template_data=cmdb_mock_data.LIST_PROC_TEMPLATE,
        list_process_instance_data=cmdb_mock_data.LIST_PROCESS_INSTANCE,
        search_object_attribute_group=cmdb_mock_data.SEARCH_OBJECT_ATTRIBUTE_GROUP,
    ):
        return CmdbMockClient(
            search_business_return={"info": search_business_data},
            search_biz_inst_topo_return=search_biz_inst_topo_data,
            search_set_return={"info": search_set_data, "count": len(search_set_data)},
            find_module_batch_return=find_module_batch_data,
            list_service_template_return={"info": list_service_template_data, "count": len(list_service_template_data)},
            create_process_instance_return=create_process_instance_data,
            batch_create_proc_template_return=batch_create_proc_template_data,
            update_process_instance_return=update_process_instance_data,
            update_proc_template_return=update_proc_template_data,
            list_process_related_info_return={
                "info": list_process_related_info_data,
                "count": len(list_process_related_info_data),
            },
            # side effect
            search_object_attribute_group=search_object_attribute_group,
            list_proc_template_return=list_proc_template_data,
            list_process_instance_return=list_process_instance_data,
        )


class TestCMDBView(MyTestCase):
    """
    测试CMDB相关的接口
    """

    # swagger文档自动化测试相关

    swagger_test_view = CMDBViews
    actions_exempt = ["biz_topo", "service_instance"]

    cmdb_mock_client = CmdbMockClient.get_cmdb_mock_client_inst()

    CC_API_MOCK_PATH = "apps.gsekit.cmdb.handlers.cmdb.CCApi"
    PERMISSION_MOCK_PATH = "apps.gsekit.cmdb.handlers.cmdb.Permission"

    def setUp(self) -> None:
        super(TestCMDBView, self).setUp()
        patch(self.PERMISSION_MOCK_PATH, PermissionMock).start()
        patch(self.CC_API_MOCK_PATH, self.cmdb_mock_client).start()

    def tearDown(self) -> None:
        super(TestCMDBView, self).tearDown()
