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

from django.db.models import Q

from apps.gsekit.configfile.models import ConfigTemplate
from iam import PathEqDjangoQuerySetConverter
from iam.resource.provider import ResourceProvider, ListResult


class BaseResourceProvider(ResourceProvider, metaclass=abc.ABCMeta):
    def list_attr(self, **options):
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        return ListResult(results=[], count=0)


class ConfigTemplateResourceProvider(BaseResourceProvider):
    def list_instance(self, filter, page, **options):
        queryset = ConfigTemplate.objects.none()
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = ConfigTemplate.objects.all()
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = ConfigTemplate.objects.filter(bk_biz_id=str(parent_id))

        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True

            keywords = filter.search.get("collection", [])

            q_filter = Q()
            for keyword in keywords:
                q_filter |= Q(template_name__icontains=keyword)

            queryset = ConfigTemplate.objects.filter(q_filter)
        if not with_path:
            results = [
                {"id": str(item.pk), "display_name": item.template_name}
                for item in queryset[page.slice_from : page.slice_to]
            ]
        else:
            results = [
                {
                    "id": str(item.pk),
                    "display_name": item.template_name,
                    "_bk_iam_path_": [
                        [{"type": "biz", "id": str(item.bk_biz_id), "display_name": str(item.bk_biz_id)}]
                    ],
                }
                for item in queryset[page.slice_from : page.slice_to]
            ]
        return ListResult(results=results, count=queryset.count())

    def fetch_instance_info(self, filter, **options):

        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        queryset = ConfigTemplate.objects.filter(pk__in=ids)

        results = [{"id": str(item.pk), "display_name": item.template_name} for item in queryset]
        return ListResult(results=results, count=queryset.count())

    def list_instance_by_policy(self, filter, page, **options):

        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        key_mapping = {
            "collection.id": "pk",
            "collection.owner": "created_by",
            "collection._bk_iam_path_": "bk_biz_id",
        }
        converter = PathEqDjangoQuerySetConverter(key_mapping, {"bk_biz_id": lambda value: value[1:-1].split(",")[1]})
        filters = converter.convert(expression)
        queryset = ConfigTemplate.objects.filter(filters)
        results = [
            {"id": str(item.pk), "display_name": item.template_name}
            for item in queryset[page.slice_from : page.slice_to]
        ]
        return ListResult(results=results, count=queryset.count())
