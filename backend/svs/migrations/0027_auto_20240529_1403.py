# Generated by Django 3.2.25 on 2024-05-29 14:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("svs", "0026_auto_20240522_1353"),
    ]

    operations = [
        migrations.AddField(
            model_name="svquery",
            name="query_settings_version_major",
            field=models.IntegerField(default=0, help_text="The query settings version (major)"),
        ),
        migrations.AddField(
            model_name="svquery",
            name="query_settings_version_minor",
            field=models.IntegerField(default=0, help_text="The query settings version (minor)"),
        ),
    ]
