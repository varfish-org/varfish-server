# -*- coding: utf-8 -*-
"""SET small variant table as UNLOGGED to improve insertion performance."""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

if not settings.IS_TESTING:
    operations = [migrations.RunSQL("ALTER TABLE variants_smallvariant SET UNLOGGED;")] + [
        migrations.RunSQL("ALTER TABLE variants_smallvariant_%d SET UNLOGGED" % i)
        for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
    ]
else:
    operations = []


class Migration(migrations.Migration):

    dependencies = [("variants", "0053_auto_20190809_1636")]

    operations = operations
