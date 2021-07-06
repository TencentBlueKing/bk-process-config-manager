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
# -*- coding: utf-8 -*-

from django.test import TestCase

from apps.gsekit.configfile.handlers.config_template import ConfigTemplateHandler
from apps.gsekit.process.models import Process


class TestConfigTemplateHandlers(TestCase):
    """
    测试配置处理器
    """

    def test_bind_template_to_process(self):
        # 新增配置模板绑定
        process_object_list = [
            {"process_object_type": Process.ProcessObjectType.INSTANCE, "process_object_id": 1},
            {"process_object_type": Process.ProcessObjectType.INSTANCE, "process_object_id": 2},
            {"process_object_type": Process.ProcessObjectType.TEMPLATE, "process_object_id": 1},
            {"process_object_type": Process.ProcessObjectType.TEMPLATE, "process_object_id": 2},
        ]
        count = ConfigTemplateHandler(config_template_id=1).bind_template_to_process(process_object_list)
        self.assertEqual(count["deleted_relations_count"], 0)
        self.assertEqual(count["created_relations_count"], 4)

        # 变更
        process_object_list = [
            {"process_object_type": Process.ProcessObjectType.INSTANCE, "process_object_id": 1},
            {"process_object_type": Process.ProcessObjectType.TEMPLATE, "process_object_id": 1},
            {"process_object_type": Process.ProcessObjectType.TEMPLATE, "process_object_id": 3},
        ]
        count = ConfigTemplateHandler(config_template_id=1).bind_template_to_process(process_object_list)
        self.assertEqual(count["deleted_relations_count"], 2)
        self.assertEqual(count["created_relations_count"], 1)

    def test_bind_process_to_template(self):
        self.test_bind_template_to_process()
        # 新增配置模板绑定
        process_object_id = 3
        process_object_type = Process.ProcessObjectType.TEMPLATE
        config_template_id_list = [1, 2, 3]
        count = ConfigTemplateHandler.bind_process_to_template(
            process_object_type, process_object_id, config_template_id_list
        )
        self.assertEqual(count["deleted_relations_count"], 0)
        self.assertEqual(count["created_relations_count"], 2)

        config_template_id_list = []
        count = ConfigTemplateHandler.bind_process_to_template(
            process_object_type, process_object_id, config_template_id_list
        )
        self.assertEqual(count["deleted_relations_count"], 3)
        self.assertEqual(count["created_relations_count"], 0)
