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
import django_celery_beat
from celery.task import periodic_task
from django.utils import timezone

from apps.gsekit.job.models import Job
from apps.gsekit.process.handlers.process import ProcessHandler
from common.log import logger


@periodic_task(run_every=django_celery_beat.tzcrontab.TzAwareCrontab(minute="*/10", tz=timezone.get_current_timezone()))
def sync_process(bk_biz_id=None):
    if bk_biz_id:
        bk_biz_id_list = [bk_biz_id]
    else:
        bk_biz_id_list = [job["bk_biz_id"] for job in Job.objects.values("bk_biz_id").order_by().distinct()]

    for biz_id in bk_biz_id_list:
        logger.info(f"[sync_process] start, bk_biz_id={biz_id}")
        try:
            ProcessHandler(bk_biz_id=biz_id).sync_biz_process()
            # TODO 由于GSE接口存在延迟，此处暂停同步状态的周期任务，待GSE优化后再开启
            # ProcessHandler(bk_biz_id=biz_id).sync_proc_status_to_db()
        except Exception as error:
            logger.exception(error)
            logger.error(f"[sync_process] failed, bk_biz_id={biz_id}")
        else:
            logger.info(f"[sync_process] succeeded, bk_biz_id={biz_id}")
