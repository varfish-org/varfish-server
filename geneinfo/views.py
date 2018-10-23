from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.views.generic import TemplateView
from .models import Hgnc, Mim2geneMedgen, Hpo
from pathways.models import EnsemblToKegg, RefseqToKegg, KeggInfo


class GeneView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    TemplateView,
):
    permission_required = "geneinfo.view_data"
    template_name = "geneinfo/gene.html"

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

        return render(self.request, self.template_name, self.get_context_data(**kwargs))
