# -*- coding: utf-8 -*-
"""Adjust the small variants statistics materialized view to the new schema.

This is done by recreating it.
"""

from django.conf import settings
from django.db import migrations, models

operations = [
    migrations.DeleteModel(name="SmallVariantSummary"),
    migrations.CreateModel(
        name="SmallVariantSummary",
        fields=[
            (
                "id",
                models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                ),
            ),
            ("release", models.CharField(max_length=32)),
            ("chromosome", models.CharField(max_length=32)),
            ("start", models.IntegerField()),
            ("end", models.IntegerField()),
            ("bin", models.IntegerField()),
            ("reference", models.CharField(max_length=512)),
            ("alternative", models.CharField(max_length=512)),
            ("count_hom_ref", models.IntegerField()),
            ("count_het", models.IntegerField()),
            ("count_hom_alt", models.IntegerField()),
            ("count_hemi_ref", models.IntegerField()),
            ("count_hemi_alt", models.IntegerField()),
        ],
        options={"db_table": "variants_smallvariantsummary", "managed": settings.IS_TESTING},
    ),
]

if not settings.IS_TESTING:
    operations.append(
        migrations.RunSQL(
            """
            DROP MATERIALIZED VIEW variants_smallvariantsummary;

            CREATE MATERIALIZED VIEW variants_smallvariantsummary
            AS
                SELECT
                    row_number() OVER (PARTITION BY true) AS id,
                    release,
                    chromosome,
                    start,
                    "end",
                    bin,
                    reference,
                    alternative,
                    sum(num_hom_ref) AS count_hom_ref,
                    sum(num_het) AS count_het,
                    sum(num_hom_alt) AS count_hom_alt,
                    sum(num_hemi_ref) AS count_hemi_ref,
                    sum(num_hemi_alt) AS count_hemi_alt
                FROM (
                    SELECT DISTINCT
                        variants.release,
                        variants.chromosome,
                        variants.start,
                        variants."end",
                        variants.bin,
                        variants.reference,
                        variants.alternative,
                        variants.num_hom_ref,
                        variants.num_het,
                        variants.num_hom_alt,
                        variants.num_hemi_ref,
                        variants.num_hemi_alt,
                        variants.case_id
                    FROM variants_smallvariant AS variants
                ) AS variants_per_case
                GROUP BY (release, chromosome, start, "end", bin, reference, alternative)
            WITH DATA;

            CREATE UNIQUE INDEX variants_smallvariantsummary_id ON variants_smallvariantsummary(id);
            CREATE INDEX variants_smallvariantsummary_coord ON variants_smallvariantsummary(
                release, chromosome, start, "end", bin, reference, alternative
            );
            """,
            """
            DROP MATERIALIZED VIEW variants_smallvariantsummary;
            """,
        )
    )


class Migration(migrations.Migration):

    dependencies = [("variants", "0043_synccaselistbgjob_synccaseresultmessage")]

    operations = operations
