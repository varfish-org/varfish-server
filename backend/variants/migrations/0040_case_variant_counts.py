"""Add variant counts to the ``Case`` class.

Update all existing case"""

from __future__ import unicode_literals

from django.db import migrations, models

from variants.models import update_variant_counts


def forwards(apps, _schema_editor):
    """Update the count for all cases."""
    Case = apps.get_model("variants", "Case")
    for case in Case.objects.all():
        update_variant_counts(case)


def backwards(apps, schema_editor):
    """Do nothing, fields will be removed anyway."""


class Migration(migrations.Migration):
    dependencies = [("variants", "0039_acmgcriteriarating")]

    operations = [
        migrations.AddField(
            model_name="case",
            name="num_small_vars",
            field=models.IntegerField(
                blank=True,
                default=None,
                help_text="Number of small variants, empty if no small variants have been imported",
                null=True,
                verbose_name="Small variants",
            ),
        ),
        migrations.AddField(
            model_name="case",
            name="num_svs",
            field=models.IntegerField(
                blank=True,
                default=None,
                help_text="Number of structural variants, empty if no structural variants have been imported",
                null=True,
                verbose_name="Structural variants",
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
