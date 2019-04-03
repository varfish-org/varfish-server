from itertools import groupby, chain
import json
import uuid

import decimal
import aldjemy.core
import numpy as np

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404, JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
import simplejson as json

from bgjobs.models import BackgroundJob
from clinvar.models import Clinvar
from geneinfo.models import (
    Hgnc,
    NcbiGeneInfo,
    NcbiGeneRif,
    Hpo,
    HpoName,
    Mim2geneMedgen,
    RefseqToHgnc,
)
from frequencies.views import FrequencyMixin
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from projectroles.plugins import get_backend_api
from annotation.models import Annotation
from .models_support import (
    LoadPrefetchedClinvarReportQuery,
    KnownGeneAAQuery,
    LoadPrefetchedFilterQuery,
    ProjectCasesLoadPrefetchedFilterQuery,
)
from .models import (
    Case,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    DistillerSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    FilterBgJob,
    CaseAwareProject,
    SmallVariant,
    SmallVariantFlags,
    SmallVariantComment,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
    ProjectCasesFilterBgJob,
    ClinvarBgJob,
    ClinvarQuery,
    annotate_with_phenotype_scores,
    annotate_with_pathogenicity_scores,
    annotate_with_joint_scores,
)
from .forms import (
    ClinvarForm,
    ExportFileResubmitForm,
    ExportProjectCasesFileResubmitForm,
    FILTER_FORM_TRANSLATE_CLINVAR_STATUS,
    FILTER_FORM_TRANSLATE_EFFECTS,
    FILTER_FORM_TRANSLATE_SIGNIFICANCE,
    FilterForm,
    ProjectCasesFilterForm,
    EmptyForm,
    ProjectStatsJobForm,
    SmallVariantCommentForm,
    SmallVariantFlagsForm,
)
from .tasks import (
    export_file_task,
    export_project_cases_file_task,
    distiller_submission_task,
    compute_project_variants_stats,
    filter_task,
    project_cases_filter_task,
    clinvar_task,
)
from .file_export import RowWithSampleProxy


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

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["project"] = CaseAwareProject.objects.get(pk=result["project"].pk)
        cases = result["object_list"]
        result["samples"] = list(
            sorted(set(chain(*(case.get_members_with_samples() for case in cases))))
        )
        result["dps"] = {
            stats.sample_name: {int(key): value for key, value in stats.ontarget_dps.items()}
            for case in cases
            for stats in case.variant_stats.sample_variant_stats.all()
        }
        dp_medians = [
            stats.ontarget_dp_quantiles[2]
            for case in cases
            for stats in case.variant_stats.sample_variant_stats.all()
        ]
        if not dp_medians:
            result["dp_quantiles"] = [0] * 5
        else:
            result["dp_quantiles"] = list(np.percentile(np.asarray(dp_medians), [0, 25, 50, 100]))
        result["dps_keys"] = list(chain(range(0, 20), range(20, 50, 2), range(50, 200, 5), (200,)))
        result["sample_stats"] = {
            stats.sample_name: stats
            for case in cases
            for stats in case.variant_stats.sample_variant_stats.all()
        }
        het_ratios = [
            stats.het_ratio
            for case in cases
            for stats in case.variant_stats.sample_variant_stats.all()
        ]
        if not het_ratios:
            result["het_ratio_quantiles"] = [0] * 5
        else:
            result["het_ratio_quantiles"] = list(
                np.percentile(np.asarray(het_ratios), [0, 25, 50, 100])
            )

        return result


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
    AlchemyConnectionMixin,  # XXX
    DetailView,
):
    """Display a case in detail."""

    template_name = "variants/case_detail.html"
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        case = result["object"]
        result["samples"] = case.get_members_with_samples()
        result["effects"] = list(FILTER_FORM_TRANSLATE_EFFECTS.values())
        result["ontarget_effect_counts"] = {
            stats.sample_name: stats.ontarget_effect_counts
            for stats in case.variant_stats.sample_variant_stats.all()
        }
        result["indel_sizes"] = {
            stats.sample_name: {
                int(key): value for key, value in stats.ontarget_indel_sizes.items()
            }
            for stats in case.variant_stats.sample_variant_stats.all()
        }
        result["indel_sizes_keys"] = list(
            sorted(
                set(
                    chain(
                        *list(
                            map(int, indel_sizes.keys())
                            for indel_sizes in result["indel_sizes"].values()
                        )
                    )
                )
            )
        )
        result["dps"] = {
            stats.sample_name: {int(key): value for key, value in stats.ontarget_dps.items()}
            for stats in case.variant_stats.sample_variant_stats.all()
        }
        dp_medians = [
            stats.ontarget_dp_quantiles[2]
            for stats in case.variant_stats.sample_variant_stats.all()
        ]
        result["dp_quantiles"] = list(np.percentile(np.asarray(dp_medians), [0, 25, 50, 100]))
        result["dps_keys"] = list(chain(range(0, 20), range(20, 50, 2), range(50, 200, 5), (200,)))
        result["sample_stats"] = {
            stats.sample_name: stats for stats in case.variant_stats.sample_variant_stats.all()
        }
        het_ratios = [stats.het_ratio for stats in case.variant_stats.sample_variant_stats.all()]
        result["het_ratio_quantiles"] = list(
            np.percentile(np.asarray(het_ratios), [0, 25, 50, 100])
        )

        return result


class CaseFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    FormView,
):
    """Display the filter form for a case."""

    template_name = "variants/filter.html"
    permission_required = "variants.view_data"
    form_class = FilterForm
    success_url = "."
    query_type = "case"

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
        elif form.cleaned_data["submit"] == "submit-mutationdistiller":
            return self._form_valid_mutation_distiller(form)

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {}".format(
                    form.cleaned_data["file_type"], self.get_case_object().name
                ),
                project=self.get_project(self.request, self.kwargs),
                job_type=ExportFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=_undecimal(form.cleaned_data),
                file_type=form.cleaned_data["file_type"],
            )
        export_file_task.delay(export_job_pk=export_job.pk)
        messages.info(
            self.request,
            "Created background job for your file download. "
            "After the file has been generated, you will be able to download it here.",
        )
        return redirect(export_job.get_absolute_url())

    def _form_valid_mutation_distiller(self, form):
        """The form is valid, we are supposed to submit to MutationDistiller."""
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Submitting case {} to MutationDistiller".format(self.get_case_object().name),
                project=self.get_project(self.request, self.kwargs),
                job_type=DistillerSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = DistillerSubmissionBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=_undecimal(form.cleaned_data),
            )
        distiller_submission_task.delay(submission_job_pk=submission_job.pk)
        messages.info(
            self.request,
            "Created background job for your MutationDistiller submission. "
            "You can find the link to the MutationDistiller job on this site. "
            "We put your email into the MutationDistiller job so you will get an email once it is done.",
        )
        return redirect(submission_job.get_absolute_url())

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        if "job" in self.kwargs:
            previous_query = FilterBgJob.objects.get(
                sodar_uuid=self.kwargs["job"]
            ).smallvariantquery
        else:
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
            for key, value in previous_query.query_settings.items():
                if key == "genomic_region":
                    result[key] = "\n".join("{}:{:,}-{:,}".format(*v) for v in value)
                elif isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        """Put the ``Case`` object into the context."""
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        context["allow_md_submittion"] = True
        # Construct the URL that is assigned to the submit button for the ajax request
        context["submit_button_url"] = reverse(
            "variants:case-filter-results",
            kwargs={"project": context["project"].sodar_uuid, "case": context["object"].sodar_uuid},
        )
        context["load_data_url"] = reverse(
            "variants:case-load-filter-results",
            kwargs={"project": context["project"].sodar_uuid, "case": context["object"].sodar_uuid},
        )
        context["request_previous_job_url"] = reverse(
            "variants:filter-job-previous",
            kwargs={"project": context["project"].sodar_uuid, "case": context["object"].sodar_uuid},
        )
        context["job_status_url"] = reverse(
            "variants:filter-job-status", kwargs={"project": context["project"].sodar_uuid}
        )
        context["query_type"] = self.query_type
        return context


class CasePrefetchFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for starting a background filter job.

    This view initiates a background filter job and returns its id as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "case"

    def post(self, request, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        # get case object
        case_object = Case.objects.get(sodar_uuid=kwargs["case"])

        # clean data first
        form = FilterForm(request.POST, case=case_object)

        if form.is_valid():
            # form is valid, we are supposed to render an HTML table with the results
            with transaction.atomic():
                # Save query parameters
                small_variant_query = SmallVariantQuery.objects.create(
                    case=case_object,
                    user=request.user,
                    form_id=form.form_id,
                    form_version=form.form_version,
                    query_settings=_undecimal(form.cleaned_data),
                )
                # Construct background job objects
                bg_job = BackgroundJob.objects.create(
                    name="Running filter query for case {}".format(case_object.name),
                    project=self.get_project(request, kwargs),
                    job_type=FilterBgJob.spec_name,
                    user=request.user,
                )
                filter_job = FilterBgJob.objects.create(
                    project=self.get_project(request, kwargs),
                    bg_job=bg_job,
                    case=case_object,
                    smallvariantquery=small_variant_query,
                )

            # Submit job
            filter_task.delay(filter_job_pk=filter_job.pk)
            return JsonResponse({"filter_job_uuid": filter_job.sodar_uuid})
        return JsonResponse(form.errors, status=400)


class FilterJobGetStatus(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for getting a filter job status.

    This view queries the current status of a filter job and returns it as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, request, *args, **kwargs):
        try:
            filter_job = FilterBgJob.objects.select_related("bg_job").get(
                sodar_uuid=request.POST["filter_job_uuid"]
            )
            log_entries = reversed(
                filter_job.bg_job.log_entries.all().order_by("-date_created")[:3]
            )
            return JsonResponse(
                {
                    "status": filter_job.bg_job.status,
                    "messages": [
                        "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                        for e in log_entries
                    ],
                }
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "No filter job with UUID {}".format(request.POST["filter_job_uuid"])},
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(request.POST["filter_job_uuid"])}, status=400
            )


class FilterJobGetPrevious(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for getting the ID of the previous filter job.

    This view returns the previous filter job ID (if available) as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        filter_job = (
            FilterBgJob.objects.filter(
                smallvariantquery__user=request.user, case__sodar_uuid=kwargs["case"]
            )
            .order_by("-bg_job__date_created")
            .first()
        )
        if filter_job:
            return JsonResponse({"filter_job_uuid": filter_job.sodar_uuid})
        return JsonResponse({"filter_job_uuid": None})


class CaseLoadPrefetchedFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for displaying filter results.

    This view fetches previous query results and renders them in a table.
    """

    template_name = "variants/filter_result/table.html"
    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "case"

    def post(self, request, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""
        # TODO: properly test prioritization
        # TODO: refactor, cleanup, break apart
        # Fetch filter job to display.
        filter_job = FilterBgJob.objects.get(sodar_uuid=request.POST["filter_job_uuid"])

        # Compute number of columns in table for the cards.
        pedigree = filter_job.smallvariantquery.case.get_filtered_pedigree_with_samples()
        card_colspan = 12 + len(pedigree)

        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = LoadPrefetchedFilterQuery(
            filter_job.smallvariantquery.case,
            SQLALCHEMY_ENGINE.connect(),
            filter_job.smallvariantquery.id,
        )
        results = query.run(filter_job.smallvariantquery.query_settings)
        num_results = results.rowcount
        # Get first N rows. This will pop the first N rows! results list will be decreased by N.
        rows = list(
            results.fetchmany(filter_job.smallvariantquery.query_settings["result_rows_limit"])
        )
        elapsed = timezone.now() - before

        # Annotate with phenotype score if any.
        gene_scores = {
            entry.gene_id: entry.score
            for entry in filter_job.smallvariantquery.smallvariantquerygenescores_set.all()
        }
        if gene_scores:
            card_colspan += 2
            rows = annotate_with_phenotype_scores(rows, gene_scores)

        # Annotate with pathogenicity score if any.
        variant_scores = {
            entry.variant_key(): entry.score
            for entry in filter_job.smallvariantquery.smallvariantqueryvariantscores_set.all()
        }
        if variant_scores:
            card_colspan += 2
            rows = annotate_with_pathogenicity_scores(rows, variant_scores)

        # Annotate with joint scores if any.
        if gene_scores and variant_scores:
            card_colspan += 2
            rows = annotate_with_joint_scores(rows)

        # Get mapping from HPO term to HpoName object.
        hpoterms = {}
        for hpo in filter_job.smallvariantquery.query_settings.get("prio_hpo_terms", []):
            matches = HpoName.objects.filter(hpo_id=hpo)
            if matches:
                hpoterms[hpo] = matches.first().name

        return render(
            request,
            self.template_name,
            self.get_context_data(
                result_rows=rows,
                result_count=num_results,
                elapsed_seconds=elapsed.total_seconds(),
                database=filter_job.smallvariantquery.query_settings["database_select"],
                pedigree=pedigree,
                hpoterms=hpoterms,
                training_mode=filter_job.smallvariantquery.query_settings.get(
                    "training_mode", False
                ),
                query_type=self.query_type,
                has_phenotype_scores=bool(gene_scores),
                has_pathogenicity_scores=bool(variant_scores),
                card_colspan=card_colspan,
                logs=[
                    "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                    for e in filter_job.bg_job.log_entries.all().order_by("date_created")
                ],
            ),
        )


class ProjectCasesLoadPrefetchedFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for displaying project cases filter results.

    This view fetches previous query results and renders them in a table.
    """

    template_name = "variants/filter_result/table.html"
    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "project"

    def post(self, request, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        filter_job = ProjectCasesFilterBgJob.objects.get(sodar_uuid=request.POST["filter_job_uuid"])

        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = ProjectCasesLoadPrefetchedFilterQuery(
            filter_job.projectcasessmallvariantquery.project,
            SQLALCHEMY_ENGINE.connect(),
            filter_job.projectcasessmallvariantquery.id,
        )
        results = query.run(filter_job.projectcasessmallvariantquery.query_settings)
        num_results = results.rowcount
        # Get first N rows. This will pop the first N rows! results list will be decreased by N.
        _rows = results.fetchmany(
            filter_job.projectcasessmallvariantquery.query_settings["result_rows_limit"]
        )
        rows = []
        for row in _rows:
            for sample in sorted(row.genotype.keys()):
                rows.append(RowWithSampleProxy(row, sample))
        elapsed = timezone.now() - before

        return render(
            request,
            self.template_name,
            self.get_context_data(
                result_rows=rows,
                result_count=num_results,
                elapsed_seconds=elapsed.total_seconds(),
                training_mode=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "training_mode", False
                ),
                database=filter_job.projectcasessmallvariantquery.query_settings["database_select"],
                query_type=self.query_type,
                card_colspan=14,
                logs=[
                    "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                    for e in filter_job.bg_job.log_entries.all().order_by("date_created")
                ],
            ),
        )


class ProjectCasesFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    FormView,
):
    """Filter all cases in a project at once.

    This allows to take a cohort-based view on the data, e.g., screening certain genes in all
    donors of a cohort.
    """

    #: Use Project proxy model that is aware of cases.
    project_class = CaseAwareProject

    template_name = "variants/filter.html"
    permission_required = "variants.view_data"
    form_class = ProjectCasesFilterForm
    success_url = "."
    query_type = "project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alchemy_connection = None

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["project"] = self.get_project(self.request, self.kwargs)
        return result

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        if form.cleaned_data["submit"] == "download":
            return self._form_valid_file(form)

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for cases in project".format(form.cleaned_data["file_type"]),
                project=self.get_project(self.request, self.kwargs),
                job_type=ExportProjectCasesFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportProjectCasesFileBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs),
                bg_job=bg_job,
                query_args=_undecimal(form.cleaned_data),
                file_type=form.cleaned_data["file_type"],
            )
        export_project_cases_file_task.delay(export_job_pk=export_job.pk)
        messages.info(
            self.request,
            "Created background job for your file download. "
            "After the file has been generated, you will be able to download it here.",
        )
        return redirect(export_job.get_absolute_url())

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        previous_query = (
            self.get_project(self.request, self.kwargs)
            .small_variant_queries.filter(user=self.request.user)
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
            for key, value in previous_query.query_settings.items():
                if isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_button_url"] = reverse(
            "variants:project-cases-filter-results",
            kwargs={"project": context["project"].sodar_uuid},
        )
        context["load_data_url"] = reverse(
            "variants:project-cases-load-filter-results",
            kwargs={"project": context["project"].sodar_uuid},
        )
        context["request_previous_job_url"] = reverse(
            "variants:project-cases-filter-job-previous",
            kwargs={"project": context["project"].sodar_uuid},
        )
        context["job_status_url"] = reverse(
            "variants:project-cases-filter-job-status",
            kwargs={"project": context["project"].sodar_uuid},
        )
        context["query_type"] = self.query_type
        return context


class ProjectCasesPrefetchFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for starting a background joint filter job.

    This view initiates a background joint filter job and returns its id as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "project"

    def post(self, request, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        # get current CaseAwareProject
        project = CaseAwareProject.objects.get(pk=self.get_project(self.request, self.kwargs).pk)

        # clean data first
        form = ProjectCasesFilterForm(request.POST, project=project)

        if form.is_valid():
            # form is valid, we are supposed to render an HTML table with the results
            with transaction.atomic():
                # Save query parameters
                small_variant_query = ProjectCasesSmallVariantQuery.objects.create(
                    project=project,
                    user=self.request.user,
                    form_id=form.form_id,
                    form_version=form.form_version,
                    query_settings=_undecimal(form.cleaned_data),
                )
                # Construct background job objects
                bg_job = BackgroundJob.objects.create(
                    name="Running filter query for project",
                    project=project,
                    job_type=ProjectCasesFilterBgJob.spec_name,
                    user=request.user,
                )
                filter_job = ProjectCasesFilterBgJob.objects.create(
                    project=project,
                    bg_job=bg_job,
                    projectcasessmallvariantquery=small_variant_query,
                )

            # Submit job
            project_cases_filter_task.delay(project_cases_filter_job_pk=filter_job.pk)
            return JsonResponse({"filter_job_uuid": filter_job.sodar_uuid})
        return JsonResponse(form.errors, status=400)


class ProjectCasesFilterJobGetStatus(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for getting a joint filter job status.

    This view queries the current status of a joint filter job and returns it as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, request, *args, **kwargs):
        try:
            filter_job = ProjectCasesFilterBgJob.objects.select_related("bg_job").get(
                sodar_uuid=request.POST["filter_job_uuid"]
            )
            log_entries = reversed(
                filter_job.bg_job.log_entries.all().order_by("-date_created")[:3]
            )
            return JsonResponse(
                {
                    "status": filter_job.bg_job.status,
                    "messages": [
                        "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                        for e in log_entries
                    ],
                }
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "No filter job with UUID {}".format(request.POST["filter_job_uuid"])},
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(request.POST["filter_job_uuid"])}, status=400
            )


class ProjectCasesFilterJobGetPrevious(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for getting the ID of the previous joint filter job.

    This view returns the previous joint filter job ID (if available) as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        filter_job = (
            ProjectCasesFilterBgJob.objects.filter(projectcasessmallvariantquery__user=request.user)
            .order_by("-bg_job__date_created")
            .first()
        )
        if filter_job:
            return JsonResponse({"filter_job_uuid": filter_job.sodar_uuid})
        return JsonResponse({"filter_job_uuid": None})


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
    """Display clinvar report form for a case."""

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

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        if " job" in self.kwargs:
            previous_query = ClinvarBgJob.objects.get(sodar_uuid=self.kwargs["job"]).clinvarquery
        else:
            previous_query = (
                self.get_case_object()
                .clinvar_queries.filter(user=self.request.user)
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
            for key, value in previous_query.query_settings.items():
                if isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        context["submit_button_url"] = reverse(
            "variants:clinvar-results",
            kwargs={"project": context["project"].sodar_uuid, "case": context["object"].sodar_uuid},
        )
        context["load_data_url"] = reverse(
            "variants:load-clinvar-results",
            kwargs={"project": context["project"].sodar_uuid, "case": context["object"].sodar_uuid},
        )
        context["request_previous_job_url"] = reverse(
            "variants:clinvar-job-previous",
            kwargs={"project": context["project"].sodar_uuid, "case": context["object"].sodar_uuid},
        )
        context["job_status_url"] = reverse(
            "variants:clinvar-job-status", kwargs={"project": context["project"].sodar_uuid}
        )
        return context


class CasePrefetchClinvarReportView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for starting a background clinvar report job.

    This view initiates a background clinvar report job and returns its id as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, request, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        # get case object
        case_object = Case.objects.get(sodar_uuid=kwargs["case"])

        # clean data first
        form = ClinvarForm(request.POST, case=case_object)

        if form.is_valid():
            # form is valid, we are supposed to render an HTML table with the results
            with transaction.atomic():
                # Save query parameters
                clinvar_query = ClinvarQuery.objects.create(
                    case=case_object,
                    user=request.user,
                    form_id=form.form_id,
                    form_version=form.form_version,
                    query_settings=_undecimal(form.cleaned_data),
                )
                # Construct background job objects
                bg_job = BackgroundJob.objects.create(
                    name="Running clinvar query for case {}".format(case_object.name),
                    project=self.get_project(request, kwargs),
                    job_type=ClinvarBgJob.spec_name,
                    user=request.user,
                )
                clinvar_job = ClinvarBgJob.objects.create(
                    project=self.get_project(request, kwargs),
                    bg_job=bg_job,
                    case=case_object,
                    clinvarquery=clinvar_query,
                )

            # Submit job
            clinvar_task.delay(clinvar_job_pk=clinvar_job.pk)
            return JsonResponse({"filter_job_uuid": clinvar_job.sodar_uuid})
        return JsonResponse(form.errors, status=400)


class CaseClinvarReportJobGetStatus(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for getting a clinvar report job status.

    This view queries the current status of a clinvar report job and returns it as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, request, *args, **kwargs):
        try:
            filter_job = ClinvarBgJob.objects.select_related("bg_job").get(
                sodar_uuid=request.POST["filter_job_uuid"]
            )
            log_entries = reversed(
                filter_job.bg_job.log_entries.all().order_by("-date_created")[:3]
            )
            return JsonResponse(
                {
                    "status": filter_job.bg_job.status,
                    "messages": [
                        "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                        for e in log_entries
                    ],
                }
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "No filter job with UUID {}".format(request.POST["filter_job_uuid"])},
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(request.POST["filter_job_uuid"])}, status=400
            )


class CaseClinvarReportJobGetPrevious(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for getting the ID of the previous clinvar report job.

    This view returns the previous clinvar report job ID (if available) as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        clinvar_job = (
            ClinvarBgJob.objects.filter(
                clinvarquery__user=request.user, case__sodar_uuid=kwargs["case"]
            )
            .order_by("-bg_job__date_created")
            .first()
        )
        if clinvar_job:
            return JsonResponse({"filter_job_uuid": clinvar_job.sodar_uuid})
        return JsonResponse({"filter_job_uuid": None})


class CaseLoadPrefetchedClinvarReportView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyConnectionMixin,
    View,
):
    """View for displaying clinvar report results.

    This view fetches previous query results and renders them in a table.
    """

    template_name = "variants/clinvar_report/index.html"
    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "case"

    def post(self, request, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        clinvar_job = ClinvarBgJob.objects.get(sodar_uuid=request.POST["filter_job_uuid"])

        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = LoadPrefetchedClinvarReportQuery(
            clinvar_job.clinvarquery.case, SQLALCHEMY_ENGINE.connect(), clinvar_job.clinvarquery.id
        )
        results = query.run(clinvar_job.clinvarquery.query_settings)
        num_results = results.rowcount
        # Get first N rows. This will pop the first N rows! results list will be decreased by N.
        rows = results.fetchmany(clinvar_job.clinvarquery.query_settings["result_rows_limit"])
        grouped_rows = {
            (r["max_significance_lvl"], r["max_clinvar_status_lvl"], key): r
            for key, r in self._yield_grouped_rows(rows)
        }
        sorted_grouped_rows = [v for k, v in sorted(grouped_rows.items())]
        elapsed = timezone.now() - before

        return render(
            request,
            self.template_name,
            self.get_context_data(
                result_rows=rows,
                grouped_rows=sorted_grouped_rows,
                result_count=num_results,
                elapsed_seconds=elapsed.total_seconds(),
                database=clinvar_job.clinvarquery.query_settings["database_select"],
                logs=[
                    "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                    for e in clinvar_job.bg_job.log_entries.all().order_by("date_created")
                ],
                # pedigree=clinvar_job.clinvarquery.case.get_filtered_pedigree_with_samples(),
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


class ClinvarReportJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the ClinvarBgJob background job."""

    permission_required = "variants.view_data"
    template_name = "variants/filter_job_detail.html"
    model = ClinvarBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    query_type = "clinvar"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["query_type"] = self.query_type
        return context


class ClinvarReportJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit the clinvar report query job and redirect to clinvar detail view."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(ClinvarBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting clinvar filter for case {}".format(job.case),
                project=job.bg_job.project,
                job_type=ClinvarBgJob.spec_name,
                user=self.request.user,
            )
            clinvar_job = ClinvarBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, clinvarquery=job.clinvarquery
            )
            clinvar_task.delay(clinvar_job_pk=clinvar_job.pk)
        return redirect(
            reverse(
                "variants:clinvar-job-detail",
                kwargs={"project": job.project.sodar_uuid, "job": clinvar_job.sodar_uuid},
            )
        )


class SmallVariantDetails(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FrequencyMixin,
    AlchemyConnectionMixin,
    DetailView,
):
    """Render details card of small variants."""

    permission_required = "variants.view_data"
    template_name = "variants/variant_details.html"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

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
        for entry in Clinvar.objects.filter(**filter_args):
            result.append(
                {
                    "clinical_significance": entry.clinical_significance,
                    "all_traits": list({trait.lower() for trait in entry.all_traits}),
                }
            )
        return result

    def _load_small_var(self, kwargs):
        return SmallVariant.objects.filter(
            case_id=self.object.pk,
            release=kwargs["release"],
            chromosome=kwargs["chromosome"],
            position=kwargs["position"],
            reference=kwargs["reference"],
            alternative=kwargs["alternative"],
        ).first()

    def _load_molecular_impact(self, kwargs):
        filter_kwargs = {
            key: kwargs[key]
            for key in ("release", "chromosome", "position", "reference", "alternative")
        }
        return [
            model_to_dict(entry)
            for entry in Annotation.objects.filter(**filter_kwargs, database="refseq")
        ]

    def _get_population_freqs(self, kwargs):
        result = {
            "populations": ("AFR", "AMR", "ASJ", "EAS", "FIN", "NFE", "OTH", "SAS"),
            "pop_freqs": {},
        }
        db_infos = {
            "gnomadexomes": "gnomAD Exomes",
            "gnomadgenomes": "gnomAD Genomes",
            "exac": "ExAC",
            "thousandgenomes": "1000GP",
        }
        frequencies = self.get_frequencies(kwargs)
        for key, label in db_infos.items():
            pop_freqs = {}
            for pop in result["populations"]:
                pop_freqs.setdefault(pop, {})["hom"] = frequencies[key].get("hom_%s" % pop.lower())
                pop_freqs.setdefault(pop, {})["het"] = frequencies[key].get("het_%s" % pop.lower())
                pop_freqs.setdefault(pop, {})["hemi"] = frequencies[key].get(
                    "hemi_%s" % pop.lower()
                )
                pop_freqs.setdefault(pop, {})["af"] = frequencies[key].get("af_%s" % pop.lower())
            result["pop_freqs"][label] = pop_freqs
        return result

    def _get_gene_infos(self, kwargs):
        if kwargs["database"] == "refseq":
            hgnc = RefseqToHgnc.objects.filter(entrez_id=kwargs["gene_id"]).first()
            gene = Hgnc.objects.filter(hgnc_id=hgnc.hgnc_id).first()
        else:
            gene = Hgnc.objects.filter(ensembl_gene_id=kwargs["gene_id"]).first()
        if not gene:
            return {"gene_id": kwargs["gene_id"]}
        else:
            gene = model_to_dict(gene)
            hpoterms = {self._get_hpo_mapping(gene["omim_id"])}
            mim2gene = Mim2geneMedgen.objects.filter(entrez_id=gene["entrez_id"])
            if mim2gene:
                for entry in mim2gene:
                    hpoterms.add(self._get_hpo_mapping(entry.omim_id))
            gene["hpo_terms"] = [h for h in hpoterms if h is not None]
            return gene

    def _get_hpo_mapping(self, omim):
        hpo = Hpo.objects.filter(database_id="OMIM:{}".format(omim)).first()
        if hpo:
            hponame = HpoName.objects.filter(hpo_id=hpo.hpo_id).first()
            if hponame:
                return hpo.hpo_id, hponame.name

    def get_context_data(self, object):
        result = super().get_context_data(*self.args, **self.kwargs)
        result["database"] = self.kwargs["database"]
        result["clinvar"] = self._load_clinvar(self.kwargs)
        result["knowngeneaa"] = self._load_knowngene_aa(self.kwargs)
        result["small_var"] = self._load_small_var(self.kwargs)
        result["effect_details"] = self._load_molecular_impact(self.kwargs)
        if self.request.GET.get("render_full", "no").lower() in ("yes", "true"):
            result["base_template"] = "projectroles/project_base.html"
        else:
            result["base_template"] = "empty_base.html"
        result.update(self._get_population_freqs(self.kwargs))
        result["gene"] = self._get_gene_infos(self.kwargs)
        entrez_id = result["small_var"].refseq_gene_id
        result["ncbi_summary"] = NcbiGeneInfo.objects.filter(entrez_id=entrez_id).first()
        result["ncbi_gene_rifs"] = NcbiGeneRif.objects.filter(entrez_id=entrez_id).order_by("pk")
        return result


class BackgroundJobListView(
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
    template_name = "variants/background_job_list.html"
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
        result["resubmit_form"] = ExportFileResubmitForm(
            initial={"file_type": result["object"].query_args["file_type"]}
        )
        return result


class ExportFileJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit export file job."""

    permission_required = "variants.view_data"
    form_class = ExportFileResubmitForm

    def form_valid(self, form):
        job = get_object_or_404(ExportFileBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {} (Resubmission)".format(
                    form.cleaned_data["file_type"], job.case
                ),
                project=job.bg_job.project,
                job_type=ExportFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                case=job.case,
                query_args={**job.query_args, "file_type": form.cleaned_data["file_type"]},
                file_type=form.cleaned_data["file_type"],
            )
        export_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())


class ExportProjectCasesFileJobDownloadView(
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
    template_name = "variants/export_project_cases_job_detail.html"
    model = ExportProjectCasesFileBgJob
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
                % (timezone.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), obj.project.sodar_uuid),
                "ext": extensions[obj.file_type],
            }
            return response
        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e


class ExportProjectCasesFileJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the file export background job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/export_project_cases_job_detail.html"
    model = ExportProjectCasesFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = ExportProjectCasesFileResubmitForm(
            initial={"file_type": result["object"].query_args["file_type"]}
        )
        return result


class ExportProjectCasesFileJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit export file job."""

    permission_required = "variants.view_data"
    form_class = ExportProjectCasesFileResubmitForm

    def form_valid(self, form):
        job = get_object_or_404(ExportProjectCasesFileBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for all cases in project (Resubmission)".format(
                    form.cleaned_data["file_type"]
                ),
                project=job.bg_job.project,
                job_type=ExportProjectCasesFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportProjectCasesFileBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                query_args={**job.query_args, "file_type": form.cleaned_data["file_type"]},
                file_type=form.cleaned_data["file_type"],
            )
        export_project_cases_file_task.delay(export_job_pk=export_job.pk)
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


class DistillerSubmissionJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the MutationDistiller submission background job."""

    permission_required = "variants.view_data"
    template_name = "variants/distiller_job_detail.html"
    model = DistillerSubmissionBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = EmptyForm()
        return result


class DistillerSubmissionJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit to MutationDistiller."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(DistillerSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to MutationDistiller".format(job.case),
                project=job.bg_job.project,
                job_type=DistillerSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = DistillerSubmissionBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, query_args=job.query_args
            )
            distiller_submission_task.delay(submission_job_pk=submission_job.pk)
        return redirect(submission_job.get_absolute_url())


class FilterJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the FilterBgJob background job."""

    permission_required = "variants.view_data"
    template_name = "variants/filter_job_detail.html"
    model = FilterBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    query_type = "case"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["query_type"] = self.query_type
        return context


class ProjectCasesFilterJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the FilterBgJob background job."""

    permission_required = "variants.view_data"
    template_name = "variants/filter_job_detail.html"
    model = ProjectCasesFilterBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    query_type = "project"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["query_type"] = self.query_type
        return context


class FilterJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit the filter query job and redirect to filter view."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(FilterBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting filter case {}".format(job.case),
                project=job.bg_job.project,
                job_type=FilterBgJob.spec_name,
                user=self.request.user,
            )
            filter_job = FilterBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                case=job.case,
                smallvariantquery=job.smallvariantquery,
            )
            filter_task.delay(filter_job_pk=filter_job.pk)
        return redirect(
            reverse(
                "variants:filter-job-detail",
                kwargs={"project": job.project.sodar_uuid, "job": filter_job.sodar_uuid},
            )
        )


class ProjectCasesFilterJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit the filter query job and redirect to filter view."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(ProjectCasesFilterBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting filter project",
                project=job.bg_job.project,
                job_type=ProjectCasesFilterBgJob.spec_name,
                user=self.request.user,
            )
            filter_job = ProjectCasesFilterBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                projectcasessmallvariantquery=job.projectcasessmallvariantquery,
            )
            project_cases_filter_task.delay(project_cases_filter_job_pk=filter_job.pk)
        return redirect(
            reverse(
                "variants:project-cases-filter-job-detail",
                kwargs={"project": job.project.sodar_uuid, "job": filter_job.sodar_uuid},
            )
        )


class ProjectStatsJobCreateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Confirm creating a new project statistics computation job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/project_stats_job_create.html"
    form_class = ProjectStatsJobForm

    def form_valid(self, form):
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Recreate variant statistic for whole project",
                project=self.get_project(self.request, self.kwargs),
                job_type=ComputeProjectVariantsStatsBgJob.spec_name,
                user=self.request.user,
            )
            recreate_job = ComputeProjectVariantsStatsBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs), bg_job=bg_job
            )
        compute_project_variants_stats.delay(export_job_pk=recreate_job.pk)
        messages.info(self.request, "Created background job to recreate project-wide statistics.")
        return redirect(recreate_job.get_absolute_url())


class ProjectStatsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of project-wide statistics computation job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/project_stats_job_detail.html"
    model = ComputeProjectVariantsStatsBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


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
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="flags_set",
                description="set flags for variant %s in case {case}: {extra-flag_values}"
                % flags.get_variant_description(),
                status_type="OK",
                extra_data={"flag_values": flags.human_readable()},
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
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
                project=self.get_project(self.request, self.kwargs),
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
