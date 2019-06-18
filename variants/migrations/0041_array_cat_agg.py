"""Add variant counts to the ``Case`` class.

Update all existing case"""
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("variants", "0040_case_variant_counts")]

    operations = [
        migrations.RunSQL(
            """
            CREATE AGGREGATE array_cat_agg(anyarray) (
                SFUNC=array_cat,
                STYPE=anyarray
            );
            """,
            """
            DROP AGGREGATE array_cat_agg(anyarray);
            """,
        )
    ]
