# -*- coding: utf-8 -*-
"""Extend StructuralVariant table as needed by varfish-annotator extension described here:

https://github.com/bihealth/varfish-annotator/issues/41

To support non-linear variants better

- chromosome2
- chromosome_no2
- bin2 (in case of non-linear breakpoint, linear: ==bin)
- pe_orientation

To help in buildling background database counts

- num_hom_alt
- num_hom_ref
- num_het
- num_hemi_alt
- num_hemi_ref
"""

from django.db import migrations, models
from django.conf import settings


if settings.IS_TESTING:
    operations = [
        migrations.AddField(
            model_name="structuralvariant",
            name="chromosome2",
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="chromosome_no2",
            field=models.IntegerField(default=-1, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="bin2",
            field=models.IntegerField(default=-1, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="pe_orientation",
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="num_hom_alt",
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="num_hom_ref",
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="num_het",
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="num_hemi_alt",
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="structuralvariant",
            name="num_hemi_ref",
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
else:
    operations = [
        migrations.RunSQL(
            r"""
            ALTER TABLE svs_structuralvariant
                ADD chromosome2 character varying(32) NULL,
                ADD chromosome_no2 integer NULL,
                ADD bin2 integer NULL,
                ADD pe_orientation character varying(32) NULL,
                ADD num_hom_alt integer NULL,
                ADD num_hom_ref integer NULL,
                ADD num_het integer NULL,
                ADD num_hemi_alt integer NULL,
                ADD num_hemi_ref integer NULL;
            """,
            r"""
            ALTER TABLE svs_structuralvariant
                DROP COLUMN chromosome2,
                DROP COLUMN chromosome_no2,
                DROP COLUMN bin2,
                DROP COLUMN pe_orientation,
                DROP COLUMN num_hom_alt,
                DROP COLUMN num_hom_ref,
                DROP COLUMN num_het,
                DROP COLUMN num_hemi_alt,
                DROP COLUMN num_hemi_ref;
            """,
        ),
    ]


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        (
            "svs",
            "0017_backgroundsv_backgroundsvset_buildbackgroundsvsetjob_cleanupbackgroundsvsetjob",
        )
    ]

    operations = operations
