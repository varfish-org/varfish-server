# Generated by Django 3.2.21 on 2023-09-26 13:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0001_initial"),
        ("cases_files", "0002_auto_20230919_1422"),
    ]

    operations = [
        migrations.AddField(
            model_name="individualinternalfile",
            name="file_attributes",
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="individualinternalfile",
            name="identifier_map",
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pedigreeinternalfile",
            name="file_attributes",
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pedigreeinternalfile",
            name="identifier_map",
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="individualexternalfile",
            name="path",
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name="individualinternalfile",
            name="designation",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="individualinternalfile",
            name="path",
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name="pedigreeexternalfile",
            name="path",
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name="pedigreeinternalfile",
            name="designation",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="pedigreeinternalfile",
            name="path",
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterUniqueTogether(
            name="individualexternalfile",
            unique_together={("individual", "path")},
        ),
        migrations.AlterUniqueTogether(
            name="individualinternalfile",
            unique_together={("individual", "path")},
        ),
        migrations.AlterUniqueTogether(
            name="pedigreeexternalfile",
            unique_together={("pedigree", "path")},
        ),
        migrations.AlterUniqueTogether(
            name="pedigreeinternalfile",
            unique_together={("pedigree", "path")},
        ),
    ]