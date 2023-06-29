from projectroles.serializers import SODARModelSerializer, SODARProjectModelSerializer
from rest_framework import serializers

from seqmeta.models import EnrichmentKit, TargetBedFile


class EnrichmentKitSerializer(SODARProjectModelSerializer):
    """Serializer for ``EnrichmentKit``."""

    #: Serialize the case as its SODAR UUID.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def create(self, validated_data):
        """Ensure project is properly set on creation."""
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = EnrichmentKit
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "identifier",
            "title",
            "description",
        )
        read_only_fields = ("sodar_uuid", "date_created", "date_modified")


class TargetBedFileSerializer(SODARModelSerializer):
    """Serializer for ``TargetBedFile``."""

    #: Serialize the case as its SODAR UUID.
    enrichmentkit = serializers.ReadOnlyField(source="enrichmentkit.sodar_uuid")

    def create(self, validated_data):
        """Ensure enrichmentkit is properly set on creation."""
        validated_data["enrichmentkit"] = self.context["enrichmentkit"]
        return super().create(validated_data)

    class Meta:
        model = TargetBedFile
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "enrichmentkit",
            "file_uri",
            "genome_release",
        )
        read_only_fields = ("sodar_uuid", "date_created", "date_modified", "enrichmentkit")
