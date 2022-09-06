# -*- coding: utf-8 -*-
"""Adjust the small variants statistics materialized view to not use excluded cases.

This is done by recreating it.
"""

from django.conf import settings
from django.db import migrations

SQL_OUTER = r"""
DROP MATERIALIZED VIEW IF EXISTS variants_smallvariantsummary;

CREATE MATERIALIZED VIEW variants_smallvariantsummary
AS
    %s
WITH NO DATA;

CREATE UNIQUE INDEX variants_smallvariantsummary_id ON variants_smallvariantsummary(id);
CREATE INDEX variants_smallvariantsummary_coord ON variants_smallvariantsummary(
    release, chromosome, start, "end", bin, reference, alternative
);
"""

SQL_INNER_FORWARD = r"""
WITH excluded_case_ids AS (
    SELECT DISTINCT variants_case.id AS case_id
    FROM variants_case
    JOIN projectroles_project ON variants_case.project_id = projectroles_project.id
    JOIN projectroles_appsetting ON
        projectroles_project.id = projectroles_appsetting.project_id AND
        projectroles_appsetting.name = 'exclude_from_inhouse_db' AND
        projectroles_appsetting.value = '1'
)
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
    WHERE NOT EXISTS (SELECT 1 from excluded_case_ids AS e WHERE e.case_id = variants.case_id)
) AS variants_per_case
GROUP BY (release, chromosome, start, "end", bin, reference, alternative)
"""

SQL_INNER_REVERSE = r"""
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
"""

if settings.IS_TESTING:
    operations = []
else:
    operations = [
        migrations.RunSQL(
            SQL_OUTER % SQL_INNER_FORWARD,
            SQL_OUTER % SQL_INNER_REVERSE,
        )
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("variants", "0085_add_variant_index"),
    ]

    operations = operations
