from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from projectroles.views import ProjectContextMixin
from .models import Annotation
from django.forms.models import model_to_dict
from frequencies.views import FrequencyMixin
from dbsnp.models import Dbsnp
from clinvar.models import Clinvar
from geneinfo.views import GeneCardMixin
from django.views.generic import TemplateView
from variants.models_support import KnownGeneAAQuery
from variants.views import AlchemyConnectionMixin


class VariantView(
    ProjectContextMixin, FrequencyMixin, GeneCardMixin, AlchemyConnectionMixin, TemplateView
):
    """View for the annotation information of a variant"""

    template_name = "annotation/variant.html"

    def get(self, *args, **kwargs):
        # make a copy of incoming arguments
        kwargs_copy = dict(kwargs)

        # define query key
        key = {
            "release": kwargs_copy["release"],
            "chromosome": kwargs_copy["chromosome"],
            "position": int(kwargs_copy["position"]),
            "reference": kwargs_copy["reference"],
            "alternative": kwargs_copy["alternative"],
        }

        # get annotation info
        annotation = [
            model_to_dict(entry)
            for entry in Annotation.objects.filter(**key, database=kwargs_copy["database"])
        ]
        if not annotation:
            raise Exception("Annotation is missing?")
        gene_id = annotation[0]["gene_id"]

        # get conservation info
        kwargs_copy["knowngeneaa"] = [
            {
                "chromosome": entry.chromosome,
                "start": entry.start,
                "end": entry.end,
                "alignment": entry.alignment,
            }
            for entry in KnownGeneAAQuery(self.get_alchemy_connection()).run(kwargs_copy)
        ]

        # get dbsnp info
        try:
            kwargs_copy["rsid"] = Dbsnp.objects.get(**key).rsid
        except ObjectDoesNotExist:
            kwargs_copy["rsid"] = None

        # get frequency info
        kwargs_copy.update(self.get_frequencies(key))

        # get clinvar info
        kwargs_copy["clinvar"] = [
            {
                "clinical_significance": entry.clinical_significance,
                "all_traits": {trait.lower() for trait in entry.all_traits},
            }
            for entry in Clinvar.objects.filter(**key)
        ]

        # get genecard info
        kwargs_copy["hgnc"] = self._fill_hgnc_info(kwargs_copy["database"], gene_id)
        kwargs_copy["kegg"] = self._fill_kegg_info(kwargs_copy["database"], gene_id)
        kwargs_copy["mim2genemedgen"], kwargs_copy["hgncomim"] = self._fill_omim_info(
            kwargs_copy["hgnc"]
        )

        return render(
            self.request, self.template_name, self.get_context_data(data=annotation, **kwargs_copy)
        )
