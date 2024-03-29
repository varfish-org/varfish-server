# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-01-06 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("geneinfo", "0020_auto_20191118_1729")]

    operations = [
        migrations.AddField(
            model_name="hgnc",
            name="ucsc_id_novers",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AddIndex(
            model_name="hgnc",
            index=models.Index(fields=["ucsc_id_novers"], name="geneinfo_hg_ucsc_id_7a67bb_idx"),
        ),
    ]
