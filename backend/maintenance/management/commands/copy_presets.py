"""Django command for copying preset from one project to another."""

import uuid

from django.core.management.base import BaseCommand
from django.db import transaction
from projectroles.models import Project

from variants.models.presets import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    QualityPresets,
    QuickPresets,
)

# TODO: Put the fuctionality to the interface. Limited to project the user has access to.


class DryRunException(Exception):
    pass


@transaction.atomic
def copy_presets(src_project, dst_project, stdout=lambda x: print(x), dry_run=True):
    mapping_presetset = {}
    mapping_presets = {
        ChromosomePresets: {},
        QualityPresets: {},
        ImpactPresets: {},
        FrequencyPresets: {},
        FlagsEtcPresets: {},
    }

    if dry_run:
        stdout("DRY RUN, not committing changes")

    for presetset in PresetSet.objects.filter(project=src_project):
        old_uuid = presetset.sodar_uuid
        presetset.pk = None
        presetset.sodar_uuid = uuid.uuid4()
        presetset.project = dst_project
        presetset.save()
        mapping_presetset[old_uuid] = presetset.sodar_uuid
        stdout(
            f"Copied presetset {presetset.label} from {src_project.title} to {dst_project.title}"
        )

    for presetset_uuid in mapping_presetset.keys():
        presetset = PresetSet.objects.get(sodar_uuid=presetset_uuid)
        for preset_model in [
            ChromosomePresets,
            FlagsEtcPresets,
            FrequencyPresets,
            ImpactPresets,
            QualityPresets,
        ]:
            for preset in list(preset_model.objects.filter(presetset=presetset)):
                old_uuid = preset.sodar_uuid
                preset.pk = None
                preset.sodar_uuid = uuid.uuid4()
                preset.presetset = PresetSet.objects.get(
                    sodar_uuid=mapping_presetset[preset.presetset.sodar_uuid]
                )
                preset.save()
                mapping_presets[preset_model][old_uuid] = preset.sodar_uuid
                stdout(
                    f"Copied preset {preset.label} from {src_project.title} to {dst_project.title}"
                )

        for preset in QuickPresets.objects.filter(presetset=presetset):
            preset.pk = None
            preset.sodar_uuid = uuid.uuid4()
            preset.presetset = PresetSet.objects.get(
                sodar_uuid=mapping_presetset[preset.presetset.sodar_uuid]
            )
            for subpreset in mapping_presets.keys():
                link = subpreset.__name__.replace("Presets", "").lower()
                setattr(
                    preset,
                    link,
                    subpreset.objects.get(
                        sodar_uuid=mapping_presets[subpreset][getattr(preset, link).sodar_uuid]
                    ),
                )
            preset.save()
            stdout(
                f"Copied quick preset {preset.label} from {src_project.title} to {dst_project.title}"
            )

    if dry_run:
        raise Exception("DRY RUN, rolling back")


class Command(BaseCommand):
    """Implementation of clearing expired exported files."""

    #: Help message displayed on the command line.
    help = "Copy all preset sets from one project to another."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("src_project_uuid", help="UUID of project to copy from.")
        parser.add_argument("dst_project_uuid", help="UUID of project to copy to.")
        parser.add_argument(
            "--no-dry-run", action="store_true", help="Do not dry run, commit changes."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Copy!"""

        src_project = Project.objects.get(sodar_uuid=options["src_project_uuid"])
        dst_project = Project.objects.get(sodar_uuid=options["dst_project_uuid"])
        dry_run = not options["no_dry_run"]

        try:
            copy_presets(
                src_project,
                dst_project,
                stdout=lambda x: self.stdout.write(self.style.NOTICE(x)),
                dry_run=dry_run,
            )
            self.stdout.write(self.style.SUCCESS("Committing changes"))
        except DryRunException as e:
            self.stdout.write(self.style.ERROR(str(e)))
