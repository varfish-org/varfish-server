# Generated by Django 3.2.20 on 2023-08-01 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("variants", "0095_auto_20230724_0820"),
        ("svs", "0021_remove_svqueryresultset_query_sql"),
    ]

    operations = [
        migrations.AddField(
            model_name="svqueryresultset",
            name="case",
            field=models.ForeignKey(
                blank=True,
                help_text="The case that this result is for",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="variants.case",
            ),
        ),
        migrations.AlterField(
            model_name="svqueryresultset",
            name="svquery",
            field=models.ForeignKey(
                blank=True,
                help_text="The query that this result is for",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="svs.svquery",
            ),
        ),
    ]