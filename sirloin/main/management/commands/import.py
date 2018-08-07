import os
import sys
from collections import namedtuple
from postgres_copy import CopyManager
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError, models, connection
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.fields import ArrayField
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


Database = namedtuple("Database", "table null release_required")


# class TemporaryAnnotation(Annotation)
# Inheritance won't work, because Django sets a ForeignKey to the base class and
# thus links a temporary table to the actual model which doesn't work
# overwriting the foreign key also doesn't work because either it reports a
# clash (when used as class parameter) or it doesn't get carried out because
# init function isn't called.


class TemporaryAnnotation(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    effect = ArrayField(models.CharField(max_length=64, null=True))
    impact = models.CharField(max_length=64, null=True)
    gene_name = models.CharField(max_length=64, null=True)
    gene_id = models.CharField(max_length=64, null=True)
    feature_type = models.CharField(max_length=64, null=True)
    feature_id = models.CharField(max_length=64, null=True)
    transcript_biotype = models.CharField(max_length=64, null=True)
    rank = models.CharField(max_length=64, null=True)
    hgvs_c = models.CharField(max_length=512, null=True)
    hgvs_p = models.CharField(max_length=512, null=True)
    cdna_pos_length = models.CharField(max_length=64, null=True)
    cds_pos_length = models.CharField(max_length=64, null=True)
    aa_pos_length = models.CharField(max_length=64, null=True)
    distance = models.CharField(max_length=64, null=True)
    errors = models.CharField(max_length=512, null=True)
    objects = CopyManager()

    class Meta:
        app_label = "main"


class Command(BaseCommand):
    help = "Sirloin database import"
    databases = {
        "sample": Database(Main, ".", False),
        "pedigree": Database(Pedigree, "", False),
        "annotation": Database(TemporaryAnnotation, ".", False),
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

        if options["database"] == "annotation":
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TEMPORARY TABLE main_temporaryannotation (LIKE main_annotation INCLUDING ALL);
                    """
                )

                # from_csv actually creates a temporary table itself, and the uses
                # INSERT INTO into the real table, but I can't find a way to pass
                # a ON CONFLICT parameter. Internally this construct creates
                # two temporary tables, first one from from_csv that it reads it
                # data to and then INSERT INTO it into my main_temporaryannotation
                # table.
                database.table.objects.from_csv(
                    options["path"], delimiter="\t", null=database.null
                )

                cursor.execute(
                    """
                    INSERT INTO main_annotation
                    SELECT * FROM main_temporaryannotation
                    ON CONFLICT (release, chromosome, position, reference, alternative)
                    DO NOTHING;
                    """
                )
                return

        database.table.objects.from_csv(
            options["path"], delimiter="\t", null=database.null
        )
