import os
import sys
import traceback
from multiprocessing.pool import ThreadPool
import tempfile

import aldjemy
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

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


#: One entry in the TABLES variable is structured as follows:
#: 'table_group': (Table,)
TABLES = {
    "acmg": (Acmg,),
    "clinvar": (Clinvar,),
    "dbSNP": (Dbsnp,),
    "ensembl_genes": (GeneInterval,),
    "ensembl_regulatory": (EnsemblRegulatoryFeature,),
    "ensembltorefseq": (EnsemblToRefseq,),
    "ExAC": (Exac,),
    "ExAC_constraints": (ExacConstraints,),
    "gnomAD_constraints": (GnomadConstraints,),
    "gnomAD_exomes": (GnomadExomes,),
    "gnomAD_genomes": (GnomadGenomes,),
    "hgmd_public": (HgmdPublicLocus,),
    "hgnc": (Hgnc, RefseqToHgnc),
    "hpo": (Hpo, HpoName),
    "kegg": (KeggInfo, EnsemblToKegg, RefseqToKegg),
    "knowngeneaa": (KnowngeneAA,),
    "mim2gene": (Mim2geneMedgen,),
    "ncbi_gene": (NcbiGeneInfo, NcbiGeneRif),
    "refseq_genes": (GeneInterval,),
    "tads_hesc": (TadInterval, TadBoundaryInterval, TadSet),
    "tads_imr90": (TadInterval, TadBoundaryInterval, TadSet),
    "refseqtoensembl": (RefseqToEnsembl,),
    "thousand_genomes": (ThousandGenomes,),
    "vista": (VistaEnhancer,),
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
        parser.add_argument(
            # Using 8 threads by default as this will make all (currently) large tables import in parallel.
            "--threads",
            help="Number of parallel import processes",
            type=int,
            default="8",
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

        import_infos = list(tsv_reader(path_import_versions))
        if options["threads"] == 0:  # sequential
            for import_info in import_infos:
                self._handle_import(import_info, options)
        else:
            pool = ThreadPool(processes=options["threads"])
            for import_info in import_infos:
                pool.apply_async(self._handle_import_try_catch, (import_info, options))
            pool.close()
            pool.join()

    def _handle_import_try_catch(self, *args, **kwargs):
        """Helper that prints exception tracebacks (used for parallel execution)."""
        try:
            return self._handle_import(*args, **kwargs)
        except Exception as e:
            print(
                "Caught exception in worker thread with arguments (%s, %s)" % (args, kwargs),
                file=sys.stderr,
            )
            traceback.print_exc(file=sys.stderr)
            raise e

    def _handle_import(self, import_info, options):
        with transaction.atomic():
            table_group = import_info["table_group"]
            version_path = os.path.join(
                options["tables_path"], import_info["build"], table_group, import_info["version"]
            )

            # Special import routine for kegg
            if table_group == "kegg":
                self._import_kegg(version_path, TABLES[table_group], force=options["force"])
            # Special import routine for gnomaAD
            elif table_group in ("gnomAD_genomes", "gnomAD_exomes"):
                self._import_gnomad(version_path, TABLES[table_group], force=options["force"])
            # Special import routine for gene intervals
            elif table_group in ("ensembl_genes", "refseq_genes"):
                self._import_gene_interval(
                    version_path,
                    TABLES[table_group],
                    table_group.rstrip("_genes"),
                    force=options["force"],
                )
            # Special import routine for tads
            elif table_group in ("tads_imr90", "tads_hesc"):
                self._import_tad_set(
                    version_path,
                    TABLES[table_group],
                    table_group.lstrip("tads_"),
                    force=options["force"],
                )
            # Import routine for no-bulk-imports
            elif table_group in ("ensembl_regulatory", "vista"):
                for table in TABLES[table_group]:
                    self._import(
                        *self._get_table_info(version_path, table.__name__),
                        table,
                        force=options["force"],
                        bulk=False,
                    )
            # Import routine for bulk imports (default)
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
        for record in tsv_reader(path_tsv):
            if prev_chromosome != record["chromosome"]:
                prev_chromosome = record["chromosome"]
                self.stdout.write("tad_set::%s  now on chr%s" % (path_tsv, prev_chromosome))
                TadInterval.objects.create(tad_set=tad_set, **record)
                PADDING = 10000
                if int(record["start"]) > PADDING:
                    TadBoundaryInterval.objects.create(
                        tad_set=tad_set,
                        bin=int(record["bin"]),
                        release=record["release"],
                        chromosome=record["chromosome"],
                        start=int(record["start"]) + 1 - PADDING,
                        # TODO This was "start" ... "end" makes more sense?
                        end=int(record["end"]) + 1 + PADDING,
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
        for record in tsv_reader(path_tsv):
            if prev_chromosome != record["chromosome"]:
                prev_chromosome = record["chromosome"]
                self.stdout.write("geneinterval::%s  now on chr%s" % (path_tsv, prev_chromosome))
            GeneInterval.objects.create(**record)
        self.stdout.write(self.style.SUCCESS("Finished importing gene intervals"))

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

    def _import(
        self, path, release_info, table, import_info=True, service=False, force=False, bulk=True
    ):
        """Bulk data into table and add entry to ImportInfo table.

        :param table_path: Path to TSV file to import
        :param release_info: Content of release info as dict
        :param table: Django model object of table to import
        :param null: Null value for bulk import
        :return: Boolean if import happened (True) or not (False)
        """

        self.stdout.write(
            "{table} -- Importing {table} {version} ({genomebuild}, source: {path}) ...".format(
                **release_info, path=path
            )
        )

        if not service and not release_info["table"] == table.__name__:
            CommandError("Table name in release_info file does not match table name.")

        if import_info:
            if not force and not self._create_import_info(release_info):
                return False
            # Clear out any existing entries for this release/database.
            self.stdout.write("{table} -- Removing old {table} results.".format(**release_info))
            sa_table = aldjemy.core.get_meta().tables[table._meta.db_table]
            if "release" in sa_table.c:
                SQLALCHEMY_ENGINE.execute(
                    sa_table.delete().where(sa_table.c.release == release_info["genomebuild"])
                )
            else:
                SQLALCHEMY_ENGINE.execute(sa_table.delete())

        if not service:
            self.stdout.write("{table} -- Importing new {table} data".format(**release_info))
            if bulk:
                table.objects.from_csv(
                    path,
                    delimiter="\t",
                    null=release_info["null_value"],
                    ignore_conflicts=False,
                    drop_constraints=True,
                    drop_indexes=True,
                )
            else:  # no bulk import
                for record in tsv_reader(path):
                    table.objects.create(**record)

        self.stdout.write(
            self.style.SUCCESS(
                "{table} -- Finished importing {table} {version}".format(**release_info)
            )
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
