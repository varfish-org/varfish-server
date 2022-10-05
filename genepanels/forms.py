from django import forms
from django.db import transaction
from django.db.models import Q

from geneinfo.models import Hgnc
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
        rows = []
        for entry in self.instance.genepanelentry_set.all():
            row = [
                entry.symbol,
                entry.hgnc_id,
                entry.ensembl_id,
                entry.ncbi_id,
            ]
            rows.append(" ".join(row))
        initial_value = "\n".join(rows)
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

    def clean(self):
        result = super().clean()
        # Validate the genes and store related entries
        invalid_genes = []
        for line in result["genes"].splitlines():
            gene_id = line.split()[0]
            try:
                Hgnc.objects.get(
                    Q(hgnc_id=gene_id)
                    | Q(ensembl_gene_id=gene_id)
                    | Q(entrez_id=gene_id)
                    | Q(symbol=gene_id)
                )
            except Hgnc.DoesNotExist:
                invalid_genes.append(gene_id)
        if invalid_genes:
            self.add_error(
                "genes",
                "The following gene identifiers were invalid: {}".format(", ").join(invalid_genes),
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
        for line in self.cleaned_data["genes"].splitlines():
            gene_id = line.split()[0]
            hgnc = Hgnc.objects.get(
                Q(hgnc_id=gene_id)
                | Q(ensembl_gene_id=gene_id)
                | Q(entrez_id=gene_id)
                | Q(symbol=gene_id)
            )
            entry = GenePanelEntry(
                panel=instance,
                hgnc_id=hgnc.hgnc_id,
                ensembl_id=hgnc.ensembl_gene_id,
                ncbi_id=hgnc.entrez_id,
                symbol=hgnc.symbol,
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
