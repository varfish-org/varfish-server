from enum import Enum
import typing

from drf_spectacular.drainage import set_override
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import ResolvedComponent
from pydantic.json_schema import model_json_schema


class DjangoPydanticFieldFix(OpenApiSerializerFieldExtension):

    target_class = "django_pydantic_field.v2.rest_framework.fields.SchemaField"
    match_subclasses = True

    def get_name(self):
        # due to the fact that it is complicated to pull out every field member BaseModel class
        # of the entry model, we simply use the class name as string for object. This hack may
        # create false positive warnings, so turn it off. However, this may suppress correct
        # warnings involving the entry class.
        set_override(self.target, "suppress_collision_warning", True)
        if typing.get_origin(self.target.schema) is list:
            inner_type = typing.get_args(self.target.schema)[0]
            return f"{inner_type.__name__}List"
        else:
            return super().get_name()

    def map_serializer_field(self, auto_schema, direction):
        _ = direction
        print(
            self.target.schema,
            typing.get_origin(self.target.schema),
            typing.get_args(self.target.schema),
        )
        if typing.get_origin(self.target.schema) is list:
            inner_type = typing.get_args(self.target.schema)[0]
            if inner_type is str:
                schema = {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                }
            elif issubclass(inner_type, Enum):
                inner_schema = {
                    "type": "string",
                    "title": inner_type.__name__,
                    "enum": [e.value for e in inner_type],
                }
                inner_schema_defs = inner_schema.pop("$defs", {})
                schema = {
                    "type": "array",
                    "title": f"{inner_schema['title']}List",
                    "items": inner_schema,
                }
                schema.update({"$defs": inner_schema_defs})
            else:
                inner_schema = model_json_schema(
                    inner_type, ref_template="#/components/schemas/{model}"
                )
                inner_schema_defs = inner_schema.pop("$defs", {})
                schema = {
                    "type": "array",
                    "title": f"{inner_schema['title']}List",
                    "items": inner_schema,
                }
                schema.update({"$defs": inner_schema_defs})
        elif (  # typing.Optional
            typing.get_origin(self.target.schema) is typing.Union
            and len(typing.get_args(self.target.schema)) == 2
            and typing.get_args(self.target.schema)[1] is type(None)
        ):
            pass
        elif issubclass(self.target.schema, Enum):
            return {
                "type": "string",
                "title": self.target.schema.__name__,
                "enum": [e.value for e in self.target.schema],
            }
        else:
            schema = model_json_schema(
                self.target.schema, ref_template="#/components/schemas/{model}"
            )

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
        "/svs/",
        "/varannos/",
        "/variants/",
    )
    blocked_infixes = ("/ajax/",)
    filtered = []
    for path, path_regex, method, callback in endpoints:
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
