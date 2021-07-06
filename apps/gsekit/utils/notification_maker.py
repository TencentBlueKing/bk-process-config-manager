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
from collections import ChainMap
from typing import List, Dict

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.api import CmsiApi, CCApi
from apps.exceptions import ApiError
from apps.gsekit.cmdb.constants import BK_SET_ENV_CHOICES
from apps.gsekit.job.handlers import JobHandlers
from apps.gsekit.job.models import JobTask, Job, JOB_STATUS_CHOICES
from apps.utils.basic import filter_values, utc_strftime2local_strftime
from apps.utils.models import model_to_dict

logger = logging.getLogger("component")


class ContentType(object):
    HTML = "HTML"
    TEXT = "TEXT"


class MsgType(object):
    WEIXIN = "weixin"
    SMS = "sms"
    MAIL = "mail"


class BaseNotificationMaker(object):
    CONTENT_TEMPLATE = {ContentType.HTML: "", ContentType.TEXT: ""}

    TITLE_TEMPLATE = ""

    def __init__(
        self,
        msg_type: str,
        receivers: List[str],
        content_type: str,
        sender: str = None,
        base_context: Dict = None,
        attachments: List[Dict] = None,
        *args,
        **kwargs,
    ):
        self.msg_type = msg_type
        self.receivers = receivers
        self.content_type = content_type
        self.sender = sender
        self.base_context = base_context or {}
        self.attachments = attachments

        self.base_context.update({"bk_saas_host": settings.BK_SAAS_HOST})

    def get_title(self, context: Dict = None) -> str:
        return _(self.TITLE_TEMPLATE).format(**(context or {}))

    def get_content(self, context: Dict = None) -> str:
        return _(self.CONTENT_TEMPLATE.get(self.content_type, "")).format(**(context or {}))

    def send(self, context: Dict = None, query_params: Dict = None, *args, **kwargs):

        context = dict(ChainMap(context or {}, self.base_context))

        base_query_params = {
            "msg_type": self.msg_type,
            "sender": self.sender,
            "receiver__username": ",".join(self.receivers),
            "title": self.get_title(context),
            "content": self.get_content(context),
        }

        query_params = filter_values(dict(ChainMap(query_params or {}, base_query_params)))

        try:
            CmsiApi.send_msg(query_params, use_admin=True)
        except ApiError as err:
            # 邮件发送失败，不影响主流程，这里仅记录日志
            logger.warning(f"send_mail error: {err}")
            pass


class JobNotificationMaker(BaseNotificationMaker):
    TITLE_TEMPLATE = "GSEKIT-任务执行结果通知"

    CONTENT_TEMPLATE = {
        ContentType.HTML: """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body style='font-family: "PingFang SC", "Microsoft Yahei", Helvetica, Aria, serif'>
            <h3>GSEKIT {job_type} #{job_id} {job_status_alias}</h3>
            <p>来自 GSEKIT 的推送</p>
            <hr/>
            <div>
                <p>业务： [{bk_biz_id}] {bk_biz_name}</p>
                <p>任务ID： #{job_id}</p>
                <p>执行账户：{created_by}</p>
                <p>任务类型：{job_type}</p>
                <p>环境类型：{bk_set_env_alias}</p>
                <p>操作范围：{expression}</p>
                <p>开始时间：{start_time}</p>
                <p>结束时间：{end_time}</p>
                <p>执行结果：
                    <span style="color: #3fc06d; font-weight: 700">{succeeded}</span> 个成功，
                    <span style="color: #ea3636; font-weight: 700">{failed}</span> 个失败，
                    <span style="color: #ff9c01; font-weight: 700">{ignored}</span> 个已忽略
                </p>
            </div>
            <a href="{bk_saas_host}task-history/detail/{job_id}?biz={bk_biz_id}" target="_blank">
                点击查看任务详细
            </a>
        </body>
        </html>
        """,
        ContentType.TEXT: "",
    }

    JOB_ACTION_ALIAS_MAP = dict(Job.JOB_ACTION_CHOICES)
    JOB_OBJECT_ALIAS_MAP = dict(Job.JOB_OBJECT_CHOICES)
    BK_ENV_ALIAS_MAP = dict(BK_SET_ENV_CHOICES)

    def __init__(
        self,
        job: Job,
        msg_type: str,
        content_type: str,
        sender: str = None,
        base_context: Dict = None,
        attachments: List[Dict] = None,
        *args,
        **kwargs,
    ):
        self.job = job

        all_biz_list = CCApi.search_business({"fields": ["bk_biz_id", "bk_biz_name"]}, use_admin=True).get("info") or []
        biz_id_name_map = {biz["bk_biz_id"]: biz["bk_biz_name"] for biz in all_biz_list}

        base_context = base_context or {}
        base_context.update(
            {
                "job_id": job.id,
                "title": self.get_title(),
                "bk_biz_name": biz_id_name_map.get(job.bk_biz_id),
                "job_status_alias": dict(JOB_STATUS_CHOICES)[job.status],
                "bk_set_env_alias": self.BK_ENV_ALIAS_MAP[job.scope["bk_set_env"]],
                "job_type": "{object_alias}{action_alias}".format(
                    object_alias=self.JOB_OBJECT_ALIAS_MAP[job.job_object],
                    action_alias=self.JOB_ACTION_ALIAS_MAP[job.job_action],
                ),
                **model_to_dict(job),
                **JobHandlers.get_task_status_counter(JobTask.objects.filter(job_id=job.id))["status_counter"],
            }
        )
        base_context["start_time"] = utc_strftime2local_strftime(base_context["start_time"])
        base_context["end_time"] = utc_strftime2local_strftime(base_context["end_time"])

        super().__init__(
            msg_type=msg_type,
            receivers=[job.created_by],
            content_type=content_type,
            sender=sender,
            base_context=base_context,
            attachments=attachments,
            *args,
            **kwargs,
        )
