import sys
from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils import timezone

from annotation.models import Annotation
from clinvar.models import Clinvar
from conservation.models import KnowngeneAA
from dbsnp.models import Dbsnp
from frequencies.models import Exac, GnomadExomes, GnomadGenomes, ThousandGenomes
from geneinfo.models import Hgnc, Mim2geneMedgen, Hpo, NcbiGeneInfo, NcbiGeneRif
from hgmd.models import HgmdPublicLocus
from importer.models import ImportInfo
from pathways.models import EnsemblToKegg, RefseqToKegg, KeggInfo
from projectroles.models import Project
from variants.models import SmallVariant, Case
from ._private import TsvReader


Table = namedtuple("Database", "table null release_required deduplicate")


# class TemporaryAnnotation(Annotation)
# Inheritance won't work, because Django sets a ForeignKey to the base class and
# thus links a temporary table to the actual model which doesn't work
# overwriting the foreign key also doesn't work because either it reports a
# clash (when used as class parameter) or it doesn't get carried out because
# init function isn't called.


class Command(BaseCommand):
    help = "Sirloin database import"
    databases = {
        "smallvariant": Table(SmallVariant, ".", False, True),
        "case": Table(Case, "", False, False),
        "annotation": Table(Annotation, ".", False, True),
        "exac": Table(Exac, ".", True, False),
        "gnomadexomes": Table(GnomadExomes, ".", True, False),
        "gnomadgenomes": Table(GnomadGenomes, ".", True, False),
        "hgmd_public": Table(HgmdPublicLocus, "", True, False),
        "thousandgenomes": Table(ThousandGenomes, ".", True, False),
        "omim": Table(Mim2geneMedgen, "-", True, False),
        "hgnc": Table(Hgnc, "", True, False),
        "hpo": Table(Hpo, "", True, False),
        "dbsnp": Table(Dbsnp, "", True, False),
        "ensembltokegg": Table(EnsemblToKegg, "", True, False),
        "refseqtokegg": Table(RefseqToKegg, "", True, False),
        "kegginfo": Table(KeggInfo, "", True, False),
        "clinvar": Table(Clinvar, "", True, False),
        "knowngeneaa": Table(KnowngeneAA, "", True, False),
        "gene_info": Table(NcbiGeneInfo, "", True, False),
        "gene_rif": Table(NcbiGeneRif, "", True, False),
    }

    def add_arguments(self, parser):
        parser.add_argument("--path", help="Input file path", required=True)
        parser.add_argument(
            "--database", help="Input database", choices=self.databases.keys(), required=True
        )
        parser.add_argument("--release", help="Release version of the imported database")
        parser.add_argument("--comment", help="Comment for the imported database")
        parser.add_argument("--uuid", help="define uuid for case and smallvariant import")

    @transaction.atomic
    def handle(self, *args, **options):
        database = self.databases[options["database"]]

        if database.release_required:
            if not options["release"]:
                sys.exit("Please specify --release when importing {}".format(options["database"]))

            try:
                ImportInfo.objects.create(
                    table=type(database.table).__name__,
                    timestamp=timezone.now(),
                    release=options["release"],
                    comment=options["comment"] if options["comment"] else "",
                )
            except IntegrityError:
                sys.exit("This import already exists!")

        # we have to import the case database manually such that django sets
        # the uuid field itself
        if options["database"] == "case":
            if not options["uuid"]:
                sys.exit("Please specify --uuid when importing {}".format(options["database"]))

            try:
                project = Project.objects.get(sodar_uuid=options["uuid"])
            except ObjectDoesNotExist:
                sys.exit("Project with UUID {} does not exist".format(options["uuid"]))

            with TsvReader(options["path"], json_fields=["pedigree"]) as reader:
                for entry in reader:
                    entry["project"] = project
                    database.table.objects.get_or_create(**entry)
                return

        database.table.objects.from_csv(
            options["path"],
            delimiter="\t",
            null=database.null,
            ignore_conflicts=database.deduplicate,
            drop_constraints=not database.deduplicate,
            drop_indexes=not database.deduplicate,
        )
