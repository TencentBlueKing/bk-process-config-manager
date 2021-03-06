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
# Generated by Django 2.2.6 on 2021-02-26 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gsekit", "0005_auto_20210118_1100"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobtask",
            name="err_code",
            field=models.IntegerField(db_index=True, default=-1, verbose_name="错误码"),
        ),
        migrations.AlterField(
            model_name="configinstance", name="is_latest", field=models.BooleanField(default=True, verbose_name="是否最新"),
        ),
        migrations.AlterField(
            model_name="configinstance",
            name="is_released",
            field=models.BooleanField(default=False, verbose_name="是否已发布"),
        ),
        migrations.AlterField(
            model_name="configtemplateversion",
            name="is_active",
            field=models.BooleanField(default=False, verbose_name="是否可用"),
        ),
        migrations.AlterField(
            model_name="configtemplateversion",
            name="is_draft",
            field=models.BooleanField(default=True, verbose_name="是否草稿"),
        ),
    ]
