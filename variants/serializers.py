"""Serializers for the variants app."""

# TODO: rename pedigree entry field "patient" also internally to name and get rid of translation below
from django.db.models import Q
from projectroles.serializers import SODARProjectModelSerializer
from rest_framework import serializers

from .models import Case


class CoreCaseSerializerMixin:
    """Validation functions for core case fields."""

    def to_representation(self, instance):
        """Convert 'patient' fields back into 'name' in pedigree."""
        # TODO: can go away after renaming
        ret = super().to_representation(instance)
        ret["pedigree"] = [
            {{"patient": "name"}.get(k, k): v for k, v in m.items()} for m in ret["pedigree"]
        ]
        return ret

    def validate(self, value):
        """Validate the whole object."""
        # This is called after the calls to ``self.validate_*()``.
        if "index" in value:
            for entry in value.get("pedigree", getattr(self.instance, "pedigree", ())):
                if entry["patient"] == value["index"]:
                    break
            else:  # no break above
                raise serializers.ValidationError(
                    "Index name %s not found in pedigree members." % repr(value["index"])
                )

        # The unique-together validation must be done here as only here, project has been set.
        if "name" in value:
            qs = self.Meta.model.objects.filter(project=self.context["project"], name=value["name"])
            if self.instance:
                qs = qs.filter(~Q(sodar_uuid=self.instance.sodar_uuid))
            if qs.exists():
                raise serializers.ValidationError(
                    "Case name %s must be unique in project." % repr(value["name"])
                )

        return value

    def validate_tags(self, value):
        """Validate tags field."""
        # TODO: compare to project's allowed tags from settings
        return value or []

    def validate_pedigree(self, pedigree):
        """Validate pedigree JSON field.

        Also, rename "name" in JSON field to "patient" for internal usage.
        """
        if not isinstance(pedigree, list):
            raise serializers.ValidationError("pedigree must be a list")
        names = [e.get("patient", e["name"]) for e in pedigree]
        for i, entry in enumerate(pedigree):
            if not isinstance(entry, dict):
                raise serializers.ValidationError(
                    "pedigree entries must be objects but no. %d is not" % (i + 1)
                )
            all_keys = {"name", "father", "mother", "sex", "affected", "has_gt_entries"}
            if entry.keys() != all_keys:
                left = entry.keys() - all_keys
                right = all_keys - entry.keys()
                raise serializers.ValidationError(
                    "pedigree entry no. %d keys mismatch, incorrect: %s, missing: %s"
                    % (i + 1, list(sorted(left)), list(sorted(right)))
                )
            for key in ("father", "mother"):
                if entry[key] != "0" and entry[key] not in names:
                    raise serializers.ValidationError(
                        "%s of pedigree entry no. %d points to invalid name: %s"
                        % (key, i + 1, repr(entry[key]))
                    )
            if entry["sex"] not in (0, 1, 2):
                raise serializers.ValidationError(
                    "pedigree entry no. %d has wrong sex value %s" % (i + 1, entry["sex"])
                )
            if entry["affected"] not in (0, 1, 2):
                raise serializers.ValidationError(
                    "pedigree entry no. %d has wrong sex value %s" % (i + 1, entry["affected"])
                )
            if not isinstance(entry["has_gt_entries"], bool):
                raise serializers.ValidationError(
                    "pedigree entry no. %d has wrong has_gt_entries value %s"
                    % (i + 1, entry["has_gt_entries"])
                )
        # TODO: can go away after renaming
        return [{{"name": "patient"}.get(k, k): v for k, v in m.items()} for m in pedigree]


class CaseSerializer(CoreCaseSerializerMixin, SODARProjectModelSerializer):
    """Serializer for the ``Case`` model."""

    pedigree = serializers.JSONField()
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = Case
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "name",
            "index",
            "pedigree",
            "num_small_vars",
            "num_svs",
            "project",
            "notes",
            "status",
            "tags",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "num_small_vars",
            "num_svs",
            "project",
        )
