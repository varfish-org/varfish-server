# -*- coding: utf-8 -*-
"""Add ``"gt_entries"`` field to ``Case.pedigree`."""

import logging

from django.db import migrations


def forwards(apps, _schema_editor):
    """Add ``has_gt_entries"`` key to pedigree members, based on them having a genotype call in the small variants."""
    Case = apps.get_model("variants", "Case")
    SmallVariant = apps.get_model("variants", "SmallVariant")
    for case in Case.objects.all():
        logging.info("Updating Case %s (pk %s)", case.name, case.id)
        first_var = SmallVariant.objects.order_by().filter(case_id=case.id).first()
        if not first_var:
            logging.warning(
                "Case %s (pk %s; uuid %s) does not have any SmallVariant record",
                case.name,
                case.id,
                case.sodar_uuid,
            )
            continue
        gt_samples = set(first_var.genotype.keys())
        pedigree = case.pedigree
        for line in pedigree:
            if line["patient"] in gt_samples:
                line["has_gt_entries"] = True
        case.pedigree = pedigree
        case.save()


def backwards(apps, schema_editor):
    """Remove ``"has_gt_entries"`` key in pedigree members again."""
    Case = apps.get_model("variants", "Case")
    for case in Case.objects.all():
        for line in case.pedigree:
            if "has_gt_entries" in line:
                line.pop("has_gt_entries")
        case.save()


class Migration(migrations.Migration):

    dependencies = [("variants", "0009_smallvariantcomment")]

    operations = [migrations.RunPython(forwards, backwards)]
