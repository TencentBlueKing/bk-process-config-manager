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
import typing

from apps.gsekit import constants
from apps.gsekit.meta import models
from apps.utils.cache import func_cache_decorator


class GrayTools:
    @classmethod
    @func_cache_decorator(cache_time=20 * constants.TimeUnit.SECOND)
    def get_or_create_gse2_gray_scope_list(cls) -> typing.List[int]:
        """
        获取 GSE2.0 灰度列表
        :return:
        """
        gray_scope_list_or_none: typing.Optional[typing.List[int]] = models.GlobalSettings.get_config(
            models.GlobalSettings.KEYS.GSE2_GRAY_SCOPE_LIST, default=None
        )
        if gray_scope_list_or_none is not None:
            return gray_scope_list_or_none

        models.GlobalSettings.set_config(models.GlobalSettings.KEYS.GSE2_GRAY_SCOPE_LIST, [])
        return []

    def __init__(self):
        self.gse2_gray_scope_set: typing.Set[int] = set(self.get_or_create_gse2_gray_scope_list(get_cache=True))

    def is_gse2_gray(self, bk_biz_id: typing.Any) -> bool:
        """
        指定业务是否属于 GSE2.0 灰度
        :param bk_biz_id: 业务 ID
        :return:
        """
        return int(bk_biz_id) in self.gse2_gray_scope_set
