# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-31 15:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("variants", "0002_exportfilebgjob_exportfilejobresult")]

    operations = [
        migrations.AlterField(
            model_name="exportfilebgjob",
            name="bg_job",
            field=models.ForeignKey(
                help_text="Background job for state etc.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="export_file_bg_job",
                to="bgjobs.BackgroundJob",
            ),
        ),
        migrations.AlterUniqueTogether(name="case", unique_together=set([])),
    ]
