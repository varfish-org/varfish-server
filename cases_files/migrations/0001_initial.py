# Generated by Django 3.2.20 on 2023-07-20 09:48

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("variants", "0094_auto_20230719_1406"),
        ("cases", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PedigreeInternalFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sodar_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("path", models.CharField(max_length=1024, unique=True)),
                (
                    "designation",
                    models.CharField(
                        choices=[
                            ("sequencing_targets", "sequencing_targets"),
                            ("read_alignments", "read_alignments"),
                            ("variant_calls", "variant_calls"),
                            ("other", "other"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "genomebuild",
                    models.CharField(
                        choices=[("other", "other"), ("grch37", "grch37"), ("grch38", "grch38")],
                        max_length=128,
                        null=True,
                    ),
                ),
                ("mimetype", models.CharField(max_length=256)),
                ("checksum", models.CharField(max_length=128, null=True)),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="variants.case"
                    ),
                ),
                (
                    "pedigree",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cases.pedigree"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PedigreeExternalFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sodar_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("path", models.CharField(max_length=1024, unique=True)),
                (
                    "designation",
                    models.CharField(
                        choices=[
                            ("sequencing_targets", "sequencing_targets"),
                            ("read_alignments", "read_alignments"),
                            ("variant_calls", "variant_calls"),
                            ("other", "other"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "genomebuild",
                    models.CharField(
                        choices=[("other", "other"), ("grch37", "grch37"), ("grch38", "grch38")],
                        max_length=128,
                        null=True,
                    ),
                ),
                ("mimetype", models.CharField(max_length=256)),
                ("available", models.BooleanField(default=None, null=True)),
                ("last_checked", models.DateTimeField(default=None, null=True)),
                ("file_attributes", models.JSONField()),
                ("identifier_map", models.JSONField()),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="variants.case"
                    ),
                ),
                (
                    "pedigree",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cases.pedigree"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="IndividualInternalFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sodar_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("path", models.CharField(max_length=1024, unique=True)),
                (
                    "designation",
                    models.CharField(
                        choices=[
                            ("sequencing_targets", "sequencing_targets"),
                            ("read_alignments", "read_alignments"),
                            ("variant_calls", "variant_calls"),
                            ("other", "other"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "genomebuild",
                    models.CharField(
                        choices=[("other", "other"), ("grch37", "grch37"), ("grch38", "grch38")],
                        max_length=128,
                        null=True,
                    ),
                ),
                ("mimetype", models.CharField(max_length=256)),
                ("checksum", models.CharField(max_length=128, null=True)),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="variants.case"
                    ),
                ),
                (
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cases.individual"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="IndividualExternalFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sodar_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("path", models.CharField(max_length=1024, unique=True)),
                (
                    "designation",
                    models.CharField(
                        choices=[
                            ("sequencing_targets", "sequencing_targets"),
                            ("read_alignments", "read_alignments"),
                            ("variant_calls", "variant_calls"),
                            ("other", "other"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "genomebuild",
                    models.CharField(
                        choices=[("other", "other"), ("grch37", "grch37"), ("grch38", "grch38")],
                        max_length=128,
                        null=True,
                    ),
                ),
                ("mimetype", models.CharField(max_length=256)),
                ("available", models.BooleanField(default=None, null=True)),
                ("last_checked", models.DateTimeField(default=None, null=True)),
                ("file_attributes", models.JSONField()),
                ("identifier_map", models.JSONField()),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="variants.case"
                    ),
                ),
                (
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cases.individual"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]