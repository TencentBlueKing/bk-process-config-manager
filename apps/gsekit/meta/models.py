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
import datetime
import typing

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.gsekit import constants


class GlobalSettings(models.Model):
    """
    全局配置表
    """

    key = models.CharField(_("键"), max_length=255, db_index=True, primary_key=True)
    v_json = models.JSONField(_("值"))

    # 这里用把各种配置维护起来，并提供默认值，避免遗忘
    class KEYS:
        FOOTER = "FOOTER"  # 页面注脚
        APIGW_PUBLIC_KEY = "APIGW_PUBLIC_KEY"  # APIGW 公钥
        PIPELINE_POLLING_TIMEOUT = "PIPELINE_POLLING_TIMEOUT"  # pipeline 轮询超时时间
        PROCESS_TASK_GRANULARITY = "PROCESS_TASK_GRANULARITY"  # 进程任务聚合粒度
        # GSE 2.0 灰度列表
        GSE2_GRAY_SCOPE_LIST = "GSE2_GRAY_SCOPE_LIST"

    @classmethod
    def process_task_aggregate_info(cls, bk_biz_id: int) -> typing.Dict[str, str]:
        biz_task_granularity: typing.Dict[str, typing.Union[str, typing.List[int]]] = cls.objects.get_or_create(
            key=cls.KEYS.PROCESS_TASK_GRANULARITY, defaults=dict(v_json={"DEFAULT": constants.TaskGranularity.BIZ})
        )[0].v_json
        default_task_granularity: str = biz_task_granularity.get("DEFAULT", constants.TaskGranularity.BIZ)
        for task_granularity in constants.TaskGranularity.TASK_GRANULARITY_CHOICES:
            if bk_biz_id in biz_task_granularity.get(task_granularity, []):
                return {
                    "task_granularity": task_granularity,
                    "node_key_field": constants.TaskGranularity.TASK_GRANULARITY_NODE_KEY_FIELD_MAP[task_granularity],
                }
        return {
            "task_granularity": default_task_granularity,
            "node_key_field": constants.TaskGranularity.TASK_GRANULARITY_NODE_KEY_FIELD_MAP[default_task_granularity],
        }

    @classmethod
    def pipeline_polling_timeout(cls):
        # 支持全局配置
        try:
            return int(cls.objects.get(key=cls.KEYS.PIPELINE_POLLING_TIMEOUT).v_json)
        except cls.DoesNotExist:
            # 默认15分钟
            return 60 * 15

    @classmethod
    def footer(cls):
        try:
            return cls.objects.get(key=cls.KEYS.FOOTER).v_json
        except cls.DoesNotExist:
            return {
                "footer": [
                    {
                        "text": _("QQ咨询(800802001)"),
                        "link": "https://wpa.b.qq.com/cgi/wpa.php?ln=1&key=XzgwMDgwMjAwMV80NDMwOTZfODAwODAyMDAxXzJf",
                        "is_blank": True,
                    },
                    {"text": _("蓝鲸论坛"), "link": "https://bk.tencent.com/s-mart/community", "is_blank": True},
                    {"text": _("蓝鲸官网"), "link": "https://bk.tencent.com/", "is_blank": True},
                    {"text": _("蓝鲸智云桌面"), "link": settings.BK_PAAS_HOST, "is_blank": True},
                ],
                "copyright": "Copyright © 2012-{year} Tencent BlueKing. All Rights Reserved.".format(
                    year=datetime.datetime.now().year
                ),
            }

    @classmethod
    def jwt_public_key(cls):
        try:
            return cls.objects.get(key=cls.KEYS.APIGW_PUBLIC_KEY).v_json
        except cls.DoesNotExist:
            return ""

    @classmethod
    def get_config(cls, key=None, default=None):
        try:
            return cls.objects.get(key=key).v_json
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_config(cls, key, value):
        cls.objects.create(key=key, v_json=value)

    @classmethod
    def update_config(cls, key, value):
        cls.objects.filter(key=key).update(v_json=value)

    class Meta:
        verbose_name = _("全局配置表（GlobalSettings）")
        verbose_name_plural = _("全局配置表（GlobalSettings）")
