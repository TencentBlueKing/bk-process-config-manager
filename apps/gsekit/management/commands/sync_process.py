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


from django.core.management.base import BaseCommand

from apps.gsekit.periodic_tasks.sync_process import sync_process


class Command(BaseCommand):
    def handle(self, **kwargs):
        bk_biz_id = kwargs.get("bk_biz_id")
        sync_process(bk_biz_id)

    def add_arguments(self, parser):

        parser.add_argument("-b", help="业务ID，可选，不传入则同步所有业务", default=None)
