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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


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

    class Meta:
        verbose_name = _("全局配置表")
        verbose_name_plural = _("全局配置表")
