# -*- coding: utf-8 -*-
"""SET svs tables as UNLOGGED to improve insertion performance."""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

if not settings.IS_TESTING:
    operations = (
        [
            migrations.RunSQL("ALTER TABLE svs_structuralvariant SET UNLOGGED;"),
            migrations.RunSQL("ALTER TABLE svs_structuralvariantgeneannotation SET UNLOGGED;"),
        ]
        + [
            migrations.RunSQL("ALTER TABLE svs_structuralvariant%d SET UNLOGGED;" % i)
            for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
        ]
        + [
            migrations.RunSQL("ALTER TABLE svs_structuralvariantgeneannotation%d SET UNLOGGED;" % i)
            for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
        ]
    )
else:
    operations = []


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("svs", "0007_partition_sv_tables")]

    operations = operations
