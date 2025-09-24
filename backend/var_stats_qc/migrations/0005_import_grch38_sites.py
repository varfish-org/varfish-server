"""Import GRCh38 sites TSV file."""

import os.path

from django.db import migrations


def import_sites(apps, schema_editor):
    from django.db import transaction

    ReferenceSite = apps.get_model("var_stats_qc", "ReferenceSite")

    # Use atomic transaction to ensure clean rollback on failure
    with transaction.atomic():
        # Clean up any existing GRCh38 data first
        deleted_count = ReferenceSite.objects.filter(release="GRCh38").delete()[0]
        print(f"Deleted {deleted_count} existing GRCh38 entries")

        # Import the sites
        ReferenceSite.objects.from_csv(
            os.path.join(os.path.dirname(__file__), "../data/grch38_sites.tsv"), delimiter="\t"
        )

        # Verify the import
        imported_count = ReferenceSite.objects.filter(release="GRCh38").count()
        print(f"Successfully imported {imported_count} GRCh38 sites")


def remove_sites(apps, _schema_editor):
    ReferenceSite = apps.get_model("var_stats_qc", "ReferenceSite")
    ReferenceSite.objects.filter(release="GRCh38").delete()


class Migration(migrations.Migration):
    dependencies = [("var_stats_qc", "0004_auto_20190628_0735")]

    operations = [migrations.RunPython(import_sites, remove_sites)]
