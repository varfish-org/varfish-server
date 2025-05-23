# Generated by Django 3.2.25 on 2024-10-30 07:38

import uuid

import bgjobs.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bgjobs", "0006_auto_20200526_1657"),
        ("seqvars", "0014_seqvarsquerypresetsset_is_factory_default"),
    ]

    operations = [
        migrations.CreateModel(
            name="SeqvarsInhouseDbBuildBackgroundJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sodar_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                (
                    "bg_job",
                    models.ForeignKey(
                        help_text="Background job for state etc.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seqvarsinhousedbbuildbackgroundjob",
                        to="bgjobs.backgroundjob",
                    ),
                ),
            ],
            options={
                "ordering": ["-pk"],
            },
            bases=(bgjobs.models.JobModelMessageMixin, models.Model),
        ),
    ]
