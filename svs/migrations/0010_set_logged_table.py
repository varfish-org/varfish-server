# -*- coding: utf-8 -*-
"""SET svs tables as LOGGED against data loss."""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

if not settings.IS_TESTING:
    operations = (
        [
            migrations.RunSQL("ALTER TABLE svs_structuralvariant SET LOGGED;"),
            migrations.RunSQL("ALTER TABLE svs_structuralvariantgeneannotation SET LOGGED;"),
        ]
        + [
            migrations.RunSQL("ALTER TABLE svs_structuralvariant%d SET LOGGED;" % i)
            for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
        ]
        + [
            migrations.RunSQL("ALTER TABLE svs_structuralvariantgeneannotation%d SET LOGGED;" % i)
            for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
        ]
    )
else:
    operations = []


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("svs", "0009_auto_20191017_0853"),
    ]

    operations = []
