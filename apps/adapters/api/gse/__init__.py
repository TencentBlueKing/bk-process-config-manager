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

from apps.api import GseApi, GseV2Api
from common.log import logger
from env import constants

from .base import GseApiBaseHelper
from .v1 import GseV1ApiHelper
from .v2 import GseV2ApiHelper

GSE_HELPERS: typing.Dict[str, typing.Type[GseApiBaseHelper]] = {
    constants.GseVersion.V1.value: GseV1ApiHelper,
    constants.GseVersion.V2.value: GseV2ApiHelper,
}


def get_gse_api_helper(gse_version: str) -> GseApiBaseHelper:
    if gse_version not in GSE_HELPERS:
        logger.warning(
            f"Get GseApiHelper failed: "
            f"unsupported gse_version -> {gse_version}, options -> {GSE_HELPERS.values()}; "
            f"use default -> {constants.GseVersion.V1.value}"
        )
        gse_version = constants.GseVersion.V1.value
    return GSE_HELPERS[gse_version](
        version=gse_version, gse_api_obj=[GseV2Api, GseApi][gse_version == constants.GseVersion.V1.value]
    )
