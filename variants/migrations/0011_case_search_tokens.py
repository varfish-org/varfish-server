# -*- coding: utf-8 -*-
"""Add ``search_tokens`` field to ``Case``."""

import logging
import re

import django.contrib.postgres.fields
from django.db import migrations, models


def set_search_tokens(case):
    """Force-update ``self.search_tokens``, will enable ``.save()`` call to always save."""
    case.search_tokens = [case.name] + [x["patient"] for x in case.pedigree if x.get("patient")]
    case.search_tokens = [re.sub(r"-\S+\d+-\S+\d+-[^-]+\d+$", "", x) for x in case.search_tokens]
    case.search_tokens = [x.lower() for x in case.search_tokens]
    case.search_tokens = [re.sub(r"[^a-zA-Z0-9]", "", x) for x in case.search_tokens]


def update_search_tokens(apps, _schema_editor):
    """Add ``has_gt_entries"`` key to pedigree members, based on them having a genotype call in the small variants."""
    Case = apps.get_model("variants", "Case")
    for case in Case.objects.all():
        logging.info("Updating Case %s (pk %s)", case.name, case.id)
        set_search_tokens(case)
        case.save()

def do_nothing(apps, _schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("variants", "0010_add_has_gt_entries_to_pedigree")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="search_tokens",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, max_length=128),
                db_index=True,
                default=list,
                help_text="Search tokens",
                size=None,
            ),
        ),
        migrations.RunPython(update_search_tokens, do_nothing),
    ]
