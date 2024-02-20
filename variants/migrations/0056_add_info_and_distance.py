"""Add ``SmallVariant.info`` and ``SmallVariant.{ensembl,refseq}_exon_dist`` fields."""

from django.conf import settings
from django.db import migrations, models

if not settings.IS_TESTING:
    # Operations using raw SQL.
    operations = [
        migrations.RunSQL("ALTER TABLE variants_smallvariant ADD info jsonb DEFAULT '{}'::jsonb"),
        migrations.RunSQL("ALTER TABLE variants_smallvariant ADD refseq_exon_dist int NULL"),
        migrations.RunSQL("ALTER TABLE variants_smallvariant ADD ensembl_exon_dist int NULL"),
    ]
else:
    # Operations using the Django ORM.
    operations = [
        migrations.AddField(
            model_name="smallvariant",
            name="info",
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name="smallvariant", name="refseq_exon_dist", field=models.IntegerField(null=True)
        ),
        migrations.AddField(
            model_name="smallvariant",
            name="ensembl_exon_dist",
            field=models.IntegerField(null=True),
        ),
    ]


class Migration(migrations.Migration):
    dependencies = [("variants", "0055_auto_20190828_1408")]

    operations = operations
