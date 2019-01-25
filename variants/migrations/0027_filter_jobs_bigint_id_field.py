# -*- coding: utf-8 -*-
"""Make the id field of SmallVariant a large integer top prevent problems with too high sequence counts.
"""
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("variants", "0026_auto_20190128_1210")]

    operations = [
        migrations.RunSQL(
            r"""ALTER TABLE "variants_smallvariantquery_query_results" ALTER COLUMN "id" TYPE bigint USING "id"::bigint"""
        ),
        migrations.RunSQL(
            r"""ALTER TABLE "variants_smallvariantquery_query_results" ALTER COLUMN "smallvariant_id" TYPE bigint USING "smallvariant_id"::bigint"""
        ),
        migrations.RunSQL(
            r"""ALTER TABLE "variants_projectcasessmallvariantquery_query_results" ALTER COLUMN "id" TYPE bigint USING "id"::bigint"""
        ),
        migrations.RunSQL(
            r"""ALTER TABLE "variants_projectcasessmallvariantquery_query_results" ALTER COLUMN "smallvariant_id" TYPE bigint USING "smallvariant_id"::bigint"""
        ),
    ]
