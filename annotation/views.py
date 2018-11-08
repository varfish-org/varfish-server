from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import ProjectContextMixin
from .models import Annotation
from django.forms.models import model_to_dict
from frequencies.views import FrequencyMixin
from dbsnp.models import Dbsnp
from pathways.models import KeggInfo, RefseqToKegg, EnsemblToKegg
from clinvar.models import Clinvar
from geneinfo.models import Hgnc, Mim2geneMedgen, Hpo
from django.views.generic import TemplateView
from querybuilder.models_support import KnownGeneAAQuery
from variants.views import AlchemyConnectionMixin


class VariantView(ProjectContextMixin, FrequencyMixin, AlchemyConnectionMixin, TemplateView):

    template_name = "annotation/variant.html"

    def get(self, *args, **kwargs):
        self.kwargs = kwargs
        key = {
            "release": self.kwargs["release"],
            "chromosome": self.kwargs["chromosome"],
            "position": int(self.kwargs["position"]),
            "reference": self.kwargs["reference"],
            "alternative": self.kwargs["alternative"],
        }

        annotation = list(Annotation.objects.filter(**key, database=self.kwargs["database"]))
        annotation = [model_to_dict(entry) for entry in annotation]
        knowngeneaa_query = KnownGeneAAQuery(self.get_alchemy_connection())
        knowngeneaa_list = list()

        for entry in knowngeneaa_query.run(self.kwargs):
            knowngeneaa_list.append(
                {
                    "chromosome": entry.chromosome,
                    "start": entry.start,
                    "end": entry.end,
                    "alignment": entry.alignment,
                }
            )

        self.kwargs["knowngeneaa"] = knowngeneaa_list

        try:
            self.kwargs["rsid"] = Dbsnp.objects.get(**key).rsid
        except ObjectDoesNotExist:
            self.kwargs["rsid"] = None

        self.kwargs.update(self.get_frequencies(key))

        if not annotation:
            raise Exception("Annotation is missing?")

        gene_id = annotation[0]["gene_id"]

        try:
            if self.kwargs["database"] == "ensembl":
                self.kwargs["hgnc"] = model_to_dict(Hgnc.objects.get(ensembl_gene_id=gene_id))
            elif self.kwargs["database"] == "refseq":
                self.kwargs["hgnc"] = model_to_dict(Hgnc.objects.get(entrez_id=gene_id))
        except ObjectDoesNotExist:
            self.kwargs["hgnc"] = None

        if self.kwargs["database"] == "ensembl":
            kegg = EnsemblToKegg.objects.filter(gene_id=gene_id)
        elif self.kwargs["database"] == "refseq":
            kegg = RefseqToKegg.objects.filter(gene_id=gene_id)

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
        key2["position"] = key2["position"]
        clinvar = Clinvar.objects.filter(**key2)
        clinvar_list = list()
        for entry in clinvar:
            clinvar_list.append(
                {
                    "clinical_significance": entry.clinical_significance,
                    "all_traits": {trait.lower() for trait in entry.all_traits},
                }
            )

        self.kwargs["clinvar"] = clinvar_list

        if not self.kwargs["hgnc"]:
            self.kwargs["mim2genemedgen"] = None
            self.kwargs["hgncomim"] = None
        else:
            self.kwargs["mim2genemedgen"] = {
                omim.omim_id: Hpo.objects.filter(database_id="OMIM:{}".format(omim.omim_id))
                for omim in Mim2geneMedgen.objects.filter(
                    entrez_id=self.kwargs["hgnc"]["entrez_id"]
                )
            }
            self.kwargs["hgncomim"] = {
                self.kwargs["hgnc"]["omim_id"]: Hpo.objects.filter(
                    database_id="OMIM:{}".format(self.kwargs["hgnc"]["omim_id"])
                )
            }

        return render(
            self.request, self.template_name, self.get_context_data(data=annotation, **self.kwargs)
        )
