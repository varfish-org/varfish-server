# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-28 12:10
from __future__ import unicode_literals

import uuid

import bgjobs.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("projectroles", "0006_add_remote_projects"),
        ("bgjobs", "0005_auto_20190128_1210"),
        ("variants", "0025_smallvariant_bigint_id_field"),
    ]

    operations = [
        migrations.CreateModel(
            name="FilterBgJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "sodar_uuid",
                    models.UUIDField(default=uuid.uuid4, help_text="Case SODAR UUID", unique=True),
                ),
                (
                    "bg_job",
                    models.ForeignKey(
                        help_text="Background job for filtering and storing query results",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="filter_bg_job",
                        to="bgjobs.BackgroundJob",
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        help_text="The case to filter",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="variants.Case",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        help_text="Project in which this objects belongs",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projectroles.Project",
                    ),
                ),
            ],
            bases=(bgjobs.models.JobModelMessageMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ProjectCasesFilterBgJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "sodar_uuid",
                    models.UUIDField(default=uuid.uuid4, help_text="Case SODAR UUID", unique=True),
                ),
                (
                    "bg_job",
                    models.ForeignKey(
                        help_text="Background job for filtering joint project and storing query results.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project_cases_filter_bg_job",
                        to="bgjobs.BackgroundJob",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        help_text="Project in which this objects belongs",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projectroles.Project",
                    ),
                ),
            ],
            bases=(bgjobs.models.JobModelMessageMixin, models.Model),
        ),
        migrations.AddField(
            model_name="projectcasessmallvariantquery",
            name="query_results",
            field=models.ManyToManyField(to="variants.SmallVariant"),
        ),
        migrations.AddField(
            model_name="smallvariantquery",
            name="query_results",
            field=models.ManyToManyField(to="variants.SmallVariant"),
        ),
        migrations.AddField(
            model_name="projectcasesfilterbgjob",
            name="projectcasessmallvariantquery",
            field=models.ForeignKey(
                help_text="Query that is executed.",
                on_delete=django.db.models.deletion.CASCADE,
                to="variants.ProjectCasesSmallVariantQuery",
            ),
        ),
        migrations.AddField(
            model_name="filterbgjob",
            name="smallvariantquery",
            field=models.ForeignKey(
                help_text="Query that is executed.",
                on_delete=django.db.models.deletion.CASCADE,
                to="variants.SmallVariantQuery",
            ),
        ),
    ]