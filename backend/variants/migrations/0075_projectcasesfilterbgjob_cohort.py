# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-01 12:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("cohorts", "0003_auto_20200701_1255"),
        ("variants", "0074_caddsubmissionbgjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectcasesfilterbgjob",
            name="cohort",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="project_cases_filter_bg_job",
                to="cohorts.Cohort",
            ),
        ),
    ]