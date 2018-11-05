from .models import GnomadGenomes, GnomadExomes, Exac, ThousandGenomes
from querybuilder.models_support import FREQUENCY_DB_INFO, FrequencyQuery


class FrequencyMixin:
    def get_frequencies(self, alchemy_connection, query_kwargs, fields=("af", "an", "ac", "hom", "het", "hemi")):
        key = {
            "release": query_kwargs["release"],
            "chromosome": query_kwargs["chromosome"],
            "position": int(query_kwargs["position"]),
            "reference": query_kwargs["reference"],
            "alternative": query_kwargs["alternative"],
        }

        result = {key: {} for key in FREQUENCY_DB_INFO}
        for db_name in FREQUENCY_DB_INFO:
            query = FrequencyQuery(alchemy_connection, db_name)
            results = list(query.run(key))
            # FIXME: remove these dummy entry setting and fix query instead
            for pop in FREQUENCY_DB_INFO[db_name]["populations"]:
                for field in fields:
                    result[db_name]["%s_%s" % (field, pop)] = -1
            continue
            # FIXME end

            if len(results) == 0:
                continue

            if len(results) > 1:
                raise Exception("Got more than one object.")

            results = results[0]

            for typ in fields:
                if db_name == "thousandgenomes" and typ == "hemi":
                    continue

                query_kwargs[db_name][typ] = getattr(results, typ)

                if db_name == "thousandgenomes" and not typ == "af":
                    continue

                for population in FREQUENCY_DB_INFO[db_name]["populations"]:
                    typpop = "{}_{}".format(typ, population)
                    result[db_name][typpop] = getattr(results, typpop)

        return result
