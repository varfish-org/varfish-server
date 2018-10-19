from django.core.management.base import BaseCommand
from django.db import transaction
from variants.models import Case
from pathways.models import KeggInfo
from django.forms.models import model_to_dict
from ._private import TsvReader


tables = {
    "case": Case,
    "kegginfo": KeggInfo,
}


class Command(BaseCommand):
    help = "Sirloin substitute foreign keys tsv file"

    def add_arguments(self, parser):
        parser.add_argument("--in", help="Input file path", required=True)
        parser.add_argument("--out", help="Output file path", required=True)
        parser.add_argument("--table", help="Table that is to be linked", choices=tables.keys(), required=True)
        parser.add_argument("--field", help="Fieldname in <table> that links the two tables in (fieldname in <in> is `<table>_id`", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        table = tables[options["table"]]
        mapping = dict()

        for obj in table.objects.all():
            d = model_to_dict(obj)
            mapping[d[options["field"]]] = d["id"]

        with open(options["out"], "w") as fh, TsvReader(options["in"]) as reader:
            fh.write("\t".join(reader.header) + "\n")
            for line in reader:
                line[options["table"] + "_id"] = str(mapping.get(line[options["table"] + "_id"], line[options["table"] + "_id"]))
                fh.write("\t".join(line[field] for field in reader.header) + "\n")

    # @transaction.atomic
    # def handle(self, *args, **options):
    #     mapping = {obj.name: obj.id for obj in Case.objects.all()}
    #
    #     with open(options["out"], "w") as fh, TsvReader(options["in"]) as reader:
    #         fh.write("\t".join(reader.header) + "\n")
    #         for line in reader:
    #             line["case_id"] = str(mapping.get(line["case_id"], line["case_id"]))
    #             fh.write("\t".join(line[field] for field in reader.header) + "\n")
