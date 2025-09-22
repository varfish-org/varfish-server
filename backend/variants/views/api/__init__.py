"""API views for ``variants`` app."""

from itertools import chain
import sys
import typing
import uuid

import attrs
from bgjobs.models import BackgroundJob
import cattr
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.forms import model_to_dict
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
import numpy as np
from projectroles.models import Project
from projectroles.templatetags.projectroles_common_tags import get_app_setting
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework import views
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from extra_annos.models import ExtraAnnoField
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning

# # TOOD: timeline update
from variants import query_presets
from variants.models import (
    AcmgCriteriaRating,
    Case,
    CaseAwareProject,
    ExportFileBgJob,
    FilterBgJob,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantQueryResultRow,
    SmallVariantQueryResultSet,
    SmallVariantSet,
    only_source_name,
)
from variants.query_presets import (
    CHROMOSOME_PRESETS,
    FLAGSETC_PRESETS,
    FREQUENCY_PRESETS,
    IMPACT_PRESETS,
    QUALITY_PRESETS,
    QUICK_PRESETS,
    Inheritance,
)
from variants.serializers import (
    AcmgCriteriaRatingSerializer,
    CaseListQcStatsSerializer,
    CaseSerializer,
    ExportFileBgJobSerializer,
    ExtraAnnoFieldSerializer,
    ProjectSettings,
    ProjectSettingsSerializer,
    SettingsShortcuts,
    SettingsShortcutsSerializer,
    SmallVariantCommentProjectSerializer,
    SmallVariantCommentSerializer,
    SmallVariantFlagsProjectSerializer,
    SmallVariantFlagsSerializer,
    SmallVariantQueryResultRowSerializer,
    SmallVariantQueryResultSetSerializer,
    SmallVariantQuerySerializer,
    SmallVariantQueryWithLogsSerializer,
)
from variants.tasks import export_file_task, single_case_filter_task

from .export import export_filter_settings  # noqa: F401


class CreatedAtCursorPagination(CursorPagination):
    """Common pagination settings

    We use cursor pagination to avoid inconsistencies when fetching while
    updating data.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000
    ordering = "-date_created"


class VariantsApiBaseMixin(SODARAPIGenericProjectMixin):
    """Mixin to enforce project-based permissions."""

    permission_classes = [SODARAPIProjectPermission]


class CaseApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        return "variants.view_data"


class CaseRetrieveApiView(
    CaseApiMixin,
    RetrieveAPIView,
):
    """
    Retrieve detail of the specified case.

    **URL:** ``/variants/api/case/retrieve/{case.sodar_uuid}/``

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
      ``"closed-partially-solved"``, ``"closed-uncertain"``, ``"closed-solved"``)
    - ``tags`` - ``list`` of ``str`` tags
    """


class SmallVariantQueryApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantQuerySerializer

    def get_queryset(self):
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


class SmallVariantPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 100


class SmallVariantQueryListCreateApiView(ListCreateAPIView):
    """API endpoint for listing and creating SmallVariant queries for a given case.

    After creation, a background job will be started to execute the query.

    **URL:** ``/variants/api/query/list-create/{case.sodar_uuid}/``

    **Methods:** ``GET``, ``POST``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SODARAPIProjectPermission]

    serializer_class = SmallVariantQuerySerializer

    def perform_create(self, serializer):
        """Override to execute the new query in the background."""
        super().perform_create(serializer)
        query = serializer.instance

        with transaction.atomic():
            # Construct background job objects
            filter_job = FilterBgJob.objects.create(
                bg_job=BackgroundJob.objects.create(
                    name="Running filter query for case {}".format(query.case.name),
                    project=query.case.project,
                    job_type=FilterBgJob.spec_name,
                    user=self.request.user,
                ),
                project=query.case.project,
                case=query.case,
                smallvariantquery=query,
            )

        single_case_filter_task.delay(filter_job_pk=filter_job.pk)  # MUST be after transaction

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return result

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SmallVariantQuery.objects.all()
        elif self.request.user.is_anonymous:
            return SmallVariantQuery.objects.none()
        else:
            return SmallVariantQuery.objects.filter(
                Q(user=self.request.user) | Q(public=True), case__sodar_uuid=self.kwargs.get("case")
            ).select_related("user", "case")

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryRetrieveUpdateDestroyApiViewPermission(SODARAPIProjectPermission):
    """Project-based permission for ``SmallVariantQueryRetrieveUpdateDestroyApiView``."""

    def get_project(self, request=None, kwargs=None):
        if "smallvariantquery" in kwargs:
            smallvariantquery = SmallVariantQuery.objects.get(
                sodar_uuid=kwargs["smallvariantquery"]
            )
            return smallvariantquery.case.project
        elif "smallvariantqueryresultset" in kwargs:
            smallvariantqueryresultset = SmallVariantQueryResultSet.objects.get(
                sodar_uuid=kwargs["smallvariantqueryresultset"]
            )
            if smallvariantqueryresultset.case:
                return smallvariantqueryresultset.case.project
            return smallvariantqueryresultset.smallvariantquery.case.project
        else:
            raise RuntimeError("Must never happen")


class SmallVariantQueryRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting SmallVariant queries for a given case.

    **URL:** ``/variants/api/query/retrieve-update-destroy/{smallvariantquery.sodar_uuid}/``

    **Methods:** ``GET``, ``PATCH``, ``PUT``, ``DELETE``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SODARAPIProjectPermission]

    serializer_class = SmallVariantQueryWithLogsSerializer

    def get_queryset(self):
        return SmallVariantQuery.objects.all().select_related("user", "case")

    def get_permission_required(self):
        # TODO: only allow update/deletion of own query
        if self.request.method == "GET":
            return "variants.view_data"
        elif self.request.method == "DELETE":
            return "variants.delete_data"
        else:
            return "variants.update_data"


class SmallVariantQueryResultSetListApiView(ListAPIView):
    """API endpoint for listing query result sets for a query.

    **URL:** ``/variants/api/query-result-set/list/{smallvariantquery.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    pagination_class = PageNumberPagination
    permission_classes = [SODARAPIProjectPermission]

    serializer_class = SmallVariantQueryResultSetSerializer

    def get_queryset(self):
        return SmallVariantQueryResultSet.objects.filter(
            smallvariantquery__sodar_uuid=self.kwargs.get("smallvariantquery")
        ).select_related("smallvariantquery")

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryResultSetRetrieveApiView(RetrieveAPIView):
    """API endpoint for retrieving query result sets.

    **URL:** ``/variants/api/query-result-set/retrieve/{smallvariantquery.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantqueryresultset"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SODARAPIProjectPermission]

    serializer_class = SmallVariantQueryResultSetSerializer

    def get_queryset(self):
        return SmallVariantQueryResultSet.objects.all().select_related("smallvariantquery")

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryResultRowPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 1000
    page_size_query_param = "page_size"


class SmallVariantQueryResultRowListApiView(ListAPIView):
    """API endpoint for listing query result rows.

    **URL:** ``/variants/api/query-result-row/list/{smallvariantqueryresultset.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantqueryresultset"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    pagination_class = SmallVariantQueryResultRowPagination
    permission_classes = [SODARAPIProjectPermission]

    serializer_class = SmallVariantQueryResultRowSerializer

    def get_queryset(self):
        ea_field_to_idx = {
            f"extra_anno{field.field}": idx
            for idx, field in enumerate(ExtraAnnoField.objects.all().order_by("field"))
        }
        order_by_str = self.request.query_params.get("order_by", "chromosome_no,start")
        order_dir = self.request.query_params.get("order_dir", "asc")

        if order_by_str.endswith(
            ("_score", "_frequency", "_carriers", "_hom_alt", "_pLI", "_mis_z", "_syn_z", "_loeuf")
        ):
            order_by_raw = RawSQL("COALESCE((payload->>%s)::float, 0)", (order_by_str,))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        elif order_by_str.endswith(
            (
                "_homozygous",
                "_count",
            )
        ):
            order_by_raw = RawSQL("COALESCE((payload->>%s)::integer, 0)", (order_by_str,))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        elif order_by_str == "symbol":
            order_by_raw = RawSQL("COALESCE((payload->>%s)::text, NULL)", (order_by_str,))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        elif order_by_str == "acmg_symbol,disease_gene":
            order_by_split = order_by_str.split(",")
            order_by = [
                RawSQL("COALESCE((payload->>%s)::text, NULL) IS NOT NULL", (order_by_split[0],)),
                RawSQL("COALESCE((payload->>%s)::boolean, FALSE)", (order_by_split[1],)),
            ]
            if order_dir == "desc":
                order_by = [value.desc() for value in order_by]
        elif order_by_str.startswith("genotype_"):
            name = order_by_str[len("genotype_") :]
            order_by_raw = RawSQL("COALESCE((payload->'genotype'->%s->>'gt')::text, NULL)", (name,))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        elif order_by_str in ea_field_to_idx:
            idx = ea_field_to_idx[order_by_str]
            order_by_raw = RawSQL("COALESCE((payload->'extra_annos'->0->>%s)::float, NULL)", (idx,))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        else:
            order_by = order_by_str.split(",")
            if order_dir == "desc":
                order_by = [f"-{value}" for value in order_by]

        qs = SmallVariantQueryResultRow.objects.filter(
            smallvariantqueryresultset__sodar_uuid=self.kwargs.get("smallvariantqueryresultset")
        ).select_related("smallvariantqueryresultset")
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryResultRowViewPermission(SODARAPIProjectPermission):
    def get_project(self, request=None, kwargs=None):
        result_set = SmallVariantQueryResultRow.objects.get(
            sodar_uuid=kwargs["smallvariantqueryresultrow"]
        ).smallvariantqueryresultset
        if result_set.case:
            return result_set.case.project
        return result_set.smallvariantquery.case.project


class SmallVariantQueryResultRowRetrieveApiView(RetrieveAPIView):
    """API endpoint for retrieving one result row.

    **URL:** ``/variants/api/query-result-row/retrieve/{smallvariantqueryresultrow.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantqueryresultrow"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SmallVariantQueryResultRowViewPermission]

    serializer_class = SmallVariantQueryResultRowSerializer

    def get_queryset(self):
        return SmallVariantQueryResultRow.objects.all()

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQuerySettingsShortcutApiView(
    CaseApiMixin,
    RetrieveAPIView,
):
    """
    Generate query settings for a given case by certain shortcuts.

    **URL:** ``/variants/api/query-case/query-settings-shortcut/{case.uuid}``

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

        - ``any`` - do not apply any thresholds
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

    - ``flagsetc`` - preset selection for "flags etc." section, valid values are

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
        - ``flagsetc`` - one of the ``flagsetc`` preset values from above

    - ``query_settings`` - a ``dict`` with the query settings ready to be used for the given case; this will
      follow :ref:`api_json_schemas_case_query_v1`.

    """

    serializer_class = SettingsShortcutsSerializer

    def get_object(self, *args, **kwargs):
        def value_to_enum(enum, value):
            for enum_val in enum:
                if enum_val.value == value:
                    return enum_val
            else:
                return None

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
        changes.update(
            {key: value_to_enum(fields_dict[key].type, value) for key, value in changes_raw.items()}
        )
        quick_preset = attrs.evolve(quick_preset, **changes)
        presets = {}
        for key in fields_dict:
            if key == "label":
                presets[key] = getattr(quick_preset, key)
            else:
                presets[key] = getattr(quick_preset, key).value
        return SettingsShortcuts(
            presets=presets,
            query_settings=cattr.unstructure(
                quick_preset.to_settings(self._get_pedigree_members())
            ),
        )

    def _get_quick_presets(self) -> query_presets.QuickPresets:
        """Return quick preset if given in request.query_params"""
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


class SmallVariantQuickPresetsApiView(
    views.APIView,
):
    """
    Resolve quick preset name to category preset.

    **URL:** ``/variants/api/query-case/quick-presets``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        return Response(cattr.unstructure(QUICK_PRESETS))


class SmallVariantCategoryPresetsApiView(
    views.APIView,
):
    """
    List all presets for the given category.

    **URL:** ``/variants/api/query-case/category-presets/{category}``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        presets = {
            "frequency": FREQUENCY_PRESETS,
            "impact": IMPACT_PRESETS,
            "quality": QUALITY_PRESETS,
            "chromosomes": CHROMOSOME_PRESETS,
            "flagsetc": FLAGSETC_PRESETS,
        }
        return Response(cattr.unstructure(presets.get(self.kwargs.get("category"))))


class SmallVariantInheritancePresetsApiView(
    views.APIView,
):
    """
    List all inheritance presets for the given case.

    **URL:** ``/variants/api/query-case/inheritance-presets/{case.sodar_uuid}``

    **Methods:** ``GET``

    **Returns:** A dict mapping each of the category names to category preset values.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        pedigree_members = self._get_pedigree_members()
        return Response(
            {
                inheritance.value: inheritance.to_settings(pedigree_members)
                for inheritance in Inheritance
                if inheritance.value != "custom"
            }
        )

    def _get_pedigree_members(self) -> typing.Tuple[query_presets.PedigreeMember]:
        """Return pedigree members for the queried case."""
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
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


class SmallVariantQueryDownloadGenerateApiView(VariantsApiBaseMixin, APIView):
    """Start generating results for download of a small variant query.

    **URL:** ``/variants/api/query-case/download/generate/tsv/{query.sodar_uuid}``

    **URL:** ``/variants/api/query-case/download/generate/xlsx/{query.sodar_uuid}``

    **URL:** ``/variants/api/query-case/download/generate/vcf/{query.sodar_uuid}``

    **Methods:** ``GET``

    **Returns:**

    """

    def get_permission_required(self):
        return "variants.view_data"

    def get(self, request, *args, **kwargs):
        project = self.get_project()
        query = SmallVariantQuery.objects.get(sodar_uuid=self.kwargs["smallvariantquery"])

        if self.request.get_full_path() == reverse(
            "variants:ajax-query-case-download-generate-tsv",
            kwargs={"smallvariantquery": query.sodar_uuid},
        ) or self.request.get_full_path() == reverse(
            "variants:api-query-case-download-generate-tsv",
            kwargs={"smallvariantquery": query.sodar_uuid},
        ):
            file_type = "tsv"
        elif self.request.get_full_path() == reverse(
            "variants:ajax-query-case-download-generate-vcf",
            kwargs={"smallvariantquery": query.sodar_uuid},
        ) or self.request.get_full_path() == reverse(
            "variants:api-query-case-download-generate-vcf",
            kwargs={"smallvariantquery": query.sodar_uuid},
        ):
            file_type = "vcf"
        else:
            file_type = "xlsx"

        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {}".format(file_type, query.case.name),
                project=project,
                job_type=ExportFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=project,
                bg_job=bg_job,
                case=query.case,
                query_args=query.query_settings,
                file_type=file_type,
            )

        export_file_task.delay(export_job_pk=export_job.pk)
        return JsonResponse({"export_job__sodar_uuid": export_job.sodar_uuid}, status=200)


class SmallVariantQueryDownloadStatusApiView(VariantsApiBaseMixin, RetrieveAPIView):
    """Get status of generating results for download of a small variant query.

    **URL:** ``/variants/api/query-case/download/status/{job.sodar_uuid}``

    **Methods:** ``GET``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "exportfilebgjob"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = ExportFileBgJobSerializer

    queryset = ExportFileBgJob.objects.all()

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryDownloadServeApiView(VariantsApiBaseMixin, APIView):
    """Serve download results of a small variant query.

    **URL:** ``/variants/api/query-case/download/serve/{exportfilebgjob.sodar_uuid}``

    **Methods:** ``GET``

    **Returns:**

    """

    def get_permission_required(self):
        return "variants.view_data"

    def get(self, request, *args, **kwargs):
        try:
            content_types = {
                "tsv": "text/tab-separated-values",
                "vcf": "text/plain+gzip",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            extensions = {"tsv": ".tsv", "vcf": ".vcf.gz", "xlsx": ".xlsx"}
            job = ExportFileBgJob.objects.get(sodar_uuid=self.kwargs["exportfilebgjob"])
            response = HttpResponse(
                job.export_result.payload, content_type=content_types[job.file_type]
            )
            response["Content-Disposition"] = 'attachment; filename="%(name)s%(ext)s"' % {
                "name": "varfish_%s_%s"
                % (timezone.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), job.case.sodar_uuid),
                "ext": extensions[job.file_type],
            }
            return response

        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e


class SmallVariantCommentApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantCommentSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        query_set = SmallVariantComment.objects.select_related("user", "case").filter(
            case__sodar_uuid=self.kwargs["case"]
        )

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})
        return query_set

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantCommentListCreateApiView(
    SmallVariantCommentApiMixin,
    ListCreateAPIView,
):
    """A view that allows to list existing comments and new ones.

    **URL:** ``/variants/api/small-variant-comment/list-create/{case.sodar_uuid}/``

    **Query Arguments:**

    - release
    - chromosome
    - start
    - end
    - reference
    - alternative

    **Methods:** ``GET``, ``POST``

    **Returns:**

    """

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result

    def perform_create(self, serializer):
        if not self.request.data.get("sodar_uuid"):
            raise ValidationError(
                detail={
                    "error": "`sodar_uuid` of SmallVariantQueryResultRow required. Aborting flag creation."
                }
            )

        super().perform_create(serializer)
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        result_row = SmallVariantQueryResultRow.objects.get(
            sodar_uuid=self.request.data.get("sodar_uuid")
        )
        result_set = case.smallvariantqueryresultset_set.filter(smallvariantquery=None).first()
        try:
            result_set.smallvariantqueryresultrow_set.get(
                release=serializer.instance.release,
                chromosome=serializer.instance.chromosome,
                start=serializer.instance.start,
                end=serializer.instance.end,
                reference=serializer.instance.reference,
                alternative=serializer.instance.alternative,
            )
        except SmallVariantQueryResultRow.DoesNotExist:
            result_row.pk = None
            result_row.sodar_uuid = uuid.uuid4()
            result_row.smallvariantqueryresultset = result_set
            result_row.save()
            result_row.smallvariantqueryresultset.result_row_count += 1
            result_row.smallvariantqueryresultset.save()


class SmallVariantCommentProjectApiMixin(SmallVariantCommentApiMixin):
    lookup_url_kwarg = "project"
    serializer_class = SmallVariantCommentProjectSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        query_set = SmallVariantComment.objects.select_related("user", "case__project").filter(
            case__project__sodar_uuid=self.kwargs["project"]
        )

        case_uuid = self.request.GET.get("exclude_case_uuid")

        if case_uuid:
            query_set = query_set.exclude(case__sodar_uuid=case_uuid)

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})

        return query_set.order_by("date_created")


class SmallVariantCommentListProjectApiView(
    SmallVariantCommentProjectApiMixin,
    ListAPIView,
):
    """A view that allows to list existing comments for a project and variant.

    **URL:** ``/variants/api/small-variant-comment/list-project/{project.sodar_uuid}/``

    **Query Arguments:**

    - release
    - chromosome
    - start
    - end
    - reference
    - alternative
    - exclude_case_uuid

    **Methods:** ``GET``

    **Returns:**

    """


class SmallVariantFlagsApiMixin(VariantsApiBaseMixin):
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantFlagsSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        query_set = SmallVariantFlags.objects.select_related("case").filter(
            case__sodar_uuid=self.kwargs["case"]
        )
        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})
        return query_set

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantFlagsListCreateApiView(
    SmallVariantFlagsApiMixin,
    ListCreateAPIView,
):
    """A view that allows to list existing flags and create new ones.

    **URL:** ``/variants/api/small-variant-flags/list-create/{case.sodar_uuid}/``

    **Query Arguments:**

    - release
    - chromosome
    - start
    - end
    - reference
    - alternative

    **Methods:** ``GET``, ``POST``

    **Returns:**

    """

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result

    def perform_create(self, serializer):
        if not self.request.data.get("sodar_uuid"):
            raise ValidationError(
                detail={
                    "error": "`sodar_uuid` of SmallVariantQueryResultRow required. Aborting flag creation."
                }
            )

        super().perform_create(serializer)
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        result_row = SmallVariantQueryResultRow.objects.get(
            sodar_uuid=self.request.data.get("sodar_uuid")
        )
        result_set = case.smallvariantqueryresultset_set.filter(smallvariantquery=None).first()
        try:
            result_set.smallvariantqueryresultrow_set.get(
                release=serializer.instance.release,
                chromosome=serializer.instance.chromosome,
                start=serializer.instance.start,
                end=serializer.instance.end,
                reference=serializer.instance.reference,
                alternative=serializer.instance.alternative,
            )
        except SmallVariantQueryResultRow.DoesNotExist:
            result_row.pk = None
            result_row.sodar_uuid = uuid.uuid4()
            result_row.smallvariantqueryresultset = result_set
            result_row.save()
            result_row.smallvariantqueryresultset.result_row_count += 1
            result_row.smallvariantqueryresultset.save()


class SmallVariantFlagsProjectApiMixin(SmallVariantFlagsApiMixin):
    lookup_url_kwarg = "project"
    serializer_class = SmallVariantFlagsProjectSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        query_set = SmallVariantFlags.objects.select_related("case__project").filter(
            case__project__sodar_uuid=self.kwargs["project"]
        )

        case_uuid = self.request.GET.get("exclude_case_uuid")

        if case_uuid:
            query_set = query_set.exclude(case__sodar_uuid=case_uuid)

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})

        return query_set.order_by("date_created")


class SmallVariantFlagsListProjectApiView(
    SmallVariantFlagsProjectApiMixin,
    ListAPIView,
):
    """A view that allows to list existing comments for a project and variant.

    **URL:** ``/variants/api/small-variant-flags/list-project/{project.sodar_uuid}/``

    **Query Arguments:**

    - release
    - chromosome
    - start
    - end
    - reference
    - alternative
    - exclude_case_uuid

    **Methods:** ``GET``

    **Returns:**

    """


class SmallVariantFlagsApiMixin(VariantsApiBaseMixin):
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantFlagsSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        query_set = SmallVariantFlags.objects.select_related("case").filter(
            case__sodar_uuid=self.kwargs["case"]
        )
        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})
        return query_set

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantFlagsUpdateApiView(
    UpdateAPIView,
):
    """A view that allows to update flags.

    **URL:** ``/variants/api/small-variant-flags/update/{smallvariantflags.sodar_uuid}/``

    **Methods:** ``PUT``, ``PATCH``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantflags"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantFlagsSerializer

    queryset = SmallVariantFlags.objects.all()

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantFlagsDeleteApiView(
    DestroyAPIView,
):
    """A view that allows to delete flags.

    **URL:** ``/variants/api/small-variant-flags/delete/{smallvariantflags.sodar_uuid}/``

    **Methods:** ``DELETE``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantflags"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantFlagsSerializer

    queryset = SmallVariantFlags.objects.all()

    def get_permission_required(self):
        return "variants.view_data"

    def perform_destroy(self, instance):
        result_set = instance.case.smallvariantqueryresultset_set.filter(
            smallvariantquery=None
        ).first()
        if result_set:
            result_row_set = result_set.smallvariantqueryresultrow_set.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            comments = SmallVariantComment.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            acmg_ratings = AcmgCriteriaRating.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            if result_row_set.exists() and not comments.exists() and not acmg_ratings.exists():
                result_row_set.first().delete()
                result_set.result_row_count -= 1
                result_set.save()
        super().perform_destroy(instance)


class SmallVariantCommentUpdateApiView(
    UpdateAPIView,
):
    """A view that allows to update comments.

    **URL:** ``/variants/api/small-variant-comment/update/{smallvariantcomment.sodar_uuid}/``

    **Methods:** ``PUT``, ``PATCH``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantcomment"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantCommentSerializer

    queryset = SmallVariantComment.objects.all()

    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantCommentDeleteApiView(
    DestroyAPIView,
):
    """A view that allows to delete comments.

    **URL:** ``/variants/api/small-variant-comment/delete/{smallvariantcomment.sodar_uuid}/``

    **Methods:** ``DELETE``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantcomment"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantCommentSerializer

    queryset = SmallVariantComment.objects.all()

    def get_permission_required(self):
        return "variants.view_data"

    def perform_destroy(self, instance):
        result_set = instance.case.smallvariantqueryresultset_set.filter(
            smallvariantquery=None
        ).first()
        if result_set:
            result_row_set = result_set.smallvariantqueryresultrow_set.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            flags = SmallVariantFlags.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            acmg_ratings = AcmgCriteriaRating.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            if result_row_set.exists() and not flags.exists() and not acmg_ratings.exists():
                result_row_set.first().delete()
                result_set.result_row_count -= 1
                result_set.save()
        super().perform_destroy(instance)


class AcmgCriteriaRatingApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    pagination_class = CreatedAtCursorPagination
    serializer_class = AcmgCriteriaRatingSerializer

    def get_queryset(self):
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        query_set = AcmgCriteriaRating.objects.select_related("case").filter(
            case__sodar_uuid=self.kwargs["case"]
        )

        for key in keys:
            if key not in self.request.GET:
                break
        else:
            query_set = query_set.filter(**{key: self.request.GET[key] for key in keys})
        return query_set

    def get_permission_required(self):
        return "variants.view_data"


class AcmgCriteriaRatingListCreateApiView(
    AcmgCriteriaRatingApiMixin,
    ListCreateAPIView,
):
    """A view that allows to create new ACMG ratings.

    **URL:** ``/variants/api/acmg-criteria-rating/list-create/{case.sodar_uuid}/``

    **Query Arguments:**

    - release
    - chromosome
    - start
    - end
    - reference
    - alternative

    **Methods:** ``POST``

    **Returns:**

    """

    serializer_class = AcmgCriteriaRatingSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by("release", "chromosome", "start", "end", "reference", "alternative")
        )

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result

    def perform_create(self, serializer):
        if not self.request.data.get("sodar_uuid"):
            raise ValidationError(
                detail={
                    "error": "`sodar_uuid` of SmallVariantQueryResultRow required. Aborting flag creation."
                }
            )

        super().perform_create(serializer)
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        result_row = SmallVariantQueryResultRow.objects.get(
            sodar_uuid=self.request.data.get("sodar_uuid")
        )
        result_set = case.smallvariantqueryresultset_set.filter(smallvariantquery=None).first()
        try:
            result_set.smallvariantqueryresultrow_set.get(
                release=serializer.instance.release,
                chromosome=serializer.instance.chromosome,
                start=serializer.instance.start,
                end=serializer.instance.end,
                reference=serializer.instance.reference,
                alternative=serializer.instance.alternative,
            )
        except SmallVariantQueryResultRow.DoesNotExist:
            result_row.pk = None
            result_row.sodar_uuid = uuid.uuid4()
            result_row.smallvariantqueryresultset = result_set
            result_row.save()
            result_row.smallvariantqueryresultset.result_row_count += 1
            result_row.smallvariantqueryresultset.save()


class AcmgCriteriaRatingUpdateApiView(
    UpdateAPIView,
):
    """A view that allows to create new ACMG ratings.

    **URL:** ``/variants/api/acmg-criteria-rating/update/{acmgcriteriarating.sodar_uuid}/``

    **Methods:** ``PUT``, ``PATCH``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "acmgcriteriarating"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = AcmgCriteriaRatingSerializer

    queryset = AcmgCriteriaRating.objects.all()

    def get_permission_required(self):
        return "variants.view_data"


class AcmgCriteriaRatingDeleteApiView(
    DestroyAPIView,
):
    """A view that allows to delete ACMG ratings.

    **URL:** ``/variants/api/acmg-criteria-rating/delete/{acmgcriteriarating.sodar_uuid}/``

    **Methods:** ``DELETE``

    **Returns:**

    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "acmgcriteriarating"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = AcmgCriteriaRatingSerializer

    queryset = AcmgCriteriaRating.objects.all()

    def get_permission_required(self):
        return "variants.view_data"

    def perform_destroy(self, instance):
        result_set = instance.case.smallvariantqueryresultset_set.filter(
            smallvariantquery=None
        ).first()
        if result_set:
            result_row_set = result_set.smallvariantqueryresultrow_set.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            flags = SmallVariantFlags.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            comments = SmallVariantComment.objects.filter(
                release=instance.release,
                chromosome=instance.chromosome,
                start=instance.start,
                end=instance.end,
                reference=instance.reference,
                alternative=instance.alternative,
            )
            if result_row_set.exists() and not flags.exists() and not comments.exists():
                result_row_set.first().delete()
                result_set.result_row_count -= 1
                result_set.save()
        super().perform_destroy(instance)


class ExtraAnnoFieldsApiView(
    ListAPIView,
):
    """A view that returns all extra annotation field names.

    **URL:** ``/variants/api/extra-anno-fields/``

    **Methods:** ``GET``

    **Returns:** List of extra annotation field names.

    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = ExtraAnnoFieldSerializer

    queryset = ExtraAnnoField.objects.all()

    def get_permission_required(self):
        return "variants.view_data"


def build_rel_data(pedigree, relatedness):
    """Return statistics"""
    rel_parent_child = set()

    for line in pedigree:
        if line["mother"] != "0":
            rel_parent_child.add((line["patient"], line["mother"]))
            rel_parent_child.add((line["mother"], line["patient"]))

        if line["father"] != "0":
            rel_parent_child.add((line["patient"], line["father"]))
            rel_parent_child.add((line["father"], line["patient"]))

    rel_siblings = set()

    for line1 in pedigree:
        for line2 in pedigree:
            if (
                line1["patient"] != line2["patient"]
                and line1["mother"] != "0"
                and line2["mother"] != "0"
                and line1["father"] != "0"
                and line2["father"] != "0"
                and line1["father"] == line2["father"]
                and line1["mother"] == line2["mother"]
            ):
                rel_siblings.add((line1["patient"], line2["patient"]))

    for rel in relatedness:
        yield {
            "sample0": only_source_name(rel.sample1),
            "sample1": only_source_name(rel.sample2),
            "parentChild": (rel.sample1, rel.sample2) in rel_parent_child,
            "sibSib": (rel.sample1, rel.sample2) in rel_siblings,
            "ibs0": rel.n_ibs0,
            "rel": rel.relatedness(),
        }


def build_sex_data(case_or_project):
    return {
        "sexErrors": {only_source_name(k): v for k, v in case_or_project.sex_errors().items()},
        "chrXHetHomRatio": {
            only_source_name(line["patient"]): case_or_project.chrx_het_hom_ratio(line["patient"])
            for line in case_or_project.get_filtered_pedigree_with_samples()
        },
    }


def build_cov_data(cases):
    dp_medians = []
    het_ratios = []
    dps = {}
    dp_het_data = []

    for case in cases:
        try:
            variant_set = case.latest_variant_set

            if variant_set:
                for stats in variant_set.variant_stats.sample_variant_stats.all():
                    dp_medians.append(stats.ontarget_dp_quantiles[2])
                    het_ratios.append(stats.het_ratio)
                    dps[stats.sample_name] = {
                        int(key): value for key, value in stats.ontarget_dps.items()
                    }
                    dp_het_data.append(
                        {
                            "x": stats.ontarget_dp_quantiles[2],
                            "y": stats.het_ratio or 0.0,
                            "sample": only_source_name(stats.sample_name),
                        }
                    )

        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow

    # Catch against empty lists, numpy will complain otherwise.
    if not dp_medians:
        dp_medians = [0]

    if not het_ratios:
        het_ratios = [0]

    result = {
        "dps": dps,
        "dpQuantiles": list(np.percentile(np.asarray(dp_medians), [0, 25, 50, 100])),
        "hetRatioQuantiles": list(np.percentile(np.asarray(het_ratios), [0, 25, 50, 100])),
        "dpHetData": dp_het_data,
    }

    return result


class CaseListQcStatsApiView(RetrieveAPIView):
    """Render JSON with project-wide case statistics"""

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = CaseListQcStatsSerializer

    def get_object(self):
        cases = Case.objects.filter(project__sodar_uuid=self.kwargs["project"]).prefetch_related(
            "smallvariantset_set__variant_stats",
            "smallvariantset_set__variant_stats__sample_variant_stats",
            "project",
        )
        project = CaseAwareProject.objects.prefetch_related("variant_stats").get(
            sodar_uuid=self.kwargs["project"]
        )

        try:
            rel_data = list(
                build_rel_data(
                    list(chain(*[case.pedigree for case in cases])),
                    project.variant_stats.relatedness.all(),
                )
            )
        except Project.variant_stats.RelatedObjectDoesNotExist:
            rel_data = []

        result = {
            "pedigree": [
                {**line, "patient": only_source_name(line["patient"])}
                for case in cases
                for line in case.pedigree
            ],
            "relData": rel_data,
            **build_sex_data(project),
            **build_cov_data(
                list(
                    project.case_set.prefetch_related(
                        "smallvariantset_set__variant_stats__sample_variant_stats"
                    ).all()
                )
            ),
            "varStats": [model_to_dict(s) for s in project.sample_variant_stats()],
        }

        return result


class ProjectSettingsRetrieveApiView(SODARAPIGenericProjectMixin, RetrieveAPIView):
    """A view that returns project settings for the given project.

    **URL:** ``/variants/api/project-settings/retrieve/{project.uuid}``

    **Methods:** ``GET``

    **Returns:** {
        ts_tv_warning_upper,
        ts_tv_warning_lower
    }
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = ProjectSettingsSerializer

    def get_permission_required(self):
        return "variants.view_data"

    def get_object(self):
        project = CaseAwareProject.objects.get(sodar_uuid=self.kwargs["project"])
        setting = get_app_setting("variants", "ts_tv_valid_range", project=project)
        try:
            lower, upper = setting.split("-")
            lower, upper = float(lower), float(upper)
        except ValueError:
            lower, upper = 2.0, 2.9
        return ProjectSettings(
            ts_tv_valid_lower=lower,
            ts_tv_valid_upper=upper,
        )
