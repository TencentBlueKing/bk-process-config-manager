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
import functools
import traceback
from django.utils.translation import ugettext_lazy as _

from django.db import models

from apps.exceptions import AppBaseException


class GsekitProcessToCCProcessTemplateMap(models.Model):
    bk_biz_id = models.IntegerField(_("业务ID"))
    gsekit_process_id = models.IntegerField(_("金枪鱼进程ID"))
    cc_process_template_id = models.IntegerField(_("CC3.0进程模板ID"))

    class Meta:
        verbose_name = _("金枪鱼进程映射表")
        verbose_name_plural = _("金枪鱼进程映射表")


class MigrationStatus(models.Model):
    class MigrateObject(object):
        PROCESS = "process"
        CONFIG = "config"
        RELATION = "relation"
        PROCESS_INST = "process_inst"
        IAM = "iam"

    MIGRATE_OBJECT_CHOICES = (
        (MigrateObject.PROCESS, _("进程")),
        (MigrateObject.CONFIG, _("配置文件")),
        (MigrateObject.RELATION, _("绑定关系")),
        (MigrateObject.PROCESS_INST, _("进程实例")),
        (MigrateObject.IAM, _("权限")),
    )

    bk_biz_id = models.IntegerField(_("业务ID"))
    migrate_obj = models.CharField(_("迁移对象"), max_length=16, choices=MIGRATE_OBJECT_CHOICES)
    is_migrated = models.BooleanField(_("是否已迁移"), default=False)

    def complete_migration(self):
        self.is_migrated = True
        self.save()

    @classmethod
    def check_is_migrated(cls, bk_biz_id, migrate_obj):
        migrate_status, _ = MigrationStatus.objects.get_or_create(bk_biz_id=bk_biz_id, migrate_obj=migrate_obj)
        if migrate_status.is_migrated:
            raise AppBaseException(f"业务[{bk_biz_id}]已迁移[{migrate_obj}]，请勿重复操作")
        return migrate_status

    @staticmethod
    def set_migrate_status(migrate_object):
        """设置迁移状态装饰器"""

        def migrate_status_deco(func):
            @functools.wraps(func)
            def wrapped_func(*args, **kwargs):
                migrate_status = MigrationStatus.check_is_migrated(args[0].bk_biz_id, migrate_object)
                try:
                    func_return = func(*args, **kwargs)
                except Exception:
                    raise AppBaseException(traceback.format_exc())
                migrate_status.complete_migration()
                return func_return

            return wrapped_func

        return migrate_status_deco

    class Meta:
        verbose_name = _("迁移状态")
        verbose_name_plural = _("迁移状态")
