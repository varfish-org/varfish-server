import sys

from django.db import transaction
from django_pydantic_field.rest_framework import AutoSchema
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import CursorPagination

from cases_analysis.models import CaseAnalysis, CaseAnalysisSession
from cases_analysis.serializers import CaseAnalysisSerializer, CaseAnalysisSessionSerializer
from variants.models import Case


class StandardPagination(CursorPagination):
    """Standard cursor navigation for the API."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
    ordering = "-date_created"


class CaseProjectPermission(SODARAPIProjectPermission):
    """Permission class that obtains the project from the ``case`` parameter in URL."""

    def get_project(self, request=None, kwargs=None):
        _ = request
        case = Case.objects.get(sodar_uuid=kwargs["case"])
        return case.project


class CaseAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """Allow listing and retrieval of ``CaseAnalysis`` records for a given case.

    As we only allow for one ``CaseAnalysis`` per case, we implicitely create one
    when listing.
    """

    serializer_class = CaseAnalysisSerializer
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "caseanalysis"

    pagination_class = StandardPagination

    permission_classes = [CaseProjectPermission]

    def get_permission_required(self):
        if self.action in ("list", "retrieve"):
            return "cases_analysis.view_data"

    def get_queryset(self):
        """Return queryset with all ``CaseAnalysis`` records for the given case.

        Currently, this will be at most one.
        """
        result = CaseAnalysis.objects.all()
        result = result.filter(case__sodar_uuid=self.kwargs["case"])
        return result

    def list(self, request, *args, **kwargs):
        """List the ``CaseAnalysis`` objects for the given case.

        Implement the "create single case analysis on listing" logic.
        """
        case = get_object_or_404(Case.objects.all(), sodar_uuid=self.kwargs["case"])
        with transaction.atomic():
            if not CaseAnalysis.objects.filter(case=case).exists():
                CaseAnalysis.objects.create(case=case)
        return super().list(request, *args, **kwargs)


class CaseAnalysisSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Allow retrieval only of ``CaseAnalysisSession`` record for current user."""

    serializer_class = CaseAnalysisSessionSerializer
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "caseanalysissession"

    pagination_class = StandardPagination

    permission_classes = [CaseProjectPermission]

    def get_permission_required(self):
        if self.action in ("list", "retrieve"):
            return "cases_analysis.view_data"

    def get_queryset(self):
        """Return queryset with all ``CaseAnalysisSession`` records for the given case and
        current user.

        Currently, this will be at most one.
        """
        result = CaseAnalysisSession.objects.all()
        result = result.filter(
            caseanalysis__case__sodar_uuid=self.kwargs["case"],
            user=self.request.user,
        )
        return result

    def list(self, request, *args, **kwargs):
        """List the ``CaseAnalysisSession`` objects for the given case and current user.

        Implement the "create single case analysis session on listing" logic.
        """
        case = get_object_or_404(Case.objects.all(), sodar_uuid=self.kwargs["case"])
        with transaction.atomic():
            caseanalysis, _ = CaseAnalysis.objects.get_or_create(case=case)
            CaseAnalysisSession.objects.get_or_create(
                caseanalysis=caseanalysis, user=self.request.user
            )
        return super().list(request, *args, **kwargs)
