"""The AJAX API views for the ``clinvar_export`` app.

The UI for this app is completely Vue-based so this is where the real logic is implemented.  Eventually, when we
add an API and ``views_api``, we might move the common parts there and have the AJAX views re-use the logic.
"""
import hashlib
import logging
import pathlib
import re

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView
from knox.auth import TokenAuthentication
from lxml import etree
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)
from projectroles.views_ajax import SODARBaseAjaxView, SODARBaseProjectAjaxView
from projectroles.views_api import APIProjectContextMixin, SODARAPIProjectPermission
import requests
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from clinvar_export.clinvar_xml import XSD_URL_1_7, SubmissionXmlGenerator
from clinvar_export.models import (
    ERROR_REPORT,
    SUBMITTER_REPORT,
    AssertionMethod,
    ClinVarReport,
    Family,
    Individual,
    Organisation,
    Submission,
    SubmissionIndividual,
    SubmissionSet,
    Submitter,
    SubmittingOrg,
    create_families_and_individuals,
)
from clinvar_export.serializers import (
    AnnotatedSmallVariantsSerializer,
    AssertionMethodSerializer,
    ClinVarReportSerializer,
    FamilySerializer,
    IndividualSerializer,
    OrganisationSerializer,
    SubmissionIndividualSerializer,
    SubmissionSerializer,
    SubmissionSetSerializer,
    SubmitterSerializer,
    SubmittingOrgSerializer,
)
from geneinfo.models import Hpo, HpoName
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.helpers import get_engine
from variants.queries import SmallVariantUserAnnotationQuery

from .clinvar_xml import XSD_URL_1_7, SubmissionXmlGenerator

#: Prefix of allowed clinvar submission URLs for fetching reports.
CLINVAR_SUBMISSION_URL_PREFIX = "https://submit.ncbi.nlm.nih.gov/api/"
#: Whether or not to verify request to ClinVar API.
CLINVAR_SUBMISSION_REPORT_FETCH_VERIFY = True
#: Timeout for requests to ClinVar.
CLINVAR_SUBMISSION_REPORT_FETCH_TIMEOUT = 10


#: Logger to use in this module.
LOGGER = logging.getLogger(__name__)


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
            ignored_message = (
                "Element 'Trait', attribute 'ClinicalFeaturesAffectedStatus': The attribute "
                "'ClinicalFeaturesAffectedStatus' is not allowed."
            )
            filtered_es = [e for e in schema.error_log if e.message != ignored_message]
            if filtered_es:
                result = {
                    "valid": False,
                    "details": "\n".join(e.message for e in filtered_es),
                }
            else:
                result = {
                    "valid": True,
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

    def get(self, *_args, **kwargs):
        family = Family.objects.get(project=self.get_project(), sodar_uuid=kwargs.get("family"))
        serializer = AnnotatedSmallVariantsSerializer(
            SmallVariantUserAnnotationQuery(get_engine()).run(case=family.case)
        )
        return Response(serializer.data)


def guess_clinvar_report_type(report_content):
    """Guess report type.

    We simply look for a #SCV header which should be "robust enough".
    """
    for line in report_content.splitlines():
        if line.startswith("#SCV"):
            return SUBMITTER_REPORT
    else:
        return ERROR_REPORT


def parse_clinvar_tsv(report_content):
    """Parse the TSV file, using the last header line for labels."""
    result = []
    header = None
    previous = None
    for line in report_content.splitlines():
        if line.startswith("#"):
            previous = line[1:].split("\t")
        else:
            if not header:
                header = previous
            arr = line.split("\t")
            if len(header) != len(arr):
                raise ParseError(
                    detail=f"Inconsistent lines in report, header={header}, line={arr}"
                )
            result.append(dict(zip(header, arr)))
    return result


def fetch_clinvar_report(report_url):
    response = requests.get(
        report_url,
        verify=CLINVAR_SUBMISSION_REPORT_FETCH_VERIFY,
        timeout=CLINVAR_SUBMISSION_REPORT_FETCH_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def checked_report_url(report_url):
    if not report_url.startswith(CLINVAR_SUBMISSION_URL_PREFIX):  # pragma: no cover
        raise ParseError(
            detail=f"Invalid URL, must start with {CLINVAR_SUBMISSION_URL_PREFIX} but was {report_url}"
        )
    return report_url


class FetchClinVarReportApiView(
    APIProjectContextMixin, SODARBaseProjectAjaxView,
):
    """Fetch ClinVar report for the submission set."""

    permission_required = "clinvar_export.update_data"
    allowed_methods = ("POST",)
    authentication_classes = [SessionAuthentication, TokenAuthentication]  # XXX

    def post(self, *_args, **kwargs):
        # Fetch SubmissionSet to fail early, query report from clinvar, and guess report type.
        submission_set = SubmissionSet.objects.get(sodar_uuid=kwargs.get("submissionset"))
        report_content = fetch_clinvar_report(
            checked_report_url(self.request.data.get("report_url", ""))
        )
        report_type = guess_clinvar_report_type(report_content)

        # We now have everything to store the report, parse it, and assign it to the submissions.
        with transaction.atomic():
            report = ClinVarReport(
                submission_set=submission_set,
                report_type=report_type,
                source_url=self.request.data.get("report_url"),
                payload_md5=hashlib.md5(report_content.encode("utf-8")).hexdigest(),
                payload=report_content,
            )
            report.save()

            records = parse_clinvar_tsv(report_content)
            is_submitter = report_type == SUBMITTER_REPORT
            local_record_col = "Your_record_id" if is_submitter else "RecordID"
            for record in records:
                submission_sodar_uuid = record[local_record_col]
                try:
                    submission = Submission.objects.get(sodar_uuid=submission_sodar_uuid)
                except Submission.DoesNotExist:
                    LOGGER.info(
                        f"Could not find submission with ID {submission_sodar_uuid} from clinvar report"
                    )
                    continue
                if is_submitter:
                    submission.clinvar_submitter_report = record
                else:
                    submission.clinvar_error_report = record
                submission.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ClinVarReportApiPermission(SODARAPIProjectPermission):
    """Project-based permission for ``ClinVarReportListView``"""

    def get_project(self, request=None, kwargs=None):
        submission_set = SubmissionSet.objects.get(sodar_uuid=kwargs["submissionset"])
        return submission_set.project


class ClinVarReportListView(
    _ReadOnlyPermMixin, APIProjectContextMixin, ListAPIView, SODARBaseProjectAjaxView
):
    """Allow to list ``ClinVarReport`` records for a submission set."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "submissionset"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [ClinVarReportApiPermission]

    serializer_class = ClinVarReportSerializer

    def get_permission_required(self):
        return "clinvar_export.view_data"

    def get_queryset(self):
        return ClinVarReport.objects.filter(submission_set__sodar_uuid=self.kwargs["submissionset"])
