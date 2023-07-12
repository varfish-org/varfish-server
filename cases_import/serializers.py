from projectroles.serializers import SODARProjectModelSerializer
from rest_framework import serializers

from cases_import.models import CaseImportAction


class CaseImportActionSerializer(SODARProjectModelSerializer):
    """Serializer for the ``CaseImportAction`` model."""

    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = CaseImportAction
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "project",
            "date_created",
            "date_modified",
        )
