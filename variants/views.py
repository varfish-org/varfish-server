from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.generic import DetailView, FormView, ListView, View
import simplejson as json

from bgjobs.models import BackgroundJob
from clinvar.models import Clinvar
from conservation.models import KnowngeneAA
from frequencies.views import FrequencyMixin
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from querybuilder.models_support import QueryBuilder

from .models import SmallVariant, Case, ExportFileBgJob
from .forms import FilterForm
from .tasks import export_file_task


class MainView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    template_name = "variants/case_select.html"
    permission_required = "variants.view_data"
    model = Case

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class FilterView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    template_name = "variants/filter.html"
    permission_required = "variants.view_data"
    form_class = FilterForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_object = None

    def get_case_object(self):
        if not self._case_object:
            self._case_object = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return self._case_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        index = self.get_case_object().index
        father = ""
        mother = ""

        for member in self.get_case_object().pedigree:
            if member["patient"] == index:
                father = member["father"]
                mother = member["mother"]

        kwargs["pedigree"] = list()
        for member in self.get_case_object().pedigree:
            name = member["patient"]
            if name == father:
                role = "father"
            elif name == index:
                role = "index"
            elif name == mother:
                role = "mother"
            else:
                role = "tbd"
            kwargs["pedigree"].append(
                {
                    "patient": name,
                    "father": member["father"],
                    "mother": member["mother"],
                    "gender": member["sex"] == 2,
                    "affected": member["affected"] == 2,
                    "role": role,
                    "fields": {
                        "gt": "%s_gt" % name,
                        "dp": "%s_dp" % name,
                        "ab": "%s_ab" % name,
                        "gq": "%s_gq" % name,
                        "ad": "%s_ad" % name,
                        "fail": "%s_fail" % name,
                    },
                }
            )

        return kwargs

    def form_valid(self, form):
        """Main branching point either render result or create an asychronous job."""
        if form.cleaned_data["result_type"] in ("tsv", "xlsx"):
            return self._form_valid_file(form)
        else:
            return self._form_valid_render(form, list(self._collect_select_effects(form)))

    def _collect_select_effects(self, form):
        """Yield the selected effects."""
        for field_name, effect in form.translate_effects.items():
            if form.cleaned_data[field_name]:
                yield effect

    def _build_query_kwargs(self, form, selected_effects):
        """Build the ``kwargs`` variable for ``form_valid`` and friends."""
        pedigree = self.get_form_kwargs()["pedigree"]
        kwargs = {
            "case": self.kwargs["case"],
            "exac_frequency": float(form.cleaned_data["exac_frequency"])
            if form.cleaned_data["exac_frequency"]
            else None,
            "exac_homozygous": int(form.cleaned_data["exac_homozygous"])
            if form.cleaned_data["exac_homozygous"]
            else None,
            "exac_heterozygous": int(form.cleaned_data["exac_heterozygous"])
            if form.cleaned_data["exac_heterozygous"]
            else None,
            "gnomad_genomes_frequency": float(form.cleaned_data["gnomad_genomes_frequency"])
            if form.cleaned_data["gnomad_genomes_frequency"]
            else None,
            "gnomad_genomes_homozygous": int(form.cleaned_data["gnomad_genomes_homozygous"])
            if form.cleaned_data["gnomad_genomes_homozygous"]
            else None,
            "gnomad_genomes_heterozygous": int(form.cleaned_data["gnomad_genomes_heterozygous"])
            if form.cleaned_data["gnomad_genomes_heterozygous"]
            else None,
            "gnomad_exomes_frequency": float(form.cleaned_data["gnomad_exomes_frequency"])
            if form.cleaned_data["gnomad_exomes_frequency"]
            else None,
            "gnomad_exomes_homozygous": int(form.cleaned_data["gnomad_exomes_homozygous"])
            if form.cleaned_data["gnomad_exomes_homozygous"]
            else None,
            "gnomad_exomes_heterozygous": int(form.cleaned_data["gnomad_exomes_heterozygous"])
            if form.cleaned_data["gnomad_exomes_heterozygous"]
            else None,
            "thousand_genomes_frequency": float(form.cleaned_data["thousand_genomes_frequency"])
            if form.cleaned_data["thousand_genomes_frequency"]
            else None,
            "thousand_genomes_homozygous": int(form.cleaned_data["thousand_genomes_homozygous"])
            if form.cleaned_data["thousand_genomes_homozygous"]
            else None,
            "thousand_genomes_heterozygous": int(form.cleaned_data["thousand_genomes_heterozygous"])
            if form.cleaned_data["thousand_genomes_heterozygous"]
            else None,
            "effects": selected_effects,
            "genotype": list(),
            "gene_blacklist": [x.strip() for x in form.cleaned_data["gene_blacklist"].split()],
            "database_select": form.cleaned_data["database_select"],
            "exac_enabled": form.cleaned_data["exac_enabled"],
            "gnomad_exomes_enabled": form.cleaned_data["gnomad_exomes_enabled"],
            "gnomad_genomes_enabled": form.cleaned_data["gnomad_genomes_enabled"],
            "thousand_genomes_enabled": form.cleaned_data["thousand_genomes_enabled"],
            "var_type_snv": form.cleaned_data["var_type_snv"],
            "var_type_mnv": form.cleaned_data["var_type_mnv"],
            "var_type_indel": form.cleaned_data["var_type_indel"],
            "compound_recessive_enabled": form.cleaned_data["compound_recessive_enabled"],
            "pedigree": pedigree,
        }
        return kwargs

    def _build_query_args(self, kwargs, form, pedigree):
        """Build the query from the postprocessed ``kwargs`` and the ``form`` instance."""
        qb = QueryBuilder()
        for member in pedigree:
            gt = form.cleaned_data[member["fields"]["gt"]]

            kwargs["genotype"].append(
                {
                    "member": member["patient"],
                    "dp": form.cleaned_data[member["fields"]["dp"]],
                    "ad": form.cleaned_data[member["fields"]["ad"]],
                    "gq": form.cleaned_data[member["fields"]["gq"]],
                    "ab": form.cleaned_data[member["fields"]["ab"]],
                    "gt": form.translate_inheritance[gt],
                    "fail": form.cleaned_data[member["fields"]["fail"]],
                }
            )

        if kwargs["compound_recessive_enabled"]:
            return qb.build_comphet_query(kwargs)
        else:
            base = qb.build_base_query(kwargs)
            conditions = [
                qb.build_vartype_term(kwargs),
                qb.build_frequency_term(kwargs),
                qb.build_homozygous_term(kwargs),
                qb.build_heterozygous_term(kwargs),
                qb.build_case_term(kwargs),
                qb.build_effects_term(kwargs),
                qb.build_genotype_term_list(kwargs),
                qb.build_gene_blacklist_term(kwargs),
            ]
            return qb.build_top_level_query(base, conditions)

    def _transform_entry_interpret_database(self, kwargs, entry):
        """Transform result entry and set ``effect``, ``hgvs_p``, ``hgvs_c``, and
        ``transcript_coding`` attributes based on selecting RefSeq/ENSEMBL.
        """
        if kwargs["database_select"] == "refseq":
            entry.effect = set(entry.refseq_effect)
            entry.hgvs_p = entry.refseq_hgvs_p
            entry.hgvs_c = entry.refseq_hgvs_c
            entry.transcript_coding = entry.refseq_transcript_coding
        elif kwargs["database_select"] == "ensembl":
            entry.effect = set(entry.ensembl_effect)
            entry.hgvs_p = entry.ensembl_hgvs_p
            entry.hgvs_c = entry.ensembl_hgvs_c
            entry.transcript_coding = entry.ensembl_transcript_coding
        return entry

    def _transform_entry_gt_fields(self, entry):
        """Transform result entry and set ``gt``, ``dp``, ``ad``, ``gq``."""
        genotype_data = dict()
        dp_data = dict()
        ad_data = dict()
        gq_data = dict()
        for patient, data in entry.genotype.items():
            genotype_data[patient] = data["gt"]
            dp_data[patient] = data["dp"]
            ad_data[patient] = data["ad"]
            gq_data[patient] = data["gq"]
        entry.gt = genotype_data
        entry.dp = dp_data
        entry.ad = ad_data
        entry.gq = gq_data
        return entry

    def _form_valid_file(self, form):
        """The form is valid, we want to asynchronously build a file for later download."""
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {}".format(
                    form.cleaned_data["result_type"], self.get_case_object().name
                ),
                project=self._get_project(self.request, self.kwargs),
                job_type="variants.export_file_bg_job",
            )
            export_job = ExportFileBgJob.objects.create(
                project=self._get_project(self.request, self.kwargs),
                bg_job=bg_job,
                case=self.get_case_object(),
                query_args=json.dumps(form.cleaned_data),
                file_type=form.cleaned_data["result_type"],
            )
        messages.info(
            self.request,
            "Created background job for your file download. "
            "After the file has been generated, you will be able to download it here.",
        )
        export_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())

    def _form_valid_render(self, form, selected_effects):
        """The form is valid, we are supposed to render an HTML table with the results."""
        pedigree = self.get_form_kwargs()["pedigree"]
        kwargs = self._build_query_kwargs(form, selected_effects)
        query, args = self._build_query_args(kwargs, form, pedigree)

        main = list(SmallVariant.objects.raw(query, args))

        for entry in main:
            self._transform_entry_interpret_database(kwargs, entry)
            self._transform_entry_gt_fields(entry)

        return render(self.request, self.template_name, self.get_context_data(main=main))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_name"] = self.get_case_object().name
        return context


class ExtendAPIView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FrequencyMixin,
    View,
):
    permission_required = "variants.view_data"

    def get(self, *args, **kwargs):
        self.kwargs = kwargs
        qb = QueryBuilder()

        key = {
            "release": self.kwargs["release"],
            "chromosome": self.kwargs["chromosome"],
            "position": self.kwargs["position"],
            "reference": self.kwargs["reference"],
            "alternative": self.kwargs["alternative"],
        }

        query = qb.build_knowngeneaa_query(self.kwargs)
        knowngeneaa = list(KnowngeneAA.objects.raw(*query))
        knowngeneaa_list = list()
        if len(knowngeneaa) > 0:
            for entry in knowngeneaa:
                knowngeneaa_list.append(
                    {
                        "chromosome": entry.chromosome,
                        "start": entry.start,
                        "end": entry.end,
                        "alignment": entry.alignment,
                    }
                )

        self.kwargs["knowngeneaa"] = knowngeneaa_list

        self.get_frequencies(fields=("af", "hom", "het"))

        try:
            filter_key = dict(key)
            filter_key["position"] = int(filter_key["position"]) - 1
            clinvar_list = list()
            clinvar = list(Clinvar.objects.filter(**filter_key))
            for entry in clinvar:
                clinvar_list.append(
                    {
                        "clinical_significance": entry.clinical_significance,
                        "all_traits": list({trait.lower() for trait in entry.all_traits}),
                    }
                )
            self.kwargs["clinvar"] = clinvar_list
            # response["clinvar"] = [model_to_dict(m) for m in clinvar]
        except ObjectDoesNotExist:
            self.kwargs["clinvar"] = None

        # return Response(response)
        return HttpResponse(json.dumps(self.kwargs), content_type="application/json")


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
    template_name = "variants/export_job_view.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


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
    template_name = "variants/export_job_view.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, request, *args, **kwargs):
        try:
            content_types = {
                "tsv": " text/tab-separated-values",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            obj = self.get_object()
            return HttpResponse(
                obj.export_result.payload, content_type=content_types[obj.file_type]
            )
        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e
