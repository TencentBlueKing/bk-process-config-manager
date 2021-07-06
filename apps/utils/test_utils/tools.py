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
import copy
from typing import Dict, List

from apps.utils.models import model_to_dict
from apps.utils.test_utils.tests import MyTestCase
from apps.gsekit.configfile.models import ConfigTemplate
from apps.gsekit.configfile import mock_data as configfile_mock_data


# 放置公共逻辑


def init_config_template(create_num) -> List[Dict]:
    conf_tmpls_to_be_created = []
    for index in range(create_num):
        create_params = copy.deepcopy(configfile_mock_data.CREATE_CONFIG_TEMPLATE_REQUEST_BODY)
        if index >= 0:
            create_params["template_name"] = f"{create_params['template_name'][0: -1]}{index}"
        conf_tmpls_to_be_created.append(ConfigTemplate(**{"bk_biz_id": MyTestCase.bk_biz_id, **create_params}))
    ConfigTemplate.objects.bulk_create(conf_tmpls_to_be_created)
    return [model_to_dict(config_template) for config_template in ConfigTemplate.objects.all()]
