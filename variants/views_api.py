"""API views for ``variants`` app."""
import typing

import attrs
import cattr
from bgjobs.models import JOB_STATE_FAILED, JOB_STATE_DONE, JOB_STATE_RUNNING, JOB_STATE_INITIAL
from django.db.models import Q
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning

# # TOOD: timeline update
from variants import query_presets
from variants.models import Case, SmallVariantQuery, FilterBgJob, SmallVariant
from variants.serializers import (
    CaseSerializer,
    SmallVariantQuerySerializer,
    SmallVariantQueryUpdateSerializer,
    SmallVariantForResultSerializer,
    SettingsShortcutsSerializer,
    SettingsShortcuts,
)


class VariantsApiBaseMixin(SODARAPIGenericProjectMixin):
    """Mixin to enforce project-based permissions."""

    permission_classes = [SODARAPIProjectPermission]


class CaseListApiView(VariantsApiBaseMixin, ListAPIView):
    """
    List all cases in the current project.

    **URL:** ``/variants/api/case/{project.sodar_uid}/``

    **Methods:** ``GET``

    **Returns:** List of project details (see :py:class:`CaseRetrieveApiView`)
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        return "variants.view_data"


class CaseRetrieveApiView(
    VariantsApiBaseMixin, RetrieveAPIView,
):
    """
    Retrieve detail of the specified case.

    **URL:** ``/variants/api/case/{project.sodar_uuid}/{case.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:**

    - ``date_created`` - creation timestamp (ISO 8601 ``str``)
    - ``date_modified`` - modification timestamp (ISO 8601 ``str``)
    - ``index`` - index sample name (``str``)
    - ``name`` - case name (``str``)
    - ``notes`` - any notes related to case (``str`` or ``null``)
    - ``num_small_vars`` - number of small variants (``int`` or ``null``)
    - ``num_svs`` - number of structural variants (``int`` or ``null``)
    - ``pedigree`` - ``list`` of ``dict`` representing pedigree entries, ``dict`` have keys

        - ``sex`` - PLINK-PED encoded biological sample sex (``int``, 0-unknown, 1-male, 2-female)
        - ``father`` - father sample name (``str``)
        - ``mother`` - mother sample name (``str``)
        - ``name`` - current sample's name (``str``)
        - ``affected`` - PLINK-PED encoded affected state (``int``, 0-unknown, 1-unaffected, 2-affected)
        - ``has_gt_entries`` - whether sample has genotype entries (``boolean``)

    - ``project`` - UUID of owning project (``str``)
    - ``release`` - genome build (``str``, one of ``["GRCh37", "GRCh37"]``)
    - ``sodar_uuid`` - case UUID (``str``)
    - ``status`` - status of case (``str``, one of ``"initial"``, ``"active"``, ``"closed-unsolved"``,
      ``"closed-uncertain"``, ``"closed-solved"``)
    - ``tags`` - ``list`` of ``str`` tags
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantQuerySerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SmallVariantQuery.objects.all()
        elif self.request.user.is_anonymous:
            return SmallVariantQuery.objects.none()
        else:
            return SmallVariantQuery.objects.filter(Q(user=self.request.user) | Q(public=True))

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryListApiView(SmallVariantQueryApiMixin, ListAPIView):
    """List small variant queries for the given Case.

    **URL:** ``/variants/api/query-case/list/{case.sodar_uuid}``

    **Methods:** ``GET``

    **Parameters:**

    - ``page`` - specify page to return (default/first is ``1``)
    - ``page_size`` -- number of elements per page (default is ``10``, maximum is ``100``)

    **Returns:**

    - ``count`` - number of total elements (``int``)
    - ``next`` - URL to next page (``str`` or ``null``)
    - ``previous`` - URL to next page (``str`` or ``null``)
    - ``results`` - ``list`` of case small variant query details (see :py:class:`SmallVariantQuery`)
    """

    def get_queryset(self):
        qs = super().get_queryset()
        case = get_object_or_404(
            Case.objects.filter(project=self.get_project()), sodar_uuid=self.kwargs["case"]
        )
        return qs.filter(case=case)


class SmallVariantQueryCreateApiView(SmallVariantQueryApiMixin, CreateAPIView):
    """Create new small variant query for the given case.

    **URL:** ``/variants/api/query-case/create/{case.sodar_uuid}``

    **Methods:** ``POST``

    **Parameters:**

    - ``form_id``: query settings form (``str``, use ``"variants.small_variant_filter_form"``)
    - ``form_version``: query settings version (``int``, only valid: ``1``)
    - ``query_settings``: the query settings (``dict``, cf. :ref:`api_json_schemas_case_query_v1`)
    - ``name``: optional string (``str``, defaults to ``None``)
    - ``public``: whether or not this query (settings) are public (``bool``, defaults to ``False``)

    **Returns:**

    JSON serialization of case small variant query details (see :py:class:`SmallVariantQuery`)
    """

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return result


class SmallVariantQueryRetrieveApiView(SmallVariantQueryApiMixin, RetrieveAPIView):
    """Retrieve small variant query details for the qiven query.

    **URL:** ``/variants/api/query-case/retrieve/{query.sodar_uuid}``

    **Methods:** ``GET``

    **Parameters:**

    None

    **Returns:**

    JSON serialization of case small variant query details (see :py:class:`SmallVariantQuery`)
    """


@attrs.define
class JobStatus:
    status: typing.Optional[str] = None


JobStatus.INITIAL = JOB_STATE_INITIAL
JobStatus.RUNNING = JOB_STATE_RUNNING
JobStatus.DONE = JOB_STATE_DONE
JobStatus.FAILED = JOB_STATE_FAILED


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)


class SmallVariantQueryStatusApiView(SmallVariantQueryApiMixin, RetrieveAPIView):
    """Returns the status of the small variant query.

    **URL:** ``/variants/api/query-case/status/{query.sodar_uuid}``

    **Methods:** ``GET``

    **Parameters:**

    None

    **Returns:**

    ``dict`` with one key ``status`` (``str``)
    """

    serializer_class = StatusSerializer

    def get_object(self):
        query = super().get_object()
        filter_job = FilterBgJob.objects.select_related("bg_job").get(smallvariantquery=query)
        return JobStatus(status=filter_job.bg_job.status)


class SmallVariantQueryUpdateApiView(SmallVariantQueryApiMixin, UpdateAPIView):
    """Update small variant query for the qiven query.

    **URL:** ``/variants/api/query-case/update/{query.sodar_uuid}``

    **Methods:** ``PUT``, ``PATCH``

    **Parameters:**

    - ``name``: new name attribute of the query
    - ``public``: whether or not to make this query public

    **Returns:**

    JSON serialization of updated case small variant query details (see :py:class:`SmallVariantQuery`)
    """

    serializer_class = SmallVariantQueryUpdateSerializer

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = self.get_object().case
        return result


class SmallVariantQueryFetchResultsApiView(SmallVariantQueryApiMixin, ListAPIView):
    """Fetch results for small variant query.

    Will return a HTTP 400 if the results are not ready yet.

    **URL:** ``/variants/api/query-case/results/{query.sodar_uuid}``

    **Methods:** ``GET``

    - ``page`` - specify page to return (default/first is ``1``)
    - ``page_size`` -- number of elements per page (default is ``10``, maximum is ``100``)

    **Returns:**

    - ``count`` - number of total elements (``int``)
    - ``next`` - URL to next page (``str`` or ``null``)
    - ``previous`` - URL to next page (``str`` or ``null``)
    - ``results`` - ``list`` of results (``dict``)
    """

    serializer_class = SmallVariantForResultSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query = None

    def get(self, *args, **kwargs):
        result = super().get(*args, **kwargs)
        query = self._get_query()
        job = FilterBgJob.objects.get(smallvariantquery=query)
        if job.bg_job.status == "done":
            return result
        else:
            if job.bg_job.status == "failed":
                reason = "query failed"
            else:
                reason = "query result not available yet"
            return Response(data={"reason": reason}, status=503)

    def _get_query(self):
        if not self._query:
            if self.request.user.is_superuser:
                qs = SmallVariantQuery.objects.all()
            elif self.request.user.is_anonymous:
                qs = SmallVariantQuery.objects.none()
            else:
                qs = SmallVariantQuery.objects.filter(Q(user=self.request.user) | Q(public=True))
            self._query = get_object_or_404(qs, sodar_uuid=self.kwargs["smallvariantquery"])
        return self._query

    def get_queryset(self):
        query = self._get_query()
        return SmallVariant.objects.filter(smallvariantquery=query, case_id=query.case_id)

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQuerySettingsShortcutApiView(
    VariantsApiBaseMixin, RetrieveAPIView,
):
    """
    Generate query settings for a given case by certain shortcuts.

    **URL:** ``/variants/api/query-case/settings-shortcut/{case.uuid}``

    **Methods:** ``GET``

    **Parameters:**

    - ``database`` - the database to query, one of ``"refseq"`` (default) and ``"ensembl"``

    - ``quick_preset`` - overall preset selection using the presets below, valid values are

         - ``defaults`` - applies presets that are recommended for starting out without a specific hypothesis
         - ``de_novo`` - applies presets that are recommended for starting out when the hypothesis is dominannt
           inheritance with *de novo* variants
         - ``dominant`` - applies presets that are recommended for starting out when the hypothesis is dominant
           inheritance (but not with *de novo* variants)
         - ``homozygous_recessive`` - applies presets that are recommended for starting out when the hypothesis is
           recessive with homzygous variants
         - ``compound_heterozygous`` - applies presets that are recommended for starting out when the hypothesis is
           recessive with compound heterozygous variants
         - ``recessive`` - applies presets that are recommended for starting out when the hypothesis is recessive mode
           of inheritance
         - ``x_recessive`` - applies presets that are recommended for starting out when the hypothesis is X recessive
           mode of inheritance
         - ``clinvar_pathogenic`` - apply presets that are recommended for screening variants for known pathogenic
           variants present Clinvar
         - ``mitochondrial`` - apply presets recommended for starting out to filter for mitochondrial mode of
           inheritance
         - ``whole_exomes`` - apply presets that return all variants of the case, regardless of frequency, quality etc.

    - ``inheritance`` - preset selection for mode of inheritance, valid values are

        - ``any`` - no particular constraint on inheritance (default)
        - ``dominant`` - allow variants compatible with dominant mode of inheritance (includes *de novo* variants)
        - ``homozygous_recessive`` - allow variants compatible with homozygous recessive mode of inheritance
        - ``compound_heterozygous`` - allow variants compatible with compound heterozygous recessive mode of
          inheritance
        - ``recessive`` - allow variants compatible with recessive mode of inheritance of a disease/trait (includes
          both homozygous and compound heterozygous recessive)
        - ``x_recessive`` - allow variants compatible with X_recessive mode of inheritance of a disease/trait
        - ``mitochondrial`` - mitochondrial inheritance (also applicable for "clinvar pathogenic")
        - ``custom`` - indicates custom settings such that none of the above inheritance settings applies

    - ``frequency`` - preset selection for frequencies, valid values are

        - ``dominant_super_strict`` - apply thresholds considered "very strict" in a dominant disease context
        - ``dominant_strict`` - apply thresholds considered "strict" in a dominant disease context (default)
        - ``dominant_relaxed`` - apply thresholds considered "relaxed" in a dominant disease context
        - ``recessive_strict`` - apply thresholds considered "strict" in a recessiv disease context
        - ``recessive_relaxed`` - apply thresholds considered "relaxed" in a recessiv disease context
        - ``custom`` - indicates custom settings such that none of the above frequency settings applies

    - ``impact`` - preset selection for molecular impact values, valid values are

        - ``null_variant`` - allow variants that are predicted to be null variants
        - ``aa_change_splicing`` - allow variants that are predicted to change the amino acid of the gene's
          protein and also splicing variants
        - ``all_coding_deep_intronic`` - allow all coding variants and also deeply intronic ones
        - ``whole_transcript`` - allow variants from the whole transcript (exonic/intronic)
        - ``any_impact`` - allow any predicted molecular impact
        - ``custom`` - indicates custom settings such that none of the above impact settings applies

    - ``quality`` - preset selection for variant call quality values, valid values are

        - ``super_strict`` - very stricdt quality settings
        - ``strict`` - strict quality settings, used as the default
        - ``relaxed`` - relaxed quality settings
        - ``any`` - ignore quality, all variants pass filter
        - ``custom`` - indicates custom settings such that none of the above quality settings applies

    - ``chromosomes`` - preset selection for selecting chromosomes/regions/genes allow/block lists, valid values are

        - ``whole_genome`` - the defaults settings selecting the whole genome
        - ``autosomes`` - select the variants lying on the autosomes only
        - ``x_chromosome`` - select variants on the X chromosome only
        - ``y_chromosome`` - select variants on the Y chromosome only
        - ``mt_chromosome`` - select variants on the mitochondrial chromosome only
        - ``custom`` - indicates custom settings such that none of the above chromosomes presets applies

    - ``flags_etc`` - preset selection for "flags etc." section, valid values are

        - ``defaults`` - the defaults also used in the user interface
        - ``clinvar_only`` - select variants present in Clinvar only
        - ``user_flagged`` - select user_flagged variants only
        - ``custom`` - indicates custom settings such that none of the above flags etc. presets apply

    **Returns:**

    - ``presets`` - a ``dict`` with the following keys; this mirrors back the quick presets and further presets
      selected in the parameters

        - ``quick_presets`` - one of the ``quick_presets`` preset values from above
        - ``inheritance`` - one of the ``inheritance`` preset values from above
        - ``frequency`` - one of the ``frequency`` preset values from above
        - ``impact`` - one of the ``impact`` preset values from above
        - ``quality`` - one of the ``quality`` preset values from above
        - ``chromosomes`` - one of the ``chromosomes`` preset values from above
        - ``flags_etc`` - one of the ``flags_etc`` preset values from above

    - ``query_settings`` - a ``dict`` with the query settings ready to be used for the given case; this will
      follow :ref:`api_json_schemas_case_query_v1`.

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = SettingsShortcutsSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_object(self, *args, **kwargs):
        quick_preset = self._get_quick_presets()
        fields_dict = attrs.fields_dict(query_presets.QuickPresets)
        changes_raw = {
            key: self.request.query_params[key]
            for key in fields_dict
            if key in self.request.query_params
        }
        if "database" in changes_raw:
            changes = {"database": changes_raw.pop("database")}
        else:
            changes = {}
        changes.update({key: fields_dict[key].type[value] for key, value in changes_raw.items()})
        quick_preset = attrs.evolve(quick_preset, **changes)
        return SettingsShortcuts(
            presets={key: getattr(quick_preset, key).value for key in fields_dict},
            query_settings=cattr.unstructure(
                quick_preset.to_settings(self._get_pedigree_members())
            ),
        )

    def _get_quick_presets(self) -> query_presets.QuickPresets:
        """"Return quick preset if given in request.query_params"""
        if "quick_preset" in self.request.query_params:
            qp_name = self.request.query_params["quick_preset"]
            if qp_name not in attrs.fields_dict(query_presets._QuickPresetList):
                raise NotFound(f"Could not find quick preset {qp_name}")
            return getattr(query_presets.QUICK_PRESETS, qp_name)
        else:
            return query_presets.QUICK_PRESETS.defaults

    def _get_pedigree_members(self) -> typing.Tuple[query_presets.PedigreeMember]:
        """Return pedigree members for the queried case."""
        case = self.get_queryset().get(sodar_uuid=self.kwargs["case"])
        return tuple(
            query_presets.PedigreeMember(
                family=None,
                name=entry["patient"],
                father=entry["father"],
                mother=entry["mother"],
                sex=query_presets.Sex(entry["sex"]),
                disease_state=query_presets.DiseaseState(entry["affected"]),
            )
            for entry in case.pedigree
        )

    def get_permission_required(self):
        return "variants.view_data"
