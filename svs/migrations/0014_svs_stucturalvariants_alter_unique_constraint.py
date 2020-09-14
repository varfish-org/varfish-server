# -*- coding: utf-8 -*-
"""Setup ``svs`` tables as partitioned.
"""

from django.db import migrations
from django.conf import settings

operations = []

if not settings.IS_TESTING:
    operations.append(
        migrations.RunSQL(
            r"""
            ALTER TABLE ONLY svs_structuralvariant
                DROP CONSTRAINT svs_structuralvariant_sv_uuid_key;
            ALTER TABLE ONLY svs_structuralvariant
                ADD CONSTRAINT svs_structuralvariant_sv_uuid_key UNIQUE (sv_uuid, case_id, set_id);
            """,
            r"""
            ALTER TABLE ONLY svs_structuralvariant
                DROP CONSTRAINT svs_structuralvariant_sv_uuid_key;
            ALTER TABLE ONLY svs_structuralvariant
                ADD CONSTRAINT svs_structuralvariant_sv_uuid_key UNIQUE (sv_uuid, case_id);
            """,
        )
    )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("svs", "0013_auto_20200909_1401")]

    operations = operations
