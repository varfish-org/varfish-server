# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-19 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("dbsnp", "0001_initial")]

    operations = [
        migrations.RemoveIndex(model_name="dbsnp", name="dbsnp_dbsnp_release_570448_idx"),
        migrations.RenameField(model_name="dbsnp", old_name="position", new_name="start"),
        migrations.AddField(
            model_name="dbsnp",
            name="bin",
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="dbsnp",
            name="end",
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="dbsnp",
            unique_together=set([("release", "chromosome", "start", "reference", "alternative")]),
        ),
        migrations.AddIndex(
            model_name="dbsnp",
            index=models.Index(
                fields=["release", "chromosome", "start", "reference", "alternative"],
                name="dbsnp_dbsnp_release_8ac946_idx",
            ),
        ),
    ]
