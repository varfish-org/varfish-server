import os
import sys
from collections import namedtuple
from postgres_copy import CopyManager
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils import timezone
from sirloin.main.models import (
    Main,
    Pedigree,
    Exac,
    Annotation,
    Hgnc,
    Mim2gene,
    Mim2geneMedgen,
    Hpo,
    ImportInfo,
)


class TSVParser:
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        with open(self.filename, "r") as fh:
            for line in fh:
                yield fh.rstrip("\n").split("\t")


Database = namedtuple("Database", "table null release_required")


class Command(BaseCommand):
    help = "Sirloin database import"
    databases = {
        "sample": Database(Main, ".", False),
        "pedigree": Database(Pedigree, "", False),
        "annotation": Database(Annotation, ".", False),
        "exac": Database(Exac, ".", True),
        "omim": Database(Mim2geneMedgen, "-", True),
        "hgnc": Database(Hgnc, "", True),
        "hpo": Database(Hpo, "", True),
    }

    def add_arguments(self, parser):
        parser.add_argument("--path", help="Input file path", required=True)
        parser.add_argument(
            "--database",
            help="Input database",
            choices=self.databases.keys(),
            required=True,
        )
        parser.add_argument(
            "--release", help="Release version of the imported database"
        )
        parser.add_argument(
            "--comment", help="Comment for the imported database"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        database = self.databases[options["database"]]

        if database.release_required:
            if not options["release"]:
                sys.exit(
                    "Please specify --release when importing {}".format(
                        options["database"]
                    )
                )

            try:
                ImportInfo.objects.create(
                    table=type(database.table).__name__,
                    timestamp=timezone.now(),
                    release=options["release"],
                    comment=options["comment"] if options["comment"] else "",
                )
            except IntegrityError:
                sys.exit("This import already exists!")

        database.table.objects.from_csv(
            options["path"], delimiter="\t", null=database.null
        )
