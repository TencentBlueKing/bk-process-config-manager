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

from django.db import models
from django.db.models import Count
from django.utils.module_loading import import_string


class OperationsHandler(object):
    @staticmethod
    def model_count_statistics_with_orm(
        model_path: str, filter_conditions: Dict, exclude_conditions: Dict, group_by: List
    ) -> List:
        """使用ORM进行过滤和分组统计"""
        # 为降低安全风险，这里不把 model_path 暴露给到view方法，按运营统计需求进行封装
        model: models.Model = import_string(model_path)
        result = (
            model.objects.filter(**filter_conditions)
            .exclude(**exclude_conditions)
            .values(*group_by)
            .annotate(count=Count("*"))
            .order_by("-count")
        )
        return result

    @classmethod
    def job_count_statistics_with_orm(cls, filter_conditions: Dict, exclude_conditions: Dict, group_by: List) -> List:
        """统计任务作业"""
        return cls.model_count_statistics_with_orm(
            "apps.gsekit.job.models.Job", filter_conditions, exclude_conditions, group_by
        )

    @classmethod
    def visit_count_statistics_with_orm(cls, filter_conditions: Dict, exclude_conditions: Dict, group_by: List) -> List:
        """统计访问记录"""
        return cls.model_count_statistics_with_orm(
            "apps.gsekit.operations.models.VisitCount", filter_conditions, exclude_conditions, group_by
        )
