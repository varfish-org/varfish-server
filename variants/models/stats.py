"""Code for computing statistics on variants."""

import math
import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from varfish.utils import JSONField
from variants.models.projectroles import Project
from variants.models.variants import SmallVariantSet


class CaseVariantStats(models.Model):
    """Statistics on various aspects of variants of a case:

    - Ts/Tv ratio
    """

    #: The related ``SmallVariantSet``.
    variant_set = models.OneToOneField(
        SmallVariantSet,
        null=False,
        related_name="variant_stats",
        help_text="The variant statistics object for this variant set",
        on_delete=models.CASCADE,
    )


class SampleVariantStatistics(models.Model):
    """Single-number variant statistics for donors in a ``Case`` via ``CaseVariantStats``."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        CaseVariantStats,
        null=False,
        related_name="sample_variant_stats",
        help_text="Single-value variant statistics for one individual",
        on_delete=models.CASCADE,
    )

    #: The name of the donor.
    sample_name = models.CharField(max_length=200, null=False)

    #: The number of on-target transitions (A <-> G, C <-> T).
    ontarget_transitions = models.IntegerField(null=False)
    #: The number of on-target transversions.
    ontarget_transversions = models.IntegerField(null=False)

    #: The number of on-target SNVs
    ontarget_snvs = models.IntegerField(null=False)
    #: The number of on-target Indels
    ontarget_indels = models.IntegerField(null=False)
    #: The number of on-target MNVs
    ontarget_mnvs = models.IntegerField(null=False)

    #: Counts for the different variant effects
    ontarget_effect_counts = JSONField(null=False)

    #: Histogram of indel sizes.
    ontarget_indel_sizes = JSONField(null=False)
    #: Histogram of read depths.
    ontarget_dps = JSONField(null=False)
    #: 5-value summary of on-target read depths.
    ontarget_dp_quantiles = ArrayField(models.FloatField(), size=5)

    #: Overall het ratio.
    het_ratio = models.FloatField(null=False)
    #: Hom/het ratio on chrX in PAR1 and PAR2, for sex checking.
    chrx_het_hom = models.FloatField(null=False)

    def ontarget_ts_tv_ratio(self):
        """Compute Ts/Tv ratio."""
        if not self.ontarget_transversions:
            return 0.0
        else:
            return self.ontarget_transitions / self.ontarget_transversions

    class Meta:
        ordering = ("sample_name",)


class BaseRelatedness(models.Model):
    """Shared functionality of relatedness of individuals in a collective.

    This could be a pedigree or a project.
    """

    #: First sample.
    sample1 = models.CharField(max_length=200, null=False)
    #: Second sample.
    sample2 = models.CharField(max_length=200, null=False)

    #: The Het_1_2 statistic
    het_1_2 = models.IntegerField(null=False)
    #: The Het_1 statistic
    het_1 = models.IntegerField(null=False)
    #: The Het_2 statistic
    het_2 = models.IntegerField(null=False)
    #: The N_IBS0 statistic
    n_ibs0 = models.IntegerField(null=False)
    #: The N_IBS1 statistic
    n_ibs1 = models.IntegerField(null=False)
    #: The N_IBS2 statistic
    n_ibs2 = models.IntegerField(null=False)

    def relatedness(self):
        """Return relatedness following Pedersen and Quinlan (2017)."""
        if self.het_1 * self.het_2:
            return (self.het_1_2 - 2 * self.n_ibs0) * 2 / math.sqrt(self.het_1 * self.het_2)
        else:
            return 0.0

    class Meta:
        abstract = True
        ordering = ("sample1", "sample2")


class PedigreeRelatedness(BaseRelatedness):
    """Store relatedness information between two donors in a pedigree/``Case``.."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        CaseVariantStats,
        null=False,
        related_name="relatedness",
        help_text="Pedigree relatedness information",
        on_delete=models.CASCADE,
    )


class ProjectVariantStats(models.Model):
    """Statistics on various aspects of variants of all cases in a project."""

    #: The related ``Project``.
    project = models.OneToOneField(
        Project,
        null=False,
        related_name="variant_stats",
        help_text="The variant statistics object for this projects",
        on_delete=models.CASCADE,
    )


class ProjectRelatedness(BaseRelatedness):
    """Store relatedness information between two donors in a case/``Case``.."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        ProjectVariantStats,
        null=False,
        related_name="relatedness",
        help_text="Pedigree relatedness information",
        on_delete=models.CASCADE,
    )


class ComputeProjectVariantsStatsBgJob(JobModelMessageMixin, models.Model):
    """Background job for computing project variants statistics."""

    #: Task description for logging.
    task_desc = "Compute project-wide variants statistics"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.compute_project_variants_stats"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Job Specialization SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="compute_project_variants_stats",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )

    def get_human_readable_type(self):
        return "Project-wide Variant Statistics Computation"

    def get_absolute_url(self):
        return reverse(
            "variants:project-stats-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )
