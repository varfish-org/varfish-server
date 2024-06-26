# Generated by Django 3.2.24 on 2024-03-22 15:02

from django.db import migrations, models

from variants.models import SmallVariantComment, SmallVariantFlags


# Was in migration 0062 before. Didn't work anymore, because of the new field in SmallVariantFlags
# Was in migration 0071 before
def update_chromosome_no_in_existing_flags_and_comments(apps, schema_editor):
    if not schema_editor.connection.alias == "default":
        return
    for o in list(SmallVariantFlags.objects.all()) + list(SmallVariantComment.objects.all()):
        o.save()


class Migration(migrations.Migration):
    dependencies = [
        ("variants", "0101_auto_20240301_1141_not_null_sodar_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="flagsetcpresets",
            name="flag_incidental",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="smallvariantflags",
            name="flag_incidental",
            field=models.BooleanField(default=False),
        ),
        # Was in migration 0062 before. Didn't work anymore, because of the new field in SmallVariantFlags
        # Was in migration 0071 before
        migrations.RunPython(update_chromosome_no_in_existing_flags_and_comments),
    ]
