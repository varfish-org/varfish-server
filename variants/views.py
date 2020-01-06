import os
import tempfile
from itertools import chain
from collections import defaultdict
import uuid
import contextlib

import decimal
import numpy as np
import requests
import vcfpy
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404, JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, View, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin

import simplejson as json
from django.views.generic.edit import FormMixin
from projectroles.templatetags.projectroles_common_tags import site_version

from bgjobs.models import BackgroundJob
from clinvar.models import Clinvar
from geneinfo.views import get_gene_infos
from geneinfo.models import NcbiGeneInfo, NcbiGeneRif, HpoName
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

from varfish.users.models import User
from .queries import (
    CaseLoadPrefetchedQuery,
    ProjectLoadPrefetchedQuery,
    KnownGeneAAQuery,
    DeleteVariantsQuery,
)
from .models import (
    only_source_name,
    Case,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    DistillerSubmissionBgJob,
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
    RowWithClinvarMax,
    CASE_STATUS_CHOICES,
    RowWithAffectedCasesPerGene,
    SmallVariantSummary,
    KioskAnnotateBgJob,
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
)
from .tasks import (
    export_file_task,
    export_project_cases_file_task,
    distiller_submission_task,
    compute_project_variants_stats,
    sync_project_upstream,
    single_case_filter_task,
    project_cases_filter_task,
    run_kiosk_bg_job,
)
from .file_export import RowWithSampleProxy
from variants.helpers import SQLALCHEMY_ENGINE


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
            self._alchemy_engine = SQLALCHEMY_ENGINE
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
            .prefetch_related(
                "smallvariantset_set__variant_stats",
                "smallvariantset_set__variant_stats__sample_variant_stats",
                "project",
            )
        )

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["project"] = CaseAwareProject.objects.prefetch_related("variant_stats").get(
            pk=result["project"].pk
        )
        result["progress"] = self._compute_progress(result["project"])
        # Build list of properly sorted coverage keys.
        try:
            coverages = set()
            for case in result["project"].case_set.all():
                variant_set = case.latest_variant_set()
                if variant_set:
                    if hasattr(variant_set, "casealignmentstats"):
                        for min_covs in variant_set.casealignmentstats.bam_stats.values():
                            if "min_cov_target" in min_covs:
                                coverages |= set(map(int, min_covs["min_cov_target"]))
            if coverages:
                filtered = filter(lambda x: x > 0, coverages)
                result["coverages"] = list(map(str, sorted(filtered)))[:5]
        except (SmallVariantSet.variant_stats.RelatedObjectDoesNotExist, AttributeError):
            pass  # swallow, defaults set above

        return result

    def _compute_progress(self, project):
        counts = {key: 0 for key, _ in CASE_STATUS_CHOICES}
        for case in Case.objects.filter(project=project):
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Sync VarFish project with upstream SODAR",
                project=self.get_project(self.request, self.kwargs),
                job_type=SyncCaseListBgJob.spec_name,
                user=user,
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
            **build_cov_data(list(project.case_set.all())),
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

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
                    user=user,
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
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

        case = self.get_object()
        form = self.get_form()
        timeline = get_backend_api("timeline_backend")
        if form.is_valid():
            if self.request.POST.get("sodar_uuid"):
                kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
                if not user.is_superuser:
                    kwargs["user"] = user
                try:
                    record = CaseComments.objects.get(**kwargs)
                except ObjectDoesNotExist as e:
                    return HttpResponse(
                        json.dumps(
                            {"result": "Not authorized to delete comment or no comment found."}
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
                        user=user,
                        event_name="case_comment_edit",
                        description="edit comment for case {case}: {text}",
                        status_type="OK",
                    )
                    tl_event.add_object(obj=case, label="case", name=case.name)
                    tl_event.add_object(obj=record, label="text", name=record.shortened_text())
            else:
                record = CaseComments(case=case, user=user, comment=form.cleaned_data["comment"])
                record.save()
                if timeline:
                    tl_event = timeline.add_event(
                        project=self.get_project(self.request, self.kwargs),
                        app_name="variants",
                        user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

        kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
        if not user.is_superuser:
            kwargs["user"] = user

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
                user=user,
                event_name="case_comment_delete",
                description="delete comment for case {case}",
                status_type="OK",
            )
            tl_event.add_object(obj=self.get_object(), label="case", name=self.get_object().name)
        return HttpResponse(json.dumps({"result": "OK"}), content_type="application/json")


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

        try:
            variant_set = case.latest_variant_set()
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
        except (SmallVariantSet.variant_stats.RelatedObjectDoesNotExist, AttributeError):
            pass  # swallow, defaults set above

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

    def post(self, *args, **kwargs):
        case = self.get_object()
        case_uuid = case.sodar_uuid
        case_name = case.name
        for query in DeleteVariantsQuery(SQLALCHEMY_ENGINE).run(case_id=case.id):
            with contextlib.closing(query):
                pass
        case.delete()
        messages.success(self.request, "Deleted case {} with UUID {}.".format(case_name, case_uuid))
        return redirect("variants:case-list", project=case.project.sodar_uuid)


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
            if case.latest_variant_set():
                for stats in case.latest_variant_set().variant_stats.sample_variant_stats.all():
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

        relatedness_set = []
        try:
            if object.latest_variant_set():
                relatedness_set = object.latest_variant_set().variant_stats.relatedness.all()
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow

        result = {
            "pedigree": [
                {**line, "patient": only_source_name(line["patient"])} for line in object.pedigree
            ],
            "relData": list(build_rel_data(object.pedigree, relatedness_set)),
            **build_sex_data(object),
            **build_cov_data([object]),
            "variantTypeData": list(self._build_var_type_data(object)),
            "variantEffectData": list(self._build_var_effect_data(object)),
            "indelSizeData": list(self._build_indel_size_data(object)),
        }
        return JsonResponse(result)

    def _build_var_type_data(self, object):
        if not object.latest_variant_set():
            return
        try:
            for item in object.latest_variant_set().variant_stats.sample_variant_stats.all():
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
        if not object.latest_variant_set():
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
            for stats in object.latest_variant_set().variant_stats.sample_variant_stats.all():
                yield {
                    "name": only_source_name(stats.sample_name),
                    "x": keys,
                    "y": list(map(stats.ontarget_effect_counts.get, keys)),
                }
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            pass  # swallow

    def _build_indel_size_data(self, object):
        if not object.latest_variant_set():
            return
        try:
            indel_sizes = {
                stats.sample_name: {
                    int(key): value for key, value in stats.ontarget_indel_sizes.items()
                }
                for stats in object.latest_variant_set().variant_stats.sample_variant_stats.all()
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        if not self._previous_query:
            if "job" in self.kwargs:
                self._previous_query = FilterBgJob.objects.get(
                    sodar_uuid=self.kwargs["job"]
                ).smallvariantquery
            else:
                self._previous_query = (
                    self.get_case_object()
                    .small_variant_queries.filter(user=user)
                    .order_by("-date_created")
                    .first()
                )
        return self._previous_query

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_form_kwargs(self):
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        result = super().get_form_kwargs()
        result["case"] = self.get_case_object()
        result["user"] = user
        return result

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        if form.cleaned_data["submit"] == "download":
            return self._form_valid_file(form)
        elif form.cleaned_data["submit"] == "submit-mutationdistiller":
            return self._form_valid_mutation_distiller(form)

    def form_invalid(self, form):
        return render(
            self.request,
            self.template_name,
            self.get_context_data(form=form, form_errors=form.errors.as_json),
        )

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {}".format(
                    form.cleaned_data["file_type"], self.get_case_object().name
                ),
                project=self.get_project(self.request, self.kwargs),
                job_type=ExportFileBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Submitting case {} to MutationDistiller".format(self.get_case_object().name),
                project=self.get_project(self.request, self.kwargs),
                job_type=DistillerSubmissionBgJob.spec_name,
                user=user,
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
                    tmp = []
                    for v in value:
                        chrom, start, end = v
                        if start and end:
                            tmp.append("{}:{:,}-{:,}".format(chrom, start, end))
                        else:
                            tmp.append(chrom)
                    result[key] = "\n".join(tmp)
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

    def post(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

        # get case object
        case_object = Case.objects.get(sodar_uuid=kwargs["case"])

        # clean data first
        form = FilterForm(self.request.POST, case=case_object, user=user)

        if form.is_valid():
            # form is valid, we are supposed to render an HTML table with the results
            with transaction.atomic():
                # Save query parameters
                small_variant_query = SmallVariantQuery.objects.create(
                    case=case_object,
                    user=user,
                    form_id=form.form_id,
                    form_version=form.form_version,
                    query_settings=_undecimal(form.cleaned_data),
                )
                # Construct background job objects
                bg_job = BackgroundJob.objects.create(
                    name="Running filter query for case {}".format(case_object.name),
                    project=self.get_project(self.request, kwargs),
                    job_type=FilterBgJob.spec_name,
                    user=user,
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

    def post(self, *args, **kwargs):
        try:
            filter_job = FilterBgJob.objects.select_related("bg_job").get(
                sodar_uuid=self.request.POST["filter_job_uuid"]
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
                {
                    "error": "No filter job with UUID {}".format(
                        self.request.POST["filter_job_uuid"]
                    )
                },
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(self.request.POST["filter_job_uuid"])},
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

    def get(self, *args, **kwargs):
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        filter_job = (
            FilterBgJob.objects.filter(
                smallvariantquery__user=user, case__sodar_uuid=kwargs["case"]
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

    def post(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""
        # TODO: properly test prioritization
        # TODO: refactor, cleanup, break apart
        # Fetch filter job to display.
        filter_job = FilterBgJob.objects.get(sodar_uuid=self.request.POST["filter_job_uuid"])

        # Compute number of columns in table for the cards.
        pedigree = filter_job.smallvariantquery.case.get_filtered_pedigree_with_samples()
        card_colspan = 13 + len(pedigree)

        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = CaseLoadPrefetchedQuery(
            filter_job.smallvariantquery.case, SQLALCHEMY_ENGINE, filter_job.smallvariantquery.id
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
        for hpo in filter_job.smallvariantquery.query_settings.get("prio_hpo_terms", []):
            matches = HpoName.objects.filter(hpo_id=hpo)
            if matches:
                hpoterms[hpo] = matches.first().name
            else:
                hpoterms[hpo] = "unknown HPO term"

        rows = annotate_with_clinvar_max(rows)

        return render(
            self.request,
            self.template_name,
            self.get_context_data(
                case=filter_job.smallvariantquery.case,
                result_rows=rows,
                result_count=num_results,
                elapsed_seconds=elapsed.total_seconds(),
                database=filter_job.smallvariantquery.query_settings.get(
                    "database_select", "refseq"
                ),
                pedigree=pedigree,
                hpoterms=hpoterms,
                compound_recessive_index=filter_job.smallvariantquery.query_settings.get(
                    "compound_recessive_index", ""
                ),
                prio_enabled=filter_job.smallvariantquery.query_settings.get("prio_enabled", False),
                training_mode=1
                if filter_job.smallvariantquery.query_settings.get("training_mode", False)
                else 0,
                query_type=self.query_type,
                has_phenotype_scores=bool(gene_scores),
                has_pathogenicity_scores=bool(variant_scores),
                patho_enabled=filter_job.smallvariantquery.query_settings.get(
                    "patho_enabled", False
                ),
                patho_score=filter_job.smallvariantquery.query_settings.get("patho_score", False),
                exac_enabled=filter_job.smallvariantquery.query_settings.get("exac_enabled", False),
                thousand_genomes_enabled=filter_job.smallvariantquery.query_settings.get(
                    "thousand_genomes_enabled", False
                ),
                gnomad_genomes_enabled=filter_job.smallvariantquery.query_settings.get(
                    "gnomad_genomes_enabled", False
                ),
                gnomad_exomes_enabled=filter_job.smallvariantquery.query_settings.get(
                    "gnomad_exomes_enabled", False
                ),
                inhouse_enabled=filter_job.smallvariantquery.query_settings.get(
                    "inhouse_enabled", False
                ),
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

    def post(self, *args, **kwargs):
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        filter_job = ProjectCasesFilterBgJob.objects.get(
            sodar_uuid=self.request.POST["filter_job_uuid"]
        )

        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = ProjectLoadPrefetchedQuery(
            filter_job.projectcasessmallvariantquery.project,
            SQLALCHEMY_ENGINE,
            filter_job.projectcasessmallvariantquery.id,
        )

        # get all rows and then inflate them with all member per case and then cut them down. we can't know the length
        # of the results beforehand. it looks inefficient, but a quick try showed that it isn't much slower.
        with contextlib.closing(
            query.run(filter_job.projectcasessmallvariantquery.query_settings)
        ) as results:
            _rows = results.fetchall()
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

        rows = annotate_with_clinvar_max(rows)

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

        card_colspan = 16
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

    def get_previous_query(self):
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        if not self._previous_query:
            if "job" in self.kwargs:
                self._previous_query = ProjectCasesFilterBgJob.objects.get(
                    sodar_uuid=self.kwargs["job"]
                ).projectcasessmallvariantquery
            else:
                self._previous_query = (
                    self.get_project(self.request, self.kwargs)
                    .small_variant_queries.filter(user=user)
                    .order_by("-date_created")
                    .first()
                )
        return self._previous_query

    def get_form_kwargs(self):
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        result = super().get_form_kwargs()
        result["project"] = self.get_project(self.request, self.kwargs)
        result["user"] = user
        return result

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        if form.cleaned_data["submit"] == "download":
            return self._form_valid_file(form)

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for cases in project".format(form.cleaned_data["file_type"]),
                project=self.get_project(self.request, self.kwargs),
                job_type=ExportProjectCasesFileBgJob.spec_name,
                user=user,
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
        if self.request.method == "GET" and self.get_previous_query():
            # TODO: the code for version conversion needs to be hooked in here
            messages.info(
                self.request,
                ("Welcome back! We have restored your previous query settings from {}.").format(
                    naturaltime(self.get_previous_query().date_created)
                ),
            )
            for key, value in self.get_previous_query().query_settings.items():
                if isinstance(value, list):
                    result[key] = " ".join(value)
                else:
                    result[key] = value
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        """process the post request. important: data is not cleaned automatically, we must initiate it here."""

        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

        # get current CaseAwareProject
        project = CaseAwareProject.objects.get(pk=self.get_project(self.request, self.kwargs).pk)

        # clean data first
        form = ProjectCasesFilterForm(self.request.POST, project=project, user=user)

        if form.is_valid():
            # form is valid, we are supposed to render an HTML table with the results
            with transaction.atomic():
                # Save query parameters
                small_variant_query = ProjectCasesSmallVariantQuery.objects.create(
                    project=project,
                    user=user,
                    form_id=form.form_id,
                    form_version=form.form_version,
                    query_settings=_undecimal(form.cleaned_data),
                )
                # Construct background job objects
                bg_job = BackgroundJob.objects.create(
                    name="Running filter query for project",
                    project=project,
                    job_type=ProjectCasesFilterBgJob.spec_name,
                    user=user,
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
    AlchemyEngineMixin,
    View,
):
    """View for getting a joint filter job status.

    This view queries the current status of a joint filter job and returns it as JSON.
    """

    permission_required = "variants.view_data"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def post(self, *args, **kwargs):
        try:
            filter_job = ProjectCasesFilterBgJob.objects.select_related("bg_job").get(
                sodar_uuid=self.request.POST["filter_job_uuid"]
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
                {
                    "error": "No filter job with UUID {}".format(
                        self.request.POST["filter_job_uuid"]
                    )
                },
                status=400,
            )
        except ValidationError:
            return JsonResponse(
                {"error": "No valid UUID {}".format(self.request.POST["filter_job_uuid"])},
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        filter_job = (
            ProjectCasesFilterBgJob.objects.filter(
                projectcasessmallvariantquery__user=user, project__sodar_uuid=kwargs["project"]
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


def annotate_with_clinvar_max(rows):
    def _find_split_positions(column):
        split_positions = []
        prev_position = 0
        for i, x in enumerate(column):
            if x == "$":
                split_positions.append((prev_position, i))
                prev_position = i + 1
        split_positions.append((prev_position, len(column)))
        return split_positions

    rows = [RowWithClinvarMax(row) for row in rows]
    for row in rows:
        candidates = []
        clinvars = []
        # Find out where a new entry in the array list begins, delimiter is the "$" sign.
        split_sig = _find_split_positions(row.clinical_significance_ordered)
        split_status = _find_split_positions(row.review_status_ordered)
        split_trait = _find_split_positions(row.all_traits)
        for i, rcv in enumerate(row.rcv):
            clinvars.append(
                {
                    "clinical_significance_ordered": row.clinical_significance_ordered[
                        split_sig[i][0] : split_sig[i][1]
                    ],
                    "review_status_ordered": row.review_status_ordered[
                        split_status[i][0] : split_status[i][1]
                    ],
                    "all_traits": list(
                        {
                            trait.lower()
                            for trait in row.all_traits[split_trait[i][0] : split_trait[i][1]]
                        }
                    ),
                }
            )
            for sig, status in zip(
                clinvars[-1]["clinical_significance_ordered"], clinvars[-1]["review_status_ordered"]
            ):
                sig_lvl = sig_level(sig)
                status_lvl = status_level(status)
                candidates.append((sig_lvl, status_lvl, sig, status, clinvars[-1]["all_traits"]))
        if candidates:
            values = min(candidates)
        else:
            values = (sig_level(None), status_level(None), None, None, None)
        row._self_max_significance = values[2]
        row._self_max_clinvar_status = values[3]
        row._self_max_all_traits = values[4]
    return rows


class SmallVariantDetails(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FrequencyMixin,
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
        url = url_tpl % {
            "base_url": settings.VARFISH_JANNOVAR_REST_API_URL,
            "database": kwargs["database"],
            "genome": "hg19",
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
            hom = getattr(inhouse, "count_hom_alt", 0)
            het = getattr(inhouse, "count_het", 0)
            hemi = getattr(inhouse, "count_hemi_alt", 0)
            result["inhouse_freq"] = {
                "hom": hom,
                "het": het,
                "hemi": hemi,
                "carriers": hom + het + hemi,
            }
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
        if self.request.GET.get("render_full", "no").lower() in ("yes", "true"):
            result["base_template"] = "projectroles/project_base.html"
        else:
            result["base_template"] = "empty_base.html"
        result.update(self._get_population_freqs(self.kwargs))
        result["gene"] = get_gene_infos(
            self.kwargs["database"], self.kwargs["gene_id"], self.kwargs["ensembl_transcript_id"]
        )
        entrez_id = result["small_var"].refseq_gene_id
        result["ncbi_summary"] = NcbiGeneInfo.objects.filter(entrez_id=entrez_id).first()
        result["ncbi_gene_rifs"] = NcbiGeneRif.objects.filter(entrez_id=entrez_id).order_by("pk")
        result["comments"] = self._load_variant_comments()
        result["flags"] = self._load_variant_flags()
        result["training_mode"] = int(self.kwargs["training_mode"])
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {} (Resubmission)".format(
                    form.cleaned_data["file_type"], job.case
                ),
                project=job.bg_job.project,
                job_type=ExportFileBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        job = get_object_or_404(ExportProjectCasesFileBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for all cases in project (Resubmission)".format(
                    form.cleaned_data["file_type"]
                ),
                project=job.bg_job.project,
                job_type=ExportProjectCasesFileBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        job = get_object_or_404(DistillerSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to MutationDistiller".format(job.case),
                project=job.bg_job.project,
                job_type=DistillerSubmissionBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        job = get_object_or_404(FilterBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting filter case {}".format(job.case),
                project=job.bg_job.project,
                job_type=FilterBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        job = get_object_or_404(ProjectCasesFilterBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting filter project",
                project=job.bg_job.project,
                job_type=ProjectCasesFilterBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        with transaction.atomic():
            # Construct background job objects
            bg_job = BackgroundJob.objects.create(
                name="Recreate variant statistic for whole project",
                project=self.get_project(self.request, self.kwargs),
                job_type=ComputeProjectVariantsStatsBgJob.spec_name,
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
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
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

        case = self.get_object()
        timeline = get_backend_api("timeline_backend")
        if self.request.POST.get("sodar_uuid"):
            kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
            if not user.is_superuser:
                kwargs["user"] = user
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
                    user=user,
                    event_name="variant_comment_edit",
                    description="edit comment for variant %s in case {case}: {text}"
                    % comment.get_variant_description(),
                    status_type="OK",
                )
                tl_event.add_object(obj=case, label="case", name=case.name)
                tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())
        else:
            comment = SmallVariantComment(case=case, user=user, sodar_uuid=uuid.uuid4())
            form = SmallVariantCommentForm(self.request.POST, instance=comment)
            comment = form.save()
            if timeline:
                tl_event = timeline.add_event(
                    project=self.get_project(self.request, self.kwargs),
                    app_name="variants",
                    user=user,
                    event_name="variant_comment_add",
                    description="add comment for variant %s in case {case}: {text}"
                    % comment.get_variant_description(),
                    status_type="OK",
                )
                tl_event.add_object(obj=case, label="case", name=case.name)
                tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())
        return HttpResponse(json.dumps({"comment": comment.text}), content_type="application/json")


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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")

        kwargs = {"sodar_uuid": self.request.POST.get("sodar_uuid")}
        if not user.is_superuser:
            kwargs["user"] = user

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
                user=user,
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
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
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
            acmg_ratings = AcmgCriteriaRating(case=case, sodar_uuid=uuid.uuid4(), user=user)
        form = AcmgCriteriaRatingForm(self.request.POST, instance=acmg_ratings)
        try:
            acmg_ratings = form.save()
        except ValueError as e:
            raise Exception(str(form.errors)) from e
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="variants",
                user=user,
                event_name="flags_set",
                description="set ACMG rating for variant %s in case {case}: {extra-rating_values}"
                % acmg_ratings.get_variant_description(),
                status_type="OK",
                extra_data={"rating_values": acmg_ratings.get_human_readable()},
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
        # TODO: allow erasing?
        result = self._model_to_dict(acmg_ratings)
        return HttpResponse(json.dumps(result, cls=UUIDEncoder), content_type="application/json")


class NewFeaturesView(LoginRequiredMixin, RedirectView):
    """Store "latest seen changelog version" for user and redirect."""

    url = "/manual/history.html"

    def get(self, *args, **kwargs):
        user = self.request.user
        if settings.KIOSK_MODE:
            user = User.objects.get(username="kiosk_user")
        setting_api = AppSettingAPI()
        setting_api.set_app_setting(
            "variants", "latest_version_seen_changelog", site_version(), user=user
        )
        return super().get(*args, **kwargs)


class HpoTermsApiView(LoginRequiredMixin, View):
    def get(self, *_args, **_kwargs):
        query = self.request.GET.get("query")
        if not query:
            return HttpResponse({}, content_type="application/json")
        hpo = HpoName.objects.filter(
            Q(hpo_id__icontains=self.request.GET.get("query"))
            | Q(name__icontains=self.request.GET.get("query"))
        )[:20]
        return HttpResponse(
            json.dumps([model_to_dict(h) for h in hpo]), content_type="application/json"
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
            user = User.objects.get(username="kiosk_user")
            bg_job = BackgroundJob.objects.create(
                name="Kiosk mode annotation",
                project=project,
                job_type=KioskAnnotateBgJob.spec_name,
                user=user,
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
                user=user,
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
            # TODO: setup celerybeat job that triggers background jobs for clearing out old cases
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
            parent=None, type="CATEGORY", title=settings.KIOSK_CAT
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
