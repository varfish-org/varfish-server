import uuid as uuid_object

from django.db import models

from cases.models import Case

#: Maximal array length for Postgres array fields
MAX_ARRAY_LENGTH = 10_000
#: Maximal length of metrics to read
MAX_METRIC_COUNT = 1000


class CaseQc(models.Model):
    """Quality control metrics set for one case."""

    #: Draft - is currently being built.
    STATE_DRAFT = "DRAFT"
    #: Active - is currently not active.
    STATE_ACTIVE = "ACTIVE"

    STATE_CHOICES = (
        (STATE_DRAFT, STATE_DRAFT),
        (STATE_ACTIVE, STATE_ACTIVE),
    )

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: State of the QC set
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default=STATE_DRAFT)
    #: The case this QC set belong to
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        #: Order by creation date
        ordering = ["-date_created"]


class CaseQcBaseModel(models.Model):
    """Base class for statistics associated with ``CaseQc``."""

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The QC metric set this histogram belongs to
    caseqc = models.ForeignKey(CaseQc, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        abstract = True


class CaseQcForSampleBaseModel(CaseQcBaseModel):
    """Base class for statistics associated with ``CaseQc`` for one sample."""

    #: The sample this histogram belongs to
    sample = models.CharField(max_length=200, null=False, blank=False)

    class Meta:
        abstract = True
