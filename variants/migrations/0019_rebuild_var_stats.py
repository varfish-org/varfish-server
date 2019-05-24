"""After introducing the models for variant statistics and QC, we have to rebuild them for existing cases."""
from __future__ import unicode_literals

import logging

import aldjemy
from django.db import migrations

from variants.models import Case
from variants.variant_stats import rebuild_case_variant_stats


#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


def rebuild_var_stats(apps, _schema_editor):
    """Rebuild variant statistics for all cases"""
    # NB: Commented out; problem with aldjemy and changed schemas, no deployment before this version in the wild
    # anyway!
    # for case in Case.objects.all():
    #     logging.info("Updating Case %s (pk %s)", case.name, case.id)
    #     rebuild_case_variant_stats(SQLALCHEMY_ENGINE, case)


def do_nothing(_apps, _schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("variants", "0018_casevariantstats_pedigreerelatedness_samplevariantstatistics")
    ]

    operations = [migrations.RunPython(rebuild_var_stats, do_nothing)]
