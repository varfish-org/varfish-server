"""Django management command for filling NULL values in StructuralVariant records.

Also see https://github.com/bihealth/varfish-server/issues/566.
"""

import itertools

from django.core.management import BaseCommand
from tqdm import tqdm

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

            record.num_hom_alt = 0
            record.num_hom_ref = 0
            record.num_het = 0
            record.num_hemi_alt = 0
            record.num_hemi_ref = 0
            for k, v in record.genotype.items():
                gt = v["gt"]
                k_sex = sex.get(record.case_id, {}).get(k, 0)
                if gt == "1":
                    record.num_hemi_alt += 1
                elif gt == "0":
                    record.num_hemi_ref += 1
                elif gt in ("0/1", "1/0", "0|1", "1|0"):
                    record.num_het += 1
                elif gt in ("0/0", "0|0"):
                    if "x" in record.chromosome.lower() and k_sex == 1:
                        record.num_hemi_ref += 1
                    else:
                        record.num_hom_ref += 1
                elif gt in ("1|1", "1|1"):
                    if "x" in record.chromosome.lower() and k_sex == 1:
                        record.num_hemi_alt += 1
                    else:
                        record.num_hom_alt += 1
            record.save()
        self.stderr.write("... all done, have a nice day!")
