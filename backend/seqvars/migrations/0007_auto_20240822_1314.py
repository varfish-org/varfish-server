# Generated by Django 3.2.25 on 2024-08-22 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("seqvars", "0006_auto_20240807_1006"),
    ]

    operations = [
        migrations.AlterField(
            model_name="seqvarsquery",
            name="settings",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="seqvars.seqvarsquerysettings"
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsqueryexecution",
            name="querysettings",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="seqvars.seqvarsquerysettings"
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="clinvarpresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetsclinvar",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="columnspresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetscolumns",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="consequencepresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetsconsequence",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="frequencypresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetsfrequency",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="locuspresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetslocus",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="phenotypepriopresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetsphenotypeprio",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="qualitypresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetsquality",
            ),
        ),
        migrations.AlterField(
            model_name="seqvarsquerysettings",
            name="variantpriopresets",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="seqvars.seqvarsquerypresetsvariantprio",
            ),
        ),
    ]