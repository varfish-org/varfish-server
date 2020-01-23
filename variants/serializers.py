"""Serializers for the variants app."""

# TODO: rename pedigree entry field "patient" also internally to name and get rid of translation below

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from projectroles.utils import build_secret
from .models import Case


class CaseSerializer(serializers.ModelSerializer):
    """Serializer for the ``Case`` model."""

    pedigree = serializers.JSONField()
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

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

    def update(self, instance, validated_data):
        validated_data["project"] = self.context["project"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    def to_representation(self, instance):
        """Convert 'patient' fields back into 'name' in pedigree."""
        # TODO: can go away after renaming
        ret = super().to_representation(instance)
        ret["pedigree"] = [
            {{"patient": "name"}.get(k, k): v for k, v in m.items()} for m in ret["pedigree"]
        ]
        return ret

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
