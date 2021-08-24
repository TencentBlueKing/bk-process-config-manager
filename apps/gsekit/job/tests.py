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

from apps.gsekit.configfile.models import ConfigTemplateBindingRelationship
from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import Job, JobTask
from apps.gsekit.process.models import Process
from apps.utils.test_utils.tests import patch_get_request


class TestJobHandlers(TestCase):
    """
    测试任务相关的接口
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
        scope = None
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


class TestJobModels(TestCase):
    def test_get_job_tasks_config_template_ids_map(self):
        job_id = 1
        bk_process_id_1 = 111
        bk_process_id_2 = 222
        bk_process_id_3 = 333
        bk_process_template_id = 444
        JobTask.objects.bulk_create(
            [
                JobTask(
                    id=1,
                    job_id=job_id,
                    bk_process_id=bk_process_id_1,
                    pipeline_id="",
                    extra_data={
                        "process_info": {
                            "process_template": {"id": None},
                            "process": {"bk_process_id": bk_process_id_1},
                        }
                    },
                ),
                JobTask(
                    id=2,
                    job_id=job_id,
                    bk_process_id=bk_process_id_2,
                    pipeline_id="",
                    extra_data={
                        "process_info": {
                            "process_template": {"id": bk_process_template_id},
                            "process": {"bk_process_id": bk_process_id_2},
                        }
                    },
                ),
                JobTask(
                    id=3,
                    job_id=job_id,
                    bk_process_id=bk_process_id_3,
                    pipeline_id="",
                    extra_data={
                        "process_info": {
                            "process_template": {"id": None},
                            "process": {"bk_process_id": bk_process_id_3},
                        },
                        "config_template_ids": [1, 2, 3, 4],
                    },
                ),
            ]
        )
        ConfigTemplateBindingRelationship.objects.bulk_create(
            [
                ConfigTemplateBindingRelationship(
                    bk_biz_id=1,
                    config_template_id=1,
                    process_object_type=Process.ProcessObjectType.INSTANCE,
                    process_object_id=bk_process_id_1,
                ),
                ConfigTemplateBindingRelationship(
                    bk_biz_id=1,
                    config_template_id=2,
                    process_object_type=Process.ProcessObjectType.INSTANCE,
                    process_object_id=bk_process_id_1,
                ),
                ConfigTemplateBindingRelationship(
                    bk_biz_id=1,
                    config_template_id=3,
                    process_object_type=Process.ProcessObjectType.TEMPLATE,
                    process_object_id=bk_process_template_id,
                ),
                ConfigTemplateBindingRelationship(
                    bk_biz_id=1,
                    config_template_id=4,
                    process_object_type=Process.ProcessObjectType.INSTANCE,
                    process_object_id=bk_process_id_3,
                ),
            ]
        )
        job_tasks = JobTask.objects.filter(job_id=job_id)
        job_task_config_template_ids_map = JobTask.get_job_tasks_config_template_ids_map(job_tasks)
        self.assertDictEqual(job_task_config_template_ids_map, {1: [1, 2], 2: [3], 3: [1, 2, 3, 4]})
