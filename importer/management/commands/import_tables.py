import os
import tempfile

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

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
)
from hgmd.models import HgmdPublicLocus
from ...models import ImportInfo
from pathways.models import EnsemblToKegg, RefseqToKegg, KeggInfo
from ..helpers.tsv_reader import tsv_reader


#: One entry in the TABLES variable is structured as follows:
#: 'table_group': (Table,)
TABLES = {
    "clinvar": (Clinvar,),
    "dbSNP": (Dbsnp,),
    "ExAC": (Exac,),
    "gnomAD_exomes": (GnomadExomes,),
    "gnomAD_genomes": (GnomadGenomes,),
    "hgmd_public": (HgmdPublicLocus,),
    "hgnc": (Hgnc, RefseqToHgnc),
    "hpo": (Hpo, HpoName),
    "kegg": (KeggInfo, EnsemblToKegg, RefseqToKegg),
    "knowngeneaa": (KnowngeneAA,),
    "ncbi_gene": (NcbiGeneInfo, NcbiGeneRif),
    "mim2gene": (Mim2geneMedgen,),
    "thousand_genomes": (ThousandGenomes,),
}


class Command(BaseCommand):
    """Command class for importing all external databases into Varfish tables.
    """

    #: Help message displayed on the command line.
    help = "Bulk import all external databases into Varfish tables."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--tables-path", required=True, help="Path to the varfish-db-downloader folder"
        )

    def handle(self, *args, **options):
        """Iterate over genomebuilds, database folders and versions to gather all required information for import.
        """

        path_import_versions = os.path.join(options["tables_path"], "import_versions.tsv")

        if not os.path.isfile(path_import_versions):
            raise CommandError("Require version import info file {}.".format(path_import_versions))

        for import_info in tsv_reader(path_import_versions):
            table_group = import_info["table_group"]
            version_path = os.path.join(
                options["tables_path"], import_info["build"], table_group, import_info["version"]
            )

            if table_group == "kegg":
                self._import_kegg(version_path, TABLES[table_group])
            elif table_group in ("gnomAD_genomes", "gnomAD_exomes"):
                self._import_gnomad(version_path, TABLES[table_group])
            else:
                for table in TABLES[table_group]:
                    self._import(*self._get_table_info(version_path, table.__name__), table)

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

    @transaction.atomic
    def _import(self, path, release_info, table, import_info=True):
        """Bulk data into table and add entry to ImportInfo table.

        :param table_path: Path to TSV file to import
        :param release_info: Content of release info as dict
        :param table: Django model object of table to import
        :param null: Null value for bulk import
        :return: Boolean if import happened (True) or not (False)
        """

        self.stdout.write(
            "Importing {} {} ({}, source: {}) ...".format(
                table.__name__, release_info["version"], release_info["genomebuild"], path
            )
        )

        if not release_info["table"] == table.__name__:
            CommandError("Table name in release_info file does not match table name.")

        if import_info:
            try:
                ImportInfo.objects.create(
                    genomebuild=release_info["genomebuild"],
                    table=table.__name__,
                    release=release_info["version"],
                )
            except IntegrityError as e:
                self.stdout.write(
                    "Skipping {table} {version} ({genomebuild}). Already imported.".format(
                        **release_info
                    )
                )
                return False

        table.objects.from_csv(
            path,
            delimiter="\t",
            null=release_info["null_value"],
            ignore_conflicts=False,
            drop_constraints=True,
            drop_indexes=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Finished importing {} {}".format(table.__name__, release_info["version"])
            )
        )
        return True

    @transaction.atomic
    def _import_kegg(self, path, tables):
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
            mapping, *self._get_table_info(path, tables[1].__name__), tables[1]
        )
        # Import RefseqToKegg
        self._replace_pk_in_kegg_and_import(
            mapping, *self._get_table_info(path, tables[2].__name__), tables[2]
        )

    def _replace_pk_in_kegg_and_import(self, mapping, path, release_info, table):
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
            self._import(tmp.name, release_info, table)

    @transaction.atomic
    def _import_gnomad(self, path, tables):
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
                chrom == 1
            ):
                break
