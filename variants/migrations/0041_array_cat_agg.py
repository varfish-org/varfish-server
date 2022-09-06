"""Add variant counts to the ``Case`` class.

Update all existing case"""
from __future__ import unicode_literals

from django.db import connection, migrations

POSTGRES_VERSION = connection.cursor().connection.server_version
ARRAY_TYPE = "anyarray" if POSTGRES_VERSION < 140000 else "anycompatiblearray"


class Migration(migrations.Migration):

    dependencies = [("variants", "0040_case_variant_counts")]

    operations = [
        migrations.RunSQL(
            """
            CREATE AGGREGATE array_cat_agg({array_type}) (
                SFUNC=array_cat,
                STYPE={array_type}
            );
            """.format(
                array_type=ARRAY_TYPE
            ),
            """
            DROP AGGREGATE array_cat_agg({array_type});
            """.format(
                array_type=ARRAY_TYPE
            ),
        )
    ]
