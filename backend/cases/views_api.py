import sys

from bgjobs.models import BackgroundJob
from django.conf import settings
from django.db import transaction
from django.middleware.csrf import get_token
from modelcluster.queryset import FakeQuerySet
from projectroles.app_settings import AppSettingAPI
from projectroles.views_api import (
    SODARAPIBaseMixin,
    SODARAPIBaseProjectMixin,
    SODARAPIProjectPermission,
)
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission

from cases.models import ExtraAnnoFieldInfo, GlobalSettings, UserAndGlobalSettings, UserSettings
from cases.serializers import (
    CaseAlignmentStatsSerializer,
    CaseCommentSerializer,
    CaseGeneAnnotationSerializer,
    CaseSerializerNg,
    PedigreeRelatednessSerializer,
    SampleVariantStatisticsSerializer,
    UserAndGlobalSettingsSerializer,
)
from extra_annos.models import ExtraAnnoField
from svs.models import SvAnnotationReleaseInfo
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import (
    AnnotationReleaseInfo,
    Case,
    CaseAlignmentStats,
    CaseComments,
    CaseGeneAnnotationEntry,
    CasePhenotypeTerms,
    ComputeProjectVariantsStatsBgJob,
    DeleteCaseBgJob,
    PedigreeRelatedness,
    SampleVariantStatistics,
)
from variants.serializers import (
    AnnotationReleaseInfoSerializer,
    CasePhenotypeTermsSerializer,
    SvAnnotationReleaseInfoSerializer,
)
from variants.tasks import delete_case_bg_job


class CasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class CaseListApiView(SODARAPIBaseProjectMixin, ListAPIView):
    """
    List all cases in the current project.

    **URL:** ``/cases/api/case/list/{project.sodar_uid}/``

    **Methods:** ``GET``

    **Returns:** List of project details (see :py:class:`CaseRetrieveApiView`)
    """

    permission_classes = [SODARAPIProjectPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseSerializerNg

    pagination_class = CasePagination

    def get_queryset(self):
        # Use ``select_related()`` so we do not have to explicitely fetch projects and preset sets for serializing as
        # projects.sodar_uuid and presetset.sodar_uuid.
        qs = Case.objects.filter(project__sodar_uuid=self.kwargs["project"])
        if self.request.GET.get("q"):
            qs = qs.filter(name__icontains=self.request.GET.get("q"))
        order_by_str = self.request.query_params.get("order_by", "")
        if order_by_str:
            order_dir = self.request.query_params.get("order_dir", "asc")
            order_by = order_by_str.split(",")
            if order_dir == "desc":
                qs = qs.order_by(*[f"-{value}" for value in order_by])
            else:
                qs = qs.order_by(*order_by)
        qs = qs.select_related("project", "presetset")
        return qs

    def get_permission_required(self):
        return "cases.view_data"


class CasesApiPermission(SODARAPIProjectPermission):
    """Project-based permission for the ``cases`` app."""

    def get_project(self, request=None, kwargs=None):
        case = Case.objects.get(sodar_uuid=kwargs["case"])
        return case.project


class CaseApiBaseMixin(SODARAPIBaseMixin):
    """Mixin to enforce project-based permissions."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasesApiPermission]

    def get_permission_required(self):
        return "cases.view_data"


class CaseRetrieveUpdateDestroyApiView(CaseApiBaseMixin, RetrieveUpdateDestroyAPIView):
    """
    Update a given case.

    **URL:** ``/cases/api/case/update/{case.sodar_uid}/``

    **Methods:** ``PATCH``, ``PUT``, ``DELETE``.

    **Returns:** Updated case details.
    """

    serializer_class = CaseSerializerNg

    def get_queryset(self):
        return Case.objects.all()

    def get_permission_required(self):
        if self.request.method == "GET":
            return "cases.view_data"
        elif self.request.method == "DELETE":
            return "cases.delete_case"
        else:
            return "cases.update_case"

    def perform_destroy(self, instance):
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Delete case",
                project=instance.project,
                job_type=DeleteCaseBgJob.spec_name,
                user=self.request.user,
            )
            delete_job = DeleteCaseBgJob.objects.create(
                project=instance.project,
                bg_job=bg_job,
                case=instance,
            )
            # Construct background job objects
            bg_job2 = BackgroundJob.objects.create(
                name="Recreate variant statistic for whole project",
                project=instance.project,
                job_type=ComputeProjectVariantsStatsBgJob.spec_name,
                user=self.request.user,
            )
            recreate_job = ComputeProjectVariantsStatsBgJob.objects.create(
                project=instance.project, bg_job=bg_job2
            )
            delete_case_bg_job.delay(
                delete_case_bg_job_pk=delete_job.pk, export_job_pk=recreate_job.pk
            )


class AnnotationReleaseInfoApiView(CaseApiBaseMixin, ListAPIView):
    """List annotation release infos for a given case.

    **URL:** ``/cases/api/annotation-release-info/list/{case.sodar_uuid}``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasesApiPermission]

    serializer_class = AnnotationReleaseInfoSerializer

    def get_queryset(self):
        return AnnotationReleaseInfo.objects.filter(case__sodar_uuid=self.kwargs["case"])

    def get_permission_required(self):
        return "cases.view_data"


class SvAnnotationReleaseInfoApiView(CaseApiBaseMixin, ListAPIView):
    """List SVannotation release infos for a given case.

    **URL:** ``/cases/api/sv-annotation-release-info/list/{case.sodar_uuid}``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasesApiPermission]

    serializer_class = SvAnnotationReleaseInfoSerializer

    def get_queryset(self):
        return SvAnnotationReleaseInfo.objects.filter(case__sodar_uuid=self.kwargs["case"])

    def get_permission_required(self):
        return "cases.view_data"


class CasePhenotypeTermsListCreateApiView(CaseApiBaseMixin, ListCreateAPIView):
    """List/create case phenotype term annotations.

    **URL:** ``/cases/api/case-phenotype-terms/list-create/{case.sodar_uuid}``

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

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasesApiPermission]

    serializer_class = CasePhenotypeTermsSerializer

    def get_queryset(self):
        return CasePhenotypeTerms.objects.filter(case__sodar_uuid=self.kwargs["case"])

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = get_object_or_404(Case.objects.all(), sodar_uuid=self.kwargs["case"])
        return result

    def get_permission_required(self):
        if self.request.method == "POST":
            return "cases.update_case"
        else:
            return "cases.view_data"


class CasePhenotypeTermsApiPermission(SODARAPIProjectPermission):
    """Project-based permission for the ``cases`` app."""

    def get_project(self, request=None, kwargs=None):
        casephenotypeterms = CasePhenotypeTerms.objects.get(sodar_uuid=kwargs["casephenotypeterms"])
        return casephenotypeterms.case.project


class CasePhenotypeTermsRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, destroy case comments for the given case.

    **URL:** ``/cases/api/case-phenotype-terms/retrieve-update-destroy/{case_phenotype_terms.sodar_uuid}``

    **Methods:** ``GET``, ``PATCH``, ``PUT``, ``DELETE``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "casephenotypeterms"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasePhenotypeTermsApiPermission]

    queryset = CasePhenotypeTerms.objects.all()
    serializer_class = CasePhenotypeTermsSerializer

    def get_permission_required(self):
        if self.request.method == "GET":
            return "cases.view_data"
        elif self.request.method == "DELETE":
            return "cases.update_case"  # sic! (is case update only)
        else:
            return "cases.update_case"


class CaseCommentListCreateApiView(CaseApiBaseMixin, ListCreateAPIView):
    """List/create case comments for the given case.

    **URL:** ``/cases/api/case-comment/list-create/{case.sodar_uuid}``

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

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasesApiPermission]

    serializer_class = CaseCommentSerializer

    def get_queryset(self):
        return CaseComments.objects.filter(case__sodar_uuid=self.kwargs["case"])

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["case"] = get_object_or_404(Case.objects.all(), sodar_uuid=self.kwargs["case"])
        return result

    def get_permission_required(self):
        if self.request.method == "POST":
            return "cases.casecomment_create"
        else:
            return "cases.view_data"


class CaseCommentsApiPermission(BasePermission):
    """Fine-granular permissions for ``CaseComments``."""

    def has_permission(self, request, view):
        if not request.user:
            return False  # no user, forbidden
        elif request.user.is_superuser:
            return True  # is superuser, allowed
        # Otherwise, check rules.
        if hasattr(view, "permission_required"):
            perm = view.permission_required
        else:
            perm = view.get_permission_required()
        casecomment = view.get_object()
        return request.user.has_perm(perm, casecomment)


class CaseCommentRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, destroy case comments for the given case.

    **URL:** ``/cases/api/case-comment/retrieve-update-destroy/{case_comment.sodar_uuid}``

    **Methods:** ``GET``, ``PATCH``, ``PUT``, ``DELETE``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "casecomment"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CaseCommentsApiPermission]

    queryset = CaseComments.objects.all()
    serializer_class = CaseCommentSerializer

    def get_permission_required(self):
        if self.request.method == "GET":
            return "cases.casecomment_view"
        elif self.request.method == "DELETE":
            return "cases.casecomment_delete"
        else:
            return "cases.casecomment_update"


class CaseGeneAnnotationApiMixin(CaseApiBaseMixin):
    serializer_class = CaseGeneAnnotationSerializer

    def get_queryset(self):
        return CaseGeneAnnotationEntry.objects.filter(case__sodar_uuid=self.kwargs["case"])


class CaseGeneAnnotationListApiView(CaseGeneAnnotationApiMixin, ListAPIView):
    """List case gene annotations for the given case.

    **URL:** ``/cases/api/case-gene-annotation/list/{case.sodar_uuid}``

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


class CaseAlignmentStatsApiMixin(CaseApiBaseMixin):
    serializer_class = CaseAlignmentStatsSerializer

    def get_queryset(self):
        return CaseAlignmentStats.objects.filter(case__sodar_uuid=self.kwargs["case"])


class CaseAlignmentStatsListApiView(CaseAlignmentStatsApiMixin, ListAPIView):
    """Retrieve alignment statistics for the given case.

    **URL:** ``/cases/api/case-alignment-stats/list/{case.sodar_uuid}/``

    **Methods:** GET

    **Returns:** List of alignment statistics information.
    """


class SampleVariantStatisticsApiMixin(CaseApiBaseMixin):
    serializer_class = SampleVariantStatisticsSerializer

    def get_queryset(self):
        return SampleVariantStatistics.objects.filter(
            stats__variant_set__case__sodar_uuid=self.kwargs["case"]
        )


class SampleVariantStatisticsListApiView(SampleVariantStatisticsApiMixin, ListAPIView):
    """Retrieve case variant statistics for the given case.

    **URL:** ``/cases/api/case-variant-stats/list/{case.sodar_uuid}/``

    **Methods:** GET

    **Returns:** List of variant statistics information.
    """


class PedigreeRelatednessApiMixin(CaseApiBaseMixin):
    serializer_class = PedigreeRelatednessSerializer

    def get_queryset(self):
        return PedigreeRelatedness.objects.filter(
            stats__variant_set__case__sodar_uuid=self.kwargs["case"]
        )


class PedigreeRelatednessListApiView(PedigreeRelatednessApiMixin, ListAPIView):
    """Retrieve relatedness information from the given case.

    **URL:** ``/cases/api/case-relatedness/list/{case.sodar_uuid}/``

    **Methods:** GET

    **Returns:** List of variant
    """


class UserAndGlobalSettingsView(RetrieveAPIView):
    """Retrieve user and global settings.

    Also, send the CSRF token as a response token.
    """

    serializer_class = UserAndGlobalSettingsSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        """Return fake query set to support spectacular schema generation."""
        return FakeQuerySet(model=UserAndGlobalSettings, results=[])

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        get_token(request)
        return result

    def get_object(self) -> UserAndGlobalSettings:
        setting_api = AppSettingAPI()

        return UserAndGlobalSettings(
            user_settings=UserSettings(
                umd_predictor_api_token=setting_api.get(
                    "variants", "umd_predictor_api_token", user=self.request.user
                ),
                ga4gh_beacon_network_widget_enabled=setting_api.get(
                    "variants", "ga4gh_beacon_network_widget_enabled", user=self.request.user
                ),
            ),
            global_settings=GlobalSettings(
                exomiser_enabled=settings.VARFISH_ENABLE_EXOMISER_PRIORITISER,
                cadd_enabled=settings.VARFISH_ENABLE_CADD,
                extra_anno_fields=self._get_extra_anno_fields(),
            ),
        )

    def _get_extra_anno_fields(self):
        return [
            ExtraAnnoFieldInfo(
                field=entry.field,
                label=entry.label,
            )
            for entry in ExtraAnnoField.objects.all()
        ]
