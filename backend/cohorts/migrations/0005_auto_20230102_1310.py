# Generated by Django 3.2.16 on 2023-01-02 13:10

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("variants", "0091_alter_casephenotypeterms_sodar_uuid"),
        ("cohorts", "0004_auto_20200710_1548"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cohort",
            name="cases",
            field=models.ManyToManyField(to="variants.Case"),
        ),
        migrations.CreateModel(
            name="CohortCase",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "sodar_uuid",
                    models.UUIDField(
                        default=uuid.uuid4, help_text="CohortCase SODAR UUID", unique=True
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="variants.case"
                    ),
                ),
                (
                    "cohort",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cohorts.cohort"
                    ),
                ),
            ],
            options={
                "unique_together": {("cohort", "case")},
            },
        ),
    ]