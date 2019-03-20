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

from .forms import FilterForm, StructuralVariantCommentForm, StructuralVariantFlagsForm
from .models import StructuralVariantFlags, StructuralVariantComment, StructuralVariant
from .models_queries import SingleCaseFilterQuery, best_matching_flags
from geneinfo.models import RefseqToHgnc, Hgnc, Hpo, HpoName, Mim2geneMedgen
from variants.models import Case
from variants.views import UUIDEncoder


#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


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
        query = SingleCaseFilterQuery(self.get_case_object(), SQLALCHEMY_ENGINE, debug=False)
        args = dict(form.cleaned_data)
        # TODO: variant types
        tmp = args.pop("region_whitelist")
        args["region_whitelist"] = []
        for entry in tmp:
            chrom, rng = entry.split(":", 1)
            start, end = rng.split("-", 1)
            start = int(start.replace(",", "").replace("_", ""))
            end = int(end.replace(",", "").replace("_", ""))
            args["region_whitelist"].append((chrom, start, end))
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
        context_data["card_colspan"] = 16 + len(self.get_case_object().pedigree)

        return context_data


class GeneDetailsView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display details for a list of genes, for the SV table card fold-out."""

    template_name = "svs/gene_details.html"
    permission_required = "svs.view_data"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get_context_data(self, **kwargs):
        """Query for the gene detail and put into "genes"."""
        genes_str = self.request.GET.get("genes", "")
        context = super().get_context_data(**kwargs)
        context["card_id"] = hashlib.sha224(genes_str.encode("utf-8")).hexdigest()
        context["genes"] = list(self._yield_gene_infos(genes_str.split(",")))
        return context

    def _yield_gene_infos(self, entrez_ids):
        for entrez_id in entrez_ids:
            hgnc = RefseqToHgnc.objects.filter(entrez_id=entrez_id).first()
            gene = None
            # TODO: handle case of ENSEMBL ids?
            if hgnc:
                gene = Hgnc.objects.filter(hgnc_id=hgnc.hgnc_id).first()

            if not gene:
                yield {"entrez_id": entrez_id}
            else:
                gene = model_to_dict(gene)
                hpoterms = {self._get_hpo_mapping(gene["omim_id"])}
                mim2gene = Mim2geneMedgen.objects.filter(entrez_id=gene["entrez_id"])
                if mim2gene:
                    for entry in mim2gene:
                        hpoterms.add(self._get_hpo_mapping(entry.omim_id))
                gene["hpo_terms"] = [h for h in hpoterms if h is not None]
                yield gene

    def _get_hpo_mapping(self, omim):
        hpo = Hpo.objects.filter(database_id="OMIM:{}".format(omim)).first()
        if hpo:
            hponame = HpoName.objects.filter(hpo_id=hpo.hpo_id).first()
            if hponame:
                return hpo.hpo_id, hponame.name


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
                containing_bins=sv.containing_bins,
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
            containing_bins=sv.containing_bins,
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
