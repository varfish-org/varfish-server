# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-04 07:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("beaconsite", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="query",
            name="src_user_identifier",
            field=models.CharField(
                blank=True, help_text="User ID from query source", max_length=128, null=True
            ),
        ),
        migrations.AddField(
            model_name="query",
            name="src_user_username",
            field=models.CharField(
                blank=True, help_text="User name from query source", max_length=128, null=True
            ),
        ),
        migrations.AddField(
            model_name="site",
            name="max_clock_skew",
            field=models.IntegerField(
                default=300, help_text="Maximal age of request based on date header"
            ),
        ),
    ]