"""Views for the ``svs`` app."""
import contextlib
import hashlib
import json
import uuid

import aldjemy.core
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, DetailView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from projectroles.plugins import get_backend_api
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from geneinfo.views import get_gene_infos
from .forms import FilterForm, StructuralVariantCommentForm, StructuralVariantFlagsForm
from .models import (
    StructuralVariantFlags,
    StructuralVariantComment,
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    ImportStructuralVariantBgJob,
)
from .queries import SingleCaseFilterQuery, best_matching_flags
from geneinfo.models import RefseqToHgnc, Hgnc, Hpo, HpoName, Mim2geneMedgen
from variants.models import Case, ImportVariantsBgJob
from variants.views import UUIDEncoder
from variants.helpers import SQLALCHEMY_ENGINE


class CaseFilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Display the structural variant filter form for a case."""

    template_name = "svs/filter.html"
    permission_required = "svs.view_data"
    form_class = FilterForm
    success_url = "."
    query_type = "case"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_object = None

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["case"] = self.get_case_object()
        return result

    def get_context_data(self, **kwargs):
        """Put the ``Case`` object into the context."""
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_case_object()
        context["query_type"] = "case"
        context["pedigree"] = self.get_case_object().get_filtered_pedigree_with_samples()
        return context

    def form_valid(self, form):
        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = SingleCaseFilterQuery(self.get_case_object(), SQLALCHEMY_ENGINE)
        args = dict(form.cleaned_data)
        # TODO: variant types
        with contextlib.closing(query.run(args)) as results:
            context_data = self._fetch_context_data(form, results)
            context_data["elapsed_seconds"] = timezone.now() - before
            return render(self.request, self.template_name, context=context_data)

    def _fetch_context_data(self, form, results):
        """Get and process all rows, return context data dict."""
        rows_by_sv = {}
        seen = set()
        gene_id_to_symbol = {}
        for entry in results.fetchall():
            key = (entry.sv_uuid, entry.gene_id)
            if key in seen:
                continue
            else:
                seen.add(key)
                row = rows_by_sv.setdefault(
                    entry.sv_uuid,
                    {"entries": [], "genes": set(), "extra_genes": set(), "all_genes": set()},
                )
                if entry.refseq_gene_id:
                    gene_id_to_symbol[entry.refseq_gene_id] = entry.symbol or entry.refseq_gene_id
                    row["all_genes"].add(entry.refseq_gene_id)
                row["entries"].append(entry)
                row["genes"].add(entry.symbol)
                if getattr(entry, "itv_shared_gene_symbols", []) and getattr(
                    entry, "itv_shared_gene_ids", []
                ):
                    for gene_id, symbol in zip(
                        entry.itv_shared_gene_ids, entry.itv_shared_gene_symbols
                    ):
                        if gene_id:
                            row["extra_genes"].add((symbol, gene_id))
                            gene_id_to_symbol[gene_id] = symbol or gene_id
                            row["all_genes"].add(gene_id)
        for row in rows_by_sv.values():
            row["genes"] = list(sorted(row["genes"], key=lambda x: x or ""))
            row["extra_genes"] = list(sorted(row["extra_genes"], key=lambda x: x[0] or x[1]))
            row["all_genes"] = list(sorted(row["all_genes"], key=lambda x: gene_id_to_symbol[x]))
            row["ensembl_sum"] = sum(
                (
                    int(v or 0)
                    for k, v in row["entries"][0].items()
                    if "ensembl_" in k and "_count" in k
                )
            )

        context_data = self.get_context_data()
        context_data["rows_by_sv"] = rows_by_sv
        context_data["database"] = form.cleaned_data["database_select"]
        context_data["card_colspan"] = 18 + len(self.get_case_object().pedigree)

        return context_data


class StructuralVariantDetailsView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display details of a structural variant, for SV result tablef old-out."""

    template_name = "svs/sv_details.html"
    permission_required = "svs.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get_context_data(self, **kwargs):
        """Query for the gene detail and put into "genes"."""

        def gene_id(sv_anno):
            """Extract gene ID from ``StructuralVariantGeneAnnotation``."""
            # TODO: import empty gene annotations as ``None`` and not ``"."``.
            if database == "refseq":
                return sv_anno.refseq_gene_id
            else:
                sv_anno.ensembl_gene_id

        context = super().get_context_data(**kwargs)
        database = self.request.GET.get("database", "refseq")

        sv = StructuralVariant.objects.filter(case_id=self.object.id).get(sv_uuid=self.kwargs["sv"])
        context["card_id"] = hashlib.sha224(str(sv.sv_uuid).encode("utf-8")).hexdigest()
        context["sv"] = sv
        context["gt_keys"] = list(sv.genotype.values())[0]
        context["gt_labels"] = {
            "dq": "diploid quality",
            "ndq": "non-diploid quality",
            "rd": "normalized read-depth (Z-score)",
            "pl": "likelihood diploid, del, dup",
            "cn": "copy number estimate",
            "npe": "normalized paired-endsupport",
            "sre": "normalized split-read support",
            "ns": "number of SNPs in region",
            "har": "heterozygous allele ration",
            "pec": "paired-read coverage",
            "pev": "paired-read ALT",
            "src": "split-read coverage",
            "srv": "split-read ALT",
            "gq": "genotype quality",
        }

        sv_annos = StructuralVariantGeneAnnotation.objects.filter(sv_uuid=self.kwargs["sv"])
        context["genes"] = [
            get_gene_infos(database, gene_id(sv_anno), sv_anno.ensembl_transcript_id)
            for sv_anno in sv_annos
            if gene_id(sv_anno) and gene_id(sv_anno) != "."
        ]
        return context


class StructuralVariantFlagsApiView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    View,
):
    """A view that returns JSON for the ``StructuralVariantFlags`` for a variant of a case and allows updates."""

    # TODO: create new permission
    permission_required = "variants.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def _model_to_dict(self, flags):
        """Helper that calls ``model_to_dict()`` and then replaces the case PK with the SODAR UUID."""
        return {**model_to_dict(flags), "case": str(self.get_object().sodar_uuid)}

    def get(self, *_args, **kwargs):
        try:
            flags = self._get_flags_for_variant(kwargs["sv"])
        except StructuralVariantFlags.DoesNotExist:
            raise Http404("No flags for variant yet")
        else:
            return HttpResponse(
                json.dumps(self._model_to_dict(flags), cls=UUIDEncoder),
                content_type="application/json",
            )

    @transaction.atomic
    def post(self, *_args, **kwargs):
        case = self.get_object()
        sv = StructuralVariant.objects.get(sv_uuid=kwargs["sv"])
        try:
            flags = self._get_flags_for_variant(kwargs["sv"])
        except StructuralVariantFlags.DoesNotExist:
            flags = StructuralVariantFlags(
                case=case,
                bin=sv.bin,
                release=sv.release,
                chromosome=sv.chromosome,
                start=sv.start,
                end=sv.end,
                sv_type=sv.sv_type,
                sv_sub_type=sv.sv_sub_type,
            )
            flags.save()
        form = StructuralVariantFlagsForm(self.request.POST, instance=flags)
        try:
            flags = form.save()
        except ValueError as e:
            raise Exception(str(form.errors)) from e
        timeline = get_backend_api("timeline_backend")
        if timeline:
            tl_event = timeline.add_event(
                project=self.get_project(self.request, self.kwargs),
                app_name="svs",
                user=self.request.user,
                event_name="flags_set",
                description="set flags for structural variant %s in case {case}: {extra-flag_values}"
                % sv,
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

    def _get_flags_for_variant(self, sv_uuid):
        case = self.get_object()
        with contextlib.closing(
            best_matching_flags(SQLALCHEMY_ENGINE, case.id, sv_uuid)
        ) as results:
            result = results.first()
            if not result:
                raise StructuralVariantFlags.DoesNotExist()
            else:
                return StructuralVariantFlags.objects.get(
                    case_id=case.id, sodar_uuid=result.flags_uuid
                )


class StructuralVariantCommentApiView(
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

    def post(self, *_args, **kwargs):
        case = self.get_object()
        sv = StructuralVariant.objects.get(sv_uuid=kwargs["sv"])
        comment = StructuralVariantComment(
            case=case,
            user=self.request.user,
            bin=sv.bin,
            release=sv.release,
            chromosome=sv.chromosome,
            start=sv.start,
            end=sv.end,
            sv_type=sv.sv_type,
            sv_sub_type=sv.sv_sub_type,
            sodar_uuid=uuid.uuid4(),
        )
        form = StructuralVariantCommentForm(self.request.POST, instance=comment)
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


class ImportStructuralVariantsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the import case background job.
    """

    permission_required = "variants.view_data"
    template_name = "svs/import_job_detail.html"
    model = ImportStructuralVariantBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
