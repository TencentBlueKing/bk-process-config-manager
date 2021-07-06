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
from contextlib import ContextDecorator

from .patch import set_thread_id, in_user_code_thread_ids


class MakoSandbox(ContextDecorator):
    def __init__(self, *args, **kwargs):
        self.thread_id = set_thread_id()

    def __enter__(self, *args, **kwargs):
        in_user_code_thread_ids.append(self.thread_id)

    def __exit__(self, exc_type, exc_value, traceback):
        in_user_code_thread_ids.remove(self.thread_id)
