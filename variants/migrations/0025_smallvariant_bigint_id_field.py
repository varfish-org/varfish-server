# -*- coding: utf-8 -*-
"""Make the id field of SmallVariant a large integer top prevent problems with too high sequence counts.
"""
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("variants", "0024_auto_20181130_0822")]

    operations = [
        migrations.RunSQL(
            r"""ALTER TABLE "variants_smallvariant" ALTER COLUMN "id" TYPE bigint USING "id"::bigint"""
        )
    ]
