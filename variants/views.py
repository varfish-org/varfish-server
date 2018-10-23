import json

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SmallVariant, Case
from frequencies.views import FrequencyMixin
from django.views.generic import FormView, View, ListView
from .forms import FilterForm
from querybuilder.models_support import QueryBuilder
from django.forms.models import model_to_dict
from conservation.models import KnowngeneAA
from clinvar.models import Clinvar
from django.http import HttpResponse


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
        self.case_object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if not self.case_object:
            self.case_object = model_to_dict(Case.objects.get(sodar_uuid=self.kwargs["case"]))
        case_object = self.case_object

        index = case_object["index"]
        father = ""
        mother = ""

        for member in case_object["pedigree"]:
            if member["patient"] == index:
                father = member["father"]
                mother = member["mother"]

        kwargs["pedigree"] = list()
        for member in case_object["pedigree"]:
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
        pedigree = self.get_form_kwargs()["pedigree"]
        selected_effects = list()
        qb = QueryBuilder()

        for field_name, effect in form.translate_effects.items():
            if form.cleaned_data[field_name]:
                selected_effects.append(effect)

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
            query, args = qb.build_comphet_query(kwargs)
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

            query, args = qb.build_top_level_query(base, conditions)

        main = list(SmallVariant.objects.raw(query, args))

        for entry in main:
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

        return render(self.request, self.template_name, self.get_context_data(main=main))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_name"] = self.case_object["name"]
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
