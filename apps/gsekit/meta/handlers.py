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
import time
import json
import fnmatch
from typing import Dict, List
from collections import defaultdict

from apps.api import UserManageApi
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler
from apps.gsekit.job.models import Job, JOB_STATUS_CHOICES, JobTask
from apps.gsekit.process.models import Process
from apps.gsekit.configfile.models import ConfigTemplate
from apps.gsekit.utils.expression_utils.parse import parse_exp2unix_shell_style
from apps.utils.basic import distinct_dict_list


class MetaHandler(object):
    @staticmethod
    def list_users(request):
        """查询平台所有用户"""
        bk_token = request.COOKIES.get("bk_token")
        data = UserManageApi.list_users({"bk_token": bk_token, "no_page": True, "fields": "username,display_name"})
        return data

    @staticmethod
    def get_user_info(request):
        return {
            "id": request.user.id,
            "username": request.user.username,
            "timestamp": time.time(),
            "is_superuser": request.user.is_superuser,
        }

    @staticmethod
    def get_job_filter_choices() -> Dict[str, List]:
        """作业过滤列表"""
        return {
            "job_object_choices": [
                {"id": job_object[0], "name": job_object[1]} for job_object in Job.JOB_OBJECT_CHOICES
            ],
            "job_action_choices": [
                {"id": job_action[0], "name": job_action[1]} for job_action in Job.JOB_ACTION_CHOICES
            ],
            "status_choices": [{"id": status[0], "name": status[1]} for status in JOB_STATUS_CHOICES],
        }

    @staticmethod
    def get_process_filter_choices(bk_biz_id: int) -> Dict[str, List]:
        """进程过滤列表"""
        bk_cloud_ids = Process.objects.filter(bk_biz_id=bk_biz_id).values_list("bk_cloud_id", flat=True).distinct()
        bk_cloud_id_name_map = {
            cloud["bk_cloud_id"]: cloud["bk_cloud_name"]
            for cloud in CMDBHandler(bk_biz_id=bk_biz_id).get_or_cache_bk_cloud_area()
        }
        return {
            "bk_cloud_id_choices": [
                {"id": bk_cloud_id, "name": bk_cloud_id_name_map.get(bk_cloud_id)} for bk_cloud_id in bk_cloud_ids
            ],
            "process_status_choices": [
                {"id": status[0], "name": status[1]} for status in Process.PROCESS_STATUS_CHOICE
            ],
            "is_auto_choices": [
                {"id": is_auto_tuple[0], "name": is_auto_tuple[1]} for is_auto_tuple in Process.IS_AUTO_CHOICE
            ],
        }

    @staticmethod
    def get_job_task_filter_choices(job_id: int):
        """ "任务详细过滤列表"""
        filter_info_list = (
            JobTask.objects.filter(job_id=job_id)
            .extra(
                select={
                    "set_info": "JSON_EXTRACT(extra_data, '$.process_info.set')",
                    "module_info": "JSON_EXTRACT(extra_data, '$.process_info.module')",
                    "bk_process_name": "JSON_EXTRACT(extra_data, '$.process_info.process.bk_process_name')",
                }
            )
            .values("set_info", "module_info", "bk_process_name")
        )

        filter_choices = defaultdict(list)
        for filter_info in filter_info_list:
            set_info = json.loads(filter_info["set_info"])
            module_info = json.loads(filter_info["module_info"])
            bk_process_name = json.loads(filter_info["bk_process_name"])
            filter_choices["set"].append({"id": set_info["bk_set_id"], "name": set_info["bk_set_name"]})
            filter_choices["module"].append({"id": module_info["bk_module_id"], "name": module_info["bk_module_name"]})
            filter_choices["process"].append({"id": bk_process_name, "name": bk_process_name})

        for key, dict_list in filter_choices.items():
            filter_choices[key] = distinct_dict_list(dict_list)

        filter_choices["status_choices"] = [{"id": status[0], "name": status[1]} for status in JOB_STATUS_CHOICES]

        return filter_choices

    @staticmethod
    def expression_match(expression: str, candidates: List[str]) -> Dict:
        exps_with_unix_shell_style = parse_exp2unix_shell_style(expression)
        filter_results = []
        for exp in exps_with_unix_shell_style:
            filter_results.extend(fnmatch.filter(candidates, exp))
        return {"exps_with_unix_shell_style": exps_with_unix_shell_style, "filter_results": list(set(filter_results))}

    @staticmethod
    def access_overview(bk_biz_id: int) -> Dict[str, bool]:
        """
        业务接入情况概览
        :param bk_biz_id: 业务 ID
        :return:
        """
        access_overview_data: Dict[str, bool] = {
            # 通过判断任务历史是否存在进程操作判断业务是否接入进程相关功能
            Job.JobObject.PROCESS: Job.objects.filter(bk_biz_id=bk_biz_id, job_object=Job.JobObject.PROCESS).exists(),
            # 通过是否存在配置模版判断业务是否接入配置相关功能
            Job.JobObject.CONFIGFILE: ConfigTemplate.objects.filter(bk_biz_id=bk_biz_id).exists(),
        }

        # 其中一个部分接入视为已接入该系统
        access_overview_data["is_access"] = any(
            [access_overview_data[Job.JobObject.PROCESS], access_overview_data[Job.JobObject.CONFIGFILE]]
        )

        return access_overview_data
