# -*- coding: utf-8 -*-
# Generated manually to optimize ClinVar query performance
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clinvar", "0010_clinvarpathogenicgenes"),
    ]

    operations = [
        # Add index including 'end' to complete the variant matching
        migrations.AddIndex(
            model_name="clinvar",
            index=models.Index(
                fields=["release", "chromosome", "start", "end", "reference", "alternative"],
                name="clinvar_variant_full_idx",
            ),
        ),
    ]
