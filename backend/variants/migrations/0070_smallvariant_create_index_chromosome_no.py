# -*- coding: utf-8 -*-
"""Setup ``variants_smallvariants`` table as partitioned.
"""

from django.conf import settings
from django.db import migrations

operations = []


if not settings.IS_TESTING:
    operations.append(
        migrations.RunSQL(
            r"""
            CREATE INDEX variants_sm_chromosome_no_idx ON variants_smallvariant USING btree (case_id, chromosome_no);
            """,
            """
            DROP INDEX variants_sm_chromosome_no_idx;
            """,
        )
    )


class Migration(migrations.Migration):
    dependencies = [("variants", "0069_set_logged_table")]
    operations = operations
