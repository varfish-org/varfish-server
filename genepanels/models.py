import enum
import uuid as uuid_object

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

# from django.urls import reverse

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class GenePanelCategory(models.Model):
    """A category of gene panels"""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    #: Title of the gene panel category
    title = models.CharField(
        max_length=128, null=False, blank=False, help_text="Title of the category"
    )
    #: Description of the gene panel category
    description = models.TextField(
        null=True, blank=True, help_text="Optional description of the category"
    )

    def __str__(self):
        return f"Category '{self.title}'"

    def get_absolute_url(self):
        return reverse("genepanels:category-detail", kwargs={"category": self.sodar_uuid})

    class Meta:
        # Order by identifier, most recent version last
        ordering = ("title",)


class GenePanelState(enum.Enum):
    """Enumeration for the valid states of a GenePanel."""

    #: The version of the gene panel is currently in draft
    DRAFT = "draft"
    #: The version of the gene panel is currently active
    ACTIVE = "active"
    #: The (version) of the gene panel has been retired
    RETIRED = "retired"


class GenePanel(models.Model):
    """A versioned gene panel"""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    #: Identifier of the gene panel; cannot be changed.
    identifier = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text="Identifier of the gene panel, e.g., 'osteoporosis.basic' or 'osteoporosis.extended'",
        validators=[
            RegexValidator(
                regex=r"^[\w\._-]+$",
                message="Identifier may only contain alphanumeric characters, dots, hyphens, and underscores",
            ),
        ],
    )
    #: State of the gene panel version
    state = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        default=GenePanelState.DRAFT.value,
        choices=[[state.value, state.value] for state in GenePanelState],
        help_text="State of teh gene panel version",
    )
    #: Major version of the gene panel
    version_major = models.IntegerField(
        null=False, default=1, help_text="Major version of the gene panel (by identifier)"
    )
    #: Minor version of the gene panel
    version_minor = models.IntegerField(
        null=False, default=1, help_text="Minor version of the gene panel (by identifier)"
    )
    #: The user who signed off the gene panel
    signed_off_by = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="The user who signed off the panel into active state",
    )

    #: Category of the gene panel
    category = models.ForeignKey(
        GenePanelCategory,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        help_text="Category of the gene panel",
    )
    #: Title of the gene panel
    title = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text="Title of the gene panel, only used for informative purposes",
    )
    #: Description of the gene panel
    description = models.TextField(null=True, blank=True, help_text="Description of the panel")

    class Meta:
        # Order by identifier, most recent version last
        ordering = ("identifier", "version_major", "version_minor")
        # Each gene panel version must be unique
        unique_together = ("identifier", "version_major", "version_minor")

    def get_hgnc_list(self):
        result = []
        for entry in self.genepanelentry_set.all():
            result.append(entry.hgnc_id)
        return result

    def get_absolute_url(self):
        return reverse("genepanels:genepanel-detail", kwargs={"panel": self.sodar_uuid})


class GenePanelEntry(models.Model):
    """An entry in a GenePanel"""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    #: The panel (version) that this entry is part of
    panel = models.ForeignKey(
        GenePanel,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        help_text="The gene panel that this entry belongs to",
    )

    #: The symbol, only used for informative purposes
    symbol = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text=(
            "Official gene symbol, only used for informative purposes as such symbols are NOT guaranteed to be "
            "stable, e.g., 'TGDS'"
        ),
    )
    #: The HGNC gene ID
    hgnc_id = models.CharField(
        max_length=64, null=False, blank=False, help_text="The stable HGNC ID, e.g., 'HGNC:20324"
    )
    #: The ENSEMBL gene ID
    ensembl_id = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        help_text="The stable ENSEMBL gene identifier, e.g., 'ENSG00000088451",
    )
    #: The NCBI/Entrez ID
    ncbi_id = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        help_text="The stable NCBI/Entrez gene identifier, e.g., '23483'",
    )

    class Meta:
        # Order by gene symbol
        ordering = ("symbol",)


def expand_panels_in_gene_list(gene_list):
    """Expand GENEPANEL: entries in gene_list"""
    result = []
    for gene in gene_list:
        if gene.startswith("GENEPANEL:"):
            panel_name = gene[len("GENEPANEL:") :]
            panels = GenePanel.objects.filter(
                identifier=panel_name, state=GenePanelState.ACTIVE.value
            ).prefetch_related("genepanelentry_set")
            if panels:
                for entry in panels[0].genepanelentry_set.all():
                    result.append(entry.hgnc_id)
            else:
                raise ValueError(f"Could not find gene panel: {panel_name}")
        else:
            result.append(gene)
    return result
