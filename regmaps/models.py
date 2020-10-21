"""Models for the ``regmaps`` app.

The current implementation allows to manage one or more regulatory map collections (``RegMapCollection``) via
administrator commands.
"""

import uuid as uuid_object

import binning
from django.db import models
from django.contrib.postgres.fields import JSONField

from geneinfo.models import RefseqToGeneSymbol


class RegMapCollection(models.Model):
    """A collection of regulatory maps (e.g., different cells related to bone development)."""

    #: The UUID of this regulatory map collection.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="UUID of regulatory map collection",
    )
    #: Genome build that this regulatory map collection is for.
    release = models.CharField(max_length=32)
    #: The version of this collection.
    version = models.CharField(max_length=50)
    #: The title of this collection.
    title = models.TextField()
    #: The short title of this collection.
    short_title = models.TextField()
    #: A slug for this collection.
    slug = models.SlugField(unique=True)
    #: A (markdown formatted) description of the collection.
    description = models.TextField(null=True)

    class Meta:
        indexes = [models.Index(fields=["sodar_uuid"])]
        ordering = ["title"]


class RegMap(models.Model):
    """A regulatory map (e.g., regulatory elements for a given cell type)."""

    #: The UUID of this regulatory map.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="UUID of regulatory map",
    )
    #: The regulatory map collection that this map belongs to.
    collection = models.ForeignKey(RegMapCollection)
    #: The title of the map.
    title = models.TextField()
    #: The short title of the map.
    short_title = models.TextField()
    #: A slug for this map.
    slug = models.SlugField()
    #: A (markdown formatted) description of the regulatory map.
    description = models.TextField(null=True)

    class Meta:
        indexes = [models.Index(fields=["sodar_uuid"])]
        unique_together = [["collection", "slug"]]
        ordering = ["title"]


class RegElementType(models.Model):
    """A type of regulatory element."""

    #: The UUID of this regulatory element type.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="UUID of regulatory map collection",
    )
    #: The regulatory map collection that this map belongs to.
    collection = models.ForeignKey(RegMapCollection)
    #: The title of the map.
    title = models.TextField()
    #: The short title of the map.
    short_title = models.TextField()
    #: A slug for this map.
    slug = models.SlugField()
    #: A (markdown formatted) description of the element type.
    description = models.TextField(null=True)

    class Meta:
        indexes = [models.Index(fields=["sodar_uuid"])]
        unique_together = [["collection", "slug"]]
        ordering = ["title"]


class RegElementManager(models.Manager):
    def overlapping(self, release, chromosome, start, end, padding=0):
        """Return overlapping ``RegElement`` objects."""
        return (
            super()
            .all()
            .filter(
                release=release,
                chromosome=chromosome,
                bin__in=binning.overlapping_bins(start - 1, end),
                start__lte=end + padding,
                end__gte=max(0, start - padding),
            )
        )


class RegElement(models.Model):
    """A regulatory element entry in a regulatory map."""

    objects = RegElementManager()

    #: The UUID of this regulatory element.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="UUID of regulatory element",
    )
    #: The regulatory map.
    reg_map = models.ForeignKey(RegMap)
    #: The element type.
    elem_type = models.ForeignKey(RegElementType)
    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: UCSC bin
    bin = models.IntegerField()
    #: Score of this regulatory element.
    score = models.FloatField()
    #: Extra information on this regulatory element.
    extra_data = JSONField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["sodar_uuid"]),
            models.Index(fields=["release", "chromosome", "bin"]),
        ]
        ordering = ["chromosome", "start", "end"]


class RegInteractionManager(models.Manager):
    def overlapping(self, release, chromosome, start, end, padding=0):
        """Return overlapping ``RegElement`` objects."""
        return (
            super()
            .all()
            .filter(
                release=release,
                chromosome=chromosome,
                bin__in=binning.overlapping_bins(start - 1, end),
                start__lte=end + padding,
                end__gte=max(0, start - padding),
            )
        )


class RegInteraction(models.Model):
    """An interaction in a regulatory map"""

    objects = RegInteractionManager()

    #: The UUID of this raw signal entry.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="UUID of interaction",
    )
    #: The regulatory map.
    reg_map = models.ForeignKey(RegMap)
    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: UCSC bin
    bin = models.IntegerField()
    #: The interaction score.
    score = models.FloatField()

    #: Interaction source -- Variant coordinates - chromosome
    chromosome1 = models.CharField(max_length=32)
    #: Interaction source -- Variant coordinates - 1-based start position
    start1 = models.IntegerField()
    #: Interaction source -- Variant coordinates - end position
    end1 = models.IntegerField()

    #: Interaction target -- Variant coordinates - chromosome
    chromosome2 = models.CharField(max_length=32)
    #: Interaction target -- Variant coordinates - 1-based start position
    start2 = models.IntegerField()
    #: Interaction target -- Variant coordinates - end position
    end2 = models.IntegerField()

    #: Extra information on this raw signal.
    extra_data = JSONField(null=True)

    @property
    def gene_symbol(self):
        try:
            RefseqToGeneSymbol.objects.get(
                entrez_id=self.extra_data.get("correlated_gene")
            ).gene_symbol
        except RefseqToGeneSymbol.DoesNotExist:
            return self.extra_data.get("correlated_gene")

    class Meta:
        indexes = [
            models.Index(fields=["sodar_uuid"]),
            models.Index(fields=["release", "chromosome", "bin"]),
        ]
        ordering = ["chromosome", "start", "end"]
