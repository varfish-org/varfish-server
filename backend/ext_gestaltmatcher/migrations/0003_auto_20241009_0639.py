# Generated by Django 3.2.25 on 2024-10-09 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ext_gestaltmatcher", "0002_smallvariantquerypediascores"),
    ]

    operations = [
        migrations.AlterField(
            model_name="smallvariantquerygestaltmatcherscores",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="smallvariantquerypediascores",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]