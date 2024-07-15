"""Models and supporting code for SV background databases"""

import uuid as uuid_object

from django.db import models
from django.urls import reverse

from svs.models.records import SV_TYPE_CHOICES
from variants.models import SiteBgJobBase


class BackgroundSvSetManager(models.Manager):
    def latest_active_if_any(self):  # -> typing.Optional[BackgroundSvSet]
        qs = self.filter(state="active").order_by("-date_created")
        if qs.count():
            return qs[0]
        else:
            return None


class BackgroundSvSet(models.Model):
    """A set of ``BackgroundSv`` records."""

    objects = BackgroundSvSetManager()

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Release of genomebuild
    genomebuild = models.CharField(max_length=32, default="GRCh37")
    #: VarFish version used for building the set.
    varfish_version = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="Version of varfish server used to build the set",
    )
    #: Status of the set (goes linearly through the states).
    state = models.CharField(
        max_length=32,
        choices=(
            ("initial", "initial"),
            ("building", "build in progress"),
            ("ready", "ready but not active"),
            ("active", "active"),
            ("inactive", "inactive"),
            ("deleting", "deletion in progress"),
        ),
        default="initial",
    )


class BackgroundSv(models.Model):
    """A structural variant background record."""

    #: The ``BackgroundSvSet`` that this record belongs to.
    bg_sv_set = models.ForeignKey(to=BackgroundSvSet, on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Chromosome as number
    chromosome_no = models.IntegerField()
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - chromosome of end position
    chromosome2 = models.CharField(max_length=32)
    #: Chromosome as number (of end position)
    chromosome_no2 = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Paried-end orientation
    pe_orientation = models.CharField(
        max_length=4,
        choices=(("3to3", "3to3"), ("3to5", "3to5"), ("5to3", "5to3"), ("5to5", "5to5")),
        blank=True,
        null=True,
    )

    #: The type of the structural variant.
    sv_type = models.CharField(max_length=32, choices=SV_TYPE_CHOICES)
    #: The bin for indexing.
    bin = models.IntegerField()

    #: Number of source records
    src_count = models.IntegerField()
    #: Number of carriers
    carriers = models.IntegerField()
    #: Number of het. carriers
    carriers_het = models.IntegerField()
    #: Number of hom. carriers
    carriers_hom = models.IntegerField()
    #: Number of hemizygous carriers
    carriers_hemi = models.IntegerField()

    class Meta:
        indexes = (models.Index(fields=["bg_sv_set_id", "release", "chromosome", "bin"]),)


class BuildBackgroundSvSetJob(SiteBgJobBase):
    """Background job for building a SV background set."""

    #: Task description for logging.
    task_desc = 'Refreshing background SV set (aka "in-house database")'

    #: String identifying model in BackgroundJob.
    spec_name = "svs.build_bg_sv_set"

    #: The release to build the background sv set for.
    genomebuild = models.CharField(max_length=32, default="GRCh37")

    def get_human_readable_type(self):
        return "Build background SV set"

    def get_absolute_url(self):
        return reverse("svs:build-bg-sv-set-job-detail", kwargs={"job": self.sodar_uuid})


class CleanupBackgroundSvSetJob(SiteBgJobBase):
    """Background job cleaning up building background SV sets."""

    #: Task description for logging.
    task_desc = "Cleaning up building background SV sets"

    #: String identifying model in BackgroundJob.
    spec_name = "svs.cleanup_bg_sv_sets"

    def get_human_readable_type(self):
        return "Cleanup building background SV set"

    def get_absolute_url(self):
        return reverse("svs:cleanup-bg-sv-set-job-detail", kwargs={"job": self.sodar_uuid})
