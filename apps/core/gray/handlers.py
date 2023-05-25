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
import logging
import typing
from apps.gsekit.meta import models


from .tools import GrayTools

logger = logging.getLogger("app")


class GrayHandler:
    @classmethod
    def update_gray_scope_list(cls, validated_data: typing.Dict[str, typing.List[typing.Any]], rollback: bool = False):
        # 使用最新的灰度列表进行更新，不走缓存
        gray_scope_list: typing.List[int] = GrayTools.get_or_create_gse2_gray_scope_list(get_cache=False)
        if rollback:
            # 将业务从灰度列表中去除
            gray_scope_list: typing.List[int] = list(set(gray_scope_list) - set(validated_data["bk_biz_ids"]))
            logger.info(f"[update_gray_scope_list][rollback={rollback}] {set(validated_data['bk_biz_ids'])}")
        else:
            # 记录灰度业务
            gray_scope_list.extend(validated_data["bk_biz_ids"])
            logger.info(
                f"[update_gray_scope_list][rollback={rollback}] bk_biz_ids -> {set(validated_data['bk_biz_ids'])}"
            )

        models.GlobalSettings.update_config(models.GlobalSettings.KEYS.GSE2_GRAY_SCOPE_LIST, list(set(gray_scope_list)))
        logger.info(f"[update_gray_scope_list][rollback={rollback}] commit to db")

        # 触发一次缓存主动更新
        GrayTools.get_or_create_gse2_gray_scope_list(get_cache=False)
        logger.info("[update_gray_scope_list][rollback={rollback}] flush cache")

    @classmethod
    def build(cls, validated_data: typing.Dict[str, typing.List[typing.Any]]):
        # 更新灰度业务范围
        cls.update_gray_scope_list(validated_data)

        return validated_data

    @classmethod
    def rollback(cls, validated_data: typing.Dict[str, typing.List[typing.Any]]):
        # 更新灰度业务范围
        cls.update_gray_scope_list(validated_data, rollback=True)

        return validated_data

    @classmethod
    def list_biz_ids(cls) -> typing.List[int]:
        return GrayTools.get_or_create_gse2_gray_scope_list(get_cache=False)
