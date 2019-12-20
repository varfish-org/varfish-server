# -*- coding: utf-8 -*-
"""Rename tables to make consistent again."""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

if not settings.IS_TESTING:
    operations = [
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS svs_structuralvariant%d RENAME TO svs_structuralvariant_%d;"
            % (i, i)
        )
        for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
    ] + [
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS svs_structuralvariantgeneannotation%d RENAME TO svs_structuralvariantgeneannotation_%d;"
            % (i, i)
        )
        for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
    ]
else:
    operations = []


class Migration(migrations.Migration):

    dependencies = [("svs", "0010_set_logged_table")]

    operations = []
