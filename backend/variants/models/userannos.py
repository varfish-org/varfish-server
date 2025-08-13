"""Code for user annotations of small variants."""

from typing import Optional
import uuid as uuid_object

import binning
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime
import requests

from variants.models.variants import SmallVariant

User = get_user_model()

#: Create mapping for chromosome as string to chromosome as integer
CHROMOSOME_STR_TO_CHROMOSOME_INT = {
    b: a for a, b in enumerate(list(map(str, range(1, 23))) + ["X", "Y", "MT"], 1)
}
#: List of chromosome names without "chr" prefix.
CHROMOSOME_NAMES = list(CHROMOSOME_STR_TO_CHROMOSOME_INT.keys())


class GetGeneSymbolsMixin:
    def get_gene_symbols(self):
        """Query for overlapping genes."""
        base_url = settings.VARFISH_BACKEND_URL_MEHARI
        if not base_url:
            return []
        url_tpl = (
            "{base_url}/api/v1/seqvars/csq?genome_release={genome_release}"
            "&chromosome={chromosome}&position={position}&reference={reference}"
            "&alternative={alternative}"
        )
        url = url_tpl.format(
            base_url=base_url,
            genome_release=self.release.lower(),
            chromosome=self.chromosome,
            position=self.start,
            reference=self.reference,
            alternative=self.alternative,
        )
        try:
            res = requests.request(method="get", url=url)
            if not res.status_code == 200:
                raise ConnectionError(
                    "ERROR: Server responded with status {} and message {}".format(
                        res.status_code, res.text
                    )
                )
            else:
                return sorted(
                    {record["gene_symbol"] for record in res.json().get("result", []) or []}
                )
        except requests.ConnectionError as e:
            raise ConnectionError("ERROR: mehari not responding.") from e


class HumanReadableMixin:
    def human_readable(self):
        """Return human-redable version of flags"""
        if self.no_flags_set():
            return "no flags set"
        else:
            flag_desc = []
            for name in ("bookmarked", "for_validation", "candidate", "final causative"):
                if getattr(self, "flag_%s" % name.replace(" ", "_")):
                    flag_desc.append(name)
            for name in ("visual", "validation", "molecular", "phenotype_match", "summary"):
                field = getattr(self, "flag_%s" % name)
                if field and field != "empty":
                    flag_desc.append("%s rating is %s" % (name.split("_")[0], field))
            return ", ".join(flag_desc)


class SmallVariantComment(GetGeneSymbolsMixin, models.Model):
    """Model for commenting on a ``SmallVariant``."""

    #: User who created the comment.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="small_variant_comments",
        help_text="User who created the comment",
    )

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Small variant flags UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: The genome release of the small variant coordinate.
    release = models.CharField(max_length=32)
    #: The chromosome of the small variant coordinate.
    chromosome = models.CharField(max_length=32)
    #: Chromosome as Integer for proper odering
    chromosome_no = models.IntegerField(default=0)
    #: The 1-based start position of the small variant coordinate.
    start = models.IntegerField()
    #: The end position of the small variant coordinate.
    end = models.IntegerField()
    #: The UCSC bin.
    bin = models.IntegerField()
    #: The reference bases of the small variant coordinate.
    reference = models.CharField(max_length=512)
    #: The alternative bases of the small variant coordinate.
    alternative = models.CharField(max_length=512)

    #: The related case.
    case = models.ForeignKey(
        "Case",
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_comments",
        help_text="Case that this variant is flagged in",
    )

    #: The comment text.
    text = models.TextField(null=False, blank=False)

    def get_variant_description(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def get_date_created(self):
        return localtime(self.date_created).strftime("%Y-%m-%d %H:%M")

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        small_vars = SmallVariant.objects.filter(
            case_id=self.case.pk,
            release=self.release,
            chromosome=self.chromosome,
            start=self.start,
            reference=self.reference,
            alternative=self.alternative,
        )
        if not small_vars.exists():
            raise ValidationError("No corresponding variant in case")

    def save(self, *args, **kwargs):
        """Save chromosome as integer for proper ordering."""
        self.chromosome_no = CHROMOSOME_STR_TO_CHROMOSOME_INT.get(self.chromosome, 0)
        super().save(*args, **kwargs)

    class Meta:
        indexes = (
            models.Index(
                fields=["release", "chromosome", "start", "end", "reference", "alternative", "case"]
            ),
        )
        ordering = ["chromosome_no", "start", "end"]

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.text) > max_chars:
            return self.text[:max_chars] + "..."
        else:
            return self.text

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


#: Choices for visual inspect, wet-lab validation, or clinical/phenotype flag statuses.
VARIANT_RATING_CHOICES = (
    ("positive", "positive"),
    ("uncertain", "uncertain"),
    ("negative", "negative"),
    ("empty", "empty"),
)


class SmallVariantFlags(GetGeneSymbolsMixin, HumanReadableMixin, models.Model):
    """Small variant flag models, at most one per variant of each model."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Small variant flags UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: The genome release of the small variant coordinate.
    release = models.CharField(max_length=32)
    #: The chromosome of the small variant coordinate.
    chromosome = models.CharField(max_length=32)
    #: Chromosome as Integer for proper odering
    chromosome_no = models.IntegerField(default=0)
    #: The 1-based start position of the small variant coordinate.
    start = models.IntegerField()
    #: The end position of the small variant coordiantes
    end = models.IntegerField()
    #: The UCSC bin.
    bin = models.IntegerField()
    #: The reference bases of the small variant coordinate.
    reference = models.CharField(max_length=512)
    #: The alternative bases of the small variant coordinate.
    alternative = models.CharField(max_length=512)

    #: The related case.
    case = models.ForeignKey(
        "Case",
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_flags",
        help_text="Case that this variant is flagged in",
    )

    # Boolean fields for checking

    #: Bookmarked: saved for later
    flag_bookmarked = models.BooleanField(default=False, null=False)
    #: Incidental finding
    flag_incidental = models.BooleanField(default=False, null=False)
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

    #: Visual inspection flag.
    flag_visual = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Molecular flag.
    flag_molecular = models.CharField(
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

    def get_variant_description(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#flags-" + self.get_variant_description()

    def no_flags_set(self):
        """Return true if no flags are set and the model can be deleted."""
        # TODO: unit test me
        return not any(
            (
                self.flag_bookmarked,
                self.flag_incidental,
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

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        small_vars = SmallVariant.objects.filter(
            case_id=self.case.pk,
            release=self.release,
            chromosome=self.chromosome,
            start=self.start,
            reference=self.reference,
            alternative=self.alternative,
        )
        if not small_vars.exists():
            raise ValidationError("No corresponding variant in case")

    def save(self, *args, **kwargs):
        """Save chromosome as integer for proper ordering."""
        self.chromosome_no = CHROMOSOME_STR_TO_CHROMOSOME_INT.get(self.chromosome, 0)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "start",
            "end",
            "reference",
            "alternative",
            "case",
        )
        indexes = (
            models.Index(
                fields=["release", "chromosome", "start", "end", "reference", "alternative", "case"]
            ),
        )
        ordering = ["chromosome_no", "start", "end"]


class AcmgCriteriaRating(models.Model):
    """Store criteria rating given by the ACMG guidelines.

    "Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the
    American College of Medical Genetics and Genomics and Association for Molecular Pathology (2015)."

    Choices are coded as follows:

    - -1 = [reserved for auto-selected as being the case]
    - 0 = user did not tick checkbox
    - 1 = [reserved for auto-selected as not being the case]
    - 2 = user tick checkbox
    """

    #: User who created the rating
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="acmg_ratings",
        help_text="User creating the original rating",
    )

    #: The related case.
    case = models.ForeignKey(
        "Case",
        on_delete=models.CASCADE,
        null=False,
        related_name="acmg_ratings",
        help_text="Case that this rating was given for",
    )

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    pvs1 = models.IntegerField(
        default=0,
        verbose_name="PVS1",
        help_text=(
            "null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or "
            "multiexon deletion) in a gene where LOF is a known mechanism of disease",
        ),
    )

    ps1 = models.IntegerField(
        default=0,
        verbose_name="PS1",
        help_text=(
            "Same amino acid change as a previously established pathogenic variant regardless of nucleotide change"
        ),
    )
    ps2 = models.IntegerField(
        default=0,
        verbose_name="PS2",
        help_text=(
            "De novo (both maternity and paternity confirmed) in a patient with the disease and no family history"
        ),
    )
    ps3 = models.IntegerField(
        default=0,
        verbose_name="PS3",
        help_text=(
            "Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or "
            "gene product"
        ),
    )
    ps4 = models.IntegerField(
        default=0,
        verbose_name="PS4",
        help_text=(
            "The prevalence of the variant in affected individuals is significantly increased compared with the "
            "prevalence in controls"
        ),
    )

    pm1 = models.IntegerField(
        default=0,
        verbose_name="PM1",
        help_text=(
            "Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active "
            "site of an enzyme) without benign variation"
        ),
    )
    pm2 = models.IntegerField(
        default=0,
        verbose_name="PM2",
        help_text=(
            "Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 "
            "Genomes Project, or Exome Aggregation Consortium"
        ),
    )
    pm3 = models.IntegerField(
        default=0,
        verbose_name="PM3",
        help_text="For recessive disorders, detected in trans with a pathogenic variant",
    )
    pm4 = models.IntegerField(
        default=0,
        verbose_name="PM4",
        help_text=(
            "Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss "
            "variants"
        ),
    )
    pm5 = models.IntegerField(
        default=0,
        verbose_name="PM5",
        help_text=(
            "Novel missense change at an amino acid residue where a different missense change determined to be "
            "pathogenic has been seen before"
        ),
    )
    pm6 = models.IntegerField(
        default=0,
        verbose_name="PM6",
        help_text="Assumed de novo, but without confirmation of paternity and maternity",
    )

    pp1 = models.IntegerField(
        default=0,
        verbose_name="PP1",
        help_text=(
            "Cosegregation with disease in multiple affected family members in a gene definitively known to cause "
            "the disease"
        ),
    )
    pp2 = models.IntegerField(
        default=0,
        verbose_name="PP2",
        help_text=(
            "Missense variant in a gene that has a low rate of benign missense variation and in which missense "
            "variants are: a common mechanism of disease"
        ),
    )
    pp3 = models.IntegerField(
        default=0,
        verbose_name="PP3",
        help_text=(
            "Multiple lines of computational evidence support a deleterious effect on the gene or gene product "
            "(conservation, evolutionary, splicing impact, etc.)"
        ),
    )
    pp4 = models.IntegerField(
        default=0,
        verbose_name="PP4",
        help_text=(
            "Patient's phenotype or family history is highly specific for a disease with a single genetic etiology"
        ),
    )
    pp5 = models.IntegerField(
        default=0,
        verbose_name="PP5",
        help_text=(
            "Reputable source recently reports variant as pathogenic, but the evidence is not available to the "
            "laboratory to perform an independent evaluation"
        ),
    )

    ba1 = models.IntegerField(
        default=0,
        verbose_name="BA1",
        help_text=(
            "Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation "
            "Consortium"
        ),
    )

    bs1 = models.IntegerField(
        default=0,
        verbose_name="BS1",
        help_text="Allele frequency is greater than expected for disorder (see Table 6)",
    )
    bs2 = models.IntegerField(
        default=0,
        verbose_name="BS2",
        help_text=(
            "Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or "
            "X-linked (hemizygous) disorder, with full penetrance expected at an early age"
        ),
    )
    bs3 = models.IntegerField(
        default=0,
        verbose_name="BS3",
        help_text=(
            "Well-established in vitro or in vivo functional studies show no damaging effect on protein function "
            "or splicing"
        ),
    )
    bs4 = models.IntegerField(
        default=0,
        verbose_name="BS4",
        help_text="BS4: Lack of segregation in affected members of a family",
    )

    bp1 = models.IntegerField(
        default=0,
        verbose_name="BP1",
        help_text="Missense variant in a gene for which primarily truncating variants are known to cause disease",
    )
    bp2 = models.IntegerField(
        default=0,
        verbose_name="BP2",
        help_text=(
            "Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in "
            "cis with a pathogenic variant in any inheritance pattern"
        ),
    )
    bp3 = models.IntegerField(
        default=0,
        verbose_name="BP3",
        help_text="In-frame deletions/insertions in a repetitive region without a known function",
    )
    bp4 = models.IntegerField(
        default=0,
        verbose_name="BP4",
        help_text=(
            "Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, "
            "evolutionary, splicing impact, etc.)"
        ),
    )
    bp5 = models.IntegerField(
        default=0,
        verbose_name="BP5",
        help_text="Variant found in a case with an alternate molecular basis for disease",
    )
    bp6 = models.IntegerField(
        default=0,
        verbose_name="BP6",
        help_text=(
            "Reputable source recently reports variant as benign, but the evidence is not available to the "
            "laboratory to perform an independent evaluation"
        ),
    )
    bp7 = models.IntegerField(
        default=0,
        verbose_name="BP7",
        help_text=(
            "A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the splice "
            "consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved"
        ),
    )

    class_auto = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="ACMG Classification",
        help_text="Result of the ACMG classification",
    )

    class_override = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Class Override",
        help_text="Use this field to override the auto-computed class assignment",
    )

    @property
    def acmg_class(self) -> Optional[int]:
        return self.class_override or self.class_auto

    get_gene_symbols = SmallVariantComment.get_gene_symbols

    def save(self, *args, **kwargs):
        self.bin = binning.assign_bin(self.start, self.end - 1)
        return super().save(*args, **kwargs)

    def get_variant_description(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def get_human_readable(self):
        """Return human-readable ACMG rating values."""

        def yesno(key):
            if getattr(self, key) and getattr(self, key) > 0:
                return "Y"
            else:
                return "N"

        keys = (
            "pvs1",
            "ps1",
            "ps2",
            "ps3",
            "ps4",
            "pm1",
            "pm2",
            "pm3",
            "pm4",
            "pm5",
            "pm6",
            "pp1",
            "pp2",
            "pp3",
            "pp4",
            "pp5",
            "ba1",
            "bs1",
            "bs2",
            "bs3",
            "bs4",
            "bp1",
            "bp2",
            "bp3",
            "bp4",
            "bp5",
            "bp6",
            "bp7",
        )
        result = ", ".join(["%s: %s" % (key.upper(), yesno(key)) for key in keys])
        result += ", ACMG classification: %s" % self.class_auto
        if self.class_override:
            result += ", ACMG class. override: %s" % self.class_override
        return result

    class Meta:
        ordering = ["chromosome", "start", "reference", "alternative"]
