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

import abc
import json
from typing import List

from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy

from apps.iam.exceptions import ResourceNotExistError
from iam import Resource


class ResourceMeta(metaclass=abc.ABCMeta):
    """
    资源定义
    """

    system_id: str = ""
    id: str = ""
    lookup_field: str = None
    name: str = ""
    selection_mode: str = ""
    related_instance_selections: List = ""

    @classmethod
    def to_json(cls):
        return {
            "system_id": cls.system_id,
            "id": cls.id,
            "lookup_field": cls.lookup_field,
            "selection_mode": cls.selection_mode,
            "related_instance_selections": cls.related_instance_selections,
        }

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        """
        创建简单资源实例
        :param instance_id: 实例ID
        :param attribute: 属性kv对
        """
        attribute = attribute or {}
        if "bk_biz_id" in attribute:
            # 补充路径信息
            attribute.update({"_bk_iam_path_": "/{},{}/".format(Business.id, attribute["bk_biz_id"])})
        return Resource(cls.system_id, cls.id, str(instance_id), attribute)

    @classmethod
    def create_instance(cls, instance_id: str, attribute=None) -> Resource:
        """
        创建资源实例（带实例名称）可由子类重载
        :param instance_id: 实例ID
        :param attribute: 属性kv对
        """
        return cls.create_simple_instance(instance_id, attribute)


class Business(ResourceMeta):
    """
    CMDB业务
    """

    system_id = "bk_cmdb"
    id = "biz"
    lookup_field = "bk_biz_id"
    name = _lazy("业务")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "business", "ignore_iam_path": True}]

    @classmethod
    def create_instance(cls, instance_id: str, attribute=None) -> Resource:

        resource = cls.create_simple_instance(instance_id, attribute)

        bk_biz_name = str(instance_id)

        resource.attribute = {"id": str(instance_id), "name": bk_biz_name}
        return resource


class ConfigTemplate(ResourceMeta):
    """
    配置模板
    """

    system_id = settings.BK_IAM_SYSTEM_ID
    id = "config_template"
    name = _lazy("配置模板")
    selection_mode = "instance"
    related_instance_selections = [{"system_id": system_id, "id": "config_template_list", "ignore_iam_path": True}]

    @classmethod
    def create_simple_instance(cls, instance_id: str, attribute=None) -> Resource:
        from apps.gsekit.configfile.models import ConfigTemplate

        resource = super().create_simple_instance(instance_id, attribute)
        if resource.attribute:
            return resource

        try:
            config = ConfigTemplate.objects.get(pk=instance_id)
        except ConfigTemplate.DoesNotExist:
            return resource
        resource.attribute = {
            "id": str(instance_id),
            "name": config.template_name,
            "bk_biz_id": config.bk_biz_id,
            "_bk_iam_path_": "/{},{}/".format(Business.id, config.bk_biz_id),
        }
        return resource


class ResourceEnum:
    """
    资源类型枚举
    """

    BUSINESS = Business
    CONFIG_TEMPLATE = ConfigTemplate


_all_resources = {resource.id: resource for resource in ResourceEnum.__dict__.values() if hasattr(resource, "id")}


def get_resource_by_id(resource_id: str) -> ResourceMeta:
    """
    根据资源ID获取资源
    """
    if resource_id not in _all_resources:
        raise ResourceNotExistError(_("资源ID不存在：{resource_id}").format(resource_id=resource_id))

    return _all_resources[resource_id]


def generate_all_resources_json() -> List:
    """
    生成migrations的json配置
    """
    results = []
    for value in _all_resources.values():
        results.append({"operation": "upsert_action", "data": value.to_json()})
    print(json.dumps(results, ensure_ascii=False, indent=4))
    return results
