"""Models for storing query presets."""

import uuid as uuid_object

import attrs
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from model_clone import CloneMixin
from projectroles.models import Project

from variants.query_presets import (
    CHROMOSOME_PRESETS,
    FLAGSETC_PRESETS,
    FREQUENCY_PRESETS,
    IMPACT_PRESETS,
    QUALITY_PRESETS,
    QUICK_PRESETS,
)

#: The User model to use.
User = get_user_model()


class PresetBase(CloneMixin, models.Model):
    """Base class for category-level presets."""

    _clone_excluded_fields = ("date_created", "date_modified", "sodar_uuid")

    class Meta:
        abstract = True

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Object UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Cohort SODAR UUID"
    )

    #: The set of presets this belongs to.
    presetset = models.ForeignKey(
        "PresetSet",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text="The preset set this belongs to.",
    )
    #: User-readable label for the preset set.
    label = models.CharField(max_length=64, help_text="User-readable label")

    def get_project(self):
        return self.presetset.project


class FrequencyPresetsManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_factory_preset(self, factory_preset_name, preset_label, preset_presetset):
        """Create as a copy of the factory presets."""
        return self.create(
            label=preset_label,
            presetset=preset_presetset,
            **getattr(FREQUENCY_PRESETS, factory_preset_name),
        )

    def create_as_copy_of_other_preset(self, other, presetset, **kwargs):
        """Create as a copy of the other presets set."""
        return other.make_clone(attrs={**kwargs, "presetset": presetset})


class FrequencyPresets(PresetBase):
    """Presets for the frequency settings."""

    objects = FrequencyPresetsManager()

    thousand_genomes_enabled = models.BooleanField(null=False, default=True)
    thousand_genomes_homozygous = models.IntegerField(null=True, default=None)
    thousand_genomes_heterozygous = models.IntegerField(null=True, default=None)
    thousand_genomes_hemizygous = models.IntegerField(null=True, default=None)
    thousand_genomes_frequency = models.FloatField(null=True, default=None)
    exac_enabled = models.BooleanField(null=False, default=True)
    exac_homozygous = models.IntegerField(null=True, default=None)
    exac_heterozygous = models.IntegerField(null=True, default=None)
    exac_hemizygous = models.IntegerField(null=True, default=None)
    exac_frequency = models.FloatField(null=True, default=None)
    gnomad_exomes_enabled = models.BooleanField(null=False, default=True)
    gnomad_exomes_homozygous = models.IntegerField(null=True, default=None)
    gnomad_exomes_heterozygous = models.IntegerField(null=True, default=None)
    gnomad_exomes_hemizygous = models.IntegerField(null=True, default=None)
    gnomad_exomes_frequency = models.FloatField(null=True, default=None)
    gnomad_genomes_enabled = models.BooleanField(null=False, default=True)
    gnomad_genomes_homozygous = models.IntegerField(null=True, default=None)
    gnomad_genomes_heterozygous = models.IntegerField(null=True, default=None)
    gnomad_genomes_hemizygous = models.IntegerField(null=True, default=None)
    gnomad_genomes_frequency = models.FloatField(null=True, default=None)
    inhouse_enabled = models.BooleanField(null=False, default=True)
    inhouse_homozygous = models.IntegerField(null=True, default=None)
    inhouse_heterozygous = models.IntegerField(null=True, default=None)
    inhouse_hemizygous = models.IntegerField(null=True, default=None)
    inhouse_carriers = models.IntegerField(null=True, default=None)
    mtdb_enabled = models.BooleanField(null=False, default=True)
    mtdb_count = models.IntegerField(null=True, default=None)
    mtdb_frequency = models.FloatField(null=True, default=None)
    helixmtdb_enabled = models.BooleanField(null=False, default=True)
    helixmtdb_het_count = models.IntegerField(null=True, default=None)
    helixmtdb_hom_count = models.IntegerField(null=True, default=None)
    helixmtdb_frequency = models.FloatField(null=True, default=None)
    mitomap_enabled = models.BooleanField(null=False, default=False)
    mitomap_count = models.IntegerField(null=True, default=None)
    mitomap_frequency = models.FloatField(null=True, default=None)


class ImpactPresetsManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_factory_preset(self, factory_preset_name, preset_label, preset_presetset):
        """Create as a copy of the factory presets."""
        return self.create(
            label=preset_label,
            presetset=preset_presetset,
            **getattr(IMPACT_PRESETS, factory_preset_name),
        )

    def create_as_copy_of_other_preset(self, other, presetset, **kwargs):
        """Create as a copy of the other presets set."""
        return other.make_clone(attrs={**kwargs, "presetset": presetset})


class ImpactPresets(PresetBase):
    """Presets for the impact settings."""

    objects = ImpactPresetsManager()

    var_type_snv = models.BooleanField(null=False, default=True)
    var_type_mnv = models.BooleanField(null=False, default=True)
    var_type_indel = models.BooleanField(null=False, default=True)
    transcripts_coding = models.BooleanField(null=False, default=True)
    transcripts_noncoding = models.BooleanField(null=False, default=True)
    max_exon_dist = models.IntegerField(null=True, default=None)
    effects = ArrayField(models.CharField(max_length=64), null=False, default=list)


class QualityPresetsManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_factory_preset(self, factory_preset_name, preset_label, preset_presetset):
        """Create as a copy of the factory presets."""
        return self.create(
            label=preset_label,
            presetset=preset_presetset,
            **getattr(QUALITY_PRESETS, factory_preset_name),
        )

    def create_as_copy_of_other_preset(self, other, presetset, **kwargs):
        """Create as a copy of the other presets set."""
        return other.make_clone(attrs={**kwargs, "presetset": presetset})


class QualityPresets(PresetBase):
    """Presets for the quality settings."""

    objects = QualityPresetsManager()

    class Fail(models.TextChoices):
        DROP_VARIANT = "drop-variant", "drop variant"
        IGNORE = "ignore", "ignore"
        NO_CALL = "no-call", "no call"

    dp_het = models.IntegerField(null=True, default=None)
    dp_hom = models.IntegerField(null=True, default=None)
    ab = models.FloatField(null=True, default=None)
    gq = models.IntegerField(null=True, default=None)
    ad = models.IntegerField(null=True, default=None)
    ad_max = models.IntegerField(null=True, default=None)
    fail = models.CharField(max_length=32, choices=Fail.choices)


class ChromosomePresetsManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_factory_preset(self, factory_preset_name, preset_label, preset_presetset):
        """Create as a copy of the factory presets."""
        return self.create(
            label=preset_label,
            presetset=preset_presetset,
            **getattr(CHROMOSOME_PRESETS, factory_preset_name),
        )

    def create_as_copy_of_other_preset(self, other, presetset, **kwargs):
        """Create as a copy of the other presets set."""
        return other.make_clone(attrs={**kwargs, "presetset": presetset})


class ChromosomePresets(PresetBase):
    """Presets for the chromosome settings."""

    objects = ChromosomePresetsManager()

    genomic_region = ArrayField(models.CharField(max_length=64), null=False, default=list)
    gene_allowlist = ArrayField(models.CharField(max_length=64), null=False, default=list)
    gene_blocklist = ArrayField(models.CharField(max_length=64), null=False, default=list)


class FlagsEtcPresetsManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_factory_preset(self, factory_preset_name, preset_label, preset_presetset):
        """Create as a copy of the factory presets."""
        return self.create(
            label=preset_label,
            presetset=preset_presetset,
            **{key: value for key, value in getattr(FLAGSETC_PRESETS, factory_preset_name).items()},
        )

    def create_as_copy_of_other_preset(self, other, presetset, **kwargs):
        """Create as a copy of the other presets set."""
        return other.make_clone(attrs={**kwargs, "presetset": presetset})


class FlagsEtcPresets(PresetBase):
    """Presets for the chromosome settings."""

    objects = FlagsEtcPresetsManager()

    clinvar_include_benign = models.BooleanField(null=False, default=True)
    clinvar_include_likely_benign = models.BooleanField(null=False, default=True)
    clinvar_include_likely_pathogenic = models.BooleanField(null=False, default=True)
    clinvar_include_pathogenic = models.BooleanField(null=False, default=True)
    clinvar_include_uncertain_significance = models.BooleanField(null=False, default=True)
    clinvar_exclude_conflicting = models.BooleanField(null=False, default=False)
    flag_bookmarked = models.BooleanField(null=False, default=True)
    flag_incidental = models.BooleanField(null=False, default=True)
    flag_candidate = models.BooleanField(null=False, default=True)
    flag_doesnt_segregate = models.BooleanField(null=False, default=True)
    flag_final_causative = models.BooleanField(null=False, default=True)
    flag_for_validation = models.BooleanField(null=False, default=True)
    flag_no_disease_association = models.BooleanField(null=False, default=True)
    flag_molecular_empty = models.BooleanField(null=False, default=True)
    flag_molecular_negative = models.BooleanField(null=False, default=True)
    flag_molecular_positive = models.BooleanField(null=False, default=True)
    flag_molecular_uncertain = models.BooleanField(null=False, default=True)
    flag_phenotype_match_empty = models.BooleanField(null=False, default=True)
    flag_phenotype_match_negative = models.BooleanField(null=False, default=True)
    flag_phenotype_match_positive = models.BooleanField(null=False, default=True)
    flag_phenotype_match_uncertain = models.BooleanField(null=False, default=True)
    flag_segregates = models.BooleanField(null=False, default=True)
    flag_simple_empty = models.BooleanField(null=False, default=True)
    flag_summary_empty = models.BooleanField(null=False, default=True)
    flag_summary_negative = models.BooleanField(null=False, default=True)
    flag_summary_positive = models.BooleanField(null=False, default=True)
    flag_summary_uncertain = models.BooleanField(null=False, default=True)
    flag_validation_empty = models.BooleanField(null=False, default=True)
    flag_validation_negative = models.BooleanField(null=False, default=True)
    flag_validation_positive = models.BooleanField(null=False, default=True)
    flag_validation_uncertain = models.BooleanField(null=False, default=True)
    flag_visual_empty = models.BooleanField(null=False, default=True)
    flag_visual_negative = models.BooleanField(null=False, default=True)
    flag_visual_positive = models.BooleanField(null=False, default=True)
    flag_visual_uncertain = models.BooleanField(null=False, default=True)
    require_in_clinvar = models.BooleanField(null=False, default=False)
    clinvar_paranoid_mode = models.BooleanField(null=False, default=False)


class QuickPresetsManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_other_preset(self, other, **kwargs):
        """Create as a copy of the other presets set."""
        return other.make_clone(attrs={**kwargs})


class QuickPresets(CloneMixin, models.Model):
    """Picks appropriate choice from each category."""

    objects = QuickPresetsManager()

    _clone_excluded_fields = ("date_created", "date_modified", "sodar_uuid")

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Object UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Cohort SODAR UUID"
    )

    #: The set of presets this belongs to.
    presetset = models.ForeignKey(
        "PresetSet",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text="The preset set this belongs to.",
    )
    #: User-readable label for the preset set.
    label = models.CharField(max_length=64, help_text="User-readable label")

    class Inheritances(models.TextChoices):
        DE_NOVO = "de_novo", "de novo"
        DOMINANT = "dominant", "dominant"
        HOMOZYGOUS_RECESSIVE = "homozygous_recessive", "homozygous recessive"
        COMPOUND_HETEROZYGOUS = "compound_heterozygous", "compound heterozygous"
        RECESSIVE = "recessive", "recessive"
        X_RECESSIVE = "x_recessive", "X-recessive"
        AFFECTED_CARRIERS = "affected_carriers", "affected carriers"
        ANY = "any", "any"

    #: Inheritance preset.
    inheritance = models.CharField(
        max_length=32,
        choices=Inheritances.choices,
        default=Inheritances.ANY,
        help_text="Presets for inheritance",
    )
    #: Frequency preset.
    frequency = models.ForeignKey(
        FrequencyPresets,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        help_text="Preset values for category frequency",
    )
    #: Impact preset.
    impact = models.ForeignKey(
        ImpactPresets,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        help_text="Preset value for category impact",
    )
    #: Quality preset.
    quality = models.ForeignKey(
        QualityPresets,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        help_text="Preset value for category quality",
    )
    #: Chromosome preset.
    chromosome = models.ForeignKey(
        ChromosomePresets,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        help_text="Preset value for category chromosome",
    )
    #: Flags etc. preset.
    flagsetc = models.ForeignKey(
        FlagsEtcPresets,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        help_text="Preset value for category 'flags etc.'",
    )

    #: Position of the preset in the list.
    position = models.IntegerField(null=False, default=0, help_text="Position in the list")

    def get_project(self):
        return self.presetset.project

    class Meta:
        ordering = ("position",)


class PresetSetManager(models.Manager):
    """Custom manager that allows creation from factory presets or other presets."""

    def create_as_copy_of_factory_preset_set(
        self, *, project, label, description=None, database="refseq"
    ):
        """Create as a copy of the factory presets."""

        def create_nested(model, presets):
            return {
                field.name: model.objects.create_as_copy_of_factory_preset(
                    field.name, field.name.replace("_", " "), presetset
                )
                for field in attrs.fields(presets.__class__)
            }

        with transaction.atomic():
            presetset = self.create(
                project=project, label=label, description=description, database=database
            )
            frequency = create_nested(FrequencyPresets, FREQUENCY_PRESETS)
            impact = create_nested(ImpactPresets, IMPACT_PRESETS)
            quality = create_nested(QualityPresets, QUALITY_PRESETS)
            chromosome = create_nested(ChromosomePresets, CHROMOSOME_PRESETS)
            flagsetc = create_nested(FlagsEtcPresets, FLAGSETC_PRESETS)
            for field in attrs.fields(QUICK_PRESETS.__class__):
                QuickPresets.objects.create(
                    presetset=presetset,
                    label=field.default.label,
                    inheritance=field.default.inheritance.value,
                    frequency=frequency[field.default.frequency.value],
                    impact=impact[field.default.impact.value],
                    quality=quality[field.default.quality.value],
                    chromosome=chromosome[field.default.chromosomes.value],
                    flagsetc=flagsetc[field.default.flagsetc.value],
                )

        return presetset

    def create_as_copy_of_other_preset_set(self, other, **kwargs):
        """Create as a copy of the other presets set."""
        clone = other.make_clone(attrs={**kwargs})
        quickpresets_other = list(other.quickpresets_set.all().order_by("id"))
        quickpresets_clone = list(clone.quickpresets_set.all().order_by("id"))
        mapping = {
            preset: {
                "other": list(getattr(other, f"{preset}presets_set").all().order_by("id")),
                "clone": list(getattr(clone, f"{preset}presets_set").all().order_by("id")),
            }
            for preset in ("frequency", "impact", "quality", "chromosome", "flagsetc")
        }

        for n, quickpreset_other in enumerate(quickpresets_other):
            for preset in mapping.keys():
                for i, o in enumerate(mapping[preset]["other"]):
                    if getattr(quickpreset_other, preset) == o:
                        setattr(quickpresets_clone[n], preset, mapping[preset]["clone"][i])
            quickpresets_clone[n].save()

        return clone


class PresetSet(CloneMixin, models.Model):
    """A set of user-defined presets."""

    _clone_excluded_fields = ("date_created", "date_modified", "sodar_uuid", "default_presetset")
    _clone_m2o_or_o2m_fields = (
        "quickpresets_set",
        "frequencypresets_set",
        "impactpresets_set",
        "qualitypresets_set",
        "chromosomepresets_set",
        "flagsetcpresets_set",
    )

    objects = PresetSetManager()

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Object UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Cohort SODAR UUID"
    )

    #: The project that the set belongs to.
    project = models.ForeignKey(
        Project,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        help_text="The project that this preset set belongs into",
    )

    class State(models.TextChoices):
        #: The version of the preset set is currently in draft state
        DRAFT = "draft", "draft"
        #: The version of the preset set is currently active
        ACTIVE = "active", "active"
        #: The (version) of the preset set has been retired
        RETIRED = "retired", "retired"

    #: State of the preset set
    state = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=State.choices,
        default=State.ACTIVE,
        help_text="State of the preset set version",
    )
    #: Major version of the gene panel
    version_major = models.IntegerField(
        null=False, default=1, help_text="Major version of the preset set"
    )
    #: Minor version of the gene panel
    version_minor = models.IntegerField(
        null=False, default=1, help_text="Minor version of the preset set"
    )
    #: The user who signed off the gene panel
    signed_off_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="The user who signed off the preset set into active state",
    )

    #: User-readable label for the preset set.
    label = models.CharField(max_length=64, help_text="User-readable label")
    #: A description.
    description = models.TextField(null=True, blank=True, help_text="Optional description")

    class Databases(models.TextChoices):
        REFSEQ = "refseq", "RefSeq"
        ENSEMBL = "ensembl", "ENSEMBL"

    #: The database to use.
    database = models.CharField(
        max_length=32, choices=Databases.choices, help_text="The database to use"
    )

    #: Set as the default preset set
    default_presetset = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        help_text="Set as the default preset set",
    )
