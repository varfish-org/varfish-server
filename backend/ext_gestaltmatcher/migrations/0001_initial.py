# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2023-10-20 07:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SmallVariantQueryGestaltMatcherScores",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("gene_id", models.CharField(help_text="Entrez gene ID", max_length=64)),
                ("gene_symbol", models.CharField(help_text="The gene symbol", max_length=128)),
                ("priority_type", models.CharField(help_text="The priority type", max_length=64)),
                ("score", models.FloatField(help_text="The gene score")),
                (
                    "query",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="variants.SmallVariantQuery"
                    ),
                ),
            ],
        )
    ]