# Generated by Django 3.2.25 on 2024-10-29 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seqvars", "0013_auto_20241028_0928"),
    ]

    operations = [
        migrations.AddField(
            model_name="seqvarsquerypresetsset",
            name="is_factory_default",
            field=models.BooleanField(default=False),
        ),
    ]