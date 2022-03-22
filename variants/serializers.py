"""Serializers for the variants app."""

# TODO: rename pedigree entry field "patient" also internally to name and get rid of translation below
import copy
import typing

import attrs
from bgjobs.models import BackgroundJob
from django.db import transaction
from django.db.models import Q
from projectroles.serializers import SODARProjectModelSerializer, SODARModelSerializer
from rest_framework import serializers

from geneinfo.models import HpoName, Hgnc
from .forms import FilterForm
from .models import Case, SmallVariantQuery, FilterBgJob, SmallVariant
from .query_schemas import (
    SCHEMA_QUERY_V1,
    DefaultValidatingDraft7Validator,
    convert_query_json_to_small_variant_filter_form_v1,
)
from variants.tasks import single_case_filter_task


def create_only_validator(value, serializer_field):
    """https://github.com/encode/django-rest-framework/issues/5745"""
    instance = serializer_field.parent.instance
    if instance is not None:
        initial = serializer_field.get_attribute(instance)
        if initial != value:
            raise serializers.ValidationError("Can only be set when creating")


# https://www.django-rest-framework.org/api-guide/validators/#accessing-the-context
create_only_validator.requires_context = True


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

    pedigree = serializers.models.JSONField()
    project = serializers.ReadOnlyField(source="case.project.sodar_uuid")

    def create(self, validated_data):
        """Make project and release writeable on creation."""
        validated_data["project"] = self.context["project"]
        validated_data["release"] = self.context["release"]
        return super().create(validated_data)

    class Meta:
        model = Case
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "release",
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
            "release",
        )


def query_settings_validator(value):
    """Validate query settings using JSON schema as well as gene and HPO term lookup."""

    def _check_gene_list_found(gene_list, label):
        """Helper that checks whether all ENSEMBL/Entrez gene IDs or HGNC symbols in gene_list can be found."""
        if not gene_list:
            return
        records = Hgnc.objects.filter(
            Q(ensembl_gene_id__in=gene_list) | Q(entrez_id__in=gene_list) | Q(symbol__in=gene_list)
        )
        result = []
        for record in records:
            result += [record.ensembl_gene_id, record.entrez_id, record.symbol]
        given_set = set(gene_list)
        found_set = set(result)
        not_found = given_set - found_set
        if not_found:
            raise serializers.ValidationError(f"Could not find gene(s) in {label}: {not_found}")

    # Validate query settings.
    query_settings = copy.deepcopy(value)
    DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(query_settings)
    # Validate gene lists.
    _check_gene_list_found(query_settings["gene_allowlist"], "gene_allowlist")
    _check_gene_list_found(query_settings["gene_blocklist"], "gene_blocklist")
    # Validate HPO term list.
    if "prio_hpo_terms" in query_settings:
        found = HpoName.objects.filter(hpo_id__in=query_settings["prio_hpo_terms"] or [])
        given_set = set(query_settings["prio_hpo_terms"] or [])
        found_set = {x.hpo_id for x in found}
        if given_set != found_set:
            not_found = given_set - found_set
            raise serializers.ValidationError(f"Used invalid ids: {not_found}")


class SmallVariantQuerySerializer(SODARModelSerializer):
    """Serializer for the ``SmallVariant`` model."""

    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    user = serializers.ReadOnlyField(source="user.sodar_uuid")

    query_settings = serializers.JSONField(
        validators=[create_only_validator, query_settings_validator]
    )

    def run_validation(self, *args, **kwargs):
        return super().run_validation(*args, **kwargs)

    def create(self, validated_data):
        """Make case and user writeable on creation."""
        validated_data["user"] = self.context["request"].user
        validated_data["case"] = self.context["case"]
        validated_data["form_version"] = FilterForm.form_version
        validated_data["form_id"] = FilterForm.form_id
        with transaction.atomic():
            small_variant_query = super().create(validated_data)
            self._post_create(small_variant_query)
        return small_variant_query

    def validate(self, attrs):
        # validation succeeded up to here, now convert to form data's "query_settings" if necessary.
        if "database_select" not in attrs.get("query_settings", {}) and "query_settings" in attrs:
            attrs["query_settings"] = convert_query_json_to_small_variant_filter_form_v1(
                self.context["case"], attrs["query_settings"]
            )
        return attrs

    def _post_create(self, small_variant_query):
        """Create the necessary background job (and enqueue it) after creating a SmallVariantQuery."""
        project = small_variant_query.case.project
        # Construct background job objects
        bg_job = BackgroundJob.objects.create(
            name="Running filter query for case {}".format(small_variant_query.case.name),
            project=project,
            job_type=FilterBgJob.spec_name,
            user=self.context["request"].user,
        )
        filter_job = FilterBgJob.objects.create(
            project=project,
            bg_job=bg_job,
            case=small_variant_query.case,
            smallvariantquery=small_variant_query,
        )
        # Submit job
        single_case_filter_task.delay(filter_job_pk=filter_job.pk)

    class Meta:
        model = SmallVariantQuery
        fields = (
            "sodar_uuid",
            "date_created",
            "case",
            "user",
            "form_id",
            "form_version",
            "query_settings",
            "name",
            "public",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "case",
            "user",
            "form_id",
            "form_version",
        )


class SmallVariantQueryUpdateSerializer(SmallVariantQuerySerializer):
    """Serializer that makes query_settings read-only."""

    query_settings = serializers.JSONField(read_only=True)


class SmallVariantForResultSerializer(serializers.ModelSerializer):
    """Serialization of ``SmallVariant`` for fetching results."""

    class Meta:
        model = SmallVariant
        fields = (
            "release",
            "chromosome",
            "start",
            "reference",
            "alternative",
            "var_type",
            "info",
            "genotype",
            "num_hom_alt",
            "num_hom_ref",
            "num_het",
            "num_hemi_alt",
            "num_hemi_ref",
            "in_clinvar",
            "exac_frequency",
            "exac_homozygous",
            "exac_heterozygous",
            "exac_hemizygous",
            "thousand_genomes_frequency",
            "thousand_genomes_homozygous",
            "thousand_genomes_heterozygous",
            "thousand_genomes_hemizygous",
            "gnomad_exomes_frequency",
            "gnomad_exomes_homozygous",
            "gnomad_exomes_heterozygous",
            "gnomad_exomes_hemizygous",
            "gnomad_genomes_frequency",
            "gnomad_genomes_homozygous",
            "gnomad_genomes_heterozygous",
            "gnomad_genomes_hemizygous",
            "refseq_gene_id",
            "refseq_transcript_id",
            "refseq_transcript_coding",
            "refseq_hgvs_c",
            "refseq_hgvs_p",
            "refseq_effect",
            "refseq_exon_dist",
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "ensembl_transcript_coding",
            "ensembl_hgvs_c",
            "ensembl_hgvs_p",
            "ensembl_effect",
            "ensembl_exon_dist",
        )


@attrs.define
class SettingsShortcuts:
    """Helper class that contains the results of the settings shortcuts"""

    presets: typing.Dict[str, str]
    query_settings: typing.Dict[str, typing.Any]


class SettingsShortcutsSerializer(serializers.Serializer):
    """Serializer for ``SettingsShortcut``"""

    presets = serializers.JSONField()
    query_settings = serializers.JSONField()

    class Meta:
        model = SettingsShortcuts
        fields = (
            "presets",
            "query_settings",
        )
