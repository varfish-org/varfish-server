"""Django management command for dumping a ``BackgroundSvSet`` as BED file."""

from django.core.management import BaseCommand
from sqlalchemy import select

from svs.models import BackgroundSv, BackgroundSvSet
from variants.helpers import get_engine, get_meta


class Command(BaseCommand):
    """Dump a single ``BackgroundSvSet`` as BED file."""

    #: Help message displayed on the command line.
    help = "List existing background SV sets"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("bg_sv_set_uuid", help="UUID of bg sv set to dump", default="GRCh37")

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        self.stderr.write("Obtaining SV set")
        bg_sv_set = BackgroundSvSet.objects.get(sodar_uuid=options["bg_sv_set_uuid"])
        self.stderr.write("Dumping SV set to BED file")
        meta = get_meta()
        sa_table = meta.tables[BackgroundSv._meta.db_table]
        query = (
            select(sa_table.c.chromosome, sa_table.c.start, sa_table.c.end, sa_table.c.sv_type)
            .select_from(sa_table)
            .where(sa_table.c.bg_sv_set_id == bg_sv_set.id)
        )
        for row in get_engine().execute(query):
            print("\t".join(map(str, [row.chromosome, row.start - 1, row.end, row.sv_type])))
        self.stderr.write(self.style.SUCCESS("All done, have a nice day!"))
