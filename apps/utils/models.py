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
import bz2
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.utils.local import get_request_username


def model_to_dict(instance, fields=None, exclude=None):
    """Return django model Dict, Override django model_to_dict: <foreignkey use column as key>"""
    opts = instance._meta
    data = {}
    from itertools import chain

    for field in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if fields and field.name not in fields:
            continue
        if exclude and field.name in exclude:
            continue
        if field.get_internal_type() == "ForeignKey":
            field.name = field.column
        # if f.choices:
        #     data[f'{f.name}_display'] = getattr(instance, f'get_{f.name}_display')()

        data[field.name] = field.value_from_object(instance)
        if isinstance(data[field.name], datetime):
            data[field.name] = str(data[field.name])

    return data


def queryset_to_dict_list(queryset):
    if queryset is None:
        return []
    return [model_to_dict(instance) for instance in queryset]


class OperateRecordQuerySet(models.query.QuerySet):
    """
    批量更新时写入更新时间和更新者
    """

    def update(self, **kwargs):
        # 是否跳过更新时间或更新人，某些特殊场景下使用
        skip_update_time = kwargs.pop("skip_update_time", False)
        skip_update_user = kwargs.pop("skip_update_user", False)
        kwargs.update({"updated_at": timezone.now(), "updated_by": get_request_username()})
        if skip_update_time:
            kwargs.pop("updated_at", "")
        if skip_update_user:
            kwargs.pop("updated_by", "")
        super().update(**kwargs)


class OperateRecordModelManager(models.Manager):
    def get_queryset(self):
        return OperateRecordQuerySet(self.model, using=self._db)

    def create(self, *args, **kwargs):
        kwargs.update(
            {
                "created_at": kwargs.get("created_at", timezone.now()),
                "created_by": kwargs.get("created_by", get_request_username()),
                "updated_at": kwargs.get("updated_at", timezone.now()),
                "updated_by": kwargs.get("updated_by", get_request_username()),
            }
        )
        return super().create(*args, **kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        for obj in objs:
            obj.created_at = obj.created_at or timezone.now()
            obj.created_by = obj.created_by or get_request_username()
            obj.updated_at = obj.updated_at or timezone.now()
            obj.updated_by = obj.updated_by or get_request_username()
        return super().bulk_create(objs, *args, **kwargs)


class OperateRecordModel(models.Model):
    """
    需要记录操作的model父类
    自动记录创建时间/修改时间与操作者
    """

    objects = OperateRecordModelManager()

    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    created_by = models.CharField(_("创建者"), max_length=32, default="")
    updated_at = models.DateTimeField(_("更新时间"), blank=True, null=True, auto_now=True)
    updated_by = models.CharField(_("修改者"), max_length=32, blank=True, default="")

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.created_at = timezone.now()
            self.created_by = get_request_username()

        self.updated_at = timezone.now()
        self.updated_by = get_request_username()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.query.QuerySet):
    def delete(self):
        self.update(is_deleted=True, deleted_by=get_request_username(), deleted_at=timezone.now())


class SoftDeleteModelManager(OperateRecordModelManager):
    """
    默认的查询和过滤方法, 不显示被标记为删除的记录
    """

    def all(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        return super(SoftDeleteModelManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        if not kwargs.get("is_deleted"):
            kwargs["is_deleted"] = False
        return super(SoftDeleteModelManager, self).filter(*args, **kwargs)

    def get(self, *args, **kwargs):
        # 默认都不显示被标记为删除的数据
        if not kwargs.get("is_deleted"):
            kwargs["is_deleted"] = False
        return super(SoftDeleteModelManager, self).get(*args, **kwargs)

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(OperateRecordModel):
    """
    需要记录删除操作的model父类
    自动记录删除时间与删除者
    对于此类的表提供软删除
    """

    objects = SoftDeleteModelManager()

    is_deleted = models.BooleanField(_("是否删除"), default=False)
    deleted_at = models.DateTimeField(_("删除时间"), blank=True, null=True)
    deleted_by = models.CharField(_("删除者"), max_length=32, blank=True, null=True)

    def delete(self, *args, **kwargs):
        """
        删除方法，不会删除数据
        而是通过标记删除字段 is_deleted 来软删除
        """
        self.is_deleted = True
        self.deleted_by = get_request_username()
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True


class CompressedTextField(models.BinaryField):
    """
    model Fields for storing text in a compressed format (bz2 by default)
    """

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        try:
            return bz2.decompress(value)
        except (TypeError, OSError, AttributeError):
            return value

    def get_prep_value(self, value):
        try:
            return bz2.compress(value.encode())
        except (TypeError, OSError, AttributeError):
            return value
