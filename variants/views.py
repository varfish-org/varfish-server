from itertools import groupby, chain
import json
import uuid

import decimal
import aldjemy.core

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
import simplejson as json

from bgjobs.models import BackgroundJob
from clinvar.models import Clinvar
from frequencies.views import FrequencyMixin
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from projectroles.plugins import get_backend_api
from variants.models_support import ClinvarReportQuery, RenderFilterQuery, KnownGeneAAQuery

from .models import Case, ExportFileBgJob, SmallVariantFlags, SmallVariantComment, SmallVariantQuery
from .forms import (
    ClinvarForm,
    FilterForm,
    ResubmitForm,
    SmallVariantFlagsForm,
    SmallVariantCommentForm,
    FILTER_FORM_TRANSLATE_SIGNIFICANCE,
    FILTER_FORM_TRANSLATE_CLINVAR_STATUS,
)
from .tasks import export_file_task


class UUIDEncoder(json.JSONEncoder):
    """JSON encoder for UUIds"""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


class AlchemyConnectionMixin:
    """Cached alchemy connection for CBVs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alchemy_connection = None

    def get_alchemy_connection(self):
        if not self._alchemy_connection:
            self._alchemy_connection = SQLALCHEMY_ENGINE.connect()
        return self._alchemy_connection


class CaseListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of all cases"""

    template_name = "variants/case_list.html"
    permission_required = "variants.view_data"
    model = Case

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


def _undecimal(the_dict):
    """Helper to replace Decimal values in a dict."""
    result = {}
    for key, value in the_dict.items():
        if isinstance(value, decimal.Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result


class CaseDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display a case in detail."""

    template_name = "variants/case_detail.html"
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"


class CaseFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    FormView,
):
    template_name = "variants/case_filter.html"
    permission_required = "variants.view_data"
    form_class = FilterForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_object = None
        self._alchemy_connection = None

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["case"] = self.get_case_object()
        return result

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        if form.cleaned_data["submit"] == "download":
            return self._form_valid_file(form)
        else:
            return self._form_valid_render(form)

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {}".format(
                    form.cleaned_data["file_type"], self.get_case_object().name
                ),
                project=self._get_project(self.request, self.kwargs),
                job_type="variants.export_file_bg_job",
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=_undecimal(form.cleaned_data),
                file_type=form.cleaned_data["file_type"],
            )
        messages.info(
            self.request,
            "Created background job for your file download. "
            "After the file has been generated, you will be able to download it here.",
        )
        export_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())

    def _form_valid_render(self, form):
        """The form is valid, we are supposed to render an HTML table with the results."""
        # Save query parameters.
        stored_query = SmallVariantQuery.objects.create(
            case=self.get_case_object(),
            user=self.request.user,
            form_id=form.form_id,
            form_version=form.form_version,
            query_settings=_undecimal(form.cleaned_data),
        )
        # Perform query while recording time.
        before = timezone.now()
        qb = RenderFilterQuery(self.get_case_object(), self.get_alchemy_connection())
        result = qb.run(form.cleaned_data)
        num_results = result.rowcount
        rows = list(result.fetchmany(form.cleaned_data["result_rows_limit"]))
        elapsed = timezone.now() - before
        return render(
            self.request,
            self.template_name,
            self.get_context_data(
                result_rows=rows, result_count=num_results, elapsed_seconds=elapsed.total_seconds()
            ),
        )

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        previous_query = (
            self.get_case_object()
            .small_variant_queries.filter(user=self.request.user)
            .order_by("-date_created")
            .first()
        )
        if self.request.method == "GET" and previous_query:
            # TODO: the code for version conversion needs to be hooked in here
            messages.info(
                self.request,
                ("Welcome back! We have restored your previous query settings from {}.").format(
                    naturaltime(previous_query.date_created)
                ),
            )
            result.update(previous_query.query_settings)
        return result

    def get_context_data(self, **kwargs):
        """Put the ``Case`` object into the context."""
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        return context


def status_level(status):
    """Return int level of highest clinvar status/pathogenicity from iterable of clinvar status strings."""
    for i, ref in enumerate(FILTER_FORM_TRANSLATE_CLINVAR_STATUS.values()):
        if ref == status:
            return i
    return len(FILTER_FORM_TRANSLATE_CLINVAR_STATUS.values())


def sig_level(significance):
    """Return int level of highest pathogenicity from iterable of pathogenicity strings."""
    for i, ref in enumerate(FILTER_FORM_TRANSLATE_SIGNIFICANCE.values()):
        if ref == significance:
            return i
    return len(FILTER_FORM_TRANSLATE_SIGNIFICANCE.values())


class CaseClinvarReportView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    FormView,
):
    template_name = "variants/case_clinvar.html"
    permission_required = "variants.view_data"
    form_class = ClinvarForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_object = None
        self._alchemy_connection = None

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["case"] = self.get_case_object()
        return result

    def form_valid(self, form):
        """The form is valid, we are supposed to render an HTML table with the results."""
        # Save query parameters.
        stored_query = SmallVariantQuery.objects.create(
            case=self.get_case_object(),
            user=self.request.user,
            form_id=form.form_id,
            form_version=form.form_version,
            query_settings=_undecimal(form.cleaned_data),
        )
        # Perform query while recording time.
        before = timezone.now()
        qb = ClinvarReportQuery(self.get_case_object(), self.get_alchemy_connection())
        result = qb.run(form.cleaned_data)
        elapsed = timezone.now() - before
        num_results = result.rowcount
        # Group results.
        # TODO: refactor grouping of results
        rows = list(result.fetchmany(form.cleaned_data["result_rows_limit"]))
        grouped_rows = {
            (r["max_significance_lvl"], r["max_clinvar_status_lvl"], key): r
            for key, r in self._yield_grouped_rows(rows)
        }
        sorted_grouped_rows = [v for k, v in sorted(grouped_rows.items())]
        return render(
            self.request,
            self.template_name,
            self.get_context_data(
                result_rows=rows,
                grouped_rows=sorted_grouped_rows,
                result_count=num_results,
                elapsed_seconds=elapsed.total_seconds(),
            ),
        )

    def _yield_grouped_rows(self, rows):
        grouped = groupby(
            rows, lambda x: (x.release, x.chromosome, x.position, x.reference, x.alternative)
        )
        for k, vs in grouped:
            key = "-".join(map(str, k))
            vs = list(vs)
            row = {"entries": vs, "clinvars": []}
            for v in vs:
                row["clinvars"].append(
                    {
                        "rcv": v.rcv,
                        "clinical_significance_ordered": v.clinical_significance_ordered,
                        "review_status_orderd": v.review_status_ordered,
                        "all_traits": v.all_traits,
                        # "dates_ordered": v.dates_ordered,
                        "origin": v.origin,
                    }
                )
                candidates = []
                for sig, status in zip(v.clinical_significance_ordered, v.review_status_ordered):
                    sig_lvl = sig_level(sig)
                    status_lvl = status_level(status)
                    candidates.append((sig_lvl, status_lvl, sig, status))
                # update dict
                keys = [
                    "max_significance_lvl",
                    "max_clinvar_status_lvl",
                    "max_significance",
                    "max_clinvar_status",
                ]
                if candidates:
                    values = min(candidates)
                else:
                    values = (sig_level(None), status_level(None), None, None)
                row = {**row, **(dict(zip(keys, values)))}
            yield key, row

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        previous_query = (
            self.get_case_object()
            .small_variant_queries.filter(user=self.request.user)
            .order_by("-date_created")
            .first()
        )
        if self.request.method == "GET" and previous_query:
            result.update(previous_query)
            self.get_context_data()["query_loaded"] = True
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        return context


class ExtendAPIView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FrequencyMixin,
    AlchemyConnectionMixin,
    View,
):
    permission_required = "variants.view_data"

    def get(self, *args, **kwargs):
        # TODO(holtgrewe): don't use self.kwargs for passing around values
        self.kwargs = dict(kwargs)
        self.kwargs["knowngeneaa"] = self._load_knowngene_aa(kwargs)
        self.kwargs.update(self.get_frequencies(kwargs))
        self.kwargs["clinvar"] = self._load_clinvar(kwargs)
        return HttpResponse(json.dumps(self.kwargs), content_type="application/json")

    def _load_knowngene_aa(self, query_kwargs):
        """Load the UCSC knownGeneAA conservation alignment information."""
        query = KnownGeneAAQuery(self.get_alchemy_connection())
        result = []
        for entry in query.run(query_kwargs):
            result.append(
                {
                    "chromosome": entry.chromosome,
                    "start": entry.start,
                    "end": entry.end,
                    "alignment": entry.alignment,
                }
            )
        return result

    def _load_clinvar(self, query_kwargs):
        """Load clinvar information"""
        filter_args = {
            "release": query_kwargs["release"],
            "chromosome": query_kwargs["chromosome"],
            "position": int(query_kwargs["position"]),
            "reference": query_kwargs["reference"],
            "alternative": query_kwargs["alternative"],
        }
        result = []
        try:
            for entry in Clinvar.objects.filter(**filter_args):
                result.append(
                    {
                        "clinical_significance": entry.clinical_significance,
                        "all_traits": list({trait.lower() for trait in entry.all_traits}),
                    }
                )
            return result
        except ObjectDoesNotExist:
            return None


class ExportFileJobListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of export jobs for case.
    """

    permission_required = "variants.view_data"
    template_name = "variants/export_job_list.html"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return super().get(*args, **kwargs)


class ExportFileJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the file export background job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/export_job_detail.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = ResubmitForm()
        return result


class ExportFileJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Display status and further details of the file export background job.
    """

    permission_required = "variants.view_data"
    form_class = ResubmitForm

    def form_valid(self, form):
        job = get_object_or_404(ExportFileBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {} (Resubmission)".format(
                    form.cleaned_data["file_type"], job.case
                ),
                project=job.bg_job.project,
                job_type="variants.export_file_bg_job",
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                case=job.case,
                query_args=job.query_args,
                file_type=form.cleaned_data["file_type"],
            )
        export_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())


class ExportFileJobDownloadView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Download the file generated, if generated.

    Otherwise, thrown 404.
    """

    http_method_names = ["get"]

    permission_required = "variants.view_data"
    template_name = "variants/export_job_detail.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        try:
            content_types = {
                "tsv": "text/tab-separated-values",
                "vcf": "text/plain+gzip",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            extensions = {"tsv": ".tsv", "vcf": ".vcf.gz", "xlsx": ".xlsx"}
            obj = self.get_object()
            response = HttpResponse(
                obj.export_result.payload, content_type=content_types[obj.file_type]
            )
            response["Content-Disposition"] = 'attachment; filename="%(name)s%(ext)s"' % {
                "name": "varfish_%s_%s"
                % (timezone.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), obj.case.sodar_uuid),
                "ext": extensions[obj.file_type],
            }
            return response
        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e


class SmallVariantFlagsApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """A view that returns JSON for the ``SmallVariantFlags`` for a variant of a case and allows updates."""

    # TODO: create new permission
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def _model_to_dict(self, flags):
        """Helper that calls ``model_to_dict()`` and then replaces the case PK with the SODAR UUID."""
        return {**model_to_dict(flags), "case": str(self.get_object().sodar_uuid)}

    def get(self, *_args, **_kwargs):
        case = self.get_object()
        small_var_flags = get_object_or_404(
            case.small_variant_flags,
            release=self.request.GET.get("release"),
            chromosome=self.request.GET.get("chromosome"),
            position=self.request.GET.get("position"),
            reference=self.request.GET.get("reference"),
            alternative=self.request.GET.get("alternative"),
            ensembl_gene_id=self.request.GET.get("ensembl_gene_id"),
        )
        return HttpResponse(
            json.dumps(self._model_to_dict(small_var_flags), cls=UUIDEncoder),
            content_type="application/json",
        )

    def post(self, *_args, **_kwargs):
        case = self.get_object()
        try:
            flags = case.small_variant_flags.get(
                release=self.request.POST.get("release"),
                chromosome=self.request.POST.get("chromosome"),
                position=self.request.POST.get("position"),
                reference=self.request.POST.get("reference"),
                alternative=self.request.POST.get("alternative"),
                ensembl_gene_id=self.request.POST.get("ensembl_gene_id"),
            )
        except SmallVariantFlags.DoesNotExist:
            flags = SmallVariantFlags(case=case, sodar_uuid=uuid.uuid4())
        form = SmallVariantFlagsForm(self.request.POST, instance=flags)
        try:
            flags = form.save()
        except ValueError as e:
            raise Exception(str(form.errors)) from e
        timeline = get_backend_api("timeline_backend")
        if timeline:
            variant = "{chromosome}-{position}-{reference}-{alternative}".format(
                **form.cleaned_data
            )
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="flags_set",
                description="set flags for variant %s in case {case} to {flags}"
                % flags.get_variant_description(),
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
            tl_event.add_object(obj=flags, label="flags", name=flags.human_readable())
        if flags.no_flags_set():
            flags.delete()
            result = {"message": "erased"}
        else:
            result = self._model_to_dict(flags)
        return HttpResponse(json.dumps(result, cls=UUIDEncoder), content_type="application/json")


class SmallVariantCommentApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """A view that allows to create a new comment."""

    # TODO: create new permission
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *_args, **_kwargs):
        case = self.get_object()
        comment = SmallVariantComment(case=case, user=self.request.user, sodar_uuid=uuid.uuid4())
        form = SmallVariantCommentForm(self.request.POST, instance=comment)
        comment = form.save()
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="comment_add",
                description="add comment for variant %s in case {case}: {text}"
                % comment.get_variant_description(),
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
            tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())
        return HttpResponse(json.dumps({"result": "OK"}), content_type="application/json")
