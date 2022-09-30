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
from collections import defaultdict
from typing import List, Dict, Set, Union

from django.db import models, transaction
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.exceptions import ValidationError
from apps.gsekit.constants import RE_WHITESPACE
from apps.gsekit.process.models import Process
from apps.utils.local import get_request_username
from apps.utils.models import OperateRecordModel, CompressedTextField


class ConfigTemplateVersion(OperateRecordModel):
    config_version_id = models.AutoField(_("模板版本ID"), primary_key=True)
    config_template_id = models.IntegerField(_("模板ID"), db_index=True)
    description = models.CharField(_("版本描述"), blank=True, default="", max_length=256)
    content = models.TextField(_("配置模板内容"), blank=True, default="")
    is_draft = models.BooleanField(_("是否草稿"), default=True)
    is_active = models.BooleanField(_("是否可用"), default=False)
    file_format = models.CharField(_("文件风格"), max_length=16, blank=True, null=True, default=None)

    @classmethod
    def get_latest_version_mapping(cls, template_ids: Union[Set[int], List[int]]) -> Dict:
        """根据模板ID查询最新的可用版本"""
        return {
            config_version.config_template_id: config_version
            for config_version in cls.objects.filter(config_template_id__in=template_ids, is_active=True)
        }

    class Meta:
        verbose_name = _("配置模板版本（ConfigTemplateVersion）")
        verbose_name_plural = _("配置模板版本（ConfigTemplateVersion）")
        ordering = ["-config_version_id"]


class ConfigTemplate(OperateRecordModel):
    class LineSeparator(object):
        CR = "CR"  # MacOs
        LF = "LF"  # Unix
        CRLF = "CRLF"  # Windows
        # CR = "\\r"  # MacOs
        # LF = "\\n"  # Unix
        # CRLF = "\\r\\n"  # Windows

    LINE_SEPARATOR_CHOICE = (
        (LineSeparator.CR, _("MacOs(\\r)")),
        (LineSeparator.LF, _("Unix(\\n)")),
        (LineSeparator.CRLF, _("Windows(\\r\\n)")),
    )

    config_template_id = models.AutoField(_("模板ID"), primary_key=True)
    bk_biz_id = models.IntegerField(_("业务ID"), db_index=True)
    template_name = models.CharField(_("模板名称"), max_length=32, db_index=True)
    file_name = models.CharField(_("文件名称"), max_length=64)
    abs_path = models.CharField(_("文件绝对路径"), max_length=256)
    owner = models.CharField(_("文件所有者"), max_length=32)
    group = models.CharField(_("文件归属群组"), max_length=32)
    filemode = models.CharField(_("文件权限"), max_length=8)
    line_separator = models.CharField(_("换行符格式"), max_length=8, choices=LINE_SEPARATOR_CHOICE)

    def save(self, *args, **kwargs):
        """保存前做校验"""
        from apps.gsekit.adapters import channel_adapter

        for non_whitespace_field in [self.template_name, self.file_name, self.owner, self.group]:
            if RE_WHITESPACE.search(non_whitespace_field):
                raise ValidationError(_("参数中不允许有空白字符"))
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self._state.adding:
                channel_adapter().post_create_config_template(self)
            else:
                channel_adapter().post_update_config_template(self)

    # 这类property注意不要在列表生成中使用，性能堪忧
    @property
    def relation_count(self):
        """关联进程数量"""
        binding_counts = (
            ConfigTemplateBindingRelationship.objects.filter(config_template_id=self.config_template_id)
            .values("config_template_id", "process_object_type")
            .annotate(relation_count=Count("config_template_id"))
        )
        data = {process_object_type_tup[0]: 0 for process_object_type_tup in Process.PROCESS_OBJECT_TYPE_CHOICE}
        for binding_count in binding_counts:
            data[binding_count["process_object_type"]] = binding_count["relation_count"]
        return data

    @property
    def is_bound(self):
        return bool(sum(self.relation_count.values()))

    @property
    def has_version(self):
        return ConfigTemplateVersion.objects.filter(config_template_id=self.config_template_id).exists()

    class Meta:
        verbose_name = _("配置模板（ConfigTemplate）")
        verbose_name_plural = _("配置模板（ConfigTemplate）")
        unique_together = ("bk_biz_id", "template_name")
        ordering = ["-config_template_id"]


class ConfigTemplateBindingRelationshipQuerySet(models.query.QuerySet):
    def delete(self):

        from apps.gsekit.adapters import channel_adapter

        with transaction.atomic():
            for obj in self:
                channel_adapter().post_delete_config_template_relation(obj)
            super().delete()


class ConfigTemplateBindingRelationshipManager(models.Manager):
    def bulk_create(self, objs, *args, **kwargs):
        """批量创建关系时需处理信号"""
        from apps.gsekit.adapters import channel_adapter

        for obj in objs:
            obj.created_at = timezone.now()
            obj.created_by = get_request_username()

        with transaction.atomic():
            objs = super().bulk_create(objs, *args, **kwargs)
            for obj in objs:
                channel_adapter().post_create_config_template_relation(obj)
        return objs

    def get_queryset(self):
        return ConfigTemplateBindingRelationshipQuerySet(self.model, using=self._db)


class ConfigTemplateBindingRelationship(OperateRecordModel):
    bk_biz_id = models.IntegerField(_("业务ID"), db_index=True)
    config_template_id = models.IntegerField(_("模板ID"), db_index=True)
    process_object_type = models.CharField(
        _("进程对象类型"), max_length=16, db_index=True, choices=Process.PROCESS_OBJECT_TYPE_CHOICE
    )
    process_object_id = models.IntegerField(_("进程实例ID/进程模板ID"), db_index=True)
    objects = ConfigTemplateBindingRelationshipManager()

    @classmethod
    def get_process_binding_config_template_ids(cls, bk_process_id: int, process_template_id: int) -> Set:
        """查询进程/进程模板绑定的配置模板"""
        template_relation_q = Q()
        if process_template_id:
            template_relation_q = Q(
                process_object_type=Process.ProcessObjectType.TEMPLATE,
                process_object_id=process_template_id,
            )

        config_template_ids = cls.objects.filter(
            Q(
                process_object_type=Process.ProcessObjectType.INSTANCE,
                process_object_id=bk_process_id,
            )
            | template_relation_q
        ).values_list("config_template_id", flat=True)
        return set(config_template_ids)

    @classmethod
    def get_config_template_relation_mapping(cls, config_template_ids: List[int]) -> Dict:
        relation_mapping = defaultdict(lambda: defaultdict(list))
        for relation in cls.objects.filter(config_template_id__in=config_template_ids):
            relation_mapping[relation.config_template_id][relation.process_object_type].append(
                relation.process_object_id
            )
        return relation_mapping

    class Meta:
        verbose_name = _("配置模板与进程的绑定关系（ConfigTemplateBindingRelationship）")
        verbose_name_plural = _("配置模板与进程的绑定关系（ConfigTemplateBindingRelationship）")


class ConfigInstance(models.Model):
    IDENTITY_KEY_TEMPLATE = "{bk_process_id}-{config_template_id}-{inst_id}"
    NOT_RELEASED_VERSION = "-"

    config_version_id = models.IntegerField(_("模板版本ID"), db_index=True)
    config_template_id = models.IntegerField(_("模板ID"), db_index=True)
    bk_process_id = models.IntegerField(_("进程实例ID"), db_index=True)
    inst_id = models.IntegerField(_("实例ID"), db_index=True)
    content = CompressedTextField(_("实例内容"))
    name = models.CharField(_("文件名"), max_length=64)
    path = models.CharField(_("文件绝对路径"), max_length=256)
    is_latest = models.BooleanField(_("是否最新"), default=True)
    is_released = models.BooleanField(_("是否已发布"), default=False)
    sha256 = models.CharField(_("SHA256"), max_length=64)
    expression = models.CharField(_("实例表达式"), max_length=256)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    created_by = models.CharField(_("创建者"), max_length=32, default="")

    class Status(object):
        GENERATED = "generated"
        NOT_GENERATED = "not_generated"
        NOT_LATEST = "not_latest"

    CONFIG_INSTANCE_STATUS_CHOICE = (
        (Status.GENERATED, _("已生成")),
        (Status.NOT_GENERATED, _("未生成")),
        (Status.NOT_LATEST, _("非最新")),
    )

    @classmethod
    def get_config_template_latest_version_process_mapping(cls, config_version_ids_map: List[Dict]) -> Dict:
        """
        查询配置模板非最新版本对应的进程映射关系
        :param config_version_ids_map: [{'config_template_id': 1, 'config_version_ids': [2, 3]}]
        :return:
        """
        version_process_mapping = defaultdict(set)
        config_template_ids = []
        config_version_ids = []
        for config in config_version_ids_map:
            config_template_ids.append(config["config_template_id"])
            config_version_ids.extend(config["config_version_ids"])

        filter_conditions = dict(config_template_id__in=config_template_ids)
        if config_version_ids:
            filter_conditions.update(config_version_id__in=config_version_ids)

        # 查询配置实例对应生成的进程的最新版本映射
        # order_by() 用于去除 ConfigInstance 默认排序对分组的影响
        process_latest_config_version_map = {
            "{}-{}-{}".format(
                config_instance["bk_process_id"], config_instance["inst_id"], config_instance["config_template_id"]
            ): config_instance["max_version_id"]
            for config_instance in cls.objects.filter(config_template_id__in=config_template_ids, is_released=True)
            .order_by()
            .values("bk_process_id", "inst_id", "config_template_id")
            .annotate(max_version_id=Max("config_version_id"))
        }

        if cls.NOT_RELEASED_VERSION in config_version_ids:
            # 选择了未下发的版本，追加未下发的版本
            for config_instance in cls.objects.filter(
                config_template_id__in=config_template_ids, is_latest=True, is_released=False
            ).values("bk_process_id", "inst_id", "config_template_id"):
                key = "{}-{}-{}".format(
                    config_instance["bk_process_id"], config_instance["inst_id"], config_instance["config_template_id"]
                )
                if key not in process_latest_config_version_map:
                    process_latest_config_version_map[key] = cls.NOT_RELEASED_VERSION
                    version_process_mapping[config_instance["config_template_id"]].add(config_instance["bk_process_id"])
            config_version_ids.remove(cls.NOT_RELEASED_VERSION)

        for config_instance in cls.objects.filter(**filter_conditions).values(
            "config_template_id", "config_version_id", "bk_process_id", "inst_id"
        ):
            key = (
                f'{config_instance["bk_process_id"]}-'
                f'{config_instance["inst_id"]}-{config_instance["config_template_id"]}'
            )
            if process_latest_config_version_map.get(key) in config_version_ids:
                version_process_mapping[config_instance["config_template_id"]].add(config_instance["bk_process_id"])
        return version_process_mapping

    @property
    def identity_key(self):
        """标识key"""
        return self.IDENTITY_KEY_TEMPLATE.format(
            bk_process_id=self.bk_process_id, config_template_id=self.config_template_id, inst_id=self.inst_id
        )

    class Meta:
        verbose_name = _("配置实例（ConfigInstance）")
        verbose_name_plural = _("配置实例（ConfigInstance）")
        ordering = ["-id"]


class ConfigSnapshot(OperateRecordModel):
    config_instance_id = models.BigIntegerField(_("配置实例 ID"), db_index=True)
    job_instance_id = models.BigIntegerField(_("作业实例ID"), db_index=True)
    content = CompressedTextField(_("快照内容"))
    sha256 = models.CharField(_("SHA256"), max_length=64)

    class Meta:
        verbose_name = _("现网配置快照（ConfigSnapshot）")
        verbose_name_plural = _("现网配置快照（ConfigSnapshot）")
