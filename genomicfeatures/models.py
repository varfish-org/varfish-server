import uuid as uuid_object

from django.db import models
from postgres_copy import CopyManager


class _Interval(models.Model):
    """Abstract base class for genomic feature intervals."""

    #: UUID to use for identifying this interval with the outside world.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, help_text="Interval set UUID", unique=True
    )

    #: The bin for indexing.
    bin = models.IntegerField()

    #: Genome build
    release = models.CharField(
        max_length=32, blank=False, null=False, help_text="Genome release of coordinates"
    )
    #: Coordinates - chromosome
    chromosome = models.CharField(
        max_length=32, blank=False, null=False, help_text="Chromosome of interval"
    )
    #: Coordinates - (1-based) start position
    start = models.IntegerField(
        blank=False, null=False, help_text="1-based start position of interval"
    )
    #: Coordinates - end position
    end = models.IntegerField(blank=False, null=False, help_text="end position of interval")

    class Meta:
        abstract = True

        indexes = [models.Index(fields=["release", "chromosome", "bin"])]

    def __str__(self):
        return "{}({}, {:,}, {:,})".format(
            str(self.__class__.__name__), repr(self.chromosome), self.start, self.end
        )


class TadSet(models.Model):
    """Define an interval set, e.g., a set of TADs or TAD boundaries."""

    #: UUID to use for identifying this interval set with the outside world.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, help_text="Interval set UUID", unique=True
    )

    #: Genome build
    release = models.CharField(
        max_length=32,
        blank=False,
        null=False,
        help_text="Genome release for interval set coordinates",
    )
    #: Identifier of the interval set
    name = models.CharField(
        max_length=32, unique=True, blank=False, null=False, help_text="Name of the interval set"
    )
    #: Version of the interval set.
    version = models.CharField(
        max_length=32, blank=False, null=False, help_text="Version of the interval set"
    )
    #: Title of the interval set
    title = models.TextField(
        blank=False, null=False, help_text="Name of the interval as displayed to the user"
    )
    #: Description of the interval set
    comment = models.TextField(
        blank=True, null=True, help_text="Name of the interval as displayed to the user"
    )

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        ordering = ["title"]
        unique_together = [("name", "version")]

    def __str__(self):
        return "IntervalSet(name={}, version={}, title={})".format(
            repr(self.name), repr(self.version), repr(self.title)
        )


class TadInterval(_Interval):
    """One TAD interval, e.g., one TAD or one TAD boundary."""

    #: The interval set that this interval belongs to.
    tad_set = models.ForeignKey(
        TadSet,
        related_name="tads",
        help_text="The TAD set this TAD belong to",
        on_delete=models.CASCADE,
    )


class TadBoundaryInterval(_Interval):
    """One TAD boundary interval."""

    #: The interval set that this interval belongs to.
    tad_set = models.ForeignKey(
        TadSet,
        related_name="boundaries",
        help_text="The TAD set this boundary belongs to",
        on_delete=models.CASCADE,
    )


class EnsemblRegulatoryFeature(_Interval):
    """Regulatory features from ENSEMBL."""

    #: Regulatory stable id
    stable_id = models.CharField(
        max_length=32, blank=False, null=False, help_text="ENSR ID of regulatory feature"
    )
    #: Feature type
    feature_type = models.CharField(
        max_length=64, blank=False, null=False, help_text="Short feature type"
    )
    #: Feature type description
    feature_type_description = models.CharField(
        max_length=128, blank=False, null=False, help_text="Feature type description"
    )
    #: SO term accession
    so_term_accession = models.CharField(
        max_length=64, blank=False, null=False, help_text="SO term accession"
    )
    #: SO term name
    so_term_name = models.CharField(
        max_length=256, blank=False, null=False, help_text="SO term name"
    )

    def __str__(self):
        return "EnsemblRegulatoryFeature({}, {}, {}, {})".format(
            repr(self.chromosome), self.start, self.end, self.stable_id
        )


#: Positive VISTA validation result
VISTA_POSITIVE = "positive"
#: Negative VISTA validation result
VISTA_NEGATIVE = "negative"


class VistaEnhancer(_Interval):
    """Enhancers validations from the VISTA project."""

    #: Name of the enhancer / element
    element_id = models.CharField(max_length=32, blank=False, null=False, help_text="enhancer name")

    #: The validation result
    validation_result = models.CharField(
        max_length=16,
        blank=False,
        null=False,
        help_text="Validation result",
        choices=((VISTA_POSITIVE, VISTA_POSITIVE), (VISTA_NEGATIVE, VISTA_NEGATIVE)),
    )

    def __str__(self):
        return "VistaEnhancer({}, {}, {}, {}, {})".format(
            repr(self.chromosome), self.start, self.end, self.element_id, self.validation_result
        )


class GeneInterval(_Interval):
    """Coordinate information of genes, e.g., from RefSeq."""

    #: Name of the database
    database = models.CharField(max_length=128)
    #: Identifier of the gene in the database
    gene_id = models.CharField(max_length=128)

    def __str__(self):
        return "GeneInterval(%s, %s, %s, %s, %s, %s)" % (
            self.release,
            self.chromosome,
            self.start,
            self.end,
            repr(self.database),
            repr(self.gene_id),
        )

    class Meta:
        indexes = [
            models.Index(fields=["gene_id"]),
            models.Index(fields=["database", "release", "chromosome", "bin"]),
        ]
