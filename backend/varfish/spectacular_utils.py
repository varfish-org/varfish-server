# import typing
# from drf_spectacular.contrib.pydantic import PydanticExtension
# from drf_spectacular.plumbing import build_object_type

# class DjangoPydanticFieldFix(PydanticExtension):
#     target_class = 'django_pydantic_field.v2.rest_framework.fields.SchemaField'

#     def get_name(self, auto_schema, direction):
#         if typing.get_origin(self.target.schema) is list:
#             inner_type = typing.get_args(self.target.schema)[0]
#             return f'{inner_type.__name__}List'
#         else:
#             return super().get_name(auto_schema, direction)

#     def map_serializer_field(self, auto_schema, direction):
#         import pdb; pdb.set_trace()
#         return super().map_serializer_field(auto_schema, direction)

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
