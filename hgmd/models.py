"""Models for ``HGMD`` annotation in VarFish.

At the moment (and for the forseeable future), only the ``HGMD_PUBLIC`` dump
from ENSEMBL can be imported.
"""

from django.db import models
from postgres_copy import CopyManager


class HgmdPublicLocus(models.Model):
    """Representation of an interval on the genome that has a HGMD_PUBLIC annotation.

    The positions are 0-based as this comes from a BED file.
    """

    #: The genome release, e.g., ``"GRCh37"``.
    release = models.CharField(max_length=32)
    #: The chromosomal, e.g., ``"1"``.
    chromosome = models.CharField(max_length=32)
    #: The start position, 0-based.
    start = models.IntegerField()
    #: The end position, 0-based.
    end = models.IntegerField()
    #: The UCSC bin.
    bin = models.IntegerField()
    #: The ``variation_name`` column from ENSEMBL variation table.
    variation_name = models.CharField(max_length=32)

    #: Enable bulk-import.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "start"])]

    def __str__(self):
        """String representation, e.g., used in Django admin."""
        values = (self.release, self.chromosome, self.start, self.end, self.variation_name)
        return "HgmdPublicLocus({})".format(", ".join(map(repr, values)))
