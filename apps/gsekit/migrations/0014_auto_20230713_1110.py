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

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gsekit", "0013_alter_job_job_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="process",
            name="bk_agent_id",
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name="AgentID"),
        ),
        migrations.AddField(
            model_name="process",
            name="bk_host_innerip_v6",
            field=models.GenericIPAddressField(blank=True, db_index=True, null=True, verbose_name="主机IPv6"),
        ),
        migrations.AlterField(
            model_name="job",
            name="bk_app_code",
            field=models.CharField(default="bk_gsekit", max_length=32, verbose_name="蓝鲸应用ID"),
        ),
        migrations.AlterField(
            model_name="process",
            name="bk_host_innerip",
            field=models.GenericIPAddressField(blank=True, db_index=True, null=True, verbose_name="主机IP"),
        ),
    ]
