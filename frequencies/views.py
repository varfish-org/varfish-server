from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.forms.models import model_to_dict

from querybuilder.models_support import FREQUENCY_DB_INFO


class FrequencyMixin:
    def get_frequencies(self, query_kwargs):
        key = {
            "release": query_kwargs["release"],
            "chromosome": query_kwargs["chromosome"],
            "position": int(query_kwargs["position"]),
            "reference": query_kwargs["reference"],
            "alternative": query_kwargs["alternative"],
        }

        result = {key: {} for key in FREQUENCY_DB_INFO}
        for db_name in FREQUENCY_DB_INFO:
            try:
                result[db_name] = model_to_dict(FREQUENCY_DB_INFO[db_name]["model"].objects.get(**key))
            except ObjectDoesNotExist:
                result[db_name] = {}
            except MultipleObjectsReturned:
                raise MultipleObjectsReturned

        return result
