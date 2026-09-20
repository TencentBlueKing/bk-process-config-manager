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
from typing import List
from django.db import transaction
import django_celery_beat
from celery.task import periodic_task, task
from django.utils import timezone
from apps.core.gray.handlers import GrayHandler
from apps.gsekit.cmdb.handlers.cmdb import CMDBHandler

from apps.gsekit.job.models import Job
from apps.gsekit.meta.models import GlobalSettings
from apps.gsekit.periodic_tasks.utils import calculate_countdown
from apps.gsekit.process.handlers.process import ProcessHandler
from common.log import logger


@task(ignore_result=True)
def sync_biz_process_task(bk_biz_id):
    logger.info(f"[sync_biz_process_task] start, bk_biz_id={bk_biz_id}")
    process_related_infos = ProcessHandler(bk_biz_id=bk_biz_id).sync_biz_process()
    ProcessHandler(bk_biz_id=bk_biz_id).sync_biz_process_status(process_related_infos=process_related_infos)
    logger.info(f"[sync_biz_process_task] finished, bk_biz_id={bk_biz_id}")


@periodic_task(run_every=django_celery_beat.tzcrontab.TzAwareCrontab(minute="*/10", tz=timezone.get_current_timezone()))
def sync_process(bk_biz_id=None):
    if bk_biz_id:
        bk_biz_id_list = [bk_biz_id]
    else:
        bk_biz_id_list = [job["bk_biz_id"] for job in Job.objects.values("bk_biz_id").order_by().distinct()]

    count = len(bk_biz_id_list)
    for index, biz_id in enumerate(bk_biz_id_list):
        logger.info(f"[sync_process] start, bk_biz_id={biz_id}")
        countdown = calculate_countdown(count, index) if count > 1 else 0
        sync_biz_process_task.apply_async((biz_id,), countdown=countdown)
        logger.info(f"[sync_process] bk_biz_id={biz_id} will be run after {countdown} seconds.")


@periodic_task(run_every=django_celery_beat.tzcrontab.TzAwareCrontab(minute="*/30", tz=timezone.get_current_timezone()))
def sync_new_biz_to_gray_scope_list():
    """
    添加新增业务到灰度列表
    """
    task_id = sync_new_biz_to_gray_scope_list.request.id
    logger.info(f"sync_new_biz_to_gray_scope_list: {task_id} Start adding new biz to GSE2_GRAY_SCOPE_LIST.")

    all_biz_ids = GlobalSettings.get_config(key=GlobalSettings.KEYS.ALL_BIZ_IDS, default=[])
    # if not all_biz_ids:
    #     logger.info(f"sync_new_biz_to_gray_scope_list: {task_id} No need to add new biz to GSE2_GRAY_SCOPE_LIST.")
    #     return None

    cc_all_biz_ids: List[int] = list(CMDBHandler.biz_id_name_without_permission().keys())
    new_biz_ids: List[int] = list(set(cc_all_biz_ids) - set(all_biz_ids))

    logger.info(f"sync_new_biz_to_gray_scope_list: {task_id} new biz ids: {new_biz_ids}.")
    if new_biz_ids:
        with transaction.atomic():
            # 更新全部业务列表
            if GlobalSettings.objects.filter(key=GlobalSettings.KEYS.ALL_BIZ_IDS):
                GlobalSettings.update_config(key=GlobalSettings.KEYS.ALL_BIZ_IDS, value=cc_all_biz_ids)
            else:
                GlobalSettings.set_config(key=GlobalSettings.KEYS.ALL_BIZ_IDS, value=cc_all_biz_ids)

            # 对新业务执行灰度操作
            result = GrayHandler.build({"bk_biz_ids": new_biz_ids})
            logger.info(f"sync_new_biz_to_gray_scope_list: {task_id}  New biz: {new_biz_ids} Build result: {result}")

    logger.info(f"sync_new_biz_to_gray_scope_list: {task_id} Add new biz to GSE2_GRAY_SCOPE_LIST completed.")
