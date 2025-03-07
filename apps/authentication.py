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
from blueapps.account import get_user_model

from common.log import logger
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser


class ApiGatewayJWTUserModelBackend(ModelBackend):
    """Get users by username"""

    def user_maker(self, bk_username):
        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(defaults={"nickname": bk_username}, username=bk_username)
        except Exception:
            logger.exception(f"[{self.__class__.__name__}] Failed to get_or_create user -> {bk_username}.")
            return None
        else:
            logger.info(f"test-user{user.username}, {user.is_superuser}")
            return user

    def make_anonymous_user(self, bk_username=None):
        user = AnonymousUser()
        user.username = bk_username  # type: ignore
        return user

    def authenticate(self, request, gateway_name, bk_username, verified, **credentials):
        if not verified:
            return self.make_anonymous_user(bk_username=bk_username)

        return self.user_maker(bk_username)
