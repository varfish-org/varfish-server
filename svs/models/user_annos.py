"""Models and supporting code for user annotations (comments/flags)"""

import uuid as uuid_object

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import localtime

from variants.models import VARIANT_RATING_CHOICES, Case, HumanReadableMixin

User = get_user_model()


class _UserAnnotation(models.Model):
    """Common attributes for structural variant comments and flags"""

    #: Annotation UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Annotation UUID"
    )
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: The bin for indexing.
    bin = models.IntegerField()

    #: The genome release of the SV
    release = models.CharField(max_length=32)
    #: The chromosome of the SV
    chromosome = models.CharField(max_length=32)
    #: The start position of the SV
    start = models.IntegerField()
    #: The end position of the SV
    end = models.IntegerField()
    #: The SV type
    sv_type = models.CharField(max_length=32)
    #: The SV sub type
    sv_sub_type = models.CharField(max_length=32)

    def get_variant_description(self):
        return "({}) chr{}:{}-{}".format(self.sv_type, self.chromosome, self.start, self.end)

    def get_date_created(self):
        return localtime(self.date_created).strftime("%Y-%m-%d %H:%M")

    class Meta:
        abstract = True
        indexes = (models.Index(fields=["case", "release", "bin"]),)


class StructuralVariantComment(_UserAnnotation):
    """Model for commenting on a ``StructuralVariant``."""

    #: User who created the comment.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="structural_variant_comments",
        help_text="User who created the comment",
    )

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="structural_variant_comments",
        help_text="Case that this SV is commented on",
    )

    #: The comment text.
    text = models.TextField(help_text="The comment text", null=False, blank=False)

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.text) > max_chars:
            return self.text[:max_chars] + "..."
        else:
            return self.text

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


class StructuralVariantFlags(HumanReadableMixin, _UserAnnotation):
    """Model for flagging structural variants.

    Structural variants are generally not as clear-cut as small variants because of ambiguities in their start
    and end points.  We can thus not prevent flagging a variant more than once ad we do not attempt to.
    """

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="structural_variant_flags",
        help_text="Case that this SV is flagged in",
    )

    #: Bookmarked: saved for later
    flag_bookmarked = models.BooleanField(default=False, null=False)
    #: Candidate variant
    flag_candidate = models.BooleanField(default=False, null=False)
    #: Finally selected causative variant
    flag_final_causative = models.BooleanField(default=False, null=False)
    #: Selected for wet-lab validation
    flag_for_validation = models.BooleanField(default=False, null=False)
    #: Gene affected by this variant has no known disease association
    flag_no_disease_association = models.BooleanField(default=False, null=False)
    #: Variant does segregate
    flag_segregates = models.BooleanField(default=False, null=False)
    #: Variant does not segregate
    flag_doesnt_segregate = models.BooleanField(default=False, null=False)

    # Choice fields for gradual rating

    #: Molecular flag.
    flag_molecular = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Visual inspection flag.
    flag_visual = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Wet-lab validation flag.
    flag_validation = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Phenotype/clinic suitability flag
    flag_phenotype_match = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Summary/colour code flag
    flag_summary = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#flags-" + self.get_variant_description()

    def no_flags_set(self):
        """Return true if no flags are set and the model can be deleted."""
        # TODO: unit test me
        return not any(
            (
                self.flag_bookmarked,
                self.flag_candidate,
                self.flag_final_causative,
                self.flag_for_validation,
                self.flag_no_disease_association,
                self.flag_segregates,
                self.flag_doesnt_segregate,
                self.flag_molecular != "empty",
                self.flag_visual != "empty",
                self.flag_validation != "empty",
                self.flag_phenotype_match != "empty",
                self.flag_summary != "empty",
            )
        )
