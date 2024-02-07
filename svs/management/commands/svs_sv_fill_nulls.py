"""Django management command for filling NULL values in StructuralVariant records.

Also see https://github.com/varfish-org/varfish-server/issues/566.
"""

import itertools

from django.core.management import BaseCommand
from tqdm import tqdm

from svs import bg_db
from svs.models import StructuralVariant
from variants.models import Case


class Command(BaseCommand):
    """Retrieve all StructuralVariant records with NULL values, fill them and write them back."""

    #: Help message displayed on the command line.
    help = "fill NULL values in sv records"

    def handle(self, *args, **options):
        self.stderr.write("counting affected records...")
        total_count = StructuralVariant.objects.filter(bin2=None).count()
        self.stderr.write("creating iterator...")
        iterator = StructuralVariant.objects.filter(bin2=None).iterator()
        first = itertools.islice(iterator, 1)
        self.stderr.write("processing records...")
        sex = {}
        for record in tqdm(iterable=itertools.chain(first, iterator), total=total_count):
            if record.case_id not in sex:
                try:
                    case = Case.objects.get(pk=record.case_id)
                except Case.DoesNotExist:
                    pass
                else:
                    record[record.case_id] = {
                        person["patient"]: person["sex"] for person in case.pedigree
                    }
            record.chromosome2 = record.chromosome
            record.chromosome_no2 = record.chromosome_no
            record.bin2 = record.bin

            bg_db._fill_null_counts(record, sex)
            record.save()
        self.stderr.write("... all done, have a nice day!")
