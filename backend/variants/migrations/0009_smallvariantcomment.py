# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-13 20:12
from __future__ import unicode_literals

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("variants", "0008_auto_20181113_1912"),
    ]

    operations = [
        migrations.CreateModel(
            name="SmallVariantComment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(auto_now_add=True, help_text="DateTime of creation"),
                ),
                (
                    "date_modified",
                    models.DateTimeField(auto_now=True, help_text="DateTime of last modification"),
                ),
                (
                    "sodar_uuid",
                    models.UUIDField(
                        default=uuid.uuid4, help_text="Small variant flags SODAR UUID", unique=True
                    ),
                ),
                ("release", models.CharField(max_length=32)),
                ("chromosome", models.CharField(max_length=32)),
                ("position", models.IntegerField()),
                ("reference", models.CharField(max_length=512)),
                ("alternative", models.CharField(max_length=512)),
                ("text", models.TextField(help_text="The comment text")),
                (
                    "case",
                    models.ForeignKey(
                        help_text="Case that this variant is flagged in",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="small_variant_comments",
                        to="variants.Case",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        help_text="User who created the comment",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="small_variant_comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]