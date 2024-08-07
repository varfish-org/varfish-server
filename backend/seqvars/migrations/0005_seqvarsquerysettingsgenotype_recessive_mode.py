# Generated by Django 3.2.25 on 2024-07-17 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seqvars", "0004_auto_20240712_1236"),
    ]

    operations = [
        migrations.AddField(
            model_name="seqvarsquerysettingsgenotype",
            name="recessive_mode",
            field=models.CharField(
                choices=[
                    ("disabled", "disabled"),
                    ("comphet_recessive", "comphet_recessive"),
                    ("homozygous_recessive", "homozygous_recessive"),
                    ("recessive", "recessive"),
                ],
                default="disabled",
                max_length=128,
            ),
        ),
    ]
