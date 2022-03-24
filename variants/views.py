import os
import re
import tempfile
from itertools import chain
from collections import defaultdict
import uuid
import contextlib

import decimal

import binning
import numpy as np
import requests
from base64 import b64encode

from variants.helpers import get_engine
from django.conf import settings
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404, JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils import timezone
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    View,
    RedirectView,
    UpdateView,
    TemplateView,
)
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
import xlsxwriter

import simplejson as json
from django.views.generic.edit import FormMixin
from projectroles.constants import SODAR_CONSTANTS
from projectroles.models import RemoteSite
from projectroles.templatetags.projectroles_common_tags import site_version

from bgjobs.models import BackgroundJob
from bgjobs.views import DEFAULT_PAGINATION as BGJOBS_DEFAULT_PAGINATION
from clinvar.models import Clinvar
from cohorts.models import Cohort
from extra_annos.views import ExtraAnnosMixin, ExtraAnnoField
from frequencies.models import MT_DB_INFO
from geneinfo.views import get_gene_infos
from geneinfo.models import (
    NcbiGeneInfo,
    NcbiGeneRif,
    HpoName,
    Hpo,
    EnsemblToGeneSymbol,
    Hgnc,
    build_entrez_id_to_symbol,
)
from frequencies.views import FrequencyMixin
from projectroles.app_settings import AppSettingAPI
from projectroles.views import (
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
    PluginContextMixin,
)
from projectroles.plugins import get_backend_api, get_active_plugins

from genomicfeatures.models import GeneInterval
from varfish.users.models import User
from .queries import (
    CaseLoadPrefetchedQuery,
    ProjectLoadPrefetchedQuery,
    KnownGeneAAQuery,
    DeleteStructuralVariantsQuery,
    DeleteSmallVariantsQuery,
    SmallVariantUserAnnotationQuery,
)
from .models import (
    only_source_name,
    Case,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    CaddSubmissionBgJob,
    DistillerSubmissionBgJob,
    SpanrSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    FilterBgJob,
    Project,
    CaseAwareProject,
    SmallVariant,
    SmallVariantFlags,
    SmallVariantComment,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
    ProjectCasesFilterBgJob,
    annotate_with_phenotype_scores,
    annotate_with_pathogenicity_scores,
    annotate_with_joint_scores,
    AcmgCriteriaRating,
    SyncCaseListBgJob,
    SmallVariantSet,
    ImportVariantsBgJob,
    CaseComments,
    CASE_STATUS_CHOICES,
    RowWithAffectedCasesPerGene,
    SmallVariantSummary,
    KioskAnnotateBgJob,
    update_variant_counts,
    DeleteCaseBgJob,
    RefreshSmallVariantSummaryBgJob,
    ClearOldKioskCasesBgJob,
    ClearInactiveVariantSetsBgJob,
    ClearExpiredExportedFilesBgJob,
)
from .forms import (
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
    AcmgCriteriaRatingForm,
    CaseForm,
    SyncProjectJobForm,
    CaseNotesStatusForm,
    CaseCommentsForm,
    KioskUploadForm,
    save_file,
    CaseTermsForm,
    RE_FIND_TERMS,
)
from .sync_upstream import fetch_remote_pedigree
from .tasks import (
    export_file_task,
    export_project_cases_file_task,
    cadd_submission_task,
    distiller_submission_task,
    compute_project_variants_stats,
    sync_project_upstream,
    single_case_filter_task,
    project_cases_filter_task,
    run_kiosk_bg_job,
    delete_case_bg_job,
    spanr_submission_task,
)
from .file_export import RowWithSampleProxy
from .templatetags.variants_tags import get_term_description, smallvar_description


class UUIDEncoder(json.JSONEncoder):
    """JSON encoder for UUIds"""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # If the obj is uuid, we simply return the value of uuid
            return obj.hex
        # Default implementation raises not-serializable TypeError exception
        return json.JSONEncoder.default(self, obj)  # pragma: no cover


# Modes of inheritance in HPO: https://hpo.jax.org/app/browse/term/HP:0000005
HPO_INHERITANCE_MAPPING = {
    "HP:0000006": "AD",
    "HP:0000007": "AR",
    "HP:0001417": "X-linked",
    "HP:0001419": "XR",
    "HP:0001423": "XD",
}


class AlchemyEngineMixin:
    """Cached alchemy connection for CBVs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alchemy_engine = None

    def get_alchemy_engine(self):
        if not self._alchemy_engine:
            self._alchemy_engine = get_engine()
        return self._alchemy_engine


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
    ordering = ("-date_modified",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__sodar_uuid=self.kwargs["project"])
            .prefetch_related("project", "case_comments",)
        )

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["project"] = CaseAwareProject.objects.prefetch_related("variant_stats").get(
            pk=result["project"].pk
        )
        result["progress"] = self._compute_progress(result["project"])
        return result

    def _compute_progress(self, project):
        counts = {key: 0 for key, _ in CASE_STATUS_CHOICES}
        for case in project.case_set.all():
            counts[case.status] = counts.get(case.status, 0) + 1
        total_count = sum(counts.values())

        result = []
        statuses = [k for k, _ in CASE_STATUS_CHOICES if counts.get(k)]  # statuses with counts >0
        width_sum = 0
        if total_count:
            for i, key in enumerate(statuses):
                if i + 1 < len(statuses):
                    width = int(100 * (counts.get(key, 0) / total_count))
                    result.append((width, counts.get(key, 0), total_count, key))
                    width_sum += width
                else:
                    width = 100 - width_sum
                    result.append((width, counts.get(key, 0), total_count, key))
        else:
            result.append((100, total_count, total_count, "initial"))
        return result


class CaseListGetAnnotationsView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin, ProjectContextMixin, View,
):
    template_name = "variants/case_list/annotation.html"
    permission_required = "variants.view_data"
    model = Case
    ordering = ("-date_modified",)

    def get(self, *args, **kwargs):
        result = dict()
        result["project"] = CaseAwareProject.objects.prefetch_related(
            "case_set__small_variant_comments",
            "case_set__small_variant_flags",
            "case_set__acmg_ratings",
            "case_set__structural_variant_comments",
            "case_set__structural_variant_flags",
            "case_set__acmg_ratings",
        ).get(sodar_uuid=kwargs["project"])
        result["limit"] = 100
        result["annotation_count"] = result["project"].get_annotation_count()
        result["commentsflags"] = self.join_small_var_comments_and_flags(
            result["project"], result["limit"]
        )
        result["sv_commentsflags"] = self.join_sv_comments_and_flags(result["project"])
        return render(self.request, self.template_name, self.get_context_data(**result),)

    def join_small_var_comments_and_flags(self, project, limit):
        def get_gene_symbol(release, chromosome, start, end):
            bins = binning.containing_bins(start - 1, end)
            gene_intervals = list(
                GeneInterval.objects.filter(
                    database="ensembl",
                    release=release,
                    chromosome=chromosome,
                    bin__in=bins,
                    start__lte=end,
                    end__gte=start,
                )
            )
            gene_ids = [itv.gene_id for itv in gene_intervals]
            symbols1 = {
                o.gene_symbol
                for o in EnsemblToGeneSymbol.objects.filter(ensembl_gene_id__in=gene_ids)
            }
            symbols2 = {o.symbol for o in Hgnc.objects.filter(ensembl_gene_id__in=gene_ids)}
            return symbols1 | symbols2

        result = defaultdict(
            lambda: defaultdict(
                lambda: dict(flags=None, comments=[], genes=set(), acmg_rating=None)
            )
        )

        gene_symbol_cache = dict()

        for case in project.case_set.all():
            flags = case.small_variant_flags.all()
            comments = case.small_variant_comments.all()
            acmg_ratings = case.acmg_ratings.all()

            for record in flags:
                position_key = (record.release, record.chromosome, record.start, record.end)
                if not position_key in gene_symbol_cache:
                    gene_symbol_cache[position_key] = get_gene_symbol(*position_key)
                result[(record.chromosome, record.start, record.reference, record.alternative)][
                    case
                ]["flags"] = model_to_dict(record)
                result[(record.chromosome, record.start, record.reference, record.alternative)][
                    case
                ]["genes"] |= gene_symbol_cache[position_key]

            for record in comments:
                position_key = (record.release, record.chromosome, record.start, record.end)
                if not position_key in gene_symbol_cache:
                    gene_symbol_cache[position_key] = get_gene_symbol(*position_key)
                result[(record.chromosome, record.start, record.reference, record.alternative)][
                    case
                ]["comments"].append(
                    {
                        **model_to_dict(record),
                        "date_created": record.date_created,
                        "user": record.user,
                        "username": record.user.username,
                    }
                )
                result[(record.chromosome, record.start, record.reference, record.alternative)][
                    case
                ]["genes"] |= gene_symbol_cache[position_key]

            for record in acmg_ratings:
                position_key = (record.release, record.chromosome, record.start, record.end)
                if not position_key in gene_symbol_cache:
                    gene_symbol_cache[position_key] = get_gene_symbol(*position_key)
                result[(record.chromosome, record.start, record.reference, record.alternative)][
                    case
                ]["acmg_rating"] = {"data": record, "class": record.acmg_class}
                result[(record.chromosome, record.start, record.reference, record.alternative)][
                    case
                ]["genes"] |= gene_symbol_cache[position_key]

            if limit and len(result) > limit:
                break

        for variant, data in result.items():
            result[variant] = dict(data)
            for case in data:
                result[variant][case]["genes"] = sorted(result[variant][case]["genes"])

        return dict(result)

    def join_sv_comments_and_flags(self, project):
        result = defaultdict(lambda: defaultdict(lambda: dict(flags=None, comments=[])))

        for case in project.case_set.all():
            flags = case.structural_variant_flags.all()
            comments = case.structural_variant_comments.all()

            for record in flags:
                result[(record.chromosome, record.start, record.end, record.sv_type)][case][
                    "flags"
                ] = model_to_dict(record)

            for record in comments:
                result[(record.chromosome, record.start, record.end, record.sv_type)][case][
                    "comments"
                ].append(
                    {
                        **model_to_dict(record),
                        "date_created": record.date_created,
                        "user": record.user,
                        "username": record.user.username,
                    }
                )

        for variant, data in result.items():
            result[variant] = dict(data)

        return dict(result)


class CaseListGetQCView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin, ProjectContextMixin, View,
):
    template_name = "variants/case_list/qc.html"
    permission_required = "variants.view_data"
    model = Case
    ordering = ("-date_modified",)

    def get(self, *args, **kwargs):
        result = dict()
        result["project"] = CaseAwareProject.objects.prefetch_related("variant_stats").get(
            sodar_uuid=kwargs["project"]
        )
        result["samples"] = result["project"].get_members()
        result["effects"] = list(FILTER_FORM_TRANSLATE_EFFECTS.values())
        result["dps_keys"] = list(chain(range(0, 20), range(20, 50, 2), range(50, 200, 5), (200,)))
        result["ontarget_effect_counts"] = {sample: {} for sample in result["samples"]}
        result["indel_sizes"] = {sample: {} for sample in result["samples"]}
        result["indel_sizes_keys"] = []
        result["dps"] = {sample: {} for sample in result["samples"]}

        # Build list of properly sorted coverage keys.
        result["sample_variant_stats"] = result["project"].sample_variant_stats()
        try:
            coverages = set()
            for stats in result["sample_variant_stats"]:
                if stats.sample_name not in result["samples"]:
                    continue
                result["ontarget_effect_counts"][stats.sample_name] = stats.ontarget_effect_counts
                for key, value in stats.ontarget_indel_sizes.items():
                    result["indel_sizes"][stats.sample_name][int(key)] = value
                for key, value in stats.ontarget_dps.items():
                    result["dps"][stats.sample_name][int(key)] = value
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
            for case in (
                result["project"]
                .case_set.prefetch_related("latest_variant_set__casealignmentstats")
                .all()
            ):
                variant_set = case.latest_variant_set
                if variant_set:
                    if hasattr(variant_set, "casealignmentstats"):
                        for min_covs in variant_set.casealignmentstats.bam_stats.values():
                            if "min_cov_target" in min_covs:
                                coverages |= set(map(int, min_covs["min_cov_target"]))
            if coverages:
                filtered = filter(lambda x: x > 0, coverages)
                result["coverages"] = list(map(str, sorted(filtered)))[:5]
            result["qcdata_relatedness"] = self.get_relatedness_content(result["project"])
            result["qcdata_sample_variant_stats"] = self.get_sample_variant_stats_content(
                result["project"], result["sample_variant_stats"]
            )
        except (SmallVariantSet.variant_stats.RelatedObjectDoesNotExist, AttributeError) as e:
            pass  # swallow, defaults set above

        # Prepare effect counts data for QC download
        qcdata_effect_content = ["\t".join(["Effect"] + result["samples"])]
        for effect in result["effects"]:
            record = [effect]
            for sample in result["samples"]:
                record.append(str(result["ontarget_effect_counts"][sample].get(effect, 0)))
            qcdata_effect_content.append("\t".join(record))
        result["qcdata_effects"] = b64encode("\n".join(qcdata_effect_content).encode("utf-8"))

        # Prepare InDel size data for QC download
        qcdata_indel_size_content = ["\t".join(["InDel Size"] + result["samples"])]
        for indel_size in result["indel_sizes_keys"]:
            record = [
                ">= %d" % indel_size
                if indel_size == 10
                else "<= %d" % indel_size
                if indel_size == -10
                else str(indel_size)
            ]
            for sample in result["samples"]:
                record.append(str(result["indel_sizes"][sample].get(indel_size, 0)))
            qcdata_indel_size_content.append("\t".join(record))
        result["qcdata_indel_sizes"] = b64encode(
            "\n".join(qcdata_indel_size_content).encode("utf-8")
        )

        # Prepare depth data for QC download
        qcdata_site_depth_content = ["\t".join(["Depth"] + result["samples"])]
        for site_depth in result["dps_keys"]:
            record = [">= %d" % site_depth if site_depth == 200 else str(site_depth)]
            for sample in result["samples"]:
                record.append(str(result["dps"][sample].get(site_depth, 0)))
            qcdata_site_depth_content.append("\t".join(record))
        result["qcdata_site_depths"] = b64encode(
            "\n".join(qcdata_site_depth_content).encode("utf-8")
        )

        return render(self.request, self.template_name, self.get_context_data(**result),)

    def get_relatedness_content(self, project):
        result = [
            "\t".join(
                [
                    "Sample 1",
                    "Sample 2",
                    "Het_1,2",
                    "Het_1",
                    "Het_2",
                    "n_IBS0",
                    "n_IBS1",
                    "n_IBS2",
                    "relatedness",
                ]
            )
        ]
        for rel in project.variant_stats.relatedness.all():
            result.append(
                "\t".join(
                    [
                        rel.sample1,
                        rel.sample2,
                        str(rel.het_1_2),
                        str(rel.het_1),
                        str(rel.het_2),
                        str(rel.n_ibs0),
                        str(rel.n_ibs1),
                        str(rel.n_ibs2),
                        str(rel.relatedness()),
                    ]
                )
            )
        return b64encode("\n".join(result).encode("utf-8"))

    def get_sample_variant_stats_content(self, project, sample_variant_stats):
        result = [
            "\t".join(["Sample", "Ts", "Tv", "Ts/Tv", "SNVs", "InDels", "MNVs", "X hom./het.",])
        ]
        for item in sample_variant_stats:
            result.append(
                "\t".join(
                    [
                        item.sample_name,
                        str(item.ontarget_transitions),
                        str(item.ontarget_transversions),
                        str(item.ontarget_ts_tv_ratio()),
                        str(item.ontarget_snvs),
                        str(item.ontarget_indels),
                        str(item.ontarget_mnvs),
                        str(item.chrx_het_hom),
                    ]
                )
            )
        return b64encode("\n".join(result).encode("utf-8"))


class CaseListSyncRemoteView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Confirm creating a new upstream synchronization job."""

    permission_required = "variants.view_data"
    template_name = "variants/sync_job_create.html"
    form_class = SyncProjectJobForm

    def form_valid(self, form):
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Sync VarFish project with upstream SODAR",
                project=self.get_project(self.request, self.kwargs),
                job_type=SyncCaseListBgJob.spec_name,
                user=self.request.user,
            )
            sync_job = SyncCaseListBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs), bg_job=bg_job
            )
        sync_project_upstream.delay(sync_job_pk=sync_job.pk)
        messages.info(self.request, "Created background job to sync with upstream SODAR.")
        return redirect(sync_job.get_absolute_url())


class CaseListQcStatsApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Render JSON with project-wide case statistics"""

    template_name = "variants/case_list.html"
    permission_required = "variants.view_data"
    model = Case
    ordering = ("-date_modified",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__sodar_uuid=self.kwargs["project"])
            .prefetch_related(
                "smallvariantset_set__variant_stats",
                "smallvariantset_set__variant_stats__sample_variant_stats",
                "project",
            )
        )

    def get(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        context_data = self.get_context_data()
        project = CaseAwareProject.objects.prefetch_related("variant_stats").get(
            pk=context_data["project"].pk
        )
        try:
            rel_data = list(
                build_rel_data(
                    list(chain(*[case.pedigree for case in self.get_queryset()])),
                    project.variant_stats.relatedness.all(),
                )
            )
        except Project.variant_stats.RelatedObjectDoesNotExist:
            rel_data = []
        result = {
            "pedigree": [
                {**line, "patient": only_source_name(line["patient"])}
                for case in self.get_queryset()
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
        }

        return JsonResponse(result)


def _undecimal(the_dict):
    """Helper to replace Decimal values in a dict."""
    result = {}
    for key, value in the_dict.items():
        if isinstance(value, decimal.Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result


class CaseNotesStatusApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    FormMixin,
    View,
):
    """API view to save case notes and status."""

    permission_required = "variants.view_data"
    model = Case
    form_class = CaseNotesStatusForm
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *args, **kwargs):
        case = self.get_object()
        form = self.get_form()
        timeline = get_backend_api("timeline_backend")
        if form.is_valid():
            case.notes = form.cleaned_data["notes"]
            case.status = form.cleaned_data["status"]
            case.tags = form.cleaned_data["tags"]
            case.save()
            if timeline:
                tl_event = timeline.add_event(
                    project=self.get_project(self.request, self.kwargs),
                    app_name="variants",
                    user=self.request.user,
                    event_name="case_status_notes_submit",
                    description="submit status and note for case {{case}}: {status}, {text}".format(
                        status=case.status, text=case.shortened_notes_text()
                    ),
                    status_type="OK",
                )
                tl_event.add_object(obj=case, label="case", name=case.name)
            return JsonResponse(
                {
                    "notes": form.cleaned_data["notes"],
                    "status": form.cleaned_data["status"],
                    "tags": form.cleaned_data["tags"],
                }
            )
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="case_status_notes_submit",
                description="failed submit status and note for case {{case}}: {status}, {text}".format(
                    status=case.status, text=case.shortened_notes_text()
                ),
                status_type="FAILED",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
        return JsonResponse(dict(form.errors.items()), status=500)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        case = self.get_object()
        kwargs.update({"project": case.project})
        return kwargs


class CaseCommentsSubmitApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    FormMixin,
    View,
):
    """API view to save case comments."""

    permission_required = "variants.view_data"
    model = Case
    form_class = CaseCommentsForm
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *args, **kwargs):
        case = self.get_object()
        form = self.get_form()
        timeline = get_backend_api("timeline_backend")
        if form.is_valid():
            if self.request.POST.get("sodar_uuid"):
                kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
                if not self.request.user.is_superuser:
                    kwargs["user"] = self.request.user
                try:
                    record = CaseComments.objects.get(**kwargs)
                except ObjectDoesNotExist as e:
                    return HttpResponse(
                        json.dumps(
                            {"result": "Not authorized to update comment or no comment found."}
                        ),
                        content_type="application/json",
                        status=500,
                    )
                record.comment = form.cleaned_data["comment"]
                record.save()
                if timeline:
                    tl_event = timeline.add_event(
                        project=self.get_project(self.request, self.kwargs),
                        app_name="variants",
                        user=self.request.user,
                        event_name="case_comment_edit",
                        description="edit comment for case {case}: {text}",
                        status_type="OK",
                    )
                    tl_event.add_object(obj=case, label="case", name=case.name)
                    tl_event.add_object(obj=record, label="text", name=record.shortened_text())
            else:
                record = CaseComments(
                    case=case, user=self.request.user, comment=form.cleaned_data["comment"]
                )
                record.save()
                if timeline:
                    tl_event = timeline.add_event(
                        project=self.get_project(self.request, self.kwargs),
                        app_name="variants",
                        user=self.request.user,
                        event_name="case_comment_add",
                        description="add comment for case {case}: {text}",
                        status_type="OK",
                    )
                    tl_event.add_object(obj=case, label="case", name=case.name)
                    tl_event.add_object(obj=record, label="text", name=record.shortened_text())
            return HttpResponse(
                json.dumps(
                    {
                        "comment": record.comment,
                        "date_created": record.date_created.strftime("%Y/%m/%d %H:%M"),
                        "user": str(record.user),
                        "sodar_uuid": str(record.sodar_uuid),
                    }
                ),
                content_type="application/json",
            )


class CaseCommentsDeleteApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """API view to save case comments."""

    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *args, **kwargs):
        kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
        if not self.request.user.is_superuser:
            kwargs["user"] = self.request.user

        try:
            comment = CaseComments.objects.get(**kwargs)
        except ObjectDoesNotExist as e:
            return HttpResponse(
                json.dumps({"result": "Not authorized to delete comment or no comment found."}),
                content_type="application/json",
                status=500,
            )

        comment.delete()
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="case_comment_delete",
                description="delete comment for case {case}",
                status_type="OK",
            )
            tl_event.add_object(obj=self.get_object(), label="case", name=self.get_object().name)
        return HttpResponse(json.dumps({"result": "OK"}), content_type="application/json")


class CaseCommentsCountApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """API view to save case comments."""

    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        return JsonResponse({"count": self.get_object().case_comments.count()})


def get_annotations_by_variant(case=None, cases=None, project=None):
    """Helper function to get all annotations by case and variant.

    The result is a dict.  First level of keys is case SODAR UUID, second is variant description, then
    "variants", "flags", "comments", "acmg_rating".
    """
    annotated_small_vars = SmallVariantUserAnnotationQuery(get_engine()).run(
        case=case, cases=cases, project=project
    )

    case_ids = list(sorted({x.case_id for x in annotated_small_vars.small_variants}))
    case_id_to_uuid = {}
    for case in Case.objects.filter(id__in=case_ids).order_by("name"):
        case_id_to_uuid[case.id] = case.sodar_uuid

    result = {}

    # Ensure that at least one entry is there if exactly one case is to be queried for.
    if case:
        result.setdefault(case.sodar_uuid, {})

    def init_var(description):
        result[case_uuid].setdefault(
            description, {"variants": [], "flags": None, "comments": [], "acmg_rating": None,},
        )

    for small_var in annotated_small_vars.small_variants:
        case_uuid = case_id_to_uuid[small_var.case_id]
        result.setdefault(case_uuid, {})
        init_var(small_var.get_description())
        result[case_uuid][small_var.get_description()]["variants"].append(small_var)
    for flags in annotated_small_vars.small_variant_flags:
        case_uuid = case_id_to_uuid[flags.case_id]
        init_var(flags.get_variant_description())
        result[case_uuid][flags.get_variant_description()]["flags"] = flags
    for comments in annotated_small_vars.small_variant_comments:
        case_uuid = case_id_to_uuid[comments.case_id]
        init_var(comments.get_variant_description())
        result[case_uuid][comments.get_variant_description()]["comments"].append(comments)
    for rating in annotated_small_vars.acmg_criteria_rating:
        case_uuid = case_id_to_uuid[rating.case_id]
        init_var(rating.get_variant_description())
        result[case_uuid][rating.get_variant_description()]["acmg_rating"] = rating
    return result


class CaseDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,  # XXX
    FormMixin,
    DetailView,
):
    """Display a case in detail."""

    template_name = "variants/case_detail.html"
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    form_class = CaseNotesStatusForm

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        case = result["object"]
        result["samples"] = case.get_members_with_samples()
        result["effects"] = list(FILTER_FORM_TRANSLATE_EFFECTS.values())
        result["dps_keys"] = list(chain(range(0, 20), range(20, 50, 2), range(50, 200, 5), (200,)))
        result["ontarget_effect_counts"] = {sample: {} for sample in result["samples"]}
        result["indel_sizes"] = {sample: {} for sample in result["samples"]}
        result["indel_sizes_keys"] = []
        result["dps"] = {sample: {} for sample in result["samples"]}
        result["casecommentsform"] = CaseCommentsForm()
        result["commentsflags"] = self.join_small_var_comments_and_flags()
        result["gene_id_to_symbol"] = build_entrez_id_to_symbol(
            [
                v.refseq_gene_id
                for entry in result["commentsflags"].values()
                for v in entry["variants"]
            ]
        )
        result["sv_commentsflags"] = self.join_sv_comments_and_flags()
        result["acmg_summary"] = {
            "count": case.acmg_ratings.count(),
            **{
                str(i): len(
                    [rating for rating in case.acmg_ratings.all() if rating.acmg_class == i]
                )
                for i in range(1, 6)
            },
        }
        result["flag_summary"] = {
            "count": case.small_variant_flags.count(),
            **{
                key: len(
                    [
                        flag
                        for flag in case.small_variant_flags.all()
                        if getattr(flag, "flag_%s" % key, None)
                    ]
                )
                for key in ("final_causative", "candidate")
            },
        }
        result["user"] = self.request.user

        try:
            variant_set = case.latest_variant_set
            import_job = ImportVariantsBgJob.objects.filter(case_name=case.name).order_by(
                "-date_created"
            )
            if import_job and not import_job[0].bg_job.status == "done":
                return result
            if variant_set:
                result["ontarget_effect_counts"] = {
                    stats.sample_name: stats.ontarget_effect_counts
                    for stats in variant_set.variant_stats.sample_variant_stats.all()
                }
                result["indel_sizes"] = {
                    stats.sample_name: {
                        int(key): value for key, value in stats.ontarget_indel_sizes.items()
                    }
                    for stats in variant_set.variant_stats.sample_variant_stats.all()
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
                    stats.sample_name: {
                        int(key): value for key, value in stats.ontarget_dps.items()
                    }
                    for stats in variant_set.variant_stats.sample_variant_stats.all()
                }
                # Build list of properly sorted coverage keys.
                coverages = set()
                if hasattr(variant_set, "casealignmentstats"):
                    for min_covs in variant_set.casealignmentstats.bam_stats.values():
                        if "min_cov_target" in min_covs:
                            coverages |= set(map(int, min_covs["min_cov_target"]))
                if coverages:
                    filtered = filter(lambda x: x > 0, coverages)
                    result["coverages"] = list(map(str, sorted(filtered)))[:10]
                result["qcdata_relatedness"] = self.get_relatedness_content()
                result["qcdata_sample_variant_stats"] = self.get_sample_variant_stats_content()
        except (SmallVariantSet.variant_stats.RelatedObjectDoesNotExist, AttributeError):
            pass  # swallow, defaults set above

        # Prepare effect counts data for QC download
        qcdata_effect_content = ["\t".join(["Effect"] + case.get_members_with_samples())]
        for effect in result["effects"]:
            record = [effect]
            for sample in case.get_members_with_samples():
                record.append(str(result["ontarget_effect_counts"][sample].get(effect, 0)))
            qcdata_effect_content.append("\t".join(record))
        result["qcdata_effects"] = b64encode("\n".join(qcdata_effect_content).encode("utf-8"))

        # Prepare InDel size data for QC download
        qcdata_indel_size_content = ["\t".join(["InDel Size"] + case.get_members_with_samples())]
        for indel_size in result["indel_sizes_keys"]:
            record = [
                ">= %d" % indel_size
                if indel_size == 10
                else "<= %d" % indel_size
                if indel_size == -10
                else str(indel_size)
            ]
            for sample in case.get_members_with_samples():
                record.append(str(result["indel_sizes"][sample].get(indel_size, 0)))
            qcdata_indel_size_content.append("\t".join(record))
        result["qcdata_indel_sizes"] = b64encode(
            "\n".join(qcdata_indel_size_content).encode("utf-8")
        )

        # Prepare depth data for QC download
        qcdata_site_depth_content = ["\t".join(["Depth"] + case.get_members_with_samples())]
        for site_depth in result["dps_keys"]:
            record = [">= %d" % site_depth if site_depth == 200 else str(site_depth)]
            for sample in case.get_members_with_samples():
                record.append(str(result["dps"][sample].get(site_depth, 0)))
            qcdata_site_depth_content.append("\t".join(record))
        result["qcdata_site_depths"] = b64encode(
            "\n".join(qcdata_site_depth_content).encode("utf-8")
        )

        return result

    def get_initial(self):
        """Returns the initial data for the form."""
        initial = super().get_initial()
        case = self.get_object()
        initial.update({"notes": case.notes, "status": case.status, "tags": case.tags})
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        case = self.get_object()
        kwargs.update({"project": case.project})
        return kwargs

    def get_relatedness_content(self):
        case = self.get_object()
        result = [
            "\t".join(
                [
                    "Sample 1",
                    "Sample 2",
                    "Het_1,2",
                    "Het_1",
                    "Het_2",
                    "n_IBS0",
                    "n_IBS1",
                    "n_IBS2",
                    "relatedness",
                ]
            )
        ]
        for rel in case.latest_variant_set.variant_stats.relatedness.all():
            result.append(
                "\t".join(
                    [
                        rel.sample1,
                        rel.sample2,
                        str(rel.het_1_2),
                        str(rel.het_1),
                        str(rel.het_2),
                        str(rel.n_ibs0),
                        str(rel.n_ibs1),
                        str(rel.n_ibs2),
                        str(rel.relatedness()),
                    ]
                )
            )
        return b64encode("\n".join(result).encode("utf-8"))

    def get_sample_variant_stats_content(self):
        case = self.get_object()
        result = [
            "\t".join(["Sample", "Ts", "Tv", "Ts/Tv", "SNVs", "InDels", "MNVs", "X hom./het.",])
        ]
        for item in case.latest_variant_set.variant_stats.sample_variant_stats.all():
            result.append(
                "\t".join(
                    [
                        item.sample_name,
                        str(item.ontarget_transitions),
                        str(item.ontarget_transversions),
                        str(item.ontarget_ts_tv_ratio()),
                        str(item.ontarget_snvs),
                        str(item.ontarget_indels),
                        str(item.ontarget_mnvs),
                        str(item.chrx_het_hom),
                    ]
                )
            )
        return b64encode("\n".join(result).encode("utf-8"))

    def get_effect_content(self):
        case = self.get_object()
        members = case.get_members_with_samples()
        result = ["\t".join(members)]
        {sample: {} for sample in result["samples"]}
        for item in case.latest_variant_set.variant_stats.sample_variant_stats.all():
            result.append(
                "\t".join(
                    [
                        item.sample_name,
                        str(item.ontarget_transitions),
                        str(item.ontarget_transversions),
                        str(item.ontarget_ts_tv_ratio()),
                        str(item.ontarget_snvs),
                        str(item.ontarget_indels),
                        str(item.ontarget_mnvs),
                        str(item.chrx_het_hom),
                    ]
                )
            )
        return b64encode("\n".join(result).encode("utf-8"))

    def join_small_var_comments_and_flags(self):
        case = self.get_object()
        return get_annotations_by_variant(case=case)[case.sodar_uuid]

    def join_sv_comments_and_flags(self):
        case = self.get_object()
        flags = case.structural_variant_flags.all()
        comments = case.structural_variant_comments.all()
        result = defaultdict(lambda: dict(flags=None, comments=[]))

        for record in flags:
            result[(record.chromosome, record.start, record.end, record.sv_type)][
                "flags"
            ] = model_to_dict(record)

        for record in comments:
            result[(record.chromosome, record.start, record.end, record.sv_type)][
                "comments"
            ].append(
                {
                    **model_to_dict(record),
                    "date_created": record.get_date_created(),
                    "user": record.user,
                    "username": record.user.username,
                }
            )

        return dict(result)


class CaseUpdateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Display a case in detail."""

    template_name = "variants/case_update.html"
    permission_required = "variants.update_case"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    form_class = CaseForm


class CaseUpdateTermView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Update phenotype and disease annotation of individuals within a case."""

    permission_required = "variants.update_case"
    template_name = "variants/case_update_terms.html"
    form_class = CaseTermsForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_object = None

    def get_context_data(self, **kwargs):
        """Put the ``Case`` object into the context."""
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        context["terms_queries"] = self._get_query_terms()
        return context

    def _get_query_terms(self):
        """Return list of terms that were used in all queries."""
        terms = set()
        for query in SmallVariantQuery.objects.filter(case=self.get_case_object()):
            terms |= set(query.query_settings.get("prio_hpo_terms", []) or [])
        return list(sorted(terms))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["case"] = self.get_case_object()
        return kwargs

    def form_valid(self, form):
        terms = {}
        prefix = "terms-"
        for key, value in form.cleaned_data.items():
            if key.startswith(prefix):
                lst = []
                for term in re.findall(RE_FIND_TERMS, value):
                    if term not in lst:
                        lst.append(term)
                terms[key[len(prefix) :]] = lst
        self.get_case_object().update_terms(terms)
        messages.success(self.request, "The case terms were successfully updated.")
        return redirect(self.get_case_object().get_absolute_url())

    def get_case_object(self):
        # TODO: move to mixin to reduce code duplication?
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object


class CaseFetchUpstreamTermsView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Load HPO and disease terms from upstream SODAR project for the "load from SODAR" button on the case update
    terms view.
    """

    permission_required = "variants.update_case"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        def term(term_id):
            return {"id": term_id, "description": get_term_description(term_id)}

        sources = [
            s for s in RemoteSite.objects.all() if s.mode == SODAR_CONSTANTS["SITE_MODE_SOURCE"]
        ]
        if len(sources) != 1:
            raise RuntimeError(
                "Expected exactly one remote source site but there were %d" % len(sources)
            )
        case = self.get_object()
        upstream_pedigree = fetch_remote_pedigree(sources[0], case.project)
        result = {}
        for name in case.get_members():
            name = name.split("-", 1)[0]
            if name in upstream_pedigree:
                upstream = upstream_pedigree[name]
                result[name] = {
                    "name": name,
                    "hpo_terms": list(map(term, upstream.hpo_terms)),
                    "orphanet_diseases": list(map(term, upstream.orphanet_diseases)),
                    "omim_diseases": list(map(term, upstream.omim_diseases)),
                }
            else:
                result[name] = {"error": "individual not found upstream"}
        return JsonResponse(result)


class CaseFixSexView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Fix sex errors in a pedigree."""

    permission_required = "variants.update_case"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        case = self.get_object()
        sex_errors = case.sex_errors_to_fix()
        if not sex_errors:
            return redirect(
                "variants:case-detail", project=case.project.sodar_uuid, case=case.sodar_uuid
            )
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="case_fix_sex",
                description="fix sex in pedigree of case {case}",
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
        for sample, sex in sex_errors.items():
            for member in case.pedigree:
                if member["patient"] == sample:
                    member["sex"] = sex
        case.save()
        messages.success(self.request, "Fixed sex in pedigree to match molecular signature.")
        return redirect(
            "variants:case-detail", project=case.project.sodar_uuid, case=case.sodar_uuid
        )


class ProjectCasesFixSexView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin, ProjectContextMixin, View
):
    """Fix sex errors in pedigree in cases of a project."""

    permission_required = "variants.update_case"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        # get current CaseAwareProject
        project = CaseAwareProject.objects.get(pk=self.get_project(self.request, self.kwargs).pk)

        timeline = get_backend_api("timeline_backend")
        if timeline:
            timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="case_fix_sex",
                description="fix sex in project cases",
                status_type="OK",
            )
        fixed_cases = []
        for case in project.get_active_smallvariant_cases():
            sex_errors = case.sex_errors_to_fix()
            if not sex_errors:
                continue
            timeline = get_backend_api("timeline_backend")
            if timeline:
                tl_event = timeline.add_event(
                    project=self.get_project(self.request, self.kwargs),
                    app_name="variants",
                    user=self.request.user,
                    event_name="case_fix_sex",
                    description="fix sex in pedigree of case {case}",
                    status_type="OK",
                )
                tl_event.add_object(obj=case, label="case", name=case.name)
            for sample, sex in sex_errors.items():
                for member in case.pedigree:
                    if member["patient"] == sample:
                        member["sex"] = sex
            case.save()
            fixed_cases.append(case.name)
        if fixed_cases:
            messages.success(
                self.request,
                "Fixed sex in pedigree to match molecular signature for case(s) {}".format(
                    ", ".join(fixed_cases)
                ),
            )
        return redirect("variants:case-list", project=project.sodar_uuid)


class CaseDeleteView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Delete case."""

    permission_required = "variants.delete_case"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        case = self.get_object()
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Delete case",
                project=self.get_project(self.request, self.kwargs),
                job_type=DeleteCaseBgJob.spec_name,
                user=self.request.user,
            )
            delete_job = DeleteCaseBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs), bg_job=bg_job, case=case,
            )
            # Construct background job objects
            bg_job2 = BackgroundJob.objects.create(
                name="Recreate variant statistic for whole project",
                project=self.get_project(self.request, self.kwargs),
                job_type=ComputeProjectVariantsStatsBgJob.spec_name,
                user=self.request.user,
            )
            recreate_job = ComputeProjectVariantsStatsBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs), bg_job=bg_job2
            )
            delete_case_bg_job.delay(
                delete_case_bg_job_pk=delete_job.pk, export_job_pk=recreate_job.pk
            )
            return redirect(delete_job.get_absolute_url())


#: Header for for table when downloading annotation data.
ANNOTATION_DOWNLOAD_HEADER = [
    "case",
    "genome_release",
    "chromosome",
    "position",
    "reference",
    "alternative",
    "refseq_genes",
    "refseq_transcripts",
    "refseq_hgvs",
    "refseq_effects",
    "acmg_rating",
    "flag_bookmarked",
    "flag_candidate",
    "flag_final_causative",
    "flag_for_validation",
    "flag_no_disease_association",
    "flag_segregates",
    "flag_doesnt_segregate",
    "flag_visual",
    "flag_molecular",
    "flag_validation",
    "flag_phenotype_match",
    "flag_summary",
    "comments",
]


class BaseDownloadAnnotationsView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Download case user annotations as Excel file."""

    permission_required = "variants.view_data"
    slug_field = "sodar_uuid"

    def get_impl(self, case=None, cases=None, project=None):
        with tempfile.NamedTemporaryFile("w+b") as f:
            # Write output to temporary file.
            if self.request.GET.get("format", "tsv") == "xlsx":
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                file_ext = "xlsx"
                self.write_xlsx(case=case, cases=cases, project=project, output_f=f)
            else:
                content_type = "text/tsv"
                file_ext = "tsv"
                self.write_tsv(case=case, cases=cases, project=project, output_f=f)
            # Build HTTP response.
            f.flush()
            f.seek(0)
            if case:
                identifier = case.name
            elif cases:
                identifier = "-".join(cases[:5].name)
            else:
                identifier = project.title.replace(" ", "-")
            response = HttpResponse(f.read(), content_type=content_type,)
            response["Content-Disposition"] = "attachment; filename=case-annotations-%s.%s" % (
                identifier,
                file_ext,
            )
            return response

    def write_xlsx(self, *, case, cases, project, output_f):
        """Write output XLSX file."""
        workbook = xlsxwriter.Workbook(output_f.name, {"remove_timezone": True})
        header_format = workbook.add_format({"bold": True})
        sheet = workbook.add_worksheet("Small Variants")
        for rowno, row in enumerate(self.yield_rows(case=case, cases=cases, project=project)):
            if rowno == 0:
                sheet.write_row(0, 0, row, header_format)
            else:
                sheet.write_row(rowno, 0, row)
        workbook.close()

    def write_tsv(self, *, case, cases, project, output_f):
        """Write output TSV file."""
        for row in self.yield_rows(case=case, cases=cases, project=project):
            output_f.write(("\t".join(map(str, row)) + "\n").encode())

    def yield_rows(self, *, case, cases, project):
        yield ANNOTATION_DOWNLOAD_HEADER

        res = get_annotations_by_variant(case=case, cases=cases, project=project)
        case_uuid_to_name = {
            c.sodar_uuid: c.name for c in Case.objects.filter(sodar_uuid__in=res.keys())
        }

        for case_uuid, annos in res.items():
            for anno in annos.values():
                comments = [
                    "%s @%s: %s"
                    % (
                        comment.user.username,
                        comment.date_modified.strftime("%Y-%m-%d %H:%M"),
                        comment.text.replace("\t", " ").replace("\n", " "),
                    )
                    for comment in anno["comments"]
                ]

                gene_id_to_symbol = build_entrez_id_to_symbol(
                    [x.refseq_gene_id for x in anno["variants"]]
                )
                genes = ", ".join(
                    gene_id_to_symbol[x.refseq_gene_id]
                    for x in anno["variants"]
                    if x.refseq_gene_id
                )
                transcripts = ", ".join(
                    x.refseq_transcript_id for x in anno["variants"] if x.refseq_gene_id
                )
                hgvs = ", ".join(
                    x.refseq_hgvs_p or x.refseq_hgvs_c
                    for x in anno["variants"]
                    if x.refseq_gene_id and (x.refseq_hgvs_p or x.refseq_hgvs_c)
                )
                effects = ", ".join(
                    "&".join(x.refseq_effect)
                    for x in anno["variants"]
                    if x.refseq_gene_id and x.refseq_effect
                )

                coord_candidates = anno["variants"] + anno["comments"]
                if anno["acmg_rating"]:
                    coord_candidates += [anno["acmg_rating"]]
                if anno["flags"]:
                    coord_candidates += [anno["flags"]]
                coord = coord_candidates[0]

                if not anno["flags"]:
                    row_flags = ["N/A"] * 12
                else:
                    row_flags = [
                        anno["flags"].flag_bookmarked,
                        anno["flags"].flag_candidate,
                        anno["flags"].flag_final_causative,
                        anno["flags"].flag_for_validation,
                        anno["flags"].flag_no_disease_association,
                        anno["flags"].flag_segregates,
                        anno["flags"].flag_doesnt_segregate,
                        anno["flags"].flag_visual,
                        anno["flags"].flag_molecular,
                        anno["flags"].flag_validation,
                        anno["flags"].flag_phenotype_match,
                        anno["flags"].flag_summary,
                    ]
                row = (
                    [
                        case_uuid_to_name[case_uuid],
                        coord.release,
                        coord.chromosome,
                        coord.start,
                        coord.reference,
                        coord.alternative,
                        genes,
                        transcripts,
                        hgvs,
                        effects,
                        anno["acmg_rating"].acmg_class if anno["acmg_rating"] else "N/A",
                    ]
                    + row_flags
                    + ["|".join(comments),]
                )
                yield row


class CaseDownloadAnnotationsView(BaseDownloadAnnotationsView):
    """Download case user annotations as Excel file."""

    model = Case
    slug_url_kwarg = "case"

    def get(self, *args, **kwargs):
        return self.get_impl(case=self.get_object())


class ProjectDownloadAnnotationsView(BaseDownloadAnnotationsView):
    """Download project user annotations as Excel file."""

    model = Project
    slug_url_kwarg = "project"

    def get(self, *args, **kwargs):
        return self.get_impl(project=self.get_object())


class SmallVariantsDeleteView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Delete case."""

    permission_required = "variants.delete_case"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        case = self.get_object()
        case_uuid = case.sodar_uuid
        case_name = case.name
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="smallvariant_delete",
                description="delete small variants from {case}",
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
        for query in DeleteSmallVariantsQuery(get_engine()).run(case_id=case.id):
            with contextlib.closing(query):
                pass
        update_variant_counts(case)
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
        messages.success(self.request, "Deleted small variants in case {}.".format(case_name))
        return redirect("variants:case-detail", project=case.project.sodar_uuid, case=case_uuid)


class StructuralVariantsDeleteView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Delete case."""

    permission_required = "variants.delete_case"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        case = self.get_object()
        case_uuid = case.sodar_uuid
        case_name = case.name
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="structuralvariant_delete",
                description="delete structural variants from {case}",
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
        for query in DeleteStructuralVariantsQuery(get_engine()).run(case_id=case.id):
            with contextlib.closing(query):
                pass
        update_variant_counts(case)
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
        messages.success(self.request, "Deleted structural variants in case {}.".format(case_name))
        return redirect("variants:case-detail", project=case.project.sodar_uuid, case=case_uuid)


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


class CaseDetailQcStatsApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Render JSON with the data required for the single-case QC statistics."""

    # template_name = "variants/case_detail.html"
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        object = self.get_object()
        import_job = ImportVariantsBgJob.objects.filter(case_name=object.name).order_by(
            "-date_created"
        )
        result = {
            "pedigree": [
                {**line, "patient": only_source_name(line["patient"])} for line in object.pedigree
            ]
        }

        if import_job and not import_job[0].bg_job.status == "done":
            result.update(
                {
                    "relData": [],
                    "sexErrors": {},
                    "chrXHetHomRatio": {},
                    "dps": {},
                    "dpQuantiles": [0, 25, 50, 100],
                    "hetRatioQuantiles": [0, 25, 50, 100],
                    "dpHetData": [],
                    "variantTypeData": [],
                    "variantEffectData": [],
                    "indelSizeData": [],
                }
            )
            return JsonResponse(result)

        relatedness_set = []
        try:
            variant_set = object.latest_variant_set
            if variant_set:
                relatedness_set = variant_set.variant_stats.relatedness.all()
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow

        result.update(
            {
                "relData": list(build_rel_data(object.pedigree, relatedness_set)),
                **build_sex_data(object),
                **build_cov_data([object]),
                "variantTypeData": list(self._build_var_type_data(object)),
                "variantEffectData": list(self._build_var_effect_data(object)),
                "indelSizeData": list(self._build_indel_size_data(object)),
            }
        )
        return JsonResponse(result)

    def _build_var_type_data(self, object):
        variant_set = object.latest_variant_set
        if not variant_set:
            return
        try:
            for item in variant_set.variant_stats.sample_variant_stats.all():
                yield {
                    "name": only_source_name(item.sample_name),
                    "hovermode": "closest",
                    "showlegend": "false",
                    "x": ["SNVs", "InDels", "MNVs"],
                    "y": [item.ontarget_snvs, item.ontarget_indels, item.ontarget_mnvs],
                }
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow

    def _build_var_effect_data(self, object):
        variant_set = object.latest_variant_set
        if not variant_set:
            return
        keys = (
            "synonymous_variant",
            "missense_variant",
            "5_prime_UTR_exon_variant",
            "3_prime_UTR_exon_variant",
            "splice_donor_variant",
            "splice_region_variant",
            "splice_acceptor_variant",
            "start_lost",
            "stop_gained",
            "stop_lost",
            "inframe_deletion",
            "inframe_insertion",
            "frameshift_variant",
            "frameshift_truncation",
            "frameshift_elongation",
        )
        try:
            for stats in variant_set.variant_stats.sample_variant_stats.all():
                yield {
                    "name": only_source_name(stats.sample_name),
                    "x": keys,
                    "y": list(map(stats.ontarget_effect_counts.get, keys)),
                }
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow

    def _build_indel_size_data(self, object):
        variant_set = object.latest_variant_set
        if not variant_set:
            return
        try:
            indel_sizes = {
                stats.sample_name: {
                    int(key): value for key, value in stats.ontarget_indel_sizes.items()
                }
                for stats in variant_set.variant_stats.sample_variant_stats.all()
            }
            indel_sizes_keys = list(
                sorted(
                    set(
                        chain(
                            *list(
                                map(int, indel_sizes.keys()) for indel_sizes in indel_sizes.values()
                            )
                        )
                    )
                )
            )
            for line in object.get_filtered_pedigree_with_samples():
                if line.get("has_gt_entries"):
                    yield {
                        "name": only_source_name(line["patient"]),
                        "x": [
                            (
                                "\u2264-10"
                                if key == -10
                                else ("\u226510" if key == 10 else "" + str(key))
                            )
                            for key in indel_sizes_keys
                        ],
                        "y": [indel_sizes[line["patient"]].get(key, 0) for key in indel_sizes_keys],
                    }
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow


class CaseFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
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
        self._alchemy_engine = None
        self._previous_query = None

    def get_previous_query(self):
        if not self._previous_query:
            if "job" in self.kwargs:
                self._previous_query = FilterBgJob.objects.get(
                    sodar_uuid=self.kwargs["job"]
                ).smallvariantquery
            else:
                self._previous_query = (
                    self.get_case_object()
                    .small_variant_queries.filter(user=self.request.user)
                    .order_by("-date_created")
                    .first()
                )
        return self._previous_query

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["case"] = self.get_case_object()
        result["user"] = self.request.user
        return result

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        if form.cleaned_data["submit"] == "download":
            return self._form_valid_file(form)
        elif form.cleaned_data["submit"] == "submit-mutationdistiller":
            return self._form_valid_mutation_distiller(form)
        elif form.cleaned_data["submit"] == "submit-cadd":
            return self._form_valid_cadd(form)
        elif form.cleaned_data["submit"] == "submit-spanr":
            return self._form_valid_spanr(form)

    def form_invalid(self, form):
        return render(
            self.request,
            self.template_name,
            self.get_context_data(form=form, form_errors=form.errors.as_json),
        )

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

    def _form_valid_cadd(self, form):
        """The form is valid, we are supposed to submit to CADD."""
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Submitting case {} to CADD".format(self.get_case_object().name),
                project=self.get_project(self.request, self.kwargs),
                job_type=CaddSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            cadd_release = "%s-%s" % (
                self.get_case_object().release,
                settings.VARFISH_CADD_SUBMISSION_VERSION,
            )
            submission_job = CaddSubmissionBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=_undecimal(form.cleaned_data),
                cadd_version=cadd_release,
            )
        cadd_submission_task.delay(submission_job_pk=submission_job.pk)
        messages.info(
            self.request,
            "Created background job for your CADD submission. "
            "You can find the link to the CADD result on this site.",
        )
        return redirect(submission_job.get_absolute_url())

    def _form_valid_spanr(self, form):
        """The form is valid, we are supposed to submit to SPANR."""
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Submitting case {} to SPANR".format(self.get_case_object().name),
                project=self.get_project(self.request, self.kwargs),
                job_type=SpanrSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = SpanrSubmissionBgJob.objects.create(
                project=self.get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=_undecimal(form.cleaned_data),
            )
        spanr_submission_task.delay(submission_job_pk=submission_job.pk)
        messages.info(
            self.request,
            "Created background job for your SPANR submission. "
            "You can find the link to the SPANR result on this site.",
        )
        return redirect(submission_job.get_absolute_url())

    def get_initial(self):
        """Put initial data in the form from the previous query if any and push information into template for the
        "welcome back" message."""
        result = self.initial.copy()
        if self.request.method == "GET" and self.get_previous_query():
            # TODO: the code for version conversion needs to be hooked in here
            messages.info(
                self.request,
                ("Welcome back! We have restored your previous query settings from {}.").format(
                    naturaltime(self.get_previous_query().date_created)
                ),
            )
            for key, value in self.get_previous_query().query_settings.items():
                if key == "genomic_region":
                    result[key] = "\n".join(
                        "{}:{:,}-{:,}".format(chrom, start, end)
                        if start is not None and end is not None
                        else chrom
                        for chrom, start, end in value
                    )
                elif key == "prio_hpo_terms":
                    result[key] = "; ".join(value or [])
                elif isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        """Put the ``Case`` object into the context."""
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        context["num_small_vars"] = context["object"].num_small_vars
        context["variant_set_exists"] = (
            context["object"].smallvariantset_set.filter(state="active").exists()
        )
        context["allow_md_submission"] = True
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
        context["settings_restored"] = 1 if self.get_previous_query() else 0
        return context


class CasePrefetchFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
    View,
):
    """View for starting a background filter job.

    This view initiates a background filter job and returns its id as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "case"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        # get case object
        case_object = Case.objects.get(sodar_uuid=kwargs["case"])

        # clean data first
        form = FilterForm(self.request.POST, case=case_object, user=self.request.user)

        if form.is_valid():
            # form is valid, we are supposed to render an HTML table with the results
            with transaction.atomic():
                # Save query parameters
                small_variant_query = SmallVariantQuery.objects.create(
                    case=case_object,
                    user=self.request.user,
                    form_id=form.form_id,
                    form_version=form.form_version,
                    query_settings=_undecimal(form.cleaned_data),
                )
                # Construct background job objects
                bg_job = BackgroundJob.objects.create(
                    name="Running filter query for case {}".format(case_object.name),
                    project=self.get_project(self.request, kwargs),
                    job_type=FilterBgJob.spec_name,
                    user=self.request.user,
                )
                filter_job = FilterBgJob.objects.create(
                    project=self.get_project(self.request, kwargs),
                    bg_job=bg_job,
                    case=case_object,
                    smallvariantquery=small_variant_query,
                )

            # Submit job
            single_case_filter_task.delay(filter_job_pk=filter_job.pk)
            return JsonResponse({"filter_job_uuid": filter_job.sodar_uuid})
        return JsonResponse(form.errors, status=400)


class FilterJobGetStatus(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
    View,
):
    """View for getting a filter job status.

    This view queries the current status of a filter job and returns it as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        try:
            filter_job = FilterBgJob.objects.select_related("bg_job").get(
                sodar_uuid=self.request.GET.get("filter_job_uuid")
            )
            log_entries = reversed(filter_job.bg_job.log_entries.all().order_by("-date_created"))
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
                {
                    "error": "No filter job with UUID {}".format(
                        self.request.GET.get("filter_job_uuid")
                    )
                },
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(self.request.GET.get("filter_job_uuid"))},
                status=400,
            )


class FilterJobGetPrevious(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
    View,
):
    """View for getting the ID of the previous filter job.

    This view returns the previous filter job ID (if available) as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):
        filter_job = (
            FilterBgJob.objects.filter(
                smallvariantquery__user=self.request.user, case__sodar_uuid=kwargs["case"]
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
    AlchemyEngineMixin,
    TemplateView,
):
    """View for displaying filter results.

    This view fetches previous query results and renders them in a table.
    """

    template_name = "variants/filter_result/table.html"
    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "case"

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""
        result = super().get_context_data()

        # TODO: properly test prioritization
        # TODO: refactor, cleanup, break apart
        # Fetch filter job to display.
        filter_job = FilterBgJob.objects.get(sodar_uuid=self.request.GET["filter_job_uuid"])
        variant_set = filter_job.case.latest_variant_set
        if not variant_set:
            return HttpResponse(
                json.dumps(
                    {
                        "msg": (
                            "Displaying previous filter results failed: no variant set found. "
                            "Possibly the variants and/or the variant set was deleted since the last filtering. "
                            "This is an inconsistent state, please report to the administrators."
                        )
                    }
                ),
                content_type="application/json",
                status=500,
            )

        # Compute number of columns in table for the cards.
        pedigree = filter_job.case.get_filtered_pedigree_with_samples()
        card_colspan = 13 + len(pedigree)

        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = CaseLoadPrefetchedQuery(
            filter_job.smallvariantquery.case, get_engine(), filter_job.smallvariantquery.id
        )
        with contextlib.closing(query.run(filter_job.smallvariantquery.query_settings)) as results:
            num_results = results.rowcount
            # Get first N rows. This will pop the first N rows! results list will be decreased by N.
            rows = list(
                results.fetchmany(
                    filter_job.smallvariantquery.query_settings.get("result_rows_limit", 200)
                )
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

        # Annotate with pathogenicity score if any. MutationTaster can have multiple predictions per variant (for each transcript).
        variant_scores = {}
        for entry in filter_job.smallvariantquery.smallvariantqueryvariantscores_set.all():
            key = entry.variant_key()
            score = variant_scores.get(key)
            if score:
                if entry.score > score[0]:
                    variant_scores[key] = (entry.score, entry.info)
            else:
                variant_scores[key] = (entry.score, entry.info)

        if variant_scores:
            card_colspan += 2
            rows = annotate_with_pathogenicity_scores(rows, variant_scores)

        # Annotate with joint scores if any.
        if gene_scores and variant_scores:
            card_colspan += 2
            rows = annotate_with_joint_scores(rows)

        # Get mapping from HPO term to HpoName object.
        hpoterms = {}
        for hpo in filter_job.smallvariantquery.query_settings.get("prio_hpo_terms", []) or []:
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

        extra_annos_header = [field.label for field in list(ExtraAnnoField.objects.all())]

        genomebuild = "GRCh37"
        if rows:
            genomebuild = rows[0]["release"]

        result.update(
            {
                "genomebuild": genomebuild,
                "user": self.request.user,
                "case": filter_job.smallvariantquery.case,
                "result_rows": rows,
                "result_extra_annos_header": extra_annos_header,
                "result_count": num_results,
                "elapsed_seconds": elapsed.total_seconds(),
                "database": filter_job.smallvariantquery.query_settings.get(
                    "database_select", "refseq"
                ),
                "pedigree": pedigree,
                "hpoterms": hpoterms,
                "compound_recessive_index": filter_job.smallvariantquery.query_settings.get(
                    "compound_recessive_index", ""
                ),
                "prio_enabled": filter_job.smallvariantquery.query_settings.get(
                    "prio_enabled", False
                ),
                "gene_allowlist": filter_job.smallvariantquery.query_settings.get(
                    "gene_allowlist", []
                ),
                "gene_blocklist": filter_job.smallvariantquery.query_settings.get(
                    "gene_blocklist", []
                ),
                "genomic_region": filter_job.smallvariantquery.query_settings.get(
                    "genomic_region", []
                ),
                "training_mode": 1
                if filter_job.smallvariantquery.query_settings.get("training_mode", False)
                else 0,
                "query_type": self.query_type,
                "has_phenotype_scores": bool(gene_scores),
                "has_pathogenicity_scores": bool(variant_scores),
                "patho_enabled": filter_job.smallvariantquery.query_settings.get(
                    "patho_enabled", False
                ),
                "patho_score": filter_job.smallvariantquery.query_settings.get(
                    "patho_score", False
                ),
                "exac_enabled": filter_job.smallvariantquery.query_settings.get(
                    "exac_enabled", False
                ),
                "thousand_genomes_enabled": filter_job.smallvariantquery.query_settings.get(
                    "thousand_genomes_enabled", False
                ),
                "gnomad_genomes_enabled": filter_job.smallvariantquery.query_settings.get(
                    "gnomad_genomes_enabled", False
                ),
                "gnomad_exomes_enabled": filter_job.smallvariantquery.query_settings.get(
                    "gnomad_exomes_enabled", False
                ),
                "inhouse_enabled": filter_job.smallvariantquery.query_settings.get(
                    "inhouse_enabled", False
                ),
                "card_colspan": card_colspan,
                "logs": [
                    "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                    for e in filter_job.bg_job.log_entries.all().order_by("date_created")
                ],
            },
        )

        return result


class ProjectCasesLoadPrefetchedFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
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

    def get(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        filter_job = ProjectCasesFilterBgJob.objects.get(
            sodar_uuid=self.request.GET["filter_job_uuid"]
        )

        # Take time while job is running
        before = timezone.now()
        cohort = getattr(filter_job, "cohort")
        # Get and run query
        query = ProjectLoadPrefetchedQuery(
            cohort or filter_job.projectcasessmallvariantquery.project,
            get_engine(),
            filter_job.projectcasessmallvariantquery.id,
            user=self.request.user,
        )

        # get all rows and then inflate them with all member per case and then cut them down. we can't know the length
        # of the results beforehand. it looks inefficient, but a quick try showed that it isn't much slower.
        with contextlib.closing(
            query.run(filter_job.projectcasessmallvariantquery.query_settings)
        ) as results:
            _rows = results.fetchall()
            missed_records = filter_job.projectcasessmallvariantquery.query_results.count() - len(
                _rows
            )
            rows = []
            cases_per_gene = defaultdict(set)
            for row in _rows:
                # Collect cases per gene
                cases_per_gene[row.gene_id].add(row.case_uuid)
                for sample in sorted(row.genotype.keys()):
                    row = RowWithSampleProxy(row, sample)
                    row = RowWithAffectedCasesPerGene(row)
                    rows.append(row)
            # Assign cases per gene count after collecting the cases per gene
            for row in rows:
                row._self_affected_cases_per_gene = len(cases_per_gene[row.gene_id])
            elapsed = timezone.now() - before

        # Annotate with pathogenicity score if any. MutationTaster can have multiple predictions per variant (for each transcript).
        variant_scores = {}
        for (
            entry
        ) in (
            filter_job.projectcasessmallvariantquery.projectcasessmallvariantqueryvariantscores_set.all()
        ):
            key = entry.variant_key()
            score = variant_scores.get(key)
            if score:
                if entry.score > score[0]:
                    variant_scores[key] = (entry.score, entry.info)
            else:
                variant_scores[key] = (entry.score, entry.info)

        card_colspan = 17
        if variant_scores:
            card_colspan += 2
            rows = annotate_with_pathogenicity_scores(rows, variant_scores)

        return render(
            self.request,
            self.template_name,
            self.get_context_data(
                result_rows=rows[
                    : filter_job.projectcasessmallvariantquery.query_settings.get(
                        "result_rows_limit", 200
                    )
                ],
                result_count=len(rows),
                elapsed_seconds=elapsed.total_seconds(),
                cohort=cohort,
                missed_records=missed_records,
                training_mode=1
                if filter_job.projectcasessmallvariantquery.query_settings.get(
                    "training_mode", False
                )
                else 0,
                exac_enabled=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "exac_enabled", False
                ),
                thousand_genomes_enabled=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "thousand_genomes_enabled", False
                ),
                gnomad_genomes_enabled=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "gnomad_genomes_enabled", False
                ),
                gnomad_exomes_enabled=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "gnomad_exomes_enabled", False
                ),
                inhouse_enabled=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "inhouse_enabled", False
                ),
                database=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "database_select", False
                ),
                query_type=self.query_type,
                has_pathogenicity_scores=bool(variant_scores),
                patho_enabled=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "patho_enabled", False
                ),
                patho_score=filter_job.projectcasessmallvariantquery.query_settings.get(
                    "patho_score", False
                ),
                card_colspan=card_colspan,
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
    AlchemyEngineMixin,
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
        self._alchemy_engine = None
        self._previous_query = None
        self._cohort = None

    def get_cohort(self):
        if not self._cohort:
            cohort = self.kwargs.get("cohort")
            self._cohort = Cohort.objects.get(sodar_uuid=cohort) if cohort else None
        return self._cohort

    def get_previous_query(self):
        if not self._previous_query:
            project = self.get_project(self.request, self.kwargs)
            cohort = self.get_cohort()
            user = self.request.user
            if "job" in self.kwargs:
                filter_job = ProjectCasesFilterBgJob.objects.get(sodar_uuid=self.kwargs["job"])
            else:
                # When cohort is None, this will return last "default" projectcases query.
                # Otherwise it will return last cohort query for this user.
                filter_job = (
                    ProjectCasesFilterBgJob.objects.filter(
                        project=project, bg_job__user=self.request.user, cohort=cohort
                    )
                    .order_by("-bg_job__date_created")
                    .first()
                )
            if filter_job:
                self._previous_query = filter_job.projectcasessmallvariantquery
        return self._previous_query

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["project"] = self.get_project(self.request, self.kwargs)
        result["user"] = self.request.user
        result["cohort"] = self.get_cohort()
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
                cohort=self.get_cohort(),
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
        if self.request.method == "GET" and self.get_previous_query():
            # TODO: the code for version conversion needs to be hooked in here
            messages.info(
                self.request,
                ("Welcome back! We have restored your previous query settings from {}.").format(
                    naturaltime(self.get_previous_query().date_created)
                ),
            )
            for key, value in self.get_previous_query().query_settings.items():
                if key == "genomic_region":
                    result[key] = "\n".join(
                        "{}:{:,}-{:,}".format(chrom, start, end)
                        if start is not None and end is not None
                        else chrom
                        for chrom, start, end in value
                    )
                elif isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cohort"] = self.get_cohort()
        if context["cohort"]:
            context["case_count"] = context["cohort"].cases.count()
        else:
            context["case_count"] = context["project"].case_set.count()
        context["num_small_vars"] = context["project"].num_small_vars()
        context["variant_set_exists"] = (
            context["project"].case_set.filter(smallvariantset__state="active").exists()
        )
        context["submit_button_url"] = reverse(
            "variants:project-cases-filter-results",
            kwargs={"project": context["project"].sodar_uuid},
        )
        context["load_data_url"] = reverse(
            "variants:project-cases-load-filter-results",
            kwargs={"project": context["project"].sodar_uuid},
        )
        if context["cohort"]:
            context["request_previous_job_url"] = reverse(
                "variants:project-cases-filter-job-previous-cohort",
                kwargs={
                    "project": context["project"].sodar_uuid,
                    "cohort": context["cohort"].sodar_uuid,
                },
            )
        else:
            context["request_previous_job_url"] = reverse(
                "variants:project-cases-filter-job-previous",
                kwargs={"project": context["project"].sodar_uuid},
            )
        context["job_status_url"] = reverse(
            "variants:project-cases-filter-job-status",
            kwargs={"project": context["project"].sodar_uuid},
        )
        context["query_type"] = self.query_type
        context["settings_restored"] = 1 if self.get_previous_query() else 0
        return context


class ProjectCasesPrefetchFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
    View,
):
    """View for starting a background joint filter job.

    This view initiates a background joint filter job and returns its id as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    query_type = "project"

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        # get current CaseAwareProject
        project = CaseAwareProject.objects.get(pk=self.get_project(self.request, self.kwargs).pk)

        cohort = self.request.POST.get("cohort")
        if cohort:
            cohort = Cohort.objects.get(sodar_uuid=cohort)

        # clean data first
        form = ProjectCasesFilterForm(
            self.request.POST, project=project, user=self.request.user, cohort=cohort
        )

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
                    user=self.request.user,
                )
                data = {
                    "project": project,
                    "bg_job": bg_job,
                    "projectcasessmallvariantquery": small_variant_query,
                }
                if cohort:
                    data["cohort"] = cohort
                filter_job = ProjectCasesFilterBgJob.objects.create(**data)

            # Submit job
            project_cases_filter_task.delay(project_cases_filter_job_pk=filter_job.pk)
            return JsonResponse({"filter_job_uuid": filter_job.sodar_uuid})
        return JsonResponse(form.errors, status=400)


class ProjectCasesFilterJobGetStatus(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
    View,
):
    """View for getting a joint filter job status.

    This view queries the current status of a joint filter job and returns it as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        try:
            filter_job = ProjectCasesFilterBgJob.objects.select_related("bg_job").get(
                sodar_uuid=self.request.GET["filter_job_uuid"]
            )
            log_entries = reversed(filter_job.bg_job.log_entries.all().order_by("-date_created"))
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
                {"error": "No filter job with UUID {}".format(self.request.GET["filter_job_uuid"])},
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(self.request.GET["filter_job_uuid"])},
                status=400,
            )


class ProjectCasesFilterJobGetPrevious(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    AlchemyEngineMixin,
    View,
):
    """View for getting the ID of the previous joint filter job.

    This view returns the previous joint filter job ID (if available) as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        project = self.get_project(self.request, self.kwargs)
        cohort_uuid = self.kwargs.get("cohort")
        cohort = Cohort.objects.get(sodar_uuid=cohort_uuid) if cohort_uuid else None
        if settings.KIOSK_MODE:
            user = User.get_kiosk_user()
        filter_job = (
            ProjectCasesFilterBgJob.objects.filter(
                project=project, bg_job__user=self.request.user, cohort=cohort
            )
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
        if ref.replace(" ", "_") == significance:
            return i
    return len(FILTER_FORM_TRANSLATE_SIGNIFICANCE.values())


class SmallVariantDetails(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FrequencyMixin,
    ExtraAnnosMixin,
    AlchemyEngineMixin,
    DetailView,
):
    """Render details card of small variants.

    Most of this information comes directly from our database but some is also loaded from web services.  If these
    web services are not configured, this information is not loaded or displayed.
    """

    permission_required = "variants.view_data"
    template_name = "variants/variant_details.html"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get_queryset(self):
        cohort = self.kwargs.get("cohort")
        if cohort:
            return Cohort.objects.get(sodar_uuid=cohort).get_accessible_cases_for_user(
                self.request.user
            )
        return super().get_queryset()

    def _load_knowngene_aa(self, query_kwargs):
        """Load the UCSC knownGeneAA conservation alignment information."""
        query = KnownGeneAAQuery(self.get_alchemy_engine())
        result = []
        with contextlib.closing(query.run(query_kwargs)) as _result:
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

    def _load_clinvar(self, query_kwargs):
        """Load clinvar information"""
        filter_args = {
            "release": query_kwargs["release"],
            "chromosome": query_kwargs["chromosome"],
            "start": int(query_kwargs["start"]),
            "end": int(query_kwargs["end"]),
            "reference": query_kwargs["reference"],
            "alternative": query_kwargs["alternative"],
        }
        records = Clinvar.objects.filter(**filter_args)
        if records:
            return records.first()
        else:
            return None

    def _load_small_var(self, kwargs):
        return SmallVariant.objects.filter(
            case_id=self.object.pk,
            release=kwargs["release"],
            chromosome=kwargs["chromosome"],
            start=kwargs["start"],
            end=kwargs["end"],
            reference=kwargs["reference"],
            alternative=kwargs["alternative"],
        ).first()

    def _load_molecular_impact(self, kwargs):
        """Load molecular impact from Jannovar REST API if configured."""
        if not settings.VARFISH_ENABLE_JANNOVAR:
            return []

        url_tpl = (
            "%(base_url)sannotate-var/%(database)s/%(genome)s/%(chromosome)s/%(position)s/%(reference)s/"
            "%(alternative)s"
        )
        genome = {"GRCh37": "hg19", "GRCh38": "hg38"}.get(kwargs["release"], "hg19")
        url = url_tpl % {
            "base_url": settings.VARFISH_JANNOVAR_REST_API_URL,
            "database": kwargs["database"],
            "genome": genome,
            "chromosome": kwargs["chromosome"],
            "position": kwargs["start"],
            "reference": kwargs["reference"],
            "alternative": kwargs["alternative"],
        }
        try:
            res = requests.request(method="get", url=url)
            if not res.status_code == 200:
                raise ConnectionError(
                    "ERROR: Server responded with status {} and message {}".format(
                        res.status_code, res.text
                    )
                )
            else:
                return res.json()
        except requests.ConnectionError as e:
            raise ConnectionError(
                "ERROR: Server at {} not responding.".format(settings.VARFISH_JANNOVAR_REST_API_URL)
            ) from e

    def _get_population_freqs(self, kwargs):
        if kwargs.get("chromosome") == "MT":
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
        frequencies = self.get_frequencies(kwargs)
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
            release=kwargs["release"],
            chromosome=kwargs["chromosome"],
            start=int(kwargs["start"]),
            end=int(kwargs["end"]),
            reference=kwargs["reference"],
            alternative=kwargs["alternative"],
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

    def _get_mitochondrial_freqs(self, kwargs):
        if not kwargs.get("chromosome") == "MT":
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
                {kwargs.get("reference"): {"ac": 0, "af": 0.0, "ac_het": 0, "ac_hom": 0}}
                if len(kwargs.get("reference")) > 1
                else {}
            )
            alts = db.objects.filter(
                release=kwargs["release"],
                chromosome=kwargs["chromosome"],
                start=int(kwargs["start"]),
                end=int(kwargs["end"]),
                reference=kwargs["reference"],
            )
            if alts:
                an = alts[0].an
                ref_count = an
                for alt in alts:
                    if dbname == "HelixMTdb" and kwargs["alternative"] == alt.alternative:
                        result["is_triallelic"] = alt.is_triallelic
                    if dbname == "mtDB" and kwargs["alternative"] == alt.alternative:
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
                assert singles[kwargs.get("reference")]["ac"] == 0
                assert singles[kwargs.get("reference")]["ac_het"] == 0
                assert singles[kwargs.get("reference")]["ac_hom"] == 0
                assert singles[kwargs.get("reference")]["af"] == 0.0
                if len(kwargs.get("reference")) == 1:
                    if dbname == "HelixMTdb":
                        singles[kwargs.get("reference")]["ac_hom"] = ref_count
                        singles[kwargs.get("reference")]["ac_het"] = 0
                    else:
                        singles[kwargs.get("reference")]["ac"] = ref_count
                    singles[kwargs.get("reference")]["af"] = ref_count / an
                else:
                    if dbname == "HelixMTdb":
                        multis[kwargs.get("reference")]["ac_hom"] = ref_count
                        multis[kwargs.get("reference")]["ac_het"] = 0
                    else:
                        multis[kwargs.get("reference")]["ac"] = ref_count
                    multis[kwargs.get("reference")]["af"] = ref_count / an
            result["vars"][dbname].update(singles)
            result["vars"][dbname].update(multis)
            result["an"][dbname] = an
        # Make sure indels are sorted
        for dbname, data in result["vars"].items():
            result["vars"][dbname] = sorted(
                data.items(), key=lambda x: (("0" if len(x[0]) == 1 else "1") + x[0], x[1])
            )
        return result

    def _load_variant_comments(self):
        return SmallVariantComment.objects.select_related("user").filter(
            case=self.object,
            release=self.kwargs["release"],
            chromosome=self.kwargs["chromosome"],
            start=int(self.kwargs["start"]),
            end=int(self.kwargs["end"]),
            reference=self.kwargs["reference"],
            alternative=self.kwargs["alternative"],
        )

    def _load_variant_flags(self):
        return SmallVariantFlags.objects.filter(
            case=self.object,
            release=self.kwargs["release"],
            chromosome=self.kwargs["chromosome"],
            start=int(self.kwargs["start"]),
            end=int(self.kwargs["end"]),
            reference=self.kwargs["reference"],
            alternative=self.kwargs["alternative"],
        ).first()

    def get_context_data(self, object):
        result = super().get_context_data(*self.args, **self.kwargs)
        result["database"] = self.kwargs["database"]
        result["clinvar"] = self._load_clinvar(self.kwargs)
        result["knowngeneaa"] = self._load_knowngene_aa(self.kwargs)
        result["small_var"] = self._load_small_var(self.kwargs)
        result["effect_details"] = self._load_molecular_impact(self.kwargs)
        result["extra_annos"] = self.get_extra_annos(self.kwargs)
        if self.request.GET.get("render_full", "no").lower() in ("yes", "true"):
            result["base_template"] = "projectroles/base.html"
        else:
            result["base_template"] = "empty_base.html"
        result.update(self._get_population_freqs(self.kwargs))
        result["mitochondrial_freqs"] = self._get_mitochondrial_freqs(self.kwargs)
        result["gene"] = get_gene_infos(
            self.kwargs["database"], self.kwargs["gene_id"], self.kwargs["ensembl_transcript_id"]
        )
        entrez_id = result["small_var"].refseq_gene_id
        result["ncbi_summary"] = NcbiGeneInfo.objects.filter(entrez_id=entrez_id).first()
        result["ncbi_gene_rifs"] = NcbiGeneRif.objects.filter(entrez_id=entrez_id).order_by("pk")
        result["comments"] = self._load_variant_comments()
        result["flags"] = self._load_variant_flags()
        result["training_mode"] = int(self.kwargs["training_mode"])
        result["user"] = self.request.user
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


class SyncJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the sync-project-upstream background job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/sync_job_detail.html"
    model = SyncCaseListBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class ImportVariantsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the import case background job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/import_job_detail.html"
    model = ImportVariantsBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class CaseDeleteJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the import case background job.
    """

    permission_required = "variants.view_data"
    template_name = "variants/case_delete_job_detail.html"
    model = DeleteCaseBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            return super().get(*args, **kwargs)
        # Object is not available when case was deleted successfully
        except Exception:
            messages.info(self.request, "Case deleted successfully.")
            return redirect(
                reverse("variants:case-list", kwargs={"project": self.get_project().sodar_uuid})
            )


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

    def get(self, *args, **kwargs):
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
                cohort=job.cohort,
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

    def get(self, *args, **kwargs):
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


class CaddSubmissionJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the CADD submission background job."""

    permission_required = "variants.view_data"
    template_name = "variants/cadd_job_detail.html"
    model = CaddSubmissionBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = EmptyForm()
        return result


class CaddSubmissionJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit to CADD."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(CaddSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to CADD".format(job.case),
                project=job.bg_job.project,
                job_type=CaddSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = CaddSubmissionBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, query_args=job.query_args
            )
            cadd_submission_task.delay(submission_job_pk=submission_job.pk)
        return redirect(submission_job.get_absolute_url())


class SpanrSubmissionJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the SPANR submission background job."""

    permission_required = "variants.view_data"
    template_name = "variants/spanr_job_detail.html"
    model = SpanrSubmissionBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = EmptyForm()
        return result


class SpanrSubmissionJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit to SPANR."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(SpanrSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to SPANR".format(job.case),
                project=job.bg_job.project,
                job_type=SpanrSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = SpanrSubmissionBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, query_args=job.query_args
            )
            spanr_submission_task.delay(submission_job_pk=submission_job.pk)
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
            single_case_filter_task.delay(filter_job_pk=filter_job.pk)
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
            start=self.request.GET.get("start"),
            end=self.request.GET.get("end"),
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
                start=self.request.POST.get("start"),
                end=self.request.POST.get("end"),
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


class SmallVariantCommentSubmitApiView(
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
        timeline = get_backend_api("timeline_backend")
        if self.request.POST.get("sodar_uuid"):
            kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
            if not self.request.user.is_superuser:
                kwargs["user"] = self.request.user
            try:
                comment = SmallVariantComment.objects.get(**kwargs)
            except ObjectDoesNotExist as e:
                return HttpResponse(
                    json.dumps({"result": "Not authorized to delete comment or no comment found."}),
                    content_type="application/json",
                    status=500,
                )
            comment.text = self.request.POST.get("variant_comment")
            comment.save()
            if timeline:
                tl_event = timeline.add_event(
                    project=self.get_project(self.request, self.kwargs),
                    app_name="variants",
                    user=self.request.user,
                    event_name="variant_comment_edit",
                    description="edit comment for variant %s in case {case}: {text}"
                    % comment.get_variant_description(),
                    status_type="OK",
                )
                tl_event.add_object(obj=case, label="case", name=case.name)
                tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())
        else:
            comment = SmallVariantComment(
                case=case, user=self.request.user, sodar_uuid=uuid.uuid4()
            )
            form = SmallVariantCommentForm(self.request.POST, instance=comment)
            comment = form.save()
            if timeline:
                tl_event = timeline.add_event(
                    project=self.get_project(self.request, self.kwargs),
                    app_name="variants",
                    user=self.request.user,
                    event_name="variant_comment_add",
                    description="add comment for variant %s in case {case}: {text}"
                    % comment.get_variant_description(),
                    status_type="OK",
                )
                tl_event.add_object(obj=case, label="case", name=case.name)
                tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())
        return HttpResponse(json.dumps({"comment": comment.text}), content_type="application/json")


class MultiSmallVariantFlagsAndCommentApiView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin, ProjectContextMixin, View,
):
    """A view that returns JSON for the ``SmallVariantFlags`` for a variant of a case and allows updates."""

    # TODO: create new permission
    permission_required = "variants.view_data"

    def get(self, *_args, **_kwargs):
        get_data = dict(self.request.GET)
        variant_list = json.loads(get_data.get("variant_list")[0])
        flags_keys = [
            "flag_bookmarked",
            "flag_candidate",
            "flag_final_causative",
            "flag_for_validation",
            "flag_no_disease_association",
            "flag_segregates",
            "flag_doesnt_segregate",
            "flag_visual",
            "flag_molecular",
            "flag_validation",
            "flag_phenotype_match",
            "flag_summary",
        ]
        flags = {i: None for i in flags_keys}
        flags_interfering = set()

        for variant in reversed(variant_list):
            case = get_object_or_404(Case, sodar_uuid=variant.get("case"))

            try:
                flag_data = model_to_dict(
                    case.small_variant_flags.get(
                        release=variant.get("release"),
                        chromosome=variant.get("chromosome"),
                        start=variant.get("start"),
                        end=variant.get("end"),
                        reference=variant.get("reference"),
                        alternative=variant.get("alternative"),
                    )
                )

                for flag in flags_keys:
                    if flags[flag] is None:
                        flags[flag] = flag_data[flag]

                    if not flags[flag] == flag_data[flag]:
                        flags_interfering.add(flag)

                    flags[flag] = flag_data[flag]

            except SmallVariantFlags.DoesNotExist:
                continue

        results = {
            "flags": flags,
            "flags_interfering": sorted(flags_interfering),
            "variant_list": variant_list,
        }

        return JsonResponse(results, UUIDEncoder)

    def post(self, *_args, **_kwargs):
        timeline = get_backend_api("timeline_backend")
        post_data = dict(self.request.POST)
        variant_list = json.loads(post_data.pop("variant_list")[0])
        post_data.pop("csrfmiddlewaretoken")
        post_data_clean = {k: v[0] for k, v in post_data.items()}
        text = post_data_clean.pop("text")
        comment_response = {
            "text": text,
            "user": self.request.user.username,
            "dates_created": {},
            "uuids": {},
        }

        for variant in variant_list:
            case = get_object_or_404(Case, sodar_uuid=variant.get("case"))
            variant_obj = SmallVariant.objects.get(
                release=variant.get("release"),
                chromosome=variant.get("chromosome"),
                start=variant.get("start"),
                end=variant.get("end"),
                reference=variant.get("reference"),
                alternative=variant.get("alternative"),
                case_id=case.id,
            )

            try:
                flags = case.small_variant_flags.get(
                    release=variant.get("release"),
                    chromosome=variant.get("chromosome"),
                    start=variant.get("start"),
                    end=variant.get("end"),
                    reference=variant.get("reference"),
                    alternative=variant.get("alternative"),
                )

            except SmallVariantFlags.DoesNotExist:
                flags = SmallVariantFlags(case=case)

            form = SmallVariantFlagsForm({**variant, **post_data_clean}, instance=flags)

            try:
                flags = form.save()

            except ValueError as e:
                raise Exception(str(form.errors)) from e

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

            if text:
                comment = SmallVariantComment(
                    case=case, user=self.request.user, sodar_uuid=uuid.uuid4()
                )
                form = SmallVariantCommentForm({**variant, "text": text}, instance=comment)

                try:
                    comment = form.save()

                except ValueError as e:
                    raise Exception(str(form.errors)) from e

                description = "{}-{}".format(
                    str(case.sodar_uuid), smallvar_description(variant_obj)
                )
                comment_response["dates_created"][description] = comment.get_date_created()
                comment_response["uuids"][description] = str(comment.sodar_uuid)

                if timeline:
                    tl_event = timeline.add_event(
                        project=self.get_project(self.request, self.kwargs),
                        app_name="variants",
                        user=self.request.user,
                        event_name="variant_comment_add",
                        description="add comment for variant %s in case {case}: {text}"
                        % comment.get_variant_description(),
                        status_type="OK",
                    )
                    tl_event.add_object(obj=case, label="case", name=case.name)
                    tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())

        return JsonResponse(
            {"message": "OK", "flags": post_data_clean, "comment": comment_response}
        )


class SmallVariantCommentDeleteApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """A view that allows to delete a comment."""

    # TODO: create new permission
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *_args, **_kwargs):
        case = self.get_object()
        kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
        if not self.request.user.is_superuser:
            kwargs["user"] = self.request.user

        try:
            comment = SmallVariantComment.objects.get(**kwargs)
        except ObjectDoesNotExist as e:
            return HttpResponse(
                json.dumps({"result": "Not authorized to delete comment or no comment found."}),
                content_type="application/json",
                status=500,
            )

        comment.delete()
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=self.request.user,
                event_name="variant_comment_delete",
                description="delete comment for variant %s in case {case}"
                % comment.get_variant_description(),
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)

        return HttpResponse(json.dumps({"result": "OK"}), content_type="application/json")


class AcmgCriteriaRatingApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """A view that returns JSON for the ``AcmgCriteriaRating`` for a variant of a case and allows updates."""

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
        acmg_ratings = get_object_or_404(
            case.acmg_ratings,
            release=self.request.GET.get("release"),
            chromosome=self.request.GET.get("chromosome"),
            start=self.request.GET.get("start"),
            end=self.request.GET.get("end"),
            reference=self.request.GET.get("reference"),
            alternative=self.request.GET.get("alternative"),
        )
        return HttpResponse(
            json.dumps(self._model_to_dict(acmg_ratings), cls=UUIDEncoder),
            content_type="application/json",
        )

    def post(self, *_args, **_kwargs):
        case = self.get_object()
        try:
            acmg_ratings = case.acmg_ratings.get(
                release=self.request.POST.get("release"),
                chromosome=self.request.POST.get("chromosome"),
                start=self.request.POST.get("start"),
                end=self.request.POST.get("end"),
                reference=self.request.POST.get("reference"),
                alternative=self.request.POST.get("alternative"),
            )
        except AcmgCriteriaRating.DoesNotExist:
            acmg_ratings = AcmgCriteriaRating(
                case=case, sodar_uuid=uuid.uuid4(), user=self.request.user
            )
        form = AcmgCriteriaRatingForm(self.request.POST, instance=acmg_ratings)
        if form.is_valid():
            if not form.cleaned_data["empty"]:
                try:
                    acmg_ratings = form.save()
                    timeline = get_backend_api("timeline_backend")
                    if timeline:
                        tl_event = timeline.add_event(
                            project=self.get_project(self.request, self.kwargs),
                            app_name="variants",
                            user=self.request.user,
                            event_name="flags_set",
                            description="set ACMG rating for variant %s in case {case}: {extra-rating_values}"
                            % acmg_ratings.get_variant_description(),
                            status_type="OK",
                            extra_data={"rating_values": acmg_ratings.get_human_readable()},
                        )
                        tl_event.add_object(obj=case, label="case", name=case.name)
                except ValueError as e:
                    raise Exception(str(form.errors)) from e
                result = self._model_to_dict(acmg_ratings)
            elif form.cleaned_data["empty"] and acmg_ratings.id:
                try:
                    acmg_ratings.delete()
                    timeline = get_backend_api("timeline_backend")
                    if timeline:
                        tl_event = timeline.add_event(
                            project=self.get_project(self.request, self.kwargs),
                            app_name="variants",
                            user=self.request.user,
                            event_name="flags_set",
                            description="delete ACMG rating for variant %s in case {case}"
                            % acmg_ratings.get_variant_description(),
                            status_type="OK",
                        )
                        tl_event.add_object(obj=case, label="case", name=case.name)
                except ValueError as e:
                    raise Exception(str(form.errors)) from e
                result = {}
            else:
                result = {}
            return HttpResponse(
                json.dumps(result, cls=UUIDEncoder), content_type="application/json"
            )


class NewFeaturesView(LoginRequiredMixin, RedirectView):
    """Store "latest seen changelog version" for user and redirect."""

    url = "/manual/history.html"

    def get(self, *args, **kwargs):
        setting_api = AppSettingAPI()
        setting_api.set_app_setting(
            "variants", "latest_version_seen_changelog", site_version(), user=self.request.user
        )
        return super().get(*args, **kwargs)


class HpoTermsApiView(LoginRequiredMixin, View):
    def get(self, *_args, **_kwargs):
        query = self.request.GET.get("query")
        if not query:
            return HttpResponse({}, content_type="application/json")
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

        return HttpResponse(json.dumps(result), content_type="application/json")


class VariantValidatorApiView(PluginContextMixin, View):
    template_name = "variants/filter_result/variant_validator_result.html"

    def post(self, *args, **kwargs):
        response = requests.get(
            "https://rest.variantvalidator.org/VariantValidator/variantvalidator/{release}/{chromosome}-{position}-{reference}-{alternative}/all?content-type=application%2Fjson".format(
                release=self.request.POST.get("release"),
                chromosome=self.request.POST.get("chromosome"),
                position=self.request.POST.get("position"),
                reference=self.request.POST.get("reference"),
                alternative=self.request.POST.get("alternative"),
            ),
        )
        if response.status_code != 200:
            return HttpResponse("<em><strong>No data available!</strong></em>")
        result = defaultdict(lambda: defaultdict(dict))
        for key, value in response.json().items():
            m = re.match(
                r"^(NM_\d+|intergenic_variant|validation_warning)(?:\.|_)(\d+)(?::(.*))?", key
            )
            if m:
                # identifier -> version -> change
                result[str(m.group(1))][int(m.group(2))][str(m.group(3) or "")] = value

        # Convert defaultdicts to dicts as django templates can't digest defaultdicts.
        for key, value in result.items():
            for key2, value2 in value.items():
                value[key2] = dict(value2)
            result[key] = dict(value)

        return render(
            self.request,
            self.template_name,
            self.get_context_data(user=self.request.user, response=dict(result),),
        )


class KioskHomeView(PluginContextMixin, FormView):
    """Home view when the app is running in kiosk mode.

    When this mode is activated
    """

    template_name = "variants/kiosk_home.html"
    form_class = KioskUploadForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["app_plugins"] = get_active_plugins(plugin_type="project_app")
        context["backend_plugins"] = get_active_plugins(plugin_type="backend")

        return context

    def form_valid(self, form):
        with transaction.atomic():
            tmp_dir = tempfile.mkdtemp(prefix="varfish_kiosk_", dir=settings.MEDIA_ROOT)
            path_vcf = save_file(
                form.cleaned_data.get("vcf_file"), form.cleaned_data.get("vcf_file").name, tmp_dir
            )
            case_index = form.cleaned_data["vcf_index"]
            project = self.get_kiosk_project()
            path_ped = save_file(form.cleaned_data.get("ped"), case_index + ".ped", tmp_dir)
            bg_job = BackgroundJob.objects.create(
                name="Kiosk mode annotation",
                project=project,
                job_type=KioskAnnotateBgJob.spec_name,
                user=self.request.user,
            )
            annotate_job = KioskAnnotateBgJob.objects.create(
                project=project,
                bg_job=bg_job,
                path_vcf=path_vcf,
                path_gts=os.path.join(tmp_dir, case_index + ".tsv.gz"),
                path_db_info=os.path.join(tmp_dir, case_index + ".db_info.gz"),
                path_tmp_dir=tmp_dir,
            )
            bg_job2 = BackgroundJob.objects.create(
                name="Kiosk mode import",
                project=project,
                job_type=ImportVariantsBgJob.spec_name,
                user=self.request.user,
            )
            import_job = ImportVariantsBgJob.objects.create(
                bg_job=bg_job2,
                project=project,
                case_name=case_index,
                index_name=case_index,
                path_ped=path_ped,
                path_genotypes=[annotate_job.path_gts],
                path_db_info=[annotate_job.path_db_info],
            )
            # This job kicks of two jobs in sync (eg one after the other).
            run_kiosk_bg_job.s(
                kiosk_annotate_bg_job_pk=annotate_job.pk, import_variants_bg_job_pk=import_job.pk
            ).apply_async(countdown=2)
            # TODO: Manuel needs to configure a jailing script that throws out user trying to guess case UUIDs.
            return redirect(
                reverse(
                    "variants:kiosk-status",
                    kwargs={
                        "project": project.sodar_uuid,
                        "annotate_job": annotate_job.sodar_uuid,
                        "import_job": import_job.sodar_uuid,
                    },
                )
            )

    def get_kiosk_project(self):
        """Return Project object for the Kiosk cases (or create it)."""
        cat, _ = Project.objects.get_or_create(
            parent=None, type="CATEGORY", title=settings.KIOSK_CAT,
        )
        proj = Project.objects.create(
            parent=cat,
            type="PROJECT",
            title="%s-%s" % (settings.KIOSK_PROJ_PREFIX, str(uuid.uuid4())),
        )
        return proj


class KioskStatusView(ProjectContextMixin, View):
    """Status view when the app is running in kiosk mode.

    When this mode is activated
    """

    template_name = "variants/kiosk_status.html"

    def get(self, *args, **kwargs):
        return render(
            self.request,
            self.template_name,
            self.get_context_data(
                annotate_job_uuid=kwargs.get("annotate_job"),
                import_job_uuid=kwargs.get("import_job"),
                full_url=self.request.build_absolute_uri(),
            ),
        )


class KioskJobGetStatus(PluginContextMixin, View):
    """View for getting a filter job status.

    This view queries the current status of a filter job and returns it as JSON.
    """

    def get(self, *args, **kwargs):
        try:
            annotate_job = KioskAnnotateBgJob.objects.get(sodar_uuid=kwargs.get("annotate_job"))
        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "No annotate job with UUID {}".format(kwargs.get("annotate_job"))},
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No GET UUID {} for annotate job".format(kwargs.get("annotate_job"))},
                status=400,
            )

        try:
            import_job = ImportVariantsBgJob.objects.get(sodar_uuid=kwargs.get("import_job"))
        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "No import job with UUID {}".format(kwargs.get("import_job_uuid"))},
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {} for import job".format(kwargs.get("import_job_uuid"))},
                status=400,
            )

        log_entries = list(annotate_job.bg_job.log_entries.all().order_by("date_created")) + list(
            import_job.bg_job.log_entries.all().order_by("date_created")
        )

        case_uuid = None
        status = 200
        if annotate_job.bg_job.status == "done" and import_job.bg_job.status == "done":
            try:
                case = Case.objects.get(project=import_job.project, name=import_job.case_name)
                case_uuid = case.sodar_uuid
            except ObjectDoesNotExist as e:
                log_entries.append(e)
                status = 500
            messages.info(
                self.request,
                (
                    "Case upload and annotation complete. Bookmark the following web address "
                    "to retrieve it in the future: %s"
                )
                % self.request.build_absolute_uri(case.get_absolute_url()),
            )

        return JsonResponse(
            {
                "annotate_status": annotate_job.bg_job.status,
                "import_status": import_job.bg_job.status,
                "messages": [
                    "[{}] {}".format(e.date_created.strftime("%Y-%m-%d %H:%M:%S"), e.message)
                    for e in log_entries
                ],
                "case_uuid": case_uuid,
            },
            status=status,
        )


class ClearExpiredExportedFilesJobDetailView(
    LoggedInPermissionMixin, DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = ClearExpiredExportedFilesBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)


class ClearInactiveVariantSetsJobDetailView(
    LoggedInPermissionMixin, DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = ClearInactiveVariantSetsBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)


class ClearOldKioskCasesJobDetailView(
    LoggedInPermissionMixin, DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = ClearOldKioskCasesBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)


class RefreshSmallVariantSummaryJobDetailView(
    LoggedInPermissionMixin, DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = RefreshSmallVariantSummaryBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)
