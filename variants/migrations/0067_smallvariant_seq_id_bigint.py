# -*- coding: utf-8 -*-
"""Make the id field of SmallVariant a large integer top prevent problems with too high sequence counts.
"""
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("variants", "0066_case_tags")]

    operations = [
        migrations.RunSQL(
            r"""ALTER SEQUENCE "variants_smallvariant_id_seq" AS bigint""",
            r"""ALTER SEQUENCE "variants_smallvariant_id_seq" AS integer""",
        ),
        migrations.RunSQL(
            r"""ALTER SEQUENCE "variants_smallvariantquery_query_results_id_seq" AS bigint""",
            r"""ALTER SEQUENCE "variants_smallvariantquery_query_results_id_seq" AS integer""",
        ),
        migrations.RunSQL(
            r"""ALTER SEQUENCE "variants_projectcasessmallvariantquery_query_results_id_seq" AS bigint""",
            r"""ALTER SEQUENCE "variants_projectcasessmallvariantquery_query_results_id_seq" AS integer""",
        ),
    ]
