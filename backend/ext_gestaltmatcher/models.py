from django.db import models


# Create your models here.
class SmallVariantQueryGestaltMatcherScores(models.Model):
    """Annotate ``SmallVariantQuery`` with Gestalt Matcher scores (if configured to do so)."""

    #: The query to annotate.
    query = models.ForeignKey("variants.SmallVariantQuery", on_delete=models.CASCADE)

    #: The Entrez gene ID.
    gene_id = models.CharField(max_length=64, null=False, blank=False, help_text="Entrez gene ID")

    #: The gene symbol.
    gene_symbol = models.CharField(
        max_length=128, null=False, blank=False, help_text="The gene symbol"
    )

    #: The priority type.
    priority_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The priority type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The gene score")


class SmallVariantQueryPediaScores(models.Model):
    """Annotate ``SmallVariantQuery`` with PEDIA scores (if configured to do so)."""

    #: The query to annotate.
    query = models.ForeignKey("variants.SmallVariantQuery", on_delete=models.CASCADE)

    #: The Entrez gene ID.
    gene_id = models.CharField(max_length=64, null=False, blank=False, help_text="Entrez gene ID")

    #: The gene symbol.
    gene_symbol = models.CharField(
        max_length=128, null=False, blank=False, help_text="The gene symbol"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The gene score")
