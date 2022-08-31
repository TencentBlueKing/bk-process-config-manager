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
import os
from django.conf import settings

ESB_PREFIX = "/api/c/compapi/v2/"

APIGATEWAY_ROOT_PREFIX_FORMAT = "{}{}{{}}/".format(settings.BK_COMPONENT_API_OVERWRITE_URL, ESB_PREFIX)

CC_APIGATEWAY_ROOT = os.getenv("BKAPP_CC_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("cc")
JOB_APIGATEWAY_ROOT_V3 = os.getenv("BKAPP_JOB_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("jobv3")
ESB_APIGATEWAY_ROOT = os.getenv("BKAPP_ESB_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("esb")
GSE_APIGATEWAY_ROOT = os.getenv("BKAPP_GSE_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("gse")
USER_MANAGE_APIGATEWAY_ROOT = os.getenv("BKAPP_USERMANAGE_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format(
    "usermanage"
)
CMSI_APIGATEWAY_ROOT = os.getenv("BKAPP_GSE_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("cmsi")
BK_NODE_APIGATEWAY_ROOT = os.getenv("BKAPP_BK_NODE_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("nodeman")
BSCP_APIGATEWAY_ROOT = os.getenv("BKAPP_BSCP_APIGATEWAY_ROOT") or APIGATEWAY_ROOT_PREFIX_FORMAT.format("bscp")
BSCP_DIRECT_ROOT = os.getenv("BKAPP_BSCP_DIRECT_ROOT") or "http://bscp.service.consul:8080"
