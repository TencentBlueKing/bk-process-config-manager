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
# Generated by Django 2.2.6 on 2021-05-02 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gsekit", "0008_job_from_app_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="VisitCount",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bk_username", models.CharField(default="", max_length=32, verbose_name="用户名")),
                ("bk_biz_id", models.IntegerField(verbose_name="业务ID")),
                ("visit_time", models.DateTimeField(auto_now_add=True, verbose_name="访问时间")),
            ],
            options={"verbose_name": "用户访问统计", "verbose_name_plural": "用户访问统计"},
        ),
    ]
