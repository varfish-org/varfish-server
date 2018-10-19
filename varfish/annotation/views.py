from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import LoggedInPermissionMixin, \
    ProjectContextMixin, ProjectPermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Annotation
from django.forms.models import model_to_dict
from varfish.conservation.models import KnowngeneAA
from varfish.frequency.views import FrequencyMixin
from varfish.dbsnp.models import Dbsnp
from varfish.pathways.models import KeggInfo, RefseqToKegg, EnsemblToKegg
from varfish.geneinfo.models import Hgnc, Mim2geneMedgen, Hpo
from django.views.generic import TemplateView


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

        return render(
            self.request, self.template_name, self.get_context_data(data=annotation, **self.kwargs)
        )

