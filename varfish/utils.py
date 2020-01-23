"""Shared utility code."""

from projectroles.views import ProjectAccessMixin


class ApiProjectAccessMixin(ProjectAccessMixin):
    """Project access mixing for DRF API view classes."""

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project(request=result["request"])
        return result


class ProjectAccessSerializerMixin:
    """Mixin that automatically sets the project fields of objects."""

    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)


# class SODARAPIBaseView(APIView):
#     """Base SODAR API View with accept header versioning"""
#
#     versioning_class = SODARAPIVersioning
#     renderer_classes = [SODARAPIRenderer]
