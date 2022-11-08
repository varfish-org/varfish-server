from projectroles.serializers import SODARProjectModelSerializer
from rest_framework import serializers

from variants.models import CaseComments, CaseGeneAnnotationEntry


class CaseCommentSerializer(SODARProjectModelSerializer):
    """Serializer for ``CaseComments``."""

    #: Serialize the case as its SODAR UUID.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: Serializer the user as its name.
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    def create(self, validated_data):
        """Make case and user writeable (only) on creation."""
        validated_data["user"] = self.context["request"].user
        validated_data["case"] = self.context["case"]
        return super().create(validated_data)

    class Meta:
        model = CaseComments
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
            "comment",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
        )


class CaseGeneAnnotationSerializer(SODARProjectModelSerializer):
    """Serializer for ``CaseGeneAnnotationEntry``."""

    #: Serialize the case as its SODAR UUID.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    class Meta:
        model = CaseGeneAnnotationEntry
        fields = (
            "sodar_uuid",
            "case",
            "gene_symbol",
            "entrez_id",
            "ensembl_gene_id",
            "annotation",
        )
        read_only_fields = fields
