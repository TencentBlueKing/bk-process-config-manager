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
from apps.gsekit.adapters.base.pipeline_managers.configfile import ConfigFilePipelineManager
from apps.gsekit.adapters.base.pipeline_managers.process import ProcessPipelineManager
from apps.gsekit.adapters.bscp.pipeline_managers.configfile import BscpReleaseConfigFilePipelineManager
from apps.gsekit.job.exceptions import NotSupportedJobObjectException
from apps.gsekit.job.models import Job

supported_pipeline_manager_map = {
    Job.JobObject.CONFIGFILE: {
        "default": ConfigFilePipelineManager,
        Job.JobAction.RELEASE: BscpReleaseConfigFilePipelineManager,
    },
    Job.JobObject.PROCESS: {"default": ProcessPipelineManager},
}


class ManagerFactory(object):
    @staticmethod
    def get_manager(job: Job):

        try:
            pipeline_action_manager_map = supported_pipeline_manager_map[job.job_object]
        except KeyError:
            raise NotSupportedJobObjectException(job_object=job.job_object)

        manager_cls = pipeline_action_manager_map.get(job.job_action) or pipeline_action_manager_map["default"]

        return manager_cls(job=job)
