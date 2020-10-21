"""Implementation of regmaps management commands."""

import json
import pathlib
import sys

import binning
from django.db import transaction
from django.core.management.base import CommandError
import yaml

from importer.models import ImportInfo
from .models import RegMapCollection, RegElementType, RegMap, RegElement, RegInteraction


class CollectionListImpl:
    """Implementation of listing all regulatory map collections."""

    def run(self, outf=sys.stdout):
        print("% -40s\t%s" % ("UUID", "title"), file=outf)
        for coll in RegMapCollection.objects.all():
            print("% -40s\t%s" % (str(coll.sodar_uuid), coll.title), file=outf)
        print(
            "\nTotal regulatory map collections: %d" % RegMapCollection.objects.count(), file=outf
        )


class CollectionDeleteImpl:
    """Implementation of deleting regulatory map collections."""

    def __init__(self, uuid, **_kwargs):
        self.uuid = uuid

    def run(self):
        try:
            with transaction.atomic():
                coll = RegMapCollection.objects.get(sodar_uuid=self.uuid)
                ImportInfo.objects.filter(
                    table="regmaps.%s" % coll.slug, release=coll.version, genomebuild=coll.release
                ).delete()
                coll.delete()
        except RegMapCollection.DoesNotExist:
            raise CommandError("Could not find regulatory map collection with UUID: %s" % self.uuid)


class CollectionImportImpl:
    """Implementation of importing regulatory map collections."""

    def __init__(self, path, stderr, style, **_kwargs):
        self.path = path
        self.stderr = stderr
        self.style = style

    def run(self):
        # Normalize path such that it points to the YAML definition file.
        path = pathlib.Path(self.path)
        if path.is_dir():
            path = path / "index.yml"
        # Load YAML description file.
        with path.open("rt") as inputf:
            print("Loading regulatory map YAML file at %s..." % path, file=self.stderr)
            yaml_data = yaml.load(inputf, Loader=yaml.FullLoader)
            self.stderr.write(self.style.SUCCESS("... done"))
        # Perform the actual import.
        self._import(yaml_data, path)

    def _import(self, yaml_data, yaml_path):
        for collection in yaml_data:
            with transaction.atomic():
                ImportInfo.objects.create(
                    table="regmaps.%s" % (collection["slug"]),
                    genomebuild=collection["release"],
                    release=collection["version"],
                )
                print(
                    "Creating regulatory map collection %s..." % collection["slug"],
                    file=self.stderr,
                )
                coll = RegMapCollection.objects.create(
                    title=collection["title"],
                    short_title=collection["short_title"],
                    slug=collection["slug"],
                    release=collection["release"],
                    version=collection["version"],
                    description=collection.get("description"),
                )
                ets = {}
                for vals in collection["element_types"]:
                    ets[vals["slug"]] = RegElementType.objects.create(
                        collection=coll,
                        title=vals["title"],
                        short_title=vals["short_title"],
                        slug=vals["slug"],
                        description=vals.get("description"),
                    )
                for vals in collection.get("maps") or []:
                    print(
                        "  Importing regulatory element BED file %s..." % vals["elements"],
                        file=self.stderr,
                    )
                    m = RegMap.objects.create(
                        collection=coll,
                        title=vals["title"],
                        short_title=vals["short_title"],
                        slug=vals["slug"],
                        description=vals.get("description"),
                    )
                    self._import_elements(ets, m, yaml_path.parent / vals["elements"])
                    self.stderr.write(self.style.SUCCESS("  ... done"))
                    print(
                        "  Importing interaction BED file %s..." % vals["interactions"],
                        file=self.stderr,
                    )
                    m, _ = RegMap.objects.get_or_create(
                        collection=coll,
                        slug=vals["slug"],
                        defaults={
                            "title": vals["title"],
                            "short_title": vals["short_title"],
                            "description": vals.get("description"),
                        },
                    )
                    self._import_interactions(m, yaml_path.parent / vals["interactions"])
                    self.stderr.write(self.style.SUCCESS("  ... done"))
            self.stderr.write(self.style.SUCCESS("... done"))

    def _import_elements(self, element_types, reg_map, path_bed):
        header = None
        with path_bed.open("rt") as inputf:
            for line in inputf:
                line = line.strip()
                arr = line.split("\t")
                if not header:
                    header = arr
                    continue
                chrom, begin, end, et_slug, score = arr[:5]
                begin = int(begin)
                end = int(end)
                elem_type = element_types[et_slug]
                score = float("NaN") if score in ("", ".", "-") else float(score)
                if len(arr) > 5:
                    extra_data = json.loads(arr[5])
                else:
                    extra_data = None
                RegElement.objects.create(
                    reg_map=reg_map,
                    elem_type=elem_type,
                    release=reg_map.collection.release,
                    chromosome=chrom,
                    start=begin + 1,
                    end=end,
                    bin=binning.assign_bin(begin, end),
                    score=score,
                    extra_data=extra_data,
                )

    def _import_interactions(self, reg_map, path_bed):
        header = None
        with path_bed.open("rt") as inputf:
            for line in inputf:
                line = line.strip()
                arr = line.split("\t")
                if not header:
                    header = arr
                    continue
                chrom, begin, end, score, chrom1, begin1, end1, chrom2, begin2, end2 = arr[:10]
                begin = int(begin)
                end = int(end)
                begin1 = int(begin1)
                end1 = int(end1)
                begin2 = int(begin2)
                end2 = int(end2)
                score = float("NaN") if score in ("", ".", "-") else float(score)
                if len(arr) > 5:
                    extra_data = json.loads(arr[10])
                else:
                    extra_data = None
                RegInteraction.objects.create(
                    reg_map=reg_map,
                    release=reg_map.collection.release,
                    chromosome=chrom,
                    start=begin + 1,
                    end=end,
                    bin=binning.assign_bin(begin, end),
                    chromosome1=chrom1,
                    start1=begin1 + 1,
                    end1=end1,
                    chromosome2=chrom2,
                    start2=begin2 + 1,
                    end2=end2,
                    score=score,
                    extra_data=extra_data,
                )
