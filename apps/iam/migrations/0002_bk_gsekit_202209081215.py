# -*- coding: utf-8 -*-

from django.db import migrations

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "initial.json"

    dependencies = [("iam", "0001_initial")]

    operations = [migrations.RunPython(forward_func)]
