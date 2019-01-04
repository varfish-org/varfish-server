from itertools import groupby, chain
import json
import uuid

import decimal
import aldjemy.core
import numpy as np

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
from geneinfo.models import Hgnc, NcbiGeneInfo, NcbiGeneRif
from frequencies.views import FrequencyMixin
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from projectroles.plugins import get_backend_api
from annotation.models import Annotation
from .models import SmallVariant
from .models_support import (
    ClinvarReportQuery,
    RenderFilterQuery,
    ProjectCasesRenderFilterQuery,
    KnownGeneAAQuery,
)
from .models import (
    Case,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    DistillerSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    CaseAwareProject,
    SmallVariantFlags,
    SmallVariantComment,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
)
from .forms import (
    ClinvarForm,
    DistillerSubmissionResubmitForm,
    ExportFileResubmitForm,
    ExportProjectCasesFileResubmitForm,
    FILTER_FORM_TRANSLATE_CLINVAR_STATUS,
    FILTER_FORM_TRANSLATE_EFFECTS,
    FILTER_FORM_TRANSLATE_SIGNIFICANCE,
    FilterForm,
    ProjectCasesFilterForm,
    ProjectStatsJobForm,
    SmallVariantCommentForm,
    SmallVariantFlagsForm,
)
from .tasks import (
    export_file_task,
    export_project_cases_file_task,
    distiller_submission_task,
    compute_project_variants_stats,
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
        elif form.cleaned_data["submit"] == "submit-mutationdistiller":
            return self._form_valid_mutation_distiller(form)
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
                job_type=ExportFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs),
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
                project=self._get_project(self.request, self.kwargs),
                job_type=DistillerSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = DistillerSubmissionBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs),
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

    def _form_valid_render(self, form):
        """The form is valid, we are supposed to render an HTML table with the results."""
        # Save query parameters.
        SmallVariantQuery.objects.create(
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
            for key, value in previous_query.query_settings.items():
                if isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        """Put the ``Case`` object into the context."""
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        context["allow_md_submittion"] = True
        return context


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

    template_name = "variants/project_cases_filter.html"
    permission_required = "variants.view_data"
    form_class = ProjectCasesFilterForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alchemy_connection = None

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["project"] = self._get_project(self.request, self.kwargs)
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
                name="Create {} file for cases in project".format(form.cleaned_data["file_type"]),
                project=self._get_project(self.request, self.kwargs),
                job_type=ExportProjectCasesFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportProjectCasesFileBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs),
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

    def _form_valid_render(self, form):
        """The form is valid, we are supposed to render an HTML table with the results."""
        # Save query parameters.
        ProjectCasesSmallVariantQuery.objects.create(
            project=self._get_project(self.request, self.kwargs),
            user=self.request.user,
            form_id=form.form_id,
            form_version=form.form_version,
            query_settings=_undecimal(form.cleaned_data),
        )
        # Perform query while recording time.
        before = timezone.now()
        qb = ProjectCasesRenderFilterQuery(
            self._get_project(self.request, self.kwargs), self.get_alchemy_connection()
        )
        result = qb.run(form.cleaned_data)
        num_results = result.rowcount
        rows = self._split_rows_per_sample(result.fetchmany(form.cleaned_data["result_rows_limit"]))
        elapsed = timezone.now() - before
        return render(
            self.request,
            self.template_name,
            self.get_context_data(
                result_rows=rows, result_count=num_results, elapsed_seconds=elapsed.total_seconds()
            ),
        )

    def _split_rows_per_sample(self, rows):
        """Create one row for each sample, adding the ``sample`` colum entry."""
        result = []
        for row in rows:
            for sample in sorted(row.genotype.keys()):
                result.append(RowWithSampleProxy(row, sample))
        return result

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        previous_query = (
            self._get_project(self.request, self.kwargs)
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
    """Display clinvar report for a case."""
    
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
        SmallVariantQuery.objects.create(
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
        return context


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
            return []

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
            gene = Hgnc.objects.filter(entrez_id=kwargs["gene_id"]).first()
        else:
            gene = Hgnc.objects.filter(ensembl_gene_id=kwargs["gene_id"]).first()
        if not gene:
            return {"gene_id": kwargs["gene_id"]}
        else:
            return gene

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
        result["resubmit_form"] = ExportFileResubmitForm()
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
                query_args=job.query_args,
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
        result["resubmit_form"] = ExportProjectCasesFileResubmitForm()
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
                query_args=job.query_args,
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
        result["resubmit_form"] = DistillerSubmissionResubmitForm()
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
    form_class = DistillerSubmissionResubmitForm

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
                project=self._get_project(self.request, self.kwargs),
                job_type=ComputeProjectVariantsStatsBgJob.spec_name,
                user=self.request.user,
            )
            recreate_job = ComputeProjectVariantsStatsBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs), bg_job=bg_job
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
            tl_event = timeline.add_event(
                project=self._get_project(self.request, self.kwargs),
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
