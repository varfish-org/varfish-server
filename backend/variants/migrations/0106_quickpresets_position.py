# Generated by Django 3.2.25 on 2024-07-11 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("variants", "0105_auto_20240529_1403"),
    ]

    operations = [
        migrations.AddField(
            model_name="quickpresets",
            name="position",
            field=models.IntegerField(default=0, help_text="Position in the list"),
        ),
    ]
