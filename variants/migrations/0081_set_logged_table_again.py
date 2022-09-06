# -*- coding: utf-8 -*-
"""SET small variant table as LOGGED to improve stability (#2)."""
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations

if not settings.IS_TESTING:
    operations = [migrations.RunSQL("ALTER TABLE variants_smallvariant SET LOGGED;")] + [
        migrations.RunSQL("ALTER TABLE variants_smallvariant_%d SET LOGGED" % i)
        for i in range(settings.VARFISH_PARTITION_MODULUS_SMALLVARIANT)
    ]
else:
    operations = []


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("variants", "0080_spanrsubmissionbgjob")]

    operations = operations
