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
import sys

from django.apps import AppConfig
from django.conf import settings
from django.db import IntegrityError

from apps import BluekingInstrumentor

logger = logging.getLogger("app")


class BackendConfig(AppConfig):
    name = "apps.gsekit"
    verbose_name = "Gsekit"

    def ready(self):
        if settings.ENABLE_OTEL_TRACE:
            BluekingInstrumentor().instrument()

        self.connect_signals()

        # 没migrate之前，无法执行 fetch_esb_api_key, 直接返回
        for argv in sys.argv:
            if "manage.py" in argv:
                return
        self.fetch_esb_api_key()

    @staticmethod
    def connect_signals():
        from pipeline.eri.signals import post_set_state

        from apps.gsekit.pipeline_plugins.signals import bamboo_engine_eri_post_set_state_handler

        post_set_state.connect(bamboo_engine_eri_post_set_state_handler, dispatch_uid="_post_set_state")

    @staticmethod
    def fetch_esb_api_key():
        from blueapps.utils import get_client_by_user
        from apps.gsekit.meta.models import GlobalSettings

        if settings.IS_LOCAL:
            return

        if hasattr(settings, "APIGW_PUBLIC_KEY"):
            return

        public_key = GlobalSettings.jwt_public_key()
        if public_key:
            # 从数据库取公钥，若存在，直接使用
            settings.APIGW_PUBLIC_KEY = public_key
            message = "[ESB][JWT]get esb api public key success (from db cache)"
            # flush=True 实时刷新输出
            print(message, flush=True)
            logger.info(message)
        else:
            client = get_client_by_user(user_or_username=settings.BK_ADMIN_USERNAME)
            esb_result = client.esb.get_api_public_key()
            if esb_result["result"]:
                api_public_key = esb_result["data"]["public_key"]
                settings.APIGW_PUBLIC_KEY = api_public_key
                # 获取到公钥之后回写DB
                try:
                    GlobalSettings.objects.create(key=GlobalSettings.KEYS.APIGW_PUBLIC_KEY, v_json=api_public_key)
                except IntegrityError:
                    pass
                message = "[ESB][JWT]get esb api public key success (from realtime api)"
                print(message, flush=True)
                logger.info(message)
            else:
                message = f'[ESB][JWT]get esb api public key error:{esb_result["message"]}'
                print(message, flush=True)
                logger.warning(message)
                return
