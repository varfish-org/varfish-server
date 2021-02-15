"""Insert a few records into the ``clinvar_export`` tables"""
from __future__ import unicode_literals

from django.db import migrations


def add_submitters(apps, _schema_editor):
    Submitter = apps.get_model("clinvar_export", "Submitter")
    Submitter.objects.create(
        clinvar_id=9131, name="Manuel Holtgrewe",
    )


def add_organisations(apps, _schema_editor):
    Organisation = apps.get_model("clinvar_export", "Organisation")
    Organisation.objects.create(
        clinvar_id=505735,
        name=(
            "Institute for Medical Genetics and Human Genetics (Charité - "
            "Universitätsmedizin Berlin), Charité - Universitätsmedizin"
        ),
    )
    Organisation.objects.create(
        clinvar_id=507461, name="CUBI - Core Unit Bioinformatics (Berlin Institute of Health)",
    )


def add_assertion_methods(apps, _schema_editor):
    AssertionMethod = apps.get_model("clinvar_export", "AssertionMethod")
    AssertionMethod.objects.create(
        is_builtin=True, title="ACMG Guidelines, 2015", reference="PMID:25741868",
    )


def noop(_apps, _schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("clinvar_export", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_submitters, noop),
        migrations.RunPython(add_organisations, noop),
        migrations.RunPython(add_assertion_methods, noop),
    ]
