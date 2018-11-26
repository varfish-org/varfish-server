"""Import GRCh37 sites TSV file."""

import os.path

from django.db import migrations


def import_sites(apps, _schema_editor):
    ReferenceSite = apps.get_model("var_stats_qc", "ReferenceSite")
    ReferenceSite.objects.from_csv(
        os.path.join(os.path.dirname(__file__), "../data/grch37_sites.tsv"), delimiter="\t"
    )


def remove_sites(apps, _schema_editor):
    ReferenceSite = apps.get_model("var_stats_qc", "ReferenceSite")
    ReferenceSite.objects.filter(release="GRCh37").delete()


class Migration(migrations.Migration):

    dependencies = [("var_stats_qc", "0001_initial")]

    operations = [migrations.RunPython(import_sites, remove_sites)]
