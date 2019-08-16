"""Import of a database of structural variants for the ``svdbs`` app.
"""
import sys
import traceback
from multiprocessing.pool import ThreadPool

import aldjemy

from importer.management.helpers import tsv_reader

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"

import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import ImportInfo

from variants.helpers import SQLALCHEMY_ENGINE


#: One entry in the TABLES variable is structured as follows:
#: 'genome_build': {'table_group': (Table,), ...}
TABLES = {
    "GRCh37": {
        "dbVar": (DbVarSv,),
        "DGV": (DgvGoldStandardSvs, DgvSvs),
        "ExAC": (ExacCnv,),
        "gnomAD_SV": (GnomAdSv,),
        "thousand_genomes": (ThousandGenomesSv,),
    },
    "GRCh38": {
        "dbVar": (DbVarSv,),
        "DGV": (DgvSvs,),
        "ExAC": (ExacCnv,),
        "gnomAD_SV": (GnomAdSv,),
        "thousand_genomes": (ThousandGenomesSv,),
    },
}
SERVICE_NAME_CHOICES = ["CADD", "Exomiser"]
SERVICE_GENOMEBUILD_CHOICES = ["GRCh37", "GRCh38"]


class Command(BaseCommand):
    """Django management command for the import of structural variant databases."""

    help = "Import of structural variant databases"

    # Copied from import_tables. For easy merge later on.
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

    # Copied from import_tables. For easy merge later on.
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
                if import_info["table_group"] in TABLES:
                    self._handle_import(import_info, options)
                else:
                    self.stderr.write(
                        "Table group {} is no registered table group.".format(
                            import_info["table_group"]
                        )
                    )
        else:
            pool = ThreadPool(processes=options["threads"])
            for import_info in import_infos:
                if import_info["table_group"] in TABLES:
                    pool.apply_async(self._handle_import_try_catch, (import_info, options))
                else:
                    self.stderr.write(
                        "Table group {} is no registered table group.".format(
                            import_info["table_group"]
                        )
                    )
            pool.close()
            pool.join()

    # Copied from import_tables. For easy merge later on.
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

    # Copied from import_tables. For easy merge later on. (changed)
    def _handle_import(self, import_info, options):
        with transaction.atomic():
            table_group = import_info["table_group"]
            version_path = os.path.join(
                options["tables_path"], import_info["build"], table_group, import_info["version"]
            )

            for table in TABLES[import_info["build"]][table_group]:
                self._import(
                    *self._get_table_info(version_path, table.__name__),
                    table,
                    force=options["force"],
                )

    # Copied from import_tables. For easy merge later on.
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

    # Copied from import_tables. For easy merge later on.
    def _read_release_info_file(self, path):
        """Read the release file info into memory.

        :param path: Path to the release info file
        :return: Dict with column names as keys and the values as values
        """
        return next(tsv_reader(path))

    # Copied from import_tables. For easy merge later on.
    def _create_import_info(self, release_info, force):
        """Create entry in ImportInfo from the given ``release_info``."""
        existing = ImportInfo.objects.filter(
            genomebuild=release_info["genomebuild"], table=release_info["table"]
        )
        if not force and existing.all():
            self.stdout.write(
                "Skipping {table} {version} ({genomebuild}). Already imported.".format(
                    **release_info
                )
            )
            return False
        else:
            # Remove existing entries, if any
            existing.delete()
            # Create new entry
            ImportInfo.objects.create(
                genomebuild=release_info["genomebuild"],
                table=release_info["table"],
                release=release_info["version"],
            )
            return True

    # Copied from import_tables. For easy merge later on.
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
            if not self._create_import_info(release_info, force):
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
