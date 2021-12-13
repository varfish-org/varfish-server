"""The AJAX API views for the ``clinvar_export`` app.

The UI for this app is completely Vue-based so this is where the real logic is implemented.  Eventually, when we
add an API and ``views_api``, we might move the common parts there and have the AJAX views re-use the logic.
"""
import pathlib
import re

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView
from lxml import etree
from projectroles.views import (
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
)
from projectroles.views_ajax import SODARBaseProjectAjaxView, SODARBaseAjaxView
from projectroles.views_api import APIProjectContextMixin
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.response import Response
from variants.helpers import get_engine

from geneinfo.models import Hpo, HpoName
from variants.queries import SmallVariantUserAnnotationQuery
from .clinvar_xml import SubmissionXmlGenerator, XSD_URL_1_7
from .models import (
    SubmissionSet,
    Submission,
    Organisation,
    Submitter,
    AssertionMethod,
    SubmissionIndividual,
    Individual,
    Family,
    create_families_and_individuals,
    SubmittingOrg,
)
from .serializers import (
    SubmissionSetSerializer,
    SubmissionSerializer,
    OrganisationSerializer,
    SubmitterSerializer,
    AssertionMethodSerializer,
    SubmissionIndividualSerializer,
    IndividualSerializer,
    FamilySerializer,
    SubmittingOrgSerializer,
    AnnotatedSmallVariantsSerializer,
)


def _read(filename):
    """Read contents after path"""
    with (pathlib.Path(__file__).parent / "data" / filename).open("rt") as inputf:
        return inputf.read()


#: Submission XSD URL to XSD string
XSD_CONTENTS = {
    XSD_URL_1_7: _read(XSD_URL_1_7.rsplit("/", 1)[1]),
}


class _ListCreatePermMixin:
    """Mixin that provides the appropriate ``get_permission_required()`` for list/create views."""

    def get_permission_required(self):
        if self.request.method == "GET":
            return "clinvar_export.view_data"
        else:
            return "clinvar_export.update_data"


class _ReadOnlyPermMixin:
    """Mixin that provides the appropriate ``get_permission_required()`` for list only views."""

    def get_permission_required(self):
        if self.request.method == "GET":
            return "clinvar_export.view_data"
        else:
            return "clinvar_export.denied"


class _RetrieveUpdateDestroyPermMixin:
    """Mixin that provides the appropriate ``get_permission_required()`` for read/update/destroy views."""

    def get_permission_required(self):
        if self.request.method == "POST":
            return "clinvar_export.add_data"
        elif self.request.method == "DELETE":
            return "clinvar_export.delete_data"
        elif self.request.method == "GET":
            return "clinvar_export.view_data"
        else:
            return "clinvar_export.update_data"


class OrganisationReadView(
    _ReadOnlyPermMixin, APIProjectContextMixin, ListAPIView, SODARBaseProjectAjaxView
):
    """List all organisations, must be entered via Admin GUI, no API access.

    NB: these are defined by ClinVar anyway, so they have to be first created through the ClinVar web UI.
    """

    serializer_class = OrganisationSerializer
    queryset = Organisation.objects.all()

    def get_queryset(self):
        """Override to make project-unaware (model has no project field)"""
        return Organisation.objects.all()


class SubmitterReadView(
    _ReadOnlyPermMixin, APIProjectContextMixin, ListAPIView, SODARBaseProjectAjaxView
):
    """List all submitters, must be entered via Admin GUI, no API access.

    NB: these are defined by ClinVar anyway, so they have to be first created through the ClinVar web UI.
    """

    serializer_class = SubmitterSerializer

    def get_queryset(self):
        """Override to make project-unaware (model has no project field)"""
        return Submitter.objects.all()


class AssertionMethodReadView(
    _ReadOnlyPermMixin, APIProjectContextMixin, ListAPIView, SODARBaseProjectAjaxView
):
    """List all assertion methods, must be entered via Admin GUI, no API access."""

    serializer_class = AssertionMethodSerializer
    queryset = AssertionMethod.objects.all()

    def get_queryset(self):
        """Override to make project-unaware (model has no project field)"""
        return AssertionMethod.objects.all()


class IndividualReadView(
    _ReadOnlyPermMixin, APIProjectContextMixin, ListAPIView, SODARBaseProjectAjaxView
):
    """List all individuals in the project cases.

    These will be created as necessary automatically from the Case information in the variants app.
    """

    serializer_class = IndividualSerializer

    def get(self, request, *args, **kwargs):
        """Create Family and Individual records according to the Case records for the current project."""
        create_families_and_individuals(self.get_project())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Override to make project aware via family"""
        return Individual.objects.filter(family__project=self.get_project())


class FamilyReadView(
    _ReadOnlyPermMixin, APIProjectContextMixin, ListAPIView, SODARBaseProjectAjaxView
):
    """List all cases in the project.

    These will be created as necessary automatically from the Case information of the variants app.
    """

    serializer_class = FamilySerializer

    def get(self, request, *args, **kwargs):
        """Create Family and Individual records according to the Case records for the current project."""
        create_families_and_individuals(self.get_project())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Override to make project aware via family"""
        return Family.objects.filter(project=self.get_project())


class SubmissionSetListCreateView(
    _ListCreatePermMixin, APIProjectContextMixin, ListCreateAPIView, SODARBaseProjectAjaxView
):
    """Base AJAX view for list/create of SubmissionSet objects."""

    serializer_class = SubmissionSetSerializer

    def get_queryset(self):
        return SubmissionSet.objects.filter(project=self.get_project())


class SubmissionSetRetrieveUpdateDestroyView(
    _RetrieveUpdateDestroyPermMixin,
    APIProjectContextMixin,
    RetrieveUpdateDestroyAPIView,
    SODARBaseProjectAjaxView,
):
    """Base AJAX view for retrieve/update/destroy of SubmissionSet objects."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "submissionset"
    serializer_class = SubmissionSetSerializer

    def get_queryset(self):
        return SubmissionSet.objects.filter(project=self.get_project())


class SubmissionSetRenderClinvarXml(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Render ClinVar XML for submission set"""

    permission_required = "clinvar_export.view_data"
    model = SubmissionSet
    slug_url_kwarg = "submissionset"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        xml_generator = SubmissionXmlGenerator()
        return HttpResponse(xml_generator.generate_str(instance), content_type="text/xml")


class SubmissionSetValidateClinvarXml(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Render ClinVar XML for submission set and validate via XSD."""

    permission_required = "clinvar_export.view_data"
    model = SubmissionSet
    slug_url_kwarg = "submissionset"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        xml_generator = SubmissionXmlGenerator()
        root = xml_generator.generate_tree(instance)
        schema = self._get_schema(root)
        if schema(root):
            result = {
                "valid": True,
            }
        else:
            result = {
                "valid": False,
                "details": "\n".join(e.message for e in schema.error_log),
            }
        return JsonResponse(result)

    def _get_schema(self, root):
        schema_root = etree.XML(XSD_CONTENTS[self._get_schema_location(root)])
        return etree.XMLSchema(schema_root)

    def _get_schema_location(self, root):
        for attr in root.attrib:
            if "noNamespaceSchemaLocation" in attr:
                return root.attrib.get(attr)


class SubmissionListCreateView(
    _ListCreatePermMixin, APIProjectContextMixin, ListCreateAPIView, SODARBaseProjectAjaxView
):
    """Base AJAX view for list/create of Submission objects."""

    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.filter(submission_set__project=self.get_project())


class SubmissionRetrieveUpdateDestroyView(
    _RetrieveUpdateDestroyPermMixin,
    APIProjectContextMixin,
    RetrieveUpdateDestroyAPIView,
    SODARBaseProjectAjaxView,
):
    """Base AJAX view for retrieve/update/destroy of Submission objects."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "submission"
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.filter(submission_set__project=self.get_project())


class SubmissionIndividualListCreateView(
    _ListCreatePermMixin, APIProjectContextMixin, ListCreateAPIView, SODARBaseProjectAjaxView
):
    """Base AJAX view for retrieve/update/destroy of Submission objects."""

    serializer_class = SubmissionIndividualSerializer

    def get_queryset(self):
        return SubmissionIndividual.objects.filter(
            submission__submission_set__project=self.get_project()
        )


class SubmissionIndividualRetrieveUpdateDestroyView(
    _RetrieveUpdateDestroyPermMixin,
    APIProjectContextMixin,
    RetrieveUpdateDestroyAPIView,
    SODARBaseProjectAjaxView,
):
    """Base AJAX view for retrieve/update/destroy of Submission objects."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "submissionindividual"
    serializer_class = SubmissionIndividualSerializer

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return SubmissionIndividual.objects.filter(
            submission__submission_set__project=self.get_project()
        )


class SubmittingOrgListCreateView(
    _ListCreatePermMixin, APIProjectContextMixin, ListCreateAPIView, SODARBaseProjectAjaxView
):
    """Base AJAX view for retrieve/update/destroy of Submission objects."""

    serializer_class = SubmittingOrgSerializer

    def get_queryset(self):
        return SubmittingOrg.objects.filter(submission_set__project=self.get_project())


class SubmittingOrgRetrieveUpdateDestroyView(
    _RetrieveUpdateDestroyPermMixin,
    APIProjectContextMixin,
    RetrieveUpdateDestroyAPIView,
    SODARBaseProjectAjaxView,
):
    """Base AJAX view for retrieve/update/destroy of Submission objects."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "submittingorg"
    serializer_class = SubmittingOrgSerializer

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return SubmittingOrg.objects.filter(submission_set__project=self.get_project())


class QueryOmimTermApiView(LoginRequiredMixin, SODARBaseAjaxView):
    """Allow searching for OMIM terms."""

    def get(self, *_args, **_kwargs):
        query = self.request.GET.get("query")
        if not query:
            return JsonResponse({"query": query, "result": []})

        query_res = (
            Hpo.objects.filter(
                Q(database_id__startswith="OMIM:")
                & (Q(database_id__icontains=query) | Q(name__icontains=query))
            )
            .values("database_id")
            .distinct()[:10]
        )

        result = []
        for o in query_res:
            seen = {None, "", ".", ";", ";;"}
            # Query database again to get all possible names for an OMIM/DECIPHER/ORPHA id
            for name in (
                Hpo.objects.filter(database_id=o["database_id"])
                .values("database_id")
                .annotate(names=ArrayAgg("name"))[0]["names"]
            ):
                if o["database_id"].startswith("OMIM"):
                    for n in re.split(r"(;+)", re.sub(r"^[#%]?\d{6} ", "", name)):
                        n = n.strip()
                        if n and n not in seen:
                            seen.add(n)
                            result.append({"term_id": o["database_id"], "term_name": n})

        result.sort(key=lambda o: o.get("term_name", ""))
        return JsonResponse({"query": query, "result": result})


class QueryHpoTermApiView(LoginRequiredMixin, SODARBaseAjaxView):
    """Allow searching for HPO terms."""

    def get(self, *_args, **_kwargs):
        query = self.request.GET.get("query")
        if not query:
            return JsonResponse({"query": query, "result": []})

        query_res = HpoName.objects.filter(Q(hpo_id__icontains=query) | Q(name__icontains=query))[
            :10
        ]
        result = [{"term_id": rec.hpo_id, "term_name": rec.name} for rec in query_res]
        return JsonResponse({"query": query, "result": result})


class AnnotatedSmallVariantsApiView(
    APIProjectContextMixin, SODARBaseProjectAjaxView,
):
    """Retrieve user annotations for all families in the current project."""

    permission_required = "clinvar_export.view_data"
    allowed_methods = ("GET",)

    def get(self, *_args, **_kwargs):
        serializer = AnnotatedSmallVariantsSerializer(
            SmallVariantUserAnnotationQuery(get_engine()).run(project=self.get_project())
        )
        return Response(serializer.data)
