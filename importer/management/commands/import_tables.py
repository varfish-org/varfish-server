import os
import tempfile

import binning
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clinvar.models import Clinvar
from conservation.models import KnowngeneAA
from dbsnp.models import Dbsnp
from frequencies.models import Exac, GnomadExomes, GnomadGenomes, ThousandGenomes
from geneinfo.models import (
    Hgnc,
    Mim2geneMedgen,
    Hpo,
    NcbiGeneInfo,
    NcbiGeneRif,
    HpoName,
    RefseqToHgnc,
    Acmg,
    GnomadConstraints,
    ExacConstraints,
    EnsemblToRefseq,
    RefseqToEnsembl,
)
from genomicfeatures.models import (
    GeneInterval,
    EnsemblRegulatoryFeature,
    TadSet,
    TadInterval,
    TadBoundaryInterval,
    VistaEnhancer,
)
from hgmd.models import HgmdPublicLocus
from ...models import ImportInfo
from pathways.models import EnsemblToKegg, RefseqToKegg, KeggInfo
from ..helpers import open_file, tsv_reader


#: One entry in the TABLES variable is structured as follows:
#: 'table_group': (Table,)
TABLES = {
    "clinvar": (Clinvar,),
    "dbSNP": (Dbsnp,),
    "ExAC": (Exac,),
    "ExAC_constraints": (ExacConstraints,),
    "gnomAD_exomes": (GnomadExomes,),
    "gnomAD_genomes": (GnomadGenomes,),
    "gnomAD_constraints": (GnomadConstraints,),
    "hgmd_public": (HgmdPublicLocus,),
    "hgnc": (Hgnc, RefseqToHgnc),
    "hpo": (Hpo, HpoName),
    "kegg": (KeggInfo, EnsemblToKegg, RefseqToKegg),
    "knowngeneaa": (KnowngeneAA,),
    "ncbi_gene": (NcbiGeneInfo, NcbiGeneRif),
    "mim2gene": (Mim2geneMedgen,),
    "thousand_genomes": (ThousandGenomes,),
    "acmg": (Acmg,),
    "vista": (VistaEnhancer,),
    "ensembl_regulatory": (EnsemblRegulatoryFeature,),
    "ensembl_genes": (GeneInterval,),
    "refseq_genes": (GeneInterval,),
    "tads_hesc": (TadInterval, TadBoundaryInterval, TadSet),
    "tads_imr90": (TadInterval, TadBoundaryInterval, TadSet),
    "ensembltorefseq": (EnsemblToRefseq,),
    "refseqtoensembl": (RefseqToEnsembl,),
}
SERVICE_NAME_CHOICES = ["CADD", "Exomiser"]
SERVICE_GENOMEBUILD_CHOICES = ["GRCh37", "GRCh38"]


#: Mapping from file ENSEMBL regulatory features header to field names
ENSEMBL_REGULATORY_HEADER_MAP = {
    "Chromosome/scaffold name": "chromosome",
    "Start (bp)": "start",
    "End (bp)": "end",
    "Regulatory stable ID": "stable_id",
    "Feature type": "feature_type",
    "Feature type description": "feature_type_description",
    "SO term accession": "so_term_accession",
    "SO term name": "so_term_name",
}


class Command(BaseCommand):
    """Command class for importing all external databases into Varfish tables.
    """

    #: Help message displayed on the command line.
    help = "Bulk import all external databases into Varfish tables."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("--tables-path", help="Path to the varfish-db-downloader folder")
        parser.add_argument(
            "--import-versions-path",
            help="Path to the import_versions.tsv file (optional; defaults to the one in --tables-path)",
        )
        parser.add_argument("--service", action="store_true", help="Import service data")
        parser.add_argument(
            "--service-name", help="Name for service import", choices=SERVICE_NAME_CHOICES
        )
        parser.add_argument("--service-version", help="Version for service import")
        parser.add_argument(
            "--service-genomebuild",
            help="Genomebuild for service import",
            choices=SERVICE_GENOMEBUILD_CHOICES,
        )
        parser.add_argument(
            "--force", help="Force import, removes old data", action="store_true", default=False
        )

    def handle(self, *args, **options):
        """Iterate over genomebuilds, database folders and versions to gather all required information for import.
        """

        if not options["service"] and options["tables_path"] is None:
            raise CommandError("Please set either --tables-path or --service")
        if options["tables_path"] and options["service"]:
            raise CommandError("Please set either --tables-path or --service")
        if options["service"] and (
            options["service_name"] is None
            or options["service_version"] is None
            or options["service_genomebuild"] is None
        ):
            raise CommandError(
                "Please set --service-name, --service-version and --service-genomebuild when using flag --service"
            )

        if options["service"]:
            self._import(
                None,
                {
                    "table": options["service_name"],
                    "genomebuild": options["service_genomebuild"],
                    "version": options["service_version"],
                },
                None,
                import_info=True,
                service=True,
            )
            return

        path_import_versions = options.get("import_versions_path") or os.path.join(
            options["tables_path"], "import_versions.tsv"
        )

        if not os.path.isfile(path_import_versions):
            raise CommandError("Require version import info file {}.".format(path_import_versions))

        for import_info in tsv_reader(path_import_versions):
            with transaction.atomic():
                table_group = import_info["table_group"]
                version_path = os.path.join(
                    options["tables_path"],
                    import_info["build"],
                    table_group,
                    import_info["version"],
                )

                if table_group == "kegg":
                    self._import_kegg(version_path, TABLES[table_group], force=options["force"])
                elif table_group in ("gnomAD_genomes", "gnomAD_exomes"):
                    self._import_gnomad(version_path, TABLES[table_group], force=options["force"])
                elif table_group == "vista":
                    self._import_vista(version_path, TABLES[table_group], force=options["force"])
                elif table_group == "ensembl_regulatory":
                    self._import_ensembl_regulatory(
                        version_path, TABLES[table_group], force=options["force"]
                    )
                elif table_group == "ensembl_genes":
                    self._import_gene_interval(
                        version_path, TABLES[table_group], "ensembl", force=options["force"]
                    )
                elif table_group == "refseq_genes":
                    self._import_gene_interval(
                        version_path, TABLES[table_group], "refseq", force=options["force"]
                    )
                elif table_group == "tads_imr90":
                    self._import_tad_set(
                        version_path, TABLES[table_group], "imr90", force=options["force"]
                    )
                elif table_group == "tads_hesc":
                    self._import_tad_set(
                        version_path, TABLES[table_group], "hesc", force=options["force"]
                    )
                else:
                    for table in TABLES[table_group]:
                        self._import(
                            *self._get_table_info(version_path, table.__name__),
                            table,
                            force=options["force"],
                        )

    def _import_tad_set(self, path, tables, subset_key, force):
        """TAD import"""
        release_info = self._get_table_info(path, tables[0].__name__)[1]
        # release_info["table"] += ":%s" % subset_key
        if not force and not self._create_import_info(release_info):
            return False

        # Clear out old data if any
        TadSet.objects.filter(release=release_info["genomebuild"], name=subset_key).delete()

        titles = {
            "hesc": "hESC TADs (Dixon et al., 2019)",
            "imr90": "IMR90 TADs (Dixon et al., 2019)",
        }

        # Create the TadSet.
        tad_set = TadSet.objects.create(
            release=release_info["genomebuild"],
            name=subset_key,
            version=release_info["version"],
            title=titles[subset_key],
        )

        # Perform the import of the TADs and boundaries
        self.stdout.write("Importing TADs %s" % release_info)
        path_tsv = os.path.join(path, "{}.tsv".format(tables[0].__name__))
        prev_chromosome = None
        with open_file(path_tsv, "rt") as inputf:
            while True:
                line = inputf.readline().strip()
                if not line:
                    break
                arr = line.split("\t")
                chromosome, begin, end = arr[:3]
                begin = int(begin)
                end = int(end)
                if prev_chromosome != chromosome:
                    self.stdout.write("  now on chr%s" % chromosome)
                    prev_chromosome = chromosome
                TadInterval.objects.create(
                    tad_set=tad_set,
                    bin=binning.assign_bin(begin, end),
                    containing_bins=binning.containing_bins(begin, end),
                    release=release_info["genomebuild"],
                    chromosome=chromosome,
                    start=begin + 1,
                    end=end,
                )
                PADDING = 10000
                if begin > PADDING:
                    TadBoundaryInterval.objects.create(
                        tad_set=tad_set,
                        bin=binning.assign_bin(begin, end),
                        containing_bins=binning.containing_bins(begin, end),
                        release=release_info["genomebuild"],
                        chromosome=chromosome,
                        start=begin + 1 - PADDING,
                        end=begin + 1 + PADDING,
                    )
        self.stdout.write(self.style.SUCCESS("Finished importing TADs"))

    def _import_gene_interval(self, path, tables, subset_key, force):
        """Common code for RefSeq and ENSEMBL gene import."""
        release_info = self._get_table_info(path, tables[0].__name__)[1]
        release_info["table"] += ":%s" % subset_key
        if not force and not self._create_import_info(release_info):
            return False
        # Clear out any existing entries for this release/database.
        GeneInterval.objects.filter(
            database=subset_key, release=release_info["genomebuild"]
        ).delete()
        # Perform the actual data import
        self.stdout.write("Importing gene intervals")
        path_tsv = os.path.join(path, "{}.tsv".format(tables[0].__name__))
        prev_chromosome = None
        with open_file(path_tsv, "rt") as inputf:
            while True:
                line = inputf.readline().strip()
                if not line:
                    break
                arr = line.split("\t")
                chromosome, begin, end = arr[:3]
                if prev_chromosome != chromosome:
                    self.stdout.write("  now on chr%s" % chromosome)
                    prev_chromosome = chromosome
                gene_id = arr[3]
                begin = int(begin)
                end = int(end)
                GeneInterval.objects.create(
                    bin=binning.assign_bin(begin, end),
                    containing_bins=binning.containing_bins(begin, end),
                    release=release_info["genomebuild"],
                    chromosome=chromosome,
                    start=begin + 1,
                    end=end,
                    database=subset_key,
                    gene_id=gene_id,
                )
        self.stdout.write(self.style.SUCCESS("Finished importing gene intervals"))

    def _import_ensembl_regulatory(self, path, tables, force):
        """Import ENSEMBL regulatory regions."""
        release_info = self._get_table_info(path, tables[0].__name__)[1]
        if not force and not self._create_import_info(release_info):
            return False

        # Clear out any existing entries for this release/database.
        o = EnsemblRegulatoryFeature.objects.filter(release=release_info["genomebuild"])
        if o.count():
            self.stdout.write("Removing old ENSEMBL regulatory features.")
            o.delete()
        # Perform the actual import
        self.stdout.write("Importing ENSEMBL regulatory features")
        path_tsv = os.path.join(path, "{}.tsv".format(tables[0].__name__))
        prev_chromosome = None
        with open_file(path_tsv, "rt") as inputf:
            header = None
            while True:
                line = inputf.readline().strip()
                if not line:
                    break
                arr = line.split("\t")
                if not header:
                    header = arr
                else:
                    values = {ENSEMBL_REGULATORY_HEADER_MAP[k]: v for k, v in zip(header, arr)}
                    if prev_chromosome != values["chromosome"]:
                        prev_chromosome = values["chromosome"]
                        self.stdout.write("  now on chr%s" % prev_chromosome)
                    values["start"] = int(values["start"])
                    values["end"] = int(values["end"])
                    EnsemblRegulatoryFeature.objects.create(
                        bin=binning.assign_bin(values["start"] - 1, values["end"] - 1),
                        containing_bins=binning.containing_bins(
                            values["start"] - 1, values["end"] - 1
                        ),
                        release=release_info["genomebuild"],
                        **values,
                    )
        self.stdout.write(self.style.SUCCESS("Finished importing ENSEMBL regulatory features"))

    def _import_vista(self, path, tables, force):
        """Import VISTA from the given path."""
        release_info = self._get_table_info(path, tables[0].__name__)[1]
        if not force and not self._create_import_info(release_info):
            return False

        # Clear out any existing entries for this release/database.
        o = VistaEnhancer.objects.filter(release=release_info["genomebuild"])
        if o.count():
            self.stdout.write("Removing old VISTA experimental results.")
            o.delete()
        # Perform the actual import.
        self.stdout.write("Importing VISTA experimental results")
        path_tsv = os.path.join(path, "{}.tsv".format(tables[0].__name__))
        with open_file(path_tsv, "rt") as inputf:
            header = ("chromosome", "start", "end", "element_id", "validation_result")
            while True:
                line = inputf.readline().strip()
                if not line:
                    break
                arr = line.split("\t")
                if not header:
                    header = arr
                else:
                    values = dict(zip(header, arr))
                    values["start"] = int(values["start"])
                    values["end"] = int(values["end"])
                    VistaEnhancer.objects.create(
                        bin=binning.assign_bin(values["start"] - 1, values["end"] - 1),
                        containing_bins=binning.containing_bins(
                            values["start"] - 1, values["end"] - 1
                        ),
                        release=release_info["genomebuild"],
                        **values,
                    )
        self.stdout.write(self.style.SUCCESS("Finished importing VISTA experimental results"))

    def _get_table_info(self, path, table_name):
        """Crawl versions of a database table.

        :param path: Path to a specific database
        :return: Returns tuple of table information as dict and the path to the table file
        """

        release_info = os.path.join(path, "{}.release_info".format(table_name))
        table_path = os.path.join(path, "{}.tsv".format(table_name))

        if not os.path.isfile(release_info):
            raise CommandError("Require {}".format(release_info))

        if not os.path.isfile(table_path):
            raise CommandError("Require {}".format(table_path))

        return table_path, self._read_release_info_file(release_info)

    def _read_release_info_file(self, path):
        """Read the release file info into memory.

        :param path: Path to the release info file
        :return: Dict with column names as keys and the values as values
        """
        return next(tsv_reader(path))

    def _create_import_info(self, release_info):
        """Create entry in ImportInfo from the given ``release_info``."""
        existing = ImportInfo.objects.filter(
            genomebuild=release_info["genomebuild"], table=release_info["table"]
        )
        if existing.all():
            self.stdout.write(
                "Skipping {table} {version} ({genomebuild}). Already imported.".format(
                    **release_info
                )
            )
            return False
        else:
            ImportInfo.objects.create(
                genomebuild=release_info["genomebuild"],
                table=release_info["table"],
                release=release_info["version"],
            )
            return True

    def _import(self, path, release_info, table, import_info=True, service=False, force=False):
        """Bulk data into table and add entry to ImportInfo table.

        :param table_path: Path to TSV file to import
        :param release_info: Content of release info as dict
        :param table: Django model object of table to import
        :param null: Null value for bulk import
        :return: Boolean if import happened (True) or not (False)
        """

        self.stdout.write(
            "Importing {table} {version} ({genomebuild}, source: {path}) ...".format(
                **release_info, path=path
            )
        )

        if not service and not release_info["table"] == table.__name__:
            CommandError("Table name in release_info file does not match table name.")

        if import_info:
            if not force and not self._create_import_info(release_info):
                return False
            try:
                o = table.objects.filter(release=release_info["genomebuild"])
            except (FieldDoesNotExist, FieldError):
                o = table.objects.all()
            if o.count():
                # Clear out any existing entries for this release/database.
                self.stdout.write("Removing old {table} results.".format(**release_info))
                o.delete()

        if not service:
            table.objects.from_csv(
                path,
                delimiter="\t",
                null=release_info["null_value"],
                ignore_conflicts=False,
                drop_constraints=True,
                drop_indexes=True,
            )

        self.stdout.write(
            self.style.SUCCESS("Finished importing {table} {version}".format(**release_info))
        )
        return True

    def _import_kegg(self, path, tables, force):
        """Wrapper function to import kegg databases.

        :param path: Path to kegg tables
        :param tables: List of kegg models
        :return: Nothing
        """
        # Import kegginfo (first entry is kegginfo)
        self._import(*self._get_table_info(path, tables[0].__name__), tables[0])
        self.stdout.write("Creating mapping for EnsemblToKegg and RefseqToKegg import ...")
        # Create kegg_id->id mapping from kegginfo import
        mapping = {entry.kegg_id: str(entry.id) for entry in KeggInfo.objects.all()}
        # Import EnsembleToKegg
        self._replace_pk_in_kegg_and_import(
            mapping, *self._get_table_info(path, tables[1].__name__), tables[1], force
        )
        # Import RefseqToKegg
        self._replace_pk_in_kegg_and_import(
            mapping, *self._get_table_info(path, tables[2].__name__), tables[2], force
        )

    def _replace_pk_in_kegg_and_import(self, mapping, path, release_info, table, force):
        """Wrapper function to replace pk in mapping tables before import (and then import).

        :param mapping: Mapping of kegg ids to KeggInfo pks.
        :param path: Path to kegg tsv files.
        :param release_info: Release info dict.
        :param table: Current model.
        :return: Nothing.
        """
        self.stdout.write("Creating temporary TSV file for replacing kegg_id with PK ...")
        with tempfile.NamedTemporaryFile("w+t") as tmp, open(path, "r") as tsv:
            header = tsv.readline().strip()
            try:
                replace_idx = header.split("\t").index("kegginfo_id")
            except ValueError as e:
                raise CommandError("Column 'kegginfo_id' not found in {}".format(path)) from e
            tmp.write("{}\n".format(header))
            while True:
                line = tsv.readline().strip()
                if not line:
                    break
                fields = line.split("\t")
                fields[replace_idx] = mapping[fields[replace_idx]]
                tmp.write("\t".join(fields))
                tmp.write("\n")
            tmp.flush()
            self._import(tmp.name, release_info, table, force=force)

    def _import_gnomad(self, path, tables, force):
        """Wrapper function to import gnomad tables

        :param path: Path to gnomad tables
        :param tables: Gnomad models.
        :return: Nothing
        """
        # Import file is scattered into chromosome pieces, collect them.
        for chrom in list(range(1, 23)) + ["X"]:
            # If the first chromosome can't be imported, don't try to import the other chromosomes.
            if not self._import(
                # Add chromosome to file name
                *self._get_table_info(path, "{}.{}".format(tables[0].__name__, chrom)),
                tables[0],
                # Import into info table only once
                chrom == 1,
                force=force,
            ):
                break
