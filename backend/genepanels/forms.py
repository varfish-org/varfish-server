from django import forms
from django.conf import settings
from django.db import transaction
import requests

from genepanels.models import GenePanel, GenePanelCategory, GenePanelEntry, GenePanelState


class GenePanelCategoryForm(forms.ModelForm):
    class Meta:
        model = GenePanelCategory
        fields = ("title", "description")


def _label_from_instance(obj):
    return obj.title


class GenePanelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].to_field_name = "sodar_uuid"
        self.fields["category"].label_from_instance = _label_from_instance
        self.fields["genes"] = self._build_genes_field()

    def _build_genes_field(self):
        if self.instance.pk:
            rows = [entry.symbol for entry in self.instance.genepanelentry_set.all()]
            initial_value = "\n".join(rows)
        else:
            initial_value = ""
        return forms.CharField(
            label="Genes",
            widget=forms.Textarea,
            required=False,
            help_text=(
                "Enter gene identifiers as &lt;gene symbol&gt;, HGNC:&lt;id&gt;, ENSG&lt;id&gt;, or NCBI/Entrez"
                "&lt;id&gt; line by line.  Everything behind the first space will be ignored on each line.  On form "
                "submission, your primary symbol will be checked for validity and the correspoding other identifiers "
                "(and the current symbol by our database) will be added."
            ),
            initial=initial_value,
        )

    def _get_geneinfos(self, gene_list):
        if not gene_list:
            return {}
        base_url = settings.VARFISH_BACKEND_URL_ANNONARS
        if not base_url:
            return
        url_tpl = "{base_url}/genes/lookup?q={gene_list_joined}"
        url = url_tpl.format(base_url=base_url, gene_list_joined=",".join(gene_list))
        try:
            res = requests.request(method="get", url=url)
            if not res.status_code == 200:
                raise ConnectionError(
                    "ERROR: Server responded with status {} and message {}".format(
                        res.status_code, res.text
                    )
                )
            else:
                records = res.json()
        except requests.ConnectionError as e:
            raise ConnectionError("ERROR: annonars nor responding.") from e
        return records["genes"]

    def clean(self):
        result = super().clean()
        # Validate the genes and store related entries
        gene_list = [line.split()[0] for line in result["genes"].splitlines()]
        records = self._get_geneinfos(gene_list)
        given_set = set(gene_list)
        found_set = {k for k, v in records.items() if v}
        not_found = given_set - found_set
        if not_found:
            self.add_error(
                "genes",
                "The following gene identifiers were invalid: {}".format(", ").join(not_found),
            )
        # Check that there our version is > any active/retired version and adjust if necessary.
        old_panels = (
            GenePanel.objects.filter(identifier=self.instance.identifier)
            .exclude(pk=self.instance.pk)
            .reverse()
        )
        if old_panels:
            old_panel = old_panels[0]
            if (old_panel.version_major, old_panel.version_minor) >= (
                self.instance.version_major,
                self.instance.version_minor,
            ):
                result["version_major"] = old_panel.version_major
                result["version_minor"] = old_panel.version_minor + 1
        # Retire any old active gene panels.
        old_panels = GenePanel.objects.filter(
            identifier=self.instance.identifier, state=GenePanelState.ACTIVE.value
        )
        for old_panel in old_panels:
            old_panel.state = GenePanelState.RETIRED.value
            old_panel.save()
        return result

    @transaction.atomic
    def save(self):
        instance = super().save(commit=True)
        # Remove old gene panel entries
        GenePanelEntry.objects.filter(panel=self.instance).delete()
        # Add new gene panel entries
        gene_list = [line.split()[0] for line in self.cleaned_data["genes"].splitlines()]
        records = self._get_geneinfos(gene_list)
        for gene_info in records.values():
            if not gene_info:
                continue
            entry = GenePanelEntry(
                panel=instance,
                hgnc_id=gene_info.get("hgnc_id"),
                ensembl_id=gene_info.get("ensembl_gene_id"),
                ncbi_id=gene_info.get("ncbi_gene_id"),
                symbol=gene_info["symbol"],
            )
            entry.save()

    class Meta:
        model = GenePanel
        fields = (
            "identifier",
            "version_major",
            "version_minor",
            "category",
            "title",
            "description",
        )
