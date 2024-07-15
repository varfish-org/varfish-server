"""Django management command for dumping StructuralVariant records as BED files"""

import sys

from django.core.management import BaseCommand

from svs.models import StructuralVariant


class Command(BaseCommand):
    """Dump all SVs as a BED file.

    Note that the resulting file will not be sorted by (chrom, begin) so the file needs to be reprocessed.
    """

    #: Help message displayed on the command line.
    help = "Dump all SVS as a BED file"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--release", help="The genome build to dump for", required=False, default="GRCh37"
        )
        parser.add_argument(
            "--chromosome", help="Chromosome to dump for", required=False, default=None
        )
        parser.add_argument(
            "--output-file",
            help="File to write to, leave blank to write to stdout",
            required=False,
            default=None,
        )

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        if options.get("output_file"):
            output_file = options["output_file"]
            self.stderr.write(f"Writing to {output_file}")
            with open(options["output_file"], "wt") as outputf:
                record_count = self._handle(options, outputf)
        else:
            self.stderr.write("Writing to stdout")
            record_count = self._handle(options, sys.stdout)
        self.stderr.write(self.style.SUCCESS(f"All done, wrote {record_count} records"))

    def _handle(self, options, outputf):
        record_count = 0
        filter_args = {"release": options["release"]}
        if options["chromosome"] is not None:
            filter_args["chromosome"] = options["chromosome"]
        for record_count, sv_record in enumerate(
            StructuralVariant.objects.filter(**filter_args).iterator()
        ):
            print(
                "\t".join(
                    map(
                        str,
                        [
                            sv_record.chromosome,
                            sv_record.start - 1,
                            sv_record.end,
                            f"{sv_record.sv_type}--{sv_record.case_id}",
                        ],
                    )
                ),
                file=outputf,
            )
        return record_count
