# Generated by Django 3.2.25 on 2024-10-28 09:28

import typing

import django.core.serializers.json
from django.db import migrations
import django_pydantic_field.compat.django
import django_pydantic_field.fields

import seqvars.models.base


class Migration(migrations.Migration):

    dependencies = [
        ("seqvars", "0012_auto_20241024_0823"),
    ]

    operations = [
        migrations.RenameField(
            model_name="seqvarsquerypresetsfrequency",
            old_name="gnomad_mitochondrial",
            new_name="gnomad_mtdna",
        ),
        migrations.RenameField(
            model_name="seqvarsquerysettingsfrequency",
            old_name="gnomad_mitochondrial",
            new_name="gnomad_mtdna",
        ),
        migrations.AlterField(
            model_name="seqvarsquerypresetsfrequency",
            name="inhouse",
            field=django_pydantic_field.fields.PydanticSchemaField(
                blank=True,
                config=None,
                default=None,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                null=True,
                schema=django_pydantic_field.compat.django.GenericContainer(
                    typing.Union,
                    (seqvars.models.base.SeqvarsInhouseFrequencySettingsPydantic, type(None)),
                ),
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettingsfrequency",
            name="inhouse",
            field=django_pydantic_field.fields.PydanticSchemaField(
                blank=True,
                config=None,
                default=None,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                null=True,
                schema=django_pydantic_field.compat.django.GenericContainer(
                    typing.Union,
                    (seqvars.models.base.SeqvarsInhouseFrequencySettingsPydantic, type(None)),
                ),
            ),
        ),
    ]