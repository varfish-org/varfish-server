from enum import Enum
from inspect import isclass
import typing

from drf_spectacular.drainage import set_override
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import ResolvedComponent
import pydantic
from pydantic.json_schema import model_json_schema


def pydantic_to_json_schema(schema_arg: typing.Any) -> typing.Dict[str, typing.Any]:
    """Convert a Python/pydantic schema to a JSON schema."""
    if schema_arg is int or schema_arg is float:
        return {
            "type": "number",
        }
    elif schema_arg is str:
        return {
            "type": "string",
        }
    elif schema_arg is type(None):
        return {
            "type": "null",
        }
    elif isclass(schema_arg) and issubclass(schema_arg, Enum):
        return {
            "type": "string",
            "title": schema_arg.__name__,
            "enum": [e.value for e in schema_arg],
        }
    elif typing.get_origin(schema_arg) is typing.Union:  # is typing.Optional[X]
        one_ofs = [pydantic_to_json_schema(arg_inner) for arg_inner in typing.get_args(schema_arg)]
        defs = {}
        for one_of in one_ofs:
            defs.update(one_of.pop("$defs", {}))
        result = {"oneOf": one_ofs, "$defs": defs}
        return result
    elif typing.get_origin(schema_arg) is list:
        inner_schema = pydantic_to_json_schema(typing.get_args(schema_arg)[0])
        defs = inner_schema.pop("$defs", {})
        return {
            "type": "array",
            "items": inner_schema,
            "$defs": defs,
        }
    elif issubclass(schema_arg, Enum):
        return {
            "type": "string",
            "title": schema_arg.__name__,
            "enum": [e.value for e in schema_arg],
        }
    elif issubclass(schema_arg, pydantic.BaseModel):
        return model_json_schema(schema_arg, ref_template="#/components/schemas/{model}")
    else:
        raise ValueError(f"Unsupported schema type: {schema_arg}")


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
        schema = pydantic_to_json_schema(self.target.schema)
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
        "/project/",
        "/timeline/",
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
