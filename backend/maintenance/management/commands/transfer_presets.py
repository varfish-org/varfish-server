import json
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.forms import model_to_dict
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


class Command(BaseCommand):
    help = "Transfer presets between projects or export/import as JSON"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        # Local transfer
        transfer_parser = subparsers.add_parser(
            "transfer", help="Transfer presets between projects locally"
        )
        transfer_parser.add_argument(
            "--src-uuid", type=str, required=True, help="Source project uuid"
        )
        transfer_parser.add_argument(
            "--dst-uuid", type=str, required=True, help="Destination project uuid"
        )
        transfer_parser.add_argument(
            "--dry-run", action="store_true", help="Perform a dry run without committing changes"
        )

        # Export
        export_parser = subparsers.add_parser("export", help="Export presets to JSON")
        export_parser.add_argument(
            "--project-uuid", type=str, required=True, help="Source project uuid"
        )
        export_parser.add_argument(
            "--output-json", type=str, required=True, help="Output JSON file"
        )

        # Import
        import_parser = subparsers.add_parser("import", help="Import presets from JSON")
        import_parser.add_argument(
            "--project-uuid", type=str, required=True, help="Destination project uuid"
        )
        import_parser.add_argument("--input-json", type=str, required=True, help="Input JSON file")
        import_parser.add_argument(
            "--dry-run", action="store_true", help="Perform a dry run without committing changes"
        )

    def handle(self, *args, **options):
        subcommand = options["subcommand"]
        if subcommand == "transfer":
            self.handle_transfer(*args, **options)
        elif subcommand == "export":
            self.handle_export(*args, **options)
        elif subcommand == "import":
            self.handle_import(*args, **options)
        else:
            raise CommandError("Unknown subcommand")

    def handle_transfer(self, *args, **options):
        src = options["src_uuid"]
        dst = options["dst_uuid"]
        dry_run = options["dry_run"]

        try:
            src_project = Project.objects.get(sodar_uuid=src)
            dst_project = Project.objects.get(sodar_uuid=dst)
        except Project.DoesNotExist as e:
            raise CommandError(f"Project not found: {e}")

        mapping_presetset = {}
        mapping_presets = {
            ChromosomePresets: {},
            QualityPresets: {},
            ImpactPresets: {},
            FrequencyPresets: {},
            FlagsEtcPresets: {},
        }

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN, not committing changes"))

        with transaction.atomic():
            # Clean destination preset sets before copying
            self.stdout.write("Deleting presetsets and preset in destination")
            dst_project.presetset_set.all().delete()
            for presetset in list(src_project.presetset_set.all()):
                old_uuid = presetset.sodar_uuid
                presetset.pk = None
                presetset.sodar_uuid = uuid.uuid4()
                presetset.project = dst_project
                presetset.save()
                mapping_presetset[old_uuid] = presetset.sodar_uuid
                self.stdout.write(f'Copied presetset "{presetset.label}" from {src} to {dst}')

            for presetset_uuid in mapping_presetset.keys():
                presetset = PresetSet.objects.get(sodar_uuid=presetset_uuid)
                for preset_model in mapping_presets.keys():
                    for preset in list(preset_model.objects.filter(presetset=presetset)):
                        old_uuid = preset.sodar_uuid
                        preset.pk = None
                        preset.sodar_uuid = uuid.uuid4()
                        preset.presetset = PresetSet.objects.get(
                            sodar_uuid=mapping_presetset[preset.presetset.sodar_uuid]
                        )
                        preset.save()
                        mapping_presets[preset_model][old_uuid] = preset.sodar_uuid
                        self.stdout.write(f'Copied {preset_model.__name__} "{preset.label}"')

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
                                sodar_uuid=mapping_presets[subpreset][
                                    getattr(preset, link).sodar_uuid
                                ]
                            ),
                        )
                    preset.save()
                    self.stdout.write(f'Copied quick preset "{preset.label}"')

            if dry_run:
                raise Exception("DRY RUN, rolling back")

            self.stdout.write(self.style.SUCCESS("Committing changes"))

    def handle_export(self, *args, **options):
        project_uuid = options["project_uuid"]
        output = options["output_json"]

        try:
            src_project = Project.objects.get(sodar_uuid=project_uuid)
        except Project.DoesNotExist as e:
            raise CommandError(f"Project not found: {e}")

        data = {
            "presetsets": [],
            "presets": {
                "chromosome": [],
                "quality": [],
                "impact": [],
                "frequency": [],
                "flagsetc": [],
            },
            "quickpresets": [],
        }

        for presetset in src_project.presetset_set.all():
            presetset_data = model_to_dict(
                presetset, exclude=["id", "date_created", "date_modified"]
            )

            presetset_data["sodar_uuid"] = str(presetset.sodar_uuid)
            presetset_data["project"] = None
            presetset_data["signed_off_by"] = None

            data["presetsets"].append(presetset_data)

        preset_models = [
            (ChromosomePresets, "chromosome"),
            (QualityPresets, "quality"),
            (ImpactPresets, "impact"),
            (FrequencyPresets, "frequency"),
            (FlagsEtcPresets, "flagsetc"),
        ]
        for model, key in preset_models:
            for preset in model.objects.filter(presetset__project=src_project):
                preset_data = model_to_dict(preset, exclude=["id", "date_created", "date_modified"])

                preset_data["sodar_uuid"] = str(preset.sodar_uuid)
                preset_data["presetset"] = str(preset.presetset.sodar_uuid)

                data["presets"][key].append(preset_data)

        for quick in QuickPresets.objects.filter(presetset__project=src_project):
            quick_data = model_to_dict(quick, exclude=["id", "date_created", "date_modified"])

            quick_data["sodar_uuid"] = str(quick.sodar_uuid)
            quick_data["presetset"] = str(quick.presetset.sodar_uuid)

            for model, key in preset_models:
                link = key
                quick_data[link] = str(getattr(quick, link).sodar_uuid)

            data["quickpresets"].append(quick_data)

        with open(output, "w") as f:
            json.dump(data, f, cls=DjangoJSONEncoder, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Exported settings to {output}"))

    def handle_import(self, *args, **options):
        project_uuid = options["project_uuid"]
        input_file = options["input_json"]
        dry_run = options.get("dry_run", False)

        try:
            dst_project = Project.objects.get(sodar_uuid=project_uuid)
        except Project.DoesNotExist as e:
            raise CommandError(f"Project not found: {e}")

        with open(input_file, "r") as f:
            data = json.load(f)

        uuid_mapping = {}

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN, not committing changes"))

        with transaction.atomic():
            self.stdout.write("Deleting presetsets and presets in destination")
            dst_project.presetset_set.all().delete()

            # Import PresetSets
            for presetset in data["presetsets"]:
                old_uuid = presetset["sodar_uuid"]
                presetset["sodar_uuid"] = uuid.uuid4()
                presetset["project"] = dst_project
                obj = PresetSet(**presetset)
                obj.save()
                uuid_mapping[old_uuid] = obj

            # Import Presets
            preset_models = [
                (ChromosomePresets, "chromosome"),
                (QualityPresets, "quality"),
                (ImpactPresets, "impact"),
                (FrequencyPresets, "frequency"),
                (FlagsEtcPresets, "flagsetc"),
            ]
            for model, key in preset_models:
                for preset in data["presets"][key]:
                    old_uuid = preset["sodar_uuid"]
                    preset["sodar_uuid"] = uuid.uuid4()
                    preset["presetset"] = uuid_mapping[preset["presetset"]]
                    obj = model(**preset)
                    obj.save()
                    uuid_mapping[old_uuid] = obj

            # Import QuickPresets
            for quick in data["quickpresets"]:
                old_uuid = quick["sodar_uuid"]
                quick["sodar_uuid"] = uuid.uuid4()
                quick["presetset"] = uuid_mapping[quick["presetset"]]
                for model, key in preset_models:
                    quick[key] = uuid_mapping[quick[key]]
                obj = QuickPresets(**quick)
                obj.save()

            if dry_run:
                raise Exception("DRY RUN, rolling back")

            self.stdout.write(self.style.SUCCESS("Imported settings from JSON"))
