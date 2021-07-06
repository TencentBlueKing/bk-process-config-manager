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

from django.db import models
from django.utils.translation import ugettext_lazy as _


class VisitCount(models.Model):
    bk_username = models.CharField(_("用户名"), max_length=32, default="")
    bk_biz_id = models.IntegerField("业务ID")
    visit_time = models.DateTimeField(_("访问时间"), auto_now_add=True)

    @classmethod
    def visit(cls, bk_username, bk_biz_id):
        cls.objects.create(bk_username=bk_username, bk_biz_id=bk_biz_id)

    class Meta:
        verbose_name = _("用户访问统计")
        verbose_name_plural = _("用户访问统计")
