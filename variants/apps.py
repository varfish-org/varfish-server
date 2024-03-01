from django.apps import AppConfig
from drf_spectacular.extensions import (
    OpenApiAuthenticationExtension,
    OpenApiSerializerFieldExtension,
)
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class VariantsConfig(AppConfig):
    name = "variants"


# Temporary workaround for integration of knox into drf-spectacular.
#
# Once this (already merged) PR is relased in the drf_spectacular, this
# can go away.
#
# - https://github.com/tfranzel/drf-spectacular/pull/1163


class KnoxTokenScheme(OpenApiAuthenticationExtension):
    target_class = "knox.auth.TokenAuthentication"
    name = "knoxApiToken"

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix=self.target.authenticate_header(""),
        )


# Glue code with ``django_pydantic_field.rest_framework``.


class PydanticFieldFix(OpenApiSerializerFieldExtension):
    target_class = "django_pydantic_field.rest_framework.SchemaField"

    def get_name(self):
        return self.target.field_name

    def map_serializer_field(self, auto_schema, direction):
        _, _ = auto_schema, direction
        return self.target.schema.schema_json()
