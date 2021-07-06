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

from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import Job
from apps.utils.test_utils.tests import patch_get_request


class TestJobHandlers(TestCase):
    """
    测试进程相关的接口
    """

    BK_BIZ_ID = 100605

    @patch_get_request
    def test_create_job(self):
        expression_scope = {
            "bk_set_env": 1,
            "bk_set_name": "*",
            "bk_module_name": "*",
            "service_instance_name": "*",
            "bk_process_name": "*",
            "bk_process_id": "*",
        }
        scope = {}
        job_object = Job.JobObject.CONFIGFILE
        job_action = Job.JobAction.GENERATE
        created_by = "admin"
        JobHandlers(bk_biz_id=self.BK_BIZ_ID).create_job(
            job_action=job_action,
            job_object=job_object,
            created_by=created_by,
            scope=scope,
            expression_scope=expression_scope,
        )
