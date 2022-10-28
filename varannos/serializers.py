from projectroles.serializers import SODARModelSerializer, SODARProjectModelSerializer
from rest_framework import serializers

from varannos.models import VarAnnoSet, VarAnnoSetEntry


class VarAnnoSetSerializer(SODARProjectModelSerializer):
    """Serializer for ``VarAnnoSet``."""

    #: Serialize the case as its SODAR UUID.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def create(self, validated_data):
        """Ensure project is properly set on creation."""
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = VarAnnoSet
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "project",
            "release",
            "title",
            "description",
            "fields",
        )
        read_only_fields = ("sodar_uuid", "date_created", "date_modified", "project")


class VarAnnoSetEntrySerializer(SODARModelSerializer):
    """Serializer for ``VarAnnoSetEntry``."""

    #: Serialize the case as its SODAR UUID.
    varannoset = serializers.ReadOnlyField(source="varannoset.sodar_uuid")

    def create(self, validated_data):
        """Ensure varannoset is properly set on creation."""
        validated_data["varannoset"] = self.context["varannoset"]
        return super().create(validated_data)

    class Meta:
        model = VarAnnoSetEntry
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "varannoset",
            "release",
            "chromosome",
            "reference",
            "alternative",
            "start",
            "end",
            "payload",
        )
        read_only_fields = ("sodar_uuid", "date_created", "date_modified", "varannoset")
