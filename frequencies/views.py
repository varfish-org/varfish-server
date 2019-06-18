from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from .models import FREQUENCY_DB_INFO


class FrequencyMixin:
    """Mixin for returing variant frequencies from all frequency databases."""

    def get_frequencies(self, query_kwargs):
        """Given a variant, return the corresponding variant frequencies."""
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
                result[db_name] = FREQUENCY_DB_INFO[db_name]["model"].objects.get(**key)
            except ObjectDoesNotExist:
                result[db_name] = None
            except MultipleObjectsReturned:
                raise MultipleObjectsReturned

        return result
