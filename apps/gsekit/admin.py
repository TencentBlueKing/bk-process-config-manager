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

from apps.gsekit.configfile import admin as configfile_admin
from apps.gsekit.process import admin as process_admin
from apps.gsekit.job import admin as job_admin
from apps.gsekit.meta import admin as meta_admin

__all__ = ["configfile_admin", "process_admin", "job_admin", "meta_admin"]

try:
    from apps.gsekit.migrate import admin as migrate_admin  # noqa
except ImportError:
    pass
else:
    __all__.append("migrate_admin")

try:
    from apps.gsekit.adapters.bscp import admin as bscp_admin  # noqa
except ImportError:
    pass
else:
    __all__.append("bscp_admin")
