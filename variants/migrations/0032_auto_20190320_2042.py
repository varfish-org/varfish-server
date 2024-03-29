# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-20 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("variants", "0031_smallvariantquerygenescores")]

    operations = [
        migrations.AddField(
            model_name="smallvariant", name="num_hemi_alt", field=models.IntegerField(default=0)
        ),
        migrations.AddField(
            model_name="smallvariant", name="num_hemi_ref", field=models.IntegerField(default=0)
        ),
        migrations.AddField(
            model_name="smallvariant", name="num_het", field=models.IntegerField(default=0)
        ),
        migrations.AddField(
            model_name="smallvariant", name="num_hom_alt", field=models.IntegerField(default=0)
        ),
        migrations.AddField(
            model_name="smallvariant", name="num_hom_ref", field=models.IntegerField(default=0)
        ),
    ]
