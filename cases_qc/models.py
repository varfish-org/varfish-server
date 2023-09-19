import uuid as uuid_object

from django.contrib.postgres.fields import ArrayField
from django.db import models

from cases.models import Case

#: Maximal array length
MAX_ARRAY_LENGTH = 10_000


class CaseQc(models.Model):
    """Quality control metrics set for one case."""

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The case this QC set belong to
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=False, blank=False, unique=True)


class FragmentLengthHistogram(models.Model):
    """Histogram of fragment lengths for one sample in a case.

    The histogram is stored in a sparse fashion, storing values and their counts.  In the case of
    more than ``MAX_ARRAY_LENGTH`` entries, the histogram must be truncated which is done in the
    import code and which will truncate reading the lines.
    """

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The QC metric set this histogram belongs to
    case_qc = models.ForeignKey(CaseQc, on_delete=models.CASCADE, null=False, blank=False)
    #: The sample this histogram belongs to
    sample = models.CharField(max_length=200, null=False, blank=False)
    #: The histogram keys
    keys = ArrayField(models.IntegerField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)
    # The histogram values
    values = ArrayField(models.IntegerField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)
