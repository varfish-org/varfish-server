# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-19 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Dbsnp",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("release", models.CharField(max_length=32)),
                ("chromosome", models.CharField(max_length=32)),
                ("position", models.IntegerField()),
                ("reference", models.CharField(max_length=512)),
                ("alternative", models.CharField(max_length=512)),
                ("rsid", models.CharField(max_length=16)),
            ],
        ),
        migrations.AddIndex(
            model_name="dbsnp",
            index=models.Index(
                fields=["release", "chromosome", "position", "reference", "alternative"],
                name="dbsnp_dbsnp_release_570448_idx",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="dbsnp",
            unique_together=set(
                [("release", "chromosome", "position", "reference", "alternative")]
            ),
        ),
    ]
