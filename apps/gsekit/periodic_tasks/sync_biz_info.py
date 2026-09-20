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
from celery.task import periodic_task
from celery.schedules import crontab
from apps.api import CCApi

from blueapps.utils.logger import logger

from apps.gsekit.process.models import Business


@periodic_task(run_every=crontab(hour=0, minute=0))
def sync_business():
    all_biz_list = CCApi.search_business({"fields": ["bk_biz_id", "bk_biz_name"]}, use_admin=True).get("info") or []

    for item in all_biz_list:
        bk_biz_id = item.get("bk_biz_id")
        bk_biz_name = item.get("bk_biz_name")
        try:
            # 假设 bk_biz_id 是唯一标识，根据它来查找记录
            Business.objects.update_or_create(bk_biz_id=bk_biz_id, defaults={"bk_biz_name": bk_biz_name})
        except Exception as e:
            logger.info(f"处理数据 {bk_biz_id} 时出现错误: {e}")
