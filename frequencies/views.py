from .models import GnomadGenomes, GnomadExomes, Exac, ThousandGenomes
from querybuilder.models_support import QueryBuilder


class FrequencyMixin:
    def get_frequencies(self, fields=("af", "an", "ac", "hom", "het", "hemi")):
        key = {
            "release": self.kwargs["release"],
            "chromosome": self.kwargs["chromosome"],
            "position": int(self.kwargs["position"]),
            "reference": self.kwargs["reference"],
            "alternative": self.kwargs["alternative"],
        }

        qb = QueryBuilder()
        dbs = (
            (
                GnomadExomes,
                qb.build_gnomadexomes_query(key),
                "gnomadexomes",
                ("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"),
            ),
            (
                GnomadGenomes,
                qb.build_gnomadgenomes_query(key),
                "gnomadgenomes",
                ("afr", "amr", "asj", "eas", "fin", "nfe", "oth"),
            ),
            (
                Exac,
                qb.build_exac_query(key),
                "exac",
                ("afr", "amr", "eas", "fin", "nfe", "oth", "sas"),
            ),
            (
                ThousandGenomes,
                qb.build_thousandgenomes_query(key),
                "thousandgenomes",
                ("afr", "amr", "eas", "eur", "sas"),
            ),
        )

        for db, query, name, populations in dbs:
            self.kwargs[name] = dict()
            results = list(db.objects.raw(*query))

            if len(results) == 0:
                continue

            if len(results) > 1:
                raise Exception("Got more than one object.")

            results = results[0]

            for typ in fields:
                if name == "thousandgenomes" and typ == "hemi":
                    continue

                self.kwargs[name][typ] = getattr(results, typ)

                if name == "thousandgenomes" and not typ == "af":
                    continue

                for population in populations:
                    typpop = "{}_{}".format(typ, population)
                    self.kwargs[name][typpop] = getattr(results, typpop)
