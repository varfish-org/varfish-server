from enum import Enum
from pydantic.json_schema import model_json_schema
from drf_spectacular.drainage import set_override, warn
import typing
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.plumbing import ResolvedComponent, build_basic_type
from drf_spectacular.types import OpenApiTypes


class DjangoPydanticFieldFix(OpenApiSerializerExtension):

    target_class = 'django_pydantic_field.v2.rest_framework.fields.SchemaField'
    match_subclasses = True

    def get_name(self, auto_schema, direction):
        # due to the fact that it is complicated to pull out every field member BaseModel class
        # of the entry model, we simply use the class name as string for object. This hack may
        # create false positive warnings, so turn it off. However, this may suppress correct
        # warnings involving the entry class.
        set_override(self.target, 'suppress_collision_warning', True)
        if typing.get_origin(self.target.schema) is list:
            inner_type = typing.get_args(self.target.schema)[0]
            return f'{inner_type.__name__}List'
        else:
            return super().get_name(auto_schema, direction)

    def map_serializer(self, auto_schema, direction):
        if getattr(self.target.schema, '__name__', None) == 'VariantTypeChoice':
            import pdb; pdb.set_trace
        if typing.get_origin(self.target.schema) is list:
            inner_type = typing.get_args(self.target.schema)[0]
            if inner_type is str:
                schema = {
                    "type": "array",
                    "items": {
                        "type": "string",
                    }
                }
            elif issubclass(inner_type, Enum):
                inner_schema = {
                    "type": "string",
                    "title": inner_type.__name__,
                    "enum": [e.value for e in inner_type]
                }
                inner_schema_defs = inner_schema.pop("$defs", {})
                schema = {
                    "type": "array",
                    "title": f"{inner_schema['title']}List",
                    "items": inner_schema
                }
                schema.update({"$defs": inner_schema_defs})
            else:
                inner_schema = model_json_schema(inner_type, ref_template="#/components/schemas/{model}")
                inner_schema_defs = inner_schema.pop("$defs", {})
                schema = {
                    "type": "array",
                    "title": f"{inner_schema['title']}List",
                    "items": inner_schema
                }
                schema.update({"$defs": inner_schema_defs})
        elif issubclass(self.target.schema, Enum):
            return {
                "type": "string",
                "title": self.target.schema.__name__,
                "enum": [e.value for e in self.target.schema]
            }
        else:
            schema = model_json_schema(self.target.schema, ref_template="#/components/schemas/{model}")

        # print("\n---SCHEMA--\n")
        # import json; print(json.dumps(schema, indent=2))
        # print("\n---SCHEMA--\n")

        # pull out potential sub-schemas and put them into component section
        for sub_name, sub_schema in schema.pop("$defs", {}).items():
            component = ResolvedComponent(
                name=sub_name,
                type=ResolvedComponent.SCHEMA,
                object=sub_name,
                schema=sub_schema,
            )
            auto_schema.registry.register_on_missing(component)

        return schema


def spectacular_preprocess_hook(endpoints):
    blocked_prefixes = (
        "/admin_alerts/",
        "/api/auth/",
        "/beaconsite/",
        "/cohorts/",
        "/importer/",
        "/project/",
        "/svs/",
        "/varannos/",
        "/variants/",
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
