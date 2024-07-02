from django_pydantic_field.v2.fields import PydanticSchemaField as ModelSchemaField
from django_pydantic_field.v2.rest_framework import SchemaField as SerializerSchemaField
from rest_framework import serializers


class SpectacularSchemaField(SerializerSchemaField):
    """Helper field to integrate ``django-pydantic-field`` with ``drf-spectacular``.

    Source: https://github.com/surenkov/django-pydantic-field/issues/44
    """

    def __init__(self, exclude_unset=True, *args, **kwargs):
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)
        super().__init__(
            schema=self._spectacular_annotation["field"],
            exclude_unset=exclude_unset,
            *args,
            **kwargs,
        )


class ModelSerializer(serializers.ModelSerializer):
    """Helper serializer to integrate ``django-pydantic-field`` with ``drf-spectacular``.

    Source: https://github.com/surenkov/django-pydantic-field/issues/44
    """

    def build_standard_field(self, field_name, model_field):
        standard_field = super().build_standard_field(field_name, model_field)
        if isinstance(model_field, ModelSchemaField):
            standard_field = (
                type(
                    model_field.schema.__name__ + "Serializer",
                    (SpectacularSchemaField,),
                    {"_spectacular_annotation": {"field": model_field.schema}},
                ),
            ) + standard_field[1:]
        return standard_field

    class Meta:
        abstract = True


def spectacular_preprocess_hook(endpoints):
    blocked_prefixes = (
        "/admin_alerts",
        "/variants",
        "/svs",
        "/importer",
        "/api/auth",
        "/varannos",
        "/cohorts",
        "/beaconsite",
    )
    blocked_infixes = ("/ajax/",)
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        block = False
        for prefix in blocked_prefixes:
            if path.startswith(prefix):
                block = True
                break
        for infix in blocked_infixes:
            if infix in path:
                block = True
                break
        if not block:
            filtered.append((path, path_regex, method, callback))
    return filtered
