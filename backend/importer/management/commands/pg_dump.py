"""Django command that is a convenience wrapper around ``pg_dump``"""

from itertools import chain
import os
import subprocess
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

#: The available dump modes.
DUMP_MODES = ("full", "backup-large", "backup-small")
#: The tables to be ignored in backup-large mode.
IGNORE_LARGE = (
    "clinvar_clinvar",
    "conservation_knowngeneaa",
    "dbsnp_dbsnp",
    "extra_annos_extraanno",
    "extra_annos_extraannofield",
    "frequencies_exac",
    "frequencies_gnomadexomes",
    "frequencies_gnomadgenomes",
    "frequencies_helixmtdb",
    "frequencies_mitomap",
    "frequencies_mtdb",
    "frequencies_thousandgenomes",
)
#: The tables to be ignored in backup-thin mode.
IGNORE_THIN = (
    "variants_smallvariant_[0-9]*",
    "svs_structuralvariant[0-9]+",
    "svs_structuralvariantgeneannotation[0-9]+",
)


class Command(BaseCommand):
    """Implementation wrapping ``pg_dump`` to support creating dumps of the underlying PostgreSQL database."""

    #: Help message displayed on the command line.
    help = "Easily create database dumps with ``pg_dump``"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("--mode", help="Backup mode, one of %s" % (DUMP_MODES,), required=True)
        parser.add_argument(
            "--output-file", help="Optional path to write output to, default is stdout"
        )
        parser.add_argument(
            "--force-overwrite", default=False, action="store_true", help="Overwrite output file"
        )

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        if options["output_file"]:
            if os.path.exists(options["output_file"]) and not options["force_overwrite"]:
                self.stderr.write(
                    self.style.ERROR(
                        "Refusing to overwrite %s; use --force to force overwriting"
                        % options["output_file"]
                    )
                )
                raise CommandError("Refusing to overwrite %s" % options["output_file"])
            with open(options["output_file"], "wb") as outputf:
                self._run(options, outputf)
        else:
            self._run(options, sys.stdout)

    def _run(self, options, outputf):
        database = settings.DATABASES["default"]
        env = dict(os.environ)
        env["PGPASSWORD"] = database["PASSWORD"]

        cmd = [
            "/usr/bin/pg_dump",
            "--dbname=%s" % database["NAME"],
            "--host=%s" % database["HOST"],
            "--username=%s" % database["USER"],
        ]

        if options["mode"] == "backup-large":
            cmd += ["--exclude-table-data=%s" % pat for pat in IGNORE_LARGE]
        elif options["mode"] == "backup-small":
            cmd += ["--exclude-table-data=%s" % pat for pat in chain(IGNORE_LARGE, IGNORE_THIN)]

        self.stderr.write(self.style.NOTICE("Running the following command: %s" % cmd))
        subprocess.check_call(cmd, stdout=outputf, env=env)
        outputf.flush()
        self.stderr.write(self.style.NOTICE("All done. Have a nice day!"))
