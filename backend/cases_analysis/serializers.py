from rest_framework import serializers

from cases_analysis.models import CaseAnalysis, CaseAnalysisSession


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer for models with sodar_uuid and creation/update time."""

    class Meta:
        fields = [
            "sodar_uuid",
            "date_created",
            "date_modified",
        ]


class CaseAnalysisSerializer(BaseSerializer):
    """Serializer for ``CaseAnalysis``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    class Meta:
        model = CaseAnalysis
        fields = BaseSerializer.Meta.fields + ["case"]
        read_only_fields = fields


class CaseAnalysisSessionSerializer(BaseSerializer):
    """Serializer for ``CaseAnalysisSession``."""

    #: Serialize ``caseanalysis`` as its ``sodar_uuid``.
    caseanalysis = serializers.ReadOnlyField(source="caseanalysis.sodar_uuid")
    #: Serialize ``case`` as its ``sodar_uuid`` (via ``caseanalysis``)
    case = serializers.ReadOnlyField(source="caseanalysis.case.sodar_uuid")
    #: Serialize ``user`` as its ``sodar_uuid``.
    user = serializers.ReadOnlyField(source="user.sodar_uuid")

    class Meta:
        model = CaseAnalysisSession
        fields = BaseSerializer.Meta.fields + ["caseanalysis", "case", "user"]
        read_only_fields = fields
