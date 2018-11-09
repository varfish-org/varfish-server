from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import ProjectContextMixin
from django.forms.models import model_to_dict
from django.views.generic import TemplateView
from .models import Hgnc, Mim2geneMedgen, Hpo
from pathways.models import EnsemblToKegg, RefseqToKegg, KeggInfo


class GeneCardMixin:
    """Mixin for filling the different parts of the gene card template"""

    def _fill_hgnc_info(self, transcript_database, gene_id):
        """Fill the HGNC info"""
        try:
            if transcript_database == "ensembl":
                return model_to_dict(Hgnc.objects.get(ensembl_gene_id=gene_id))
            else:
                return model_to_dict(Hgnc.objects.get(entrez_id=gene_id))
        except ObjectDoesNotExist:
            return None

    def _fill_kegg_info(self, transcript_database, gene_id):
        """Fill the kegg info"""
        if transcript_database == "ensembl":
            kegg = EnsemblToKegg.objects.filter(gene_id=gene_id)
        else:  # transcript_database == "refseq"
            kegg = RefseqToKegg.objects.filter(gene_id=gene_id)

        kegg_list = list()
        for entry in kegg:
            try:
                kegg_list.append(model_to_dict(KeggInfo.objects.get(id=entry.kegginfo_id)))
            except ObjectDoesNotExist:
                pass
        return kegg_list

    def _fill_omim_info(self, hgnc):
        """Fill the HPO/OMIM info"""
        mim2genemedgen = None
        hgncomim = None

        if hgnc:
            # we can have multiple OMIM ids in this case
            mim2genemedgen = dict()
            for omim in Mim2geneMedgen.objects.filter(entrez_id=hgnc["entrez_id"]):
                mimhpo_result = Hpo.objects.filter(database_id="OMIM:{}".format(omim.omim_id))
                if mimhpo_result:
                    mim2genemedgen[str(omim.omim_id)] = [
                        model_to_dict(hpo) for hpo in mimhpo_result
                    ]

            # in this case we just have a single omim id.
            hgncomim = dict()
            omimhpo_result = Hpo.objects.filter(database_id="OMIM:{}".format(hgnc["omim_id"]))
            if omimhpo_result:
                hgncomim[hgnc["omim_id"]] = [model_to_dict(hpo) for hpo in omimhpo_result]

        return mim2genemedgen, hgncomim


class GeneView(ProjectContextMixin, GeneCardMixin, TemplateView):
    template_name = "geneinfo/gene.html"

    def get(self, *args, **kwargs):
        kwargs_copy = dict(kwargs)
        gene_id = kwargs_copy["gene_id"]
        transcript_database = "ensembl" if kwargs_copy["gene_id"].startswith("ENSG") else "refseq"

        kwargs_copy["hgnc"] = self._fill_hgnc_info(transcript_database, gene_id)
        kwargs_copy["kegg"] = self._fill_kegg_info(transcript_database, gene_id)
        kwargs_copy["mim2genemedgen"], kwargs_copy["hgncomim"] = self._fill_omim_info(
            kwargs_copy["hgnc"]
        )

        return render(self.request, self.template_name, self.get_context_data(**kwargs_copy))
