# Generated by Django 3.2.22 on 2023-10-25 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="individual",
            name="affected",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="individual",
            name="father",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="individual",
            name="mother",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]