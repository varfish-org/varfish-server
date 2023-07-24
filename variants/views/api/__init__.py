"""API views for ``variants`` app."""
import contextlib
from itertools import chain
import re
import typing

import attrs
from bgjobs.models import BackgroundJob
import cattr
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
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
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework import views
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from clinvar.models import Clinvar
from extra_annos.models import ExtraAnnoField
from extra_annos.views import ExtraAnnosMixin
from frequencies.models import MT_DB_INFO
from frequencies.views import FrequencyMixin
from geneinfo.models import Hpo, HpoName
from geneinfo.serializers import Gene
from geneinfo.views import get_gene_infos
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning

# # TOOD: timeline update
from variants import query_presets
from variants.helpers import get_engine
from variants.models import (
    AcmgCriteriaRating,
    Case,
    CaseAwareProject,
    ExportFileBgJob,
    FilterBgJob,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantQueryResultRow,
    SmallVariantQueryResultSet,
    SmallVariantSet,
    SmallVariantSummary,
    load_molecular_impact,
    only_source_name,
)
from variants.queries import KnownGeneAAQuery
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
    HpoTerms,
    HpoTermSerializer,
    SettingsShortcuts,
    SettingsShortcutsSerializer,
    SmallVariantCommentSerializer,
    SmallVariantDetails,
    SmallVariantDetailsSerializer,
    SmallVariantFlagsSerializer,
    SmallVariantQueryHpoTermSerializer,
    SmallVariantQueryResultRowSerializer,
    SmallVariantQueryResultSetSerializer,
    SmallVariantQuerySerializer,
    SmallVariantQueryWithLogsSerializer,
)
from variants.tasks import export_file_task, single_case_filter_task


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
      ``"closed-uncertain"``, ``"closed-solved"``)
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
        smallvariantqueryresultrow = SmallVariantQueryResultRow.objects.get(
            sodar_uuid=kwargs["smallvariantqueryresultrow"]
        )
        return smallvariantqueryresultrow.smallvariantqueryresultset.smallvariantquery.case.project


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


class SmallVariantQueryHpoTermsApiView(SmallVariantQueryApiMixin, RetrieveAPIView):
    """Fetch HPO terms for small variant query.

    **URL:** ``/variants/api/query-case/hpo-terms/{query.sodar_uuid}``

    **Methods:** ``GET``

    **Returns:**

    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantQueryHpoTermSerializer

    def _get_query(self):
        if self.request.user.is_superuser:
            qs = SmallVariantQuery.objects.all()
        elif self.request.user.is_anonymous:
            qs = SmallVariantQuery.objects.none()
        else:
            qs = SmallVariantQuery.objects.filter(Q(user=self.request.user) | Q(public=True))
        return get_object_or_404(qs, sodar_uuid=self.kwargs["smallvariantquery"])

    def get_object(self):
        query = self._get_query()
        # Get mapping from HPO term to HpoName object.
        hpoterms = {}
        for hpo in query.query_settings.get("prio_hpo_terms", []) or []:
            if hpo.startswith("HP"):
                matches = HpoName.objects.filter(hpo_id=hpo)
                hpoterms[hpo] = matches.first().name if matches else "unknown HPO term"
            else:
                matches = (
                    Hpo.objects.filter(database_id=hpo)
                    .values("database_id")
                    .annotate(names=ArrayAgg("name"))
                )
                if matches:
                    hpoterms[hpo] = re.sub(r"^[#%]?\d+ ", "", matches.first()["names"][0]).split(
                        ";;"
                    )[0]
                else:
                    hpoterms[hpo] = "unknown term"

        return HpoTerms(hpoterms=hpoterms)


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
        ):
            file_type = "tsv"
        elif self.request.get_full_path() == reverse(
            "variants:ajax-query-case-download-generate-vcf",
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


class SmallVariantDetailsApiView(CaseApiMixin, FrequencyMixin, ExtraAnnosMixin, RetrieveAPIView):
    """Fetch details for a small variant.

    **URL:** ``/variants/api/small-variant-details/{case.sodar_uuid}/{case.release}-{small_var.chromosome}-{small_var.start}-{small_var.end}-{small_var.reference}-{small_var.alternative}/{query.database}/{small_var.gene_id}/

    **Methods:** ``GET``

    **Returns:**

    """

    serializer_class = SmallVariantDetailsSerializer

    def _load_knowngene_aa(self):
        """Load the UCSC knownGeneAA conservation alignment information."""
        query = KnownGeneAAQuery(get_engine())
        result = []
        with contextlib.closing(query.run(self.kwargs)) as _result:
            for entry in _result:
                result.append(
                    {
                        "chromosome": entry.chromosome,
                        "start": entry.start,
                        "end": entry.end,
                        "alignment": entry.alignment,
                    }
                )
        return result

    def _load_clinvar(self):
        """Load clinvar information"""
        filter_args = {
            "release": self.kwargs["release"],
            "chromosome": self.kwargs["chromosome"],
            "start": int(self.kwargs["start"]),
            "end": int(self.kwargs["end"]),
            "reference": self.kwargs["reference"],
            "alternative": self.kwargs["alternative"],
        }
        records = Clinvar.objects.filter(**filter_args)
        if records:
            return records
        return None

    def _get_population_freqs(self):
        if self.kwargs.get("chromosome") == "MT":
            return {}
        result = {
            "populations": ("AFR", "AMR", "ASJ", "EAS", "FIN", "NFE", "OTH", "SAS", "Total"),
            "pop_freqs": {},
        }
        db_infos = {
            "gnomadexomes": "gnomAD Exomes",
            "gnomadgenomes": "gnomAD Genomes",
            "exac": "ExAC",
            "thousandgenomes": "1000GP",
        }
        frequencies = self.get_frequencies(self.kwargs)
        for key, label in db_infos.items():
            pop_freqs = {}
            for pop in result["populations"]:
                pop_freqs.setdefault(pop, {})["hom"] = getattr(
                    frequencies[key],
                    "hom%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                    0,
                )
                pop_freqs.setdefault(pop, {})["het"] = getattr(
                    frequencies[key],
                    "het%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                    0,
                )
                pop_freqs.setdefault(pop, {})["hemi"] = getattr(
                    frequencies[key],
                    "hemi%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                    0,
                )
                pop_freqs.setdefault(pop, {})["af"] = getattr(
                    frequencies[key],
                    "af%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                    0.0,
                )
                if key.startswith("gnomad"):
                    pop_freqs.setdefault(pop, {})["controls_het"] = getattr(
                        frequencies[key],
                        "controls_het%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                        0,
                    )
                    pop_freqs.setdefault(pop, {})["controls_hom"] = getattr(
                        frequencies[key],
                        "controls_hom%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                        0,
                    )
                    pop_freqs.setdefault(pop, {})["controls_hemi"] = getattr(
                        frequencies[key],
                        "controls_hemi%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                        0,
                    )
                    pop_freqs.setdefault(pop, {})["controls_af"] = getattr(
                        frequencies[key],
                        "controls_af%s" % ("_%s" % pop.lower() if not pop == "Total" else ""),
                        0.0,
                    )
            result["pop_freqs"][label] = pop_freqs
        inhouse = SmallVariantSummary.objects.filter(
            release=self.kwargs["release"],
            chromosome=self.kwargs["chromosome"],
            start=int(self.kwargs["start"]),
            end=int(self.kwargs["end"]),
            reference=self.kwargs["reference"],
            alternative=self.kwargs["alternative"],
        )
        result["inhouse_freq"] = {}
        if inhouse and not settings.KIOSK_MODE:
            hom = getattr(inhouse[0], "count_hom_alt", 0)
            het = getattr(inhouse[0], "count_het", 0)
            hemi = getattr(inhouse[0], "count_hemi_alt", 0)
            result["inhouse_freq"] = {
                "hom": hom,
                "het": het,
                "hemi": hemi,
                "carriers": hom + het + hemi,
            }
        return result

    def _get_mitochondrial_freqs(self):
        if not self.kwargs.get("chromosome") == "MT":
            return {}
        result = {
            "vars": {db: dict() for db in MT_DB_INFO},
            "an": {db: 0 for db in MT_DB_INFO},
            "is_triallelic": False,
            "dloop": False,
        }
        for dbname, db in MT_DB_INFO.items():
            singles = {
                "A": {"ac": 0, "af": 0.0, "ac_het": 0, "ac_hom": 0},
                "C": {"ac": 0, "af": 0.0, "ac_het": 0, "ac_hom": 0},
                "G": {"ac": 0, "af": 0.0, "ac_het": 0, "ac_hom": 0},
                "T": {"ac": 0, "af": 0.0, "ac_het": 0, "ac_hom": 0},
            }
            an = 0
            multis = (
                {self.kwargs.get("reference"): {"ac": 0, "af": 0.0, "ac_het": 0, "ac_hom": 0}}
                if len(self.kwargs.get("reference")) > 1
                else {}
            )
            alts = db.objects.filter(
                release=self.kwargs["release"],
                chromosome=self.kwargs["chromosome"],
                start=int(self.kwargs["start"]),
                end=int(self.kwargs["end"]),
                reference=self.kwargs["reference"],
            )
            if alts:
                an = alts[0].an
                ref_count = an
                for alt in alts:
                    if dbname == "HelixMTdb" and self.kwargs["alternative"] == alt.alternative:
                        result["is_triallelic"] = alt.is_triallelic
                    if dbname == "mtDB" and self.kwargs["alternative"] == alt.alternative:
                        result["dloop"] = alt.location == "D-loop"
                    assert an == alt.an
                    ref_count -= (alt.ac_hom + alt.ac_het) if dbname == "HelixMTdb" else alt.ac
                    if len(alt.alternative) == 1:
                        if dbname == "HelixMTdb":
                            singles[alt.alternative]["ac_hom"] = alt.ac_hom
                            singles[alt.alternative]["ac_het"] = alt.ac_het
                        else:
                            singles[alt.alternative]["ac"] = alt.ac
                        singles[alt.alternative]["af"] = alt.af
                    else:
                        if dbname == "HelixMTdb":
                            multis[alt.alternative] = {
                                "af": alt.af,
                                "ac_het": alt.ac_het,
                                "ac_hom": alt.ac_hom,
                            }
                        else:
                            multis[alt.alternative] = {
                                "ac": alt.ac,
                                "af": alt.af,
                            }
                        # Add allele to other databases if it does not exist there yet
                        for other_db in set(MT_DB_INFO).difference({dbname}):
                            result["vars"][other_db].setdefault(
                                alt.alternative, {"ac": 0, "af": 0.0, "ac_hom": 0, "ac_het": 0}
                            )
                assert singles[self.kwargs.get("reference")]["ac"] == 0
                assert singles[self.kwargs.get("reference")]["ac_het"] == 0
                assert singles[self.kwargs.get("reference")]["ac_hom"] == 0
                assert singles[self.kwargs.get("reference")]["af"] == 0.0
                if len(self.kwargs.get("reference")) == 1:
                    if dbname == "HelixMTdb":
                        singles[self.kwargs.get("reference")]["ac_hom"] = ref_count
                        singles[self.kwargs.get("reference")]["ac_het"] = 0
                    else:
                        singles[self.kwargs.get("reference")]["ac"] = ref_count
                    singles[self.kwargs.get("reference")]["af"] = ref_count / an
                else:
                    if dbname == "HelixMTdb":
                        multis[self.kwargs.get("reference")]["ac_hom"] = ref_count
                        multis[self.kwargs.get("reference")]["ac_het"] = 0
                    else:
                        multis[self.kwargs.get("reference")]["ac"] = ref_count
                    multis[self.kwargs.get("reference")]["af"] = ref_count / an
            result["vars"][dbname].update(singles)
            result["vars"][dbname].update(multis)
            result["an"][dbname] = an
        # Make sure indels are sorted
        for dbname, data in result["vars"].items():
            result["vars"][dbname] = sorted(
                data.items(), key=lambda x: (("0" if len(x[0]) == 1 else "1") + x[0], x[1])
            )
        return result

    def _load_acmg_rating(self):
        return AcmgCriteriaRating.objects.filter(
            case=super().get_object(),
            release=self.kwargs["release"],
            chromosome=self.kwargs["chromosome"],
            start=int(self.kwargs["start"]),
            end=int(self.kwargs["end"]),
            reference=self.kwargs["reference"],
            alternative=self.kwargs["alternative"],
        ).first()

    def get_object(self):
        case = super().get_object()
        small_var = SmallVariant.objects.filter(
            case_id=case.pk,
            release=self.kwargs["release"],
            chromosome=self.kwargs["chromosome"],
            start=self.kwargs["start"],
            end=self.kwargs["end"],
            reference=self.kwargs["reference"],
            alternative=self.kwargs["alternative"],
        ).first()
        frequencies = self._get_population_freqs()
        return SmallVariantDetails(
            clinvar=self._load_clinvar(),
            knowngeneaa=self._load_knowngene_aa(),
            effect_details=load_molecular_impact(self.kwargs),
            extra_annos=self.get_extra_annos_api(self.kwargs),
            populations=frequencies.get("populations"),
            pop_freqs=frequencies.get("pop_freqs"),
            inhouse_freq=frequencies.get("inhouse_freq"),
            mitochondrial_freqs=self._get_mitochondrial_freqs(),
            gene=Gene(
                **get_gene_infos(
                    self.kwargs["database"], self.kwargs["gene_id"], small_var.ensembl_transcript_id
                )
            ),
            acmg_rating=self._load_acmg_rating(),
        )


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

    serializer_class = SmallVariantCommentSerializer

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result


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
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result


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


class AcmgCriteriaRatingApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

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

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        keys = ("release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            if key in self.request.query_params:
                result[key] = self.request.query_params[key]
        return result


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


class HpoTermsApiView(ListAPIView):
    """A view that lists HPO terms based on a query string.
    Also includes OMIM, ORPHAN and DECIPHER terms.

    **URL:** ``/variants/api/hpo-terms/?query={string}/``

    **Methods:** ``GET``

    **Returns:** List of HPO terms that were found for that term, HPO id and name.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = HpoTermSerializer

    def get_queryset(self):
        query = self.request.GET.get("query")

        if not query:
            return []

        hpo = HpoName.objects.filter(Q(hpo_id__icontains=query) | Q(name__icontains=query))[:10]
        omim_decipher_orpha = (
            Hpo.objects.filter(Q(database_id__icontains=query) | Q(name__icontains=query))
            .values("database_id")
            .distinct()[:10]
        )
        result = []

        for h in hpo:
            result.append({"id": h.hpo_id, "name": h.name})

        for o in omim_decipher_orpha:
            names = []

            # Query database again to get all possible names for an OMIM/DECIPHER/ORPHA id
            for name in (
                Hpo.objects.filter(database_id=o["database_id"])
                .values("database_id")
                .annotate(names=ArrayAgg("name"))[0]["names"]
            ):
                if o["database_id"].startswith("OMIM"):
                    for n in re.sub(r"^[#%]?\d{6} ", "", name).split(";;"):
                        if n not in names:
                            names.append(n)

                else:
                    if name not in names:
                        names.append(name)
            result.append({"id": o["database_id"], "name": ";;".join(names)})

        return result


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
