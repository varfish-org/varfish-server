from django.shortcuts import render
from django.views.generic import FormView, ListView, TemplateView, View
from django.http import HttpResponse
#from rest_framework.views import APIView
#from rest_framework.response import Response
#from django.contrib import messages
from django.forms.models import model_to_dict
from .forms import FilterForm
from .models import SmallVariant, Case, Hgnc, Annotation, Exac, Clinvar, GnomadExomes, EnsemblToKegg, RefseqToKegg, KeggInfo, \
    Mim2geneMedgen, Hpo, Dbsnp, KnowngeneAA, GnomadGenomes, ThousandGenomes
from .models_support import QueryBuilder
import json
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import LoggedInPermissionMixin, \
    ProjectContextMixin, ProjectPermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class FrequencyMixin:
    def get_frequencies(self, fields=("af", "an", "ac", "hom", "het", "hemi")):
        key = {
            'release': self.kwargs["release"],
            'chromosome': self.kwargs["chromosome"],
            'position': int(self.kwargs["position"]),
            'reference': self.kwargs["reference"],
            'alternative': self.kwargs["alternative"],
        }

        qb = QueryBuilder()
        dbs = (
            (GnomadExomes, qb.build_gnomadexomes_query(key), "gnomadexomes", ("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas")),
            (GnomadGenomes, qb.build_gnomadgenomes_query(key), "gnomadgenomes", ("afr", "amr", "asj", "eas", "fin", "nfe", "oth")),
            (Exac, qb.build_exac_query(key), "exac", ("afr", "amr", "eas", "fin", "nfe", "oth", "sas")),
            (ThousandGenomes, qb.build_thousandgenomes_query(key), "thousandgenomes", ("afr", "amr", "eas", "eur", "sas")),
        )

        for db, query, name, populations in dbs:
            self.kwargs[name] = dict()
            results = list(db.objects.raw(*query))

            if len(results) == 0:
                continue

            if len(results) > 1:
                raise Exception('Got more than one object.')

            results = results[0]

            for typ in fields:
                if name == "thousandgenomes" and typ == "hemi":
                    continue

                self.kwargs[name][typ] = getattr(results, typ)

                if name == "thousandgenomes" and not typ == "af":
                    continue

                for population in populations:
                    typpop = "{}_{}".format(typ, population)
                    self.kwargs[name][typpop] = getattr(results, typpop)


class MainView(LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin,
                ProjectContextMixin, ListView):
    template_name = "main/case_select.html"
    permission_required = 'varfish.main.view_data'
    model = Case


class FilterView(LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin,
                ProjectContextMixin, FormView):
    template_name = "main/filter.html"
    permission_required = 'varfish.main.view_data'
    form_class = FilterForm
    success_url = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.case_object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if not self.case_object:
            self.case_object = model_to_dict(
                Case.objects.get(name=self.kwargs["case_name"])
            )
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
            "case_name": self.kwargs["case_name"],
            "exac_frequency": float(form.cleaned_data["exac_frequency"]) if form.cleaned_data["exac_frequency"] else None,
            "exac_homozygous": int(form.cleaned_data["exac_homozygous"]) if form.cleaned_data["exac_homozygous"] else None,
            "exac_heterozygous": int(form.cleaned_data["exac_heterozygous"]) if form.cleaned_data["exac_heterozygous"] else None,
            "gnomad_genomes_frequency": float(form.cleaned_data["gnomad_genomes_frequency"]) if form.cleaned_data["gnomad_genomes_frequency"] else None,
            "gnomad_genomes_homozygous": int(form.cleaned_data["gnomad_genomes_homozygous"]) if form.cleaned_data["gnomad_genomes_homozygous"] else None,
            "gnomad_genomes_heterozygous": int(form.cleaned_data["gnomad_genomes_heterozygous"]) if form.cleaned_data["gnomad_genomes_heterozygous"] else None,
            "gnomad_exomes_frequency": float(form.cleaned_data["gnomad_exomes_frequency"]) if form.cleaned_data["gnomad_exomes_frequency"] else None,
            "gnomad_exomes_homozygous": int(form.cleaned_data["gnomad_exomes_homozygous"]) if form.cleaned_data["gnomad_exomes_homozygous"] else None,
            "gnomad_exomes_heterozygous": int(form.cleaned_data["gnomad_exomes_heterozygous"]) if form.cleaned_data["gnomad_exomes_heterozygous"] else None,
            "thousand_genomes_frequency": float(form.cleaned_data["thousand_genomes_frequency"]) if form.cleaned_data["thousand_genomes_frequency"] else None,
            "thousand_genomes_homozygous": int(form.cleaned_data["thousand_genomes_homozygous"]) if form.cleaned_data["thousand_genomes_homozygous"] else None,
            "thousand_genomes_heterozygous": int(form.cleaned_data["thousand_genomes_heterozygous"]) if form.cleaned_data["thousand_genomes_heterozygous"] else None,
            "effects": selected_effects,
            "genotype": list(),
            "gene_blacklist": [
                x.strip() for x in form.cleaned_data["gene_blacklist"].split()
            ],
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

        return render(
            self.request, self.template_name, self.get_context_data(main=main)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_name"] = self.kwargs["case_name"]
        return context


class GeneView(LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin,
                ProjectContextMixin, TemplateView):
    permission_required = 'varfish.main.view_data'
    template_name = "main/gene.html"

    def get(self, *args, **kwargs):
        try:
            if kwargs["gene_id"].startswith("ENSG"):
                kwargs["hgnc"] = model_to_dict(Hgnc.objects.get(ensembl_gene_id=kwargs["gene_id"]))
            else:
                kwargs["hgnc"] = model_to_dict(Hgnc.objects.get(entrez_id=kwargs["gene_id"]))
        except ObjectDoesNotExist:
            kwargs["hgnc"] = None

        if kwargs["gene_id"].startswith("ENSG"):
            kegg = EnsemblToKegg.objects.filter(gene_id=kwargs["gene_id"])
        else:
            kegg = RefseqToKegg.objects.filter(gene_id=kwargs["gene_id"])

        kegg_list = list()
        for entry in kegg:
            try:
                kegg_list.append(model_to_dict(KeggInfo.objects.get(id=entry.kegginfo_id)))
            except ObjectDoesNotExist:
                pass

        kwargs["kegg"] = kegg_list

        if not kwargs["gene_id"].startswith("ENSG"):
            omim = Mim2geneMedgen.objects.filter(entrez_id=kwargs["gene_id"])
            hpo_list = list()
            for entry in omim:
                hpo_list.append(Hpo.objects.filter(database_id="OMIM:{}".format(entry.omim_id)))
            kwargs["omim"] = hpo_list

        return render(
            self.request, self.template_name, self.get_context_data(**kwargs)
        )


class VariantView(LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin,
                ProjectContextMixin, FrequencyMixin, TemplateView):
    template_name = "main/variant.html"
    permission_required = 'varfish.main.view_data'

    def get(self, *args, **kwargs):
        self.kwargs = kwargs
        key = {
            'release': self.kwargs["release"],
            'chromosome': self.kwargs["chromosome"],
            'position': int(self.kwargs["position"]),
            'reference': self.kwargs["reference"],
            'alternative': self.kwargs["alternative"],
        }

        qb = QueryBuilder()
        # dbs = (
        #     (GnomadExomes, qb.build_gnomadexomes_query(key), "gnomadexomes"),
        #     (GnomadGenomes, qb.build_gnomadgenomes_query(key), "gnomadgenomes"),
        #     (Exac, qb.build_exac_query(key), "exac"),
        # )

        annotation = list(Annotation.objects.filter(**key, database=self.kwargs["database"]))

        knowngeneaa_query = qb.build_knowngeneaa_query(self.kwargs)
        knowngeneaa = list(KnowngeneAA.objects.raw(*knowngeneaa_query))
        knowngeneaa_list = list()
        if len(knowngeneaa) > 0:
            for entry in knowngeneaa:
                knowngeneaa_list.append({
                    'chromosome': entry.chromosome,
                    'start': entry.start,
                    'end': entry.end,
                    'alignment': entry.alignment,
                })

        self.kwargs["knowngeneaa"] = knowngeneaa_list

        try:
            self.kwargs["rsid"] = Dbsnp.objects.get(**key).rsid
        except ObjectDoesNotExist:
            self.kwargs["rsid"] = None

        self.get_frequencies(fields=("af", "an", "ac", "hom", "het", "hemi"))
        # for db, query, name in dbs:
        #     kwargs[name] = dict()
        #     results = list(db.objects.raw(*query))
        #
        #     if len(results) == 0:
        #         continue
        #
        #     if len(results) > 1:
        #         raise Exception('Got more than one object.')
        #
        #     results = results[0]
        #
        #     for typ in ("af", "an", "ac", "hom", "het", "hemi"):
        #         kwargs[name][typ] = getattr(results, typ)
        #         for population in ("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"):
        #             if name == "exac" and population == "asj":
        #                 continue
        #             if name == "gnomadgenomes" and population == "sas":
        #                 continue
        #             typpop = "{}_{}".format(typ, population)
        #             kwargs[name][typpop] = getattr(results, typpop)

        try:
            if self.kwargs["database"] == "ensembl":
                self.kwargs["hgnc"] = model_to_dict(Hgnc.objects.get(ensembl_gene_id=annotation[0].gene_id))
            elif self.kwargs["database"] == "refseq":
                self.kwargs["hgnc"] = model_to_dict(Hgnc.objects.get(entrez_id=annotation[0].gene_id))
        except ObjectDoesNotExist:
            self.kwargs["hgnc"] = None

        if self.kwargs["database"] == "ensembl":
            kegg = EnsemblToKegg.objects.filter(gene_id=annotation[0].gene_id)
        elif self.kwargs["database"] == "refseq":
            kegg = RefseqToKegg.objects.filter(gene_id=annotation[0].gene_id)

        kegg_list = list()
        for entry in kegg:
            try:
                kegg_list.append(model_to_dict(KeggInfo.objects.get(id=entry.kegginfo_id)))
            except ObjectDoesNotExist:
                pass

        self.kwargs["kegg"] = kegg_list

        # for var in ("symbol", "name", "location", "ucsc_id", "entrez_id", "ensembl_gene_id", "omim_id", "cosmic", "rsid",
        # "alias_name", "gene_family"):
        #     kwargs[var] = getattr(annotation[0], var)

        # for var in (
        # "symbol", "name", "location", "ucsc_id", "entrez_id", "ensembl_gene_id", "omim_id", "cosmic", "rsid",
        # "alias_name", "gene_family"):
        #     kwargs[var] = getattr(data[0], var)

        # clinvar is not in the main query, because it inflates the datatables. I just need the clinvar entries once,
        # not #transcript-times.
        key2 = dict(key)
        key2["position"] = key2["position"] - 1
        clinvar = Clinvar.objects.filter(**key2)
        clinvar_list = list()
        for entry in clinvar:
            clinvar_list.append({
                "clinical_significance": entry.clinical_significance,
                "all_traits": {trait.lower() for trait in entry.all_traits}
            })

        self.kwargs["clinvar"] = clinvar_list
        self.kwargs["mim2genemedgen"] = {
            omim.omim_id: Hpo.objects.filter(database_id="OMIM:{}".format(omim.omim_id)) for omim in
            Mim2geneMedgen.objects.filter(entrez_id=self.kwargs["hgnc"]["entrez_id"])
        }
        self.kwargs["hgncomim"] = {
            self.kwargs["hgnc"]["omim_id"]: Hpo.objects.filter(database_id="OMIM:{}".format(self.kwargs["hgnc"]["omim_id"]))
        }

        # for entry in omim:
        #     hpo_list.append(Hpo.objects.filter(database_id="OMIM:{}".format(entry.omim_id)))
        #
        # kwargs["omim"] = hpo_list
        #
        # for entry in data:
        #     match = re.search(REGEX, entry.hgvs_c)
        #     if match:
        #         entry.mt_loc = int(match.group(1))

        # return render(
        #     self.request, self.template_name, self.get_context_data(data=data, **kwargs)
        # )

        return render(
            self.request, self.template_name, self.get_context_data(data=annotation, **self.kwargs)
        )


# Switch to API view when integrating in SODAR
#class ExtendAPIView(APIView):
class ExtendAPIView(LoginRequiredMixin, LoggedInPermissionMixin, ProjectPermissionMixin,
                ProjectContextMixin, FrequencyMixin, View):
    permission_required = 'varfish.main.view_data'

    def get(self, *args, **kwargs):
        self.kwargs = kwargs
        qb = QueryBuilder()
        # dbs = (
        #     (GnomadExomes, qb.build_gnomadexomes_query(kwargs), "gnomadexomes"),
        #     (GnomadGenomes, qb.build_gnomadgenomes_query(kwargs), "gnomadgenomes"),
        #     (Exac, qb.build_exac_query(kwargs), "exac")
        # )

        key = {
            "release": self.kwargs["release"],
            "chromosome": self.kwargs["chromosome"],
            "position": self.kwargs["position"],
            "reference": self.kwargs["reference"],
            "alternative": self.kwargs["alternative"],
        }

        #response = dict(key)
        query = qb.build_knowngeneaa_query(self.kwargs)
        knowngeneaa = list(KnowngeneAA.objects.raw(*query))
        knowngeneaa_list = list()
        if len(knowngeneaa) > 0:
            for entry in knowngeneaa:
                knowngeneaa_list.append({
                    'chromosome': entry.chromosome,
                    'start': entry.start,
                    'end': entry.end,
                    'alignment': entry.alignment,
                })

        self.kwargs["knowngeneaa"] = knowngeneaa_list

        self.get_frequencies(fields=("af", "hom", "het"))
        # for db, query, name in dbs:
        #     response[name] = dict()
        #     results = list(db.objects.raw(*query))
        #
        #     if len(results) == 0:
        #         continue
        #
        #     if len(results) > 1:
        #         raise Exception('Got more than one object.')
        #
        #     results = results[0]
        #
        #     for typ in ("af", "hom", "het"):
        #         response[name][typ] = getattr(results, typ)
        #         for population in ("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"):
        #             if name == "exac" and population == "asj":
        #                 continue
        #             if name == "gnomadgenomes" and population == "sas":
        #                 continue
        #             typpop = "{}_{}".format(typ, population)
        #             response[name][typpop] = getattr(results, typpop)

        try:
            filter_key = dict(key)
            filter_key['position'] = int(filter_key['position']) - 1
            clinvar_list = list()
            clinvar = list(Clinvar.objects.filter(**filter_key))
            for entry in clinvar:
                clinvar_list.append({
                    "clinical_significance": entry.clinical_significance,
                    "all_traits": list({trait.lower() for trait in entry.all_traits})
                })
            self.kwargs["clinvar"] = clinvar_list
            # response["clinvar"] = [model_to_dict(m) for m in clinvar]
        except ObjectDoesNotExist:
            self.kwargs["clinvar"] = None

        #return Response(response)
        return HttpResponse(json.dumps(self.kwargs), content_type='application/json')
