from google.protobuf.json_format import ParseDict, ParseError
from phenopackets import Family
from projectroles.serializers import SODARProjectModelSerializer
from rest_framework import serializers

from cases_import.models import CaseImportAction
from cases_import.proto import FamilyValidator, get_case_name_from_family_payload
from variants.models.case import Case


class CaseImportActionSerializer(SODARProjectModelSerializer):
    """Serializer for the ``CaseImportAction`` model."""

    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    # Users can only create/update to states "draft" and "submitted" through the API.
    state = serializers.ChoiceField(
        choices=[CaseImportAction.STATE_DRAFT, CaseImportAction.STATE_SUBMITTED]
    )

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    def validate_payload(self, value):
        """Perform validation by constructing protobuf and then running our hand-rolled
        validation."""
        try:
            family: Family = ParseDict(js_dict=value, message=Family())
        except ParseError as e:
            raise serializers.ValidationError(
                f"payload is not a valid phenopackets.Family protocoolbuffer: {e}"
            ) from e
        warnings = FamilyValidator(family).validate()
        if warnings:
            raise serializers.ValidationError(details=list(map(str, warnings)))
        else:
            return value

    def validate(self, data):
        """Perform validation that needs more than one field."""
        case_name = get_case_name_from_family_payload(data.get("payload", {}))
        # An action=create case import with a case name collision fails.
        if data["action"] == CaseImportAction.ACTION_CREATE and Case.objects.filter(
            project=self.context["project"], name=case_name
        ):
            raise serializers.ValidationError(
                f"Cannot re-create case of name {case_name}. "
                "Try to create an import with action=update."
            )
        # An action=update case import fails if there is no case with this name.
        if data["action"] == CaseImportAction.ACTION_UPDATE and not Case.objects.filter(
            project=self.context["project"], name=case_name
        ):
            raise serializers.ValidationError(
                f"Cannot update case with non-existing name {case_name}. "
                "Try to create an import with action=create."
            )
        return data

    class Meta:
        model = CaseImportAction
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "project",
            "date_created",
            "date_modified",
        )
