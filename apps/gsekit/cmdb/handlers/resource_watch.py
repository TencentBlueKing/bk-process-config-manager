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
import logging
import gc
from apps.api import CCApi
from apps.gsekit.job.models import Job
from apps.gsekit.process.handlers.process import ProcessHandler

logger = logging.getLogger("app")


def process_watch():
    """
    监听CMDB进程变更事件
    """
    bk_cursor = None
    kwargs = {
        "bk_resource": "process",
        "bk_fields": ["bk_biz_id"],
    }
    try:
        while True:
            kwargs["bk_cursor"] = bk_cursor
            result = CCApi.resource_watch(kwargs, use_admin=True)
            if not result:
                # 期间没有变更，继续下一次调用
                continue
            bk_events = result["bk_events"]
            # 拿该事件的cursor进行下一次的watch
            bk_cursor = bk_events[-1]["bk_cursor"]

            # 如果bk_watched为false，表明未监听到事件
            if not result["bk_watched"]:
                continue

            # 有进程变更的业务集合
            bk_biz_ids = {bk_event["bk_detail"]["bk_biz_id"] for bk_event in bk_events if bk_event.get("bk_detail")}
            for bk_biz_id in bk_biz_ids:

                # 订阅触发的进程变更，需判断是否在GSEKIT执行过任务，避免没有使用GSEKIT的业务写入无用的进程数据
                if not Job.objects.filter(bk_biz_id=bk_biz_id).exists():
                    logger.info("[process_watch] bk_biz_id->({}) dose not run any job, skip.".format(bk_biz_id))
                    continue

                try:
                    ProcessHandler(bk_biz_id=bk_biz_id).sync_biz_process()
                except Exception:
                    logger.exception("[process_watch] bk_biz_id->({}) sync_biz_process err!".format(bk_biz_id))

            # 进行垃圾回收，避免某些不可控原因导致这个事件监听长进程内存不停增长
            gc.collect()
    except Exception:
        logger.exception("[process_watch] some error occur!")
        process_watch()
