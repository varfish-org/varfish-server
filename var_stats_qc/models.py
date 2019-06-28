"""Models for the ``var_stats_qc`` module."""

from django.db import models
from postgres_copy import CopyManager


class CopyManagerInMigration(CopyManager):
    """This sub class only exists to enforce using it in migrations."""

    use_in_migrations = True


class ReferenceSite(models.Model):
    """A reference site used for the QC."""

    #: The genome release.
    release = models.CharField(max_length=32)
    #: The chromosome.
    chromosome = models.CharField(max_length=32)
    #: The 1-based position.
    start = models.IntegerField()
    #: The reference allele.
    reference = models.CharField(max_length=1)
    #: The alternative allele.
    alternative = models.CharField(max_length=1)

    #: Enable COPY FROM support.
    objects = CopyManagerInMigration()

    class Meta:
        unique_together = ("release", "chromosome", "start", "reference", "alternative")
        indexes = [models.Index(fields=["release", "chromosome", "start"])]
