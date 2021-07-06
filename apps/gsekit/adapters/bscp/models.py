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
from django.utils.translation import ugettext_lazy as _

from apps.gsekit.process.models import Process


class BscpApplication(models.Model):
    biz_id = models.IntegerField(_("业务ID"), db_index=True)
    biz_name = models.CharField(_("BSCP业务ID"), max_length=64, primary_key=True)
    app_id = models.CharField(_("BSCP应用ID"), max_length=64, db_index=True)
    process_object_type = models.CharField(
        _("进程对象类型"), max_length=16, db_index=True, choices=Process.PROCESS_OBJECT_TYPE_CHOICE
    )
    process_object_id = models.IntegerField(_("进程实例ID/进程模板ID"), db_index=True)

    class DeployType(object):
        """配置文件格式"""

        DOCKER = 0
        PROCESS = 1

    class Meta:
        verbose_name = _("BSCP应用")
        verbose_name_plural = _("BSCP应用")
        unique_together = ("app_id", "process_object_type", "process_object_id")
        db_table = "bscp_application"


class BscpConfig(models.Model):
    app_id = models.CharField(_("BSCP应用ID"), max_length=64, db_index=True)
    config_template_id = models.IntegerField(_("模板ID"), db_index=True)
    file_name = models.CharField(_("文件名"), max_length=64)
    path = models.CharField(_("文件路径"), max_length=256)
    cfg_id = models.CharField(_("BSCP配置ID"), max_length=64, primary_key=True)

    @classmethod
    def batch_get_template_cfg_mapping(cls, config_template_ids: List[int], app_id) -> Dict:
        """
        批量获取 模板ID 和 BSCP配置 的映射关系
        :return:
        """
        return {
            cfg.config_template_id: cfg
            for cfg in cls.objects.filter(config_template_id__in=config_template_ids, app_id=app_id)
        }

    class FileMode(object):
        """配置文件类型"""

        TEXT = 0
        BINARY = 1
        TEMPLATE = 2

    class FileFormat(object):
        """配置文件格式"""

        UNIX = "unix"
        WINDOWS = "windows"

    class Meta:
        verbose_name = _("BSCP配置")
        verbose_name_plural = _("BSCP配置")
        unique_together = ("app_id", "config_template_id", "file_name", "path")
        db_table = "bscp_config"
