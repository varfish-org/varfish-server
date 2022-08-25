"""Views for the ``svs`` app."""
import contextlib
import hashlib
import json
import re
import uuid

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.urls import resolve
from projectroles.models import Project

from variants.helpers import get_engine
from projectroles.views import LoginRequiredMixin
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from projectroles.plugins import get_backend_api
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from geneinfo.views import get_gene_infos
from regmaps.models import RegElement, RegInteraction
from .forms import (
    FilterForm,
    StructuralVariantCommentForm,
    StructuralVariantFlagsForm,
)
from .models import (
    StructuralVariantFlags,
    StructuralVariantComment,
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    ImportStructuralVariantBgJob,
    StructuralVariantSet,
    BuildBackgroundSvSetJob,
    CleanupBackgroundSvSetJob,
)
from .queries import SingleCaseFilterQuery, best_matching_flags
from variants.models import Case
from variants.views import UUIDEncoder


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
        context["variant_set_exists"] = StructuralVariantSet.objects.filter(
            case_id=context["object"].id, state="active"
        ).exists()
        return context

    def form_valid(self, form):
        # Take time while job is running
        before = timezone.now()
        # Get and run query
        query = SingleCaseFilterQuery(self.get_case_object(), get_engine())
        args = dict(form.cleaned_data)
        # TODO: variant types
        print("XXX\n\n", args, "\n\nXXX")
        with contextlib.closing(query.run(args)) as results:
            context_data = self._fetch_context_data(form, results)
            context_data["elapsed_seconds"] = timezone.now() - before
            return render(self.request, self.template_name, context=context_data)

    def _fetch_context_data(self, form, results):
        """Get and process all rows, return context data dict."""
        rows_by_sv = {}
        seen = set()
        gene_id_to_symbol = {}
        num_results = results.rowcount
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
        context_data["num_results"] = num_results
        results_limit = form.cleaned_data.get("result_rows_limit", 0)
        context_data["results_limit"] = results_limit
        context_data["rows_by_sv"] = dict(list(rows_by_sv.items())[:results_limit])
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
        context["regulatory_general_padding"] = int(
            self.request.GET.get("regulatory_general_padding", 0)
        )
        context["reg_elements"] = RegElement.objects.overlapping(
            sv.release,
            sv.chromosome,
            sv.start,
            sv.end,
            padding=context["regulatory_general_padding"],
        ).order_by("reg_map__short_title")
        all_interactions = RegInteraction.objects.overlapping(
            sv.release,
            sv.chromosome,
            sv.start,
            sv.end,
            padding=context["regulatory_general_padding"],
        ).order_by("reg_map__short_title", "-score")
        grouped_interactions = {}
        for inter in all_interactions:
            key = (inter.reg_map.slug, inter.reg_map.short_title)
            grouped_interactions.setdefault(key, []).append(inter)
        context["reg_interactions"] = grouped_interactions

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
        with contextlib.closing(best_matching_flags(get_engine(), case.id, sv_uuid)) as results:
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
                app_name="svs",
                user=self.request.user,
                event_name="comment_add",
                description="add comment for structural variant %s in case {case}: {text}"
                % comment.get_variant_description(),
                status_type="OK",
            )
            tl_event.add_object(obj=case, label="case", name=case.name)
            tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())
        return HttpResponse(json.dumps({"result": "OK"}), content_type="application/json")


class MultiStructuralVariantFlagsAndCommentApiView(
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
                flag_data = model_to_dict(self._get_flags_for_variant(variant.get("sv_uuid"), case))

                for flag in flags_keys:
                    if flags[flag] is None:
                        flags[flag] = flag_data[flag]

                    if not flags[flag] == flag_data[flag]:
                        flags_interfering.add(flag)

                    flags[flag] = flag_data[flag]

            except StructuralVariantFlags.DoesNotExist:
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
        variant_list = post_data.pop("variant_list")[0]
        post_data.pop("csrfmiddlewaretoken")
        post_data_clean = {k: v[0] for k, v in post_data.items()}
        text = post_data_clean.pop("text")

        for variant in json.loads(variant_list):
            case = get_object_or_404(Case, sodar_uuid=variant.get("case"))
            sv = StructuralVariant.objects.get(sv_uuid=variant.get("sv_uuid"))

            try:
                flags = self._get_flags_for_variant(variant.get("sv_uuid"), case)

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

            form = StructuralVariantFlagsForm({**variant, **post_data_clean}, instance=flags)

            try:
                flags = form.save()

            except ValueError as e:
                raise Exception(str(form.errors)) from e

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

            if text:
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
                form = StructuralVariantCommentForm({**variant, "text": text}, instance=comment)

                try:
                    comment = form.save()

                except ValueError as e:
                    raise Exception(str(form.errors)) from e

                if timeline:
                    tl_event = timeline.add_event(
                        project=self.get_project(self.request, self.kwargs),
                        app_name="svs",
                        user=self.request.user,
                        event_name="comment_add",
                        description="add comment for structural variant %s in case {case}: {text}"
                        % comment.get_variant_description(),
                        status_type="OK",
                    )
                    tl_event.add_object(obj=case, label="case", name=case.name)
                    tl_event.add_object(obj=comment, label="text", name=comment.shortened_text())

        return JsonResponse({"message": "OK", "flags": post_data_clean, "comment": text})

    def _get_flags_for_variant(self, sv_uuid, case):
        with contextlib.closing(best_matching_flags(get_engine(), case.id, sv_uuid)) as results:
            result = results.first()
            if not result:
                raise StructuralVariantFlags.DoesNotExist()
            else:
                return StructuralVariantFlags.objects.get(
                    case_id=case.id, sodar_uuid=result.flags_uuid
                )


class ImportStructuralVariantsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of import case background jobs.
    """

    permission_required = "variants.view_data"
    template_name = "svs/import_job_detail.html"
    model = ImportStructuralVariantBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class _ProjectAccessMixin:
    """Mixin for providing access to a Project object from request kwargs"""

    #: The model class to use for projects.  You can override this to replace it
    #: with a proxy model, for example.
    project_class = Project

    def get_project(self, request=None, kwargs=None):
        """
        Return SODAR Project object based or None if not found, based on
        the current request and view kwargs. If arguments are not provided,
        uses self.request and/or self.kwargs.

        :param request: Request object (optional)
        :param kwargs: View kwargs (optional)
        :return: Object of project_class or None if not found
        """
        request = request or getattr(self, "request")
        kwargs = kwargs or getattr(self, "kwargs")
        # Ensure kwargs can be accessed
        if kwargs is None:
            raise ImproperlyConfigured("View kwargs are not accessible")

        # Project class object
        if "project" in kwargs:
            return self.project_class.objects.filter(sodar_uuid=kwargs["project"]).first()

        # Other object types
        if not request:
            raise ImproperlyConfigured("Current HTTP request is not accessible")

        if getattr(self, "model", None):
            model = getattr(self, "model")
            uuid_kwarg = getattr(self, "slug_url_kwarg")
        else:
            model = None
            uuid_kwarg = None

        for k, v in kwargs.items():
            if re.match(r"[0-9a-f-]+", v):
                try:
                    app_name = resolve(request.path).app_name
                    if app_name.find(".") != -1:
                        app_name = app_name.split(".")[0]
                    model = apps.get_model(app_name, k)
                    uuid_kwarg = k
                    break
                except LookupError:
                    pass

        if not model:
            return None

        try:
            obj = model.objects.get(sodar_uuid=kwargs[uuid_kwarg])
            if hasattr(obj, "project"):
                return obj.project
            # Some objects may have a get_project() func instead of foreignkey
            elif hasattr(obj, "get_project") and callable(getattr(obj, "get_project", None)):
                return obj.get_project()
        except model.DoesNotExist:
            return None


class SecondHitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
    _ProjectAccessMixin,
    TemplateView,
):
    """Render HTML with second small variant hits in a given gene.

    Optionally, exclude small variant with the given specification in GET parameters:

    - release
    - chromosome
    - start
    - end
    - reference
    - alternative
    """

    permission_required = "variants.view_data"
    template_name = "svs/second_hit.html"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

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
        context["pedigree"] = self.get_case_object().get_filtered_pedigree_with_samples()
        context["variant_set_exists"] = StructuralVariantSet.objects.filter(
            case_id=context["object"].id, state="active"
        ).exists()
        return context

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)

        database = self.kwargs["database"]
        if database not in ("refseq", "ensembl"):
            raise ValueError("Invalid database: %s" % database)

        before = timezone.now()
        query = SingleCaseFilterQuery(self.get_case_object(), get_engine())
        form = FilterForm(data=self._get_form_data(database), case=self.get_case_object())
        if not form.is_valid():
            raise ValueError("Invalid form data!")
        with contextlib.closing(query.run(form.cleaned_data)) as results:
            context_data = self._augment_context_data(
                context_data=context_data, form_data=form.cleaned_data, results=results
            )
            context_data["elapsed_seconds"] = timezone.now() - before
        return context_data

    def _get_form_data(self, database):
        """Return form data to pass into the query."""
        dummy_form = FilterForm(case=self.get_case_object())
        initial_values = {key: field.initial for key, field in dummy_form.fields.items()}
        initial_values.update(
            {
                "database_select": database,
                "submit": "display",
                "gene_allowlist": self.kwargs["gene_id"],
                "sv_size_min": None,
                "dgv_max_carriers": None,
                "dgv_sv_max_carriers": None,
                "dbvar_max_carriers": None,
                "exac_max_carriers": None,
                "g1k_max_alleles": None,
                "gnomad_max_carriers": None,
                "inhouse_max_carriers": None,
            }
        )

        case = self.get_case_object().get_members()
        for member_name in case:
            if member_name == case.index:
                initial_values["%s_gt" % member_name] = "variant"
            else:
                initial_values["%s_gt" % member_name] = "any"

        return initial_values

    def _augment_context_data(self, context_data, form_data, results):
        """Get and process all rows, return context data dict."""
        rows_by_sv = {}
        seen = set()
        gene_id_to_symbol = {}
        num_results = results.rowcount
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

        sv_uuid = self.request.GET.get("sv_uuid")
        if sv_uuid in rows_by_sv:
            rows_by_sv.pop(sv_uuid)

        context_data["pedigree"] = self.get_case_object().pedigree
        context_data["num_results"] = num_results
        results_limit = 200
        context_data["results_limit"] = results_limit
        context_data["rows_by_sv"] = dict(list(rows_by_sv.items())[:results_limit])
        context_data["database"] = form_data["database_select"]
        context_data["card_colspan"] = 18 + len(self.get_case_object().pedigree)

        return context_data


class BuildBackgroundSvSetJobDetailView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DetailView,
):
    """Display status and further details of build sv set background jobs.
    """

    permission_required = "variants.view_data"
    template_name = "svs/build_bg_job_detail.html"
    model = BuildBackgroundSvSetJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class CleanupBackgroundSvSetJobDetailView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DetailView,
):
    """Display status and further details of cleanup sv set background jobs.
    """

    permission_required = "variants.view_data"
    template_name = "svs/cleanup_bg_job_detail.html"
    model = CleanupBackgroundSvSetJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
