"""Presets for structural variant query configuration."""

from enum import Enum, unique
import typing

import attrs

from svs.query_schemas import Database, GenotypeCriteria, Pathogenicity, SvSubType, SvType
from variants.query_presets import DiseaseState as _DiseaseState
from variants.query_presets import GenotypeChoice
from variants.query_presets import Inheritance as _Inheritance
from variants.query_presets import PedigreeMember
from variants.query_presets import Sex as _Sex

DiseaseState = _DiseaseState

Inheritance = _Inheritance

Sex = _Sex


#: All SVs
SVTYPES_ALL = [e.value for e in SvType]

#: Almost all SV types (no BND, no INS)
SVTYPES_ALMOST_ALL = [SvType.DEL.value, SvType.DUP.value, SvType.CNV.value, SvType.INV.value]

#: CNVs
SVTYPES_CNV = [SvType.DEL.value, SvType.DUP.value, SvType.CNV.value]

#: SV sub types for deletions.
SVSUBTYPES_DEL = [
    SvSubType.DEL.value,
    SvSubType.DEL_ME.value,
    SvSubType.DEL_ME_SVA.value,
    SvSubType.DEL_ME_L1.value,
    SvSubType.DEL_ME_ALU.value,
]

#: SV sub types for duplications.
SVSUBTYPES_DUP = [SvSubType.DUP.value, SvSubType.DUP_TANDEM.value]

#: SV Sub types for copy number variable variants.
SVSUBTYPES_CNV = SVSUBTYPES_DEL + SVSUBTYPES_DUP + [SvSubType.CNV.value]

#: SV Sub types for copy number "neutral" variants (including insertions).
SVSUBTYPES_NEUTRAL = [
    SvSubType.INV.value,
    SvSubType.INS.value,
    SvSubType.INS_ME.value,
    SvSubType.INS_ME_SVA.value,
    SvSubType.INS_ME_L1.value,
    SvSubType.INS_ME_ALU.value,
    SvSubType.BND.value,
]

#: "Almost all" SV sub types"
SVSUBTYPES_ALMOST_ALL = SVSUBTYPES_CNV + [SvSubType.INV.value]

#: All SV sub types.
SVSUBTYPES_ALL = SVSUBTYPES_CNV + SVSUBTYPES_NEUTRAL


@attrs.define(frozen=True)
class _KnownPathoPresets:
    #: Presets for "default" overlaps.
    default: typing.Dict[str, typing.Any] = {
        "clinvar_sv_min_overlap": 0.75,
        "clinvar_sv_min_pathogenicity": Pathogenicity.LIKELY_PATHOGENIC.value,
    }


#: Presets for the databases with known pathogenic variants and clinvar.
KNOWN_PATHO_PRESETS: _KnownPathoPresets = _KnownPathoPresets()


@unique
class KnownPatho(Enum):
    DEFAULT = "default"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the known pathogenic variants / clinvar"""
        return getattr(KNOWN_PATHO_PRESETS, self.value)


@attrs.define(frozen=True)
class _FrequencyPresets:
    #: Presets for "strict" frequency.
    strict: typing.Dict[str, typing.Any] = {
        "svdb_dgv_enabled": False,
        "svdb_dgv_min_overlap": 0.75,
        "svdb_dgv_max_count": None,
        "svdb_dgv_gs_enabled": False,
        "svdb_dgv_gs_min_overlap": 0.75,
        "svdb_dgv_gs_max_count": None,
        "svdb_gnomad_enabled": True,
        "svdb_gnomad_min_overlap": 0.75,
        "svdb_gnomad_max_count": 20,
        "svdb_exac_enabled": True,
        "svdb_exac_min_overlap": 0.75,
        "svdb_exac_max_count": 20,
        "svdb_dbvar_enabled": True,
        "svdb_dbvar_min_overlap": 0.75,
        "svdb_dbvar_max_count": 40,
        "svdb_g1k_enabled": True,
        "svdb_g1k_min_overlap": 0.75,
        "svdb_g1k_max_count": 10,
        "svdb_inhouse_enabled": True,
        "svdb_inhouse_min_overlap": 0.75,
        "svdb_inhouse_max_count": 30,
    }
    #: Presets for "relaxed" frequency.
    relaxed: typing.Dict[str, typing.Any] = {
        "svdb_dgv_enabled": False,
        "svdb_dgv_min_overlap": 0.75,
        "svdb_dgv_max_count": None,
        "svdb_dgv_gs_enabled": False,
        "svdb_dgv_gs_min_overlap": 0.75,
        "svdb_dgv_gs_max_count": None,
        "svdb_gnomad_enabled": True,
        "svdb_gnomad_min_overlap": 0.75,
        "svdb_gnomad_max_count": 50,
        "svdb_exac_enabled": True,
        "svdb_exac_min_overlap": 0.75,
        "svdb_exac_max_count": 50,
        "svdb_dbvar_enabled": True,
        "svdb_dbvar_min_overlap": 0.75,
        "svdb_dbvar_max_count": 50,
        "svdb_g1k_enabled": True,
        "svdb_g1k_min_overlap": 0.75,
        "svdb_g1k_max_count": 50,
        "svdb_inhouse_enabled": True,
        "svdb_inhouse_min_overlap": 0.75,
        "svdb_inhouse_max_count": 50,
    }
    #: Presets for "any" frequency.
    any: typing.Dict[str, typing.Any] = {
        "svdb_dgv_enabled": False,
        "svdb_dgv_min_overlap": None,
        "svdb_dgv_max_count": None,
        "svdb_dgv_gs_enabled": False,
        "svdb_dgv_gs_min_overlap": None,
        "svdb_dgv_gs_max_count": None,
        "svdb_gnomad_enabled": False,
        "svdb_gnomad_min_overlap": None,
        "svdb_gnomad_max_count": None,
        "svdb_exac_enabled": False,
        "svdb_exac_min_overlap": None,
        "svdb_exac_max_count": None,
        "svdb_dbvar_enabled": False,
        "svdb_dbvar_min_overlap": None,
        "svdb_dbvar_max_count": None,
        "svdb_g1k_enabled": False,
        "svdb_g1k_min_overlap": None,
        "svdb_g1k_max_count": None,
        "svdb_inhouse_enabled": False,
        "svdb_inhouse_min_overlap": None,
        "svdb_inhouse_max_count": None,
    }


#: Presets for the frequency related settings by frequency preset option
FREQUENCY_PRESETS: _FrequencyPresets = _FrequencyPresets()


@unique
class Frequency(Enum):
    """Preset options for category frequency"""

    ANY = "any"
    STRICT = "strict"
    RELAXED = "relaxed"
    CUSTOM = "custom"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the regions/genes category"""
        return getattr(FREQUENCY_PRESETS, self.value)


@attrs.define(frozen=True)
class _ImpactPresets:
    """Type for providing immutable impact presets"""

    #: Presets for "any" impact.
    any: typing.Dict[str, typing.Any] = {
        "sv_size_min": None,
        "sv_size_max": None,
        "sv_types": SVTYPES_ALL,
        "sv_sub_types": SVSUBTYPES_ALL,
    }
    #: Presets for "almost all" impact.
    almost_all: typing.Dict[str, typing.Any] = {
        "sv_size_min": None,
        "sv_size_max": None,
        "sv_types": SVTYPES_ALMOST_ALL,
        "sv_sub_types": SVSUBTYPES_ALMOST_ALL,
    }
    #: Presets for "only CNVs" impact.
    cnv_only: typing.Dict[str, typing.Any] = {
        "sv_size_min": None,
        "sv_size_max": None,
        "sv_types": SVTYPES_CNV,
        "sv_sub_types": SVSUBTYPES_CNV,
    }


#: Presets for the impact related settings by impact preset option
IMPACT_PRESETS: _ImpactPresets = _ImpactPresets()


@unique
class Impact(Enum):
    """Preset options for category impact"""

    ANY = "any"
    ALMOST_ALL = "almost_all"
    CNV_ONLY = "cnv_only"
    CUSTOM = "custom"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the impact category"""
        return getattr(IMPACT_PRESETS, self.value)


@attrs.define(frozen=True)
class _ChromosomePresets:
    """Type for providing immutable chromosome/region/gene presets"""

    #: Presets for the "whole genome" chromosome/region/gene settings
    whole_genome: typing.Dict[str, typing.Any] = {"genomic_region": [], "gene_allowlist": []}
    #: Presets for the "autosomes" chromosome/region/gene settings
    autosomes: typing.Dict[str, typing.Any] = {
        "genomic_region": list(f"{num}" for num in range(1, 23)),
        "gene_allowlist": None,
    }
    #: Presets for the "X-chromosome" chromosome/region/gene settings
    x_chromosome: typing.Dict[str, typing.Any] = {"genomic_region": ["X"], "gene_allowlist": []}
    #: Presets for the "Y-chromosomes" chromosome/region/gene settings
    y_chromosome: typing.Dict[str, typing.Any] = {"genomic_region": ["Y"], "gene_allowlist": []}
    #: Presets for the "mitochondrial" chromosome/region/gene settings
    mt_chromosome: typing.Dict[str, typing.Any] = {"genomic_region": ["MT"], "gene_allowlist": []}


#: Presets for the chromosome/region/gene related settings, by chromosome preset option
CHROMOSOME_PRESETS: _ChromosomePresets = _ChromosomePresets()


@unique
class Chromosomes(Enum):
    WHOLE_GENOME = "whole_genome"
    AUTOSOMES = "autosomes"
    X_CHROMOSOME = "x_chromosome"
    Y_CHROMOSOME = "y_chromosome"
    MT_CHROMOSOME = "mt_chromosome"
    CUSTOM = "custom"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the regions/genes category"""
        return getattr(CHROMOSOME_PRESETS, self.value)


@attrs.define(frozen=True)
class _RegulatoryPresets:
    default: typing.Dict[str, typing.Any] = {
        "regulatory_overlap": 100,
        "regulatory_ensembl_features": None,
        "regulatory_vista_validation": None,
        "regulatory_custom_configs": [],
    }


#: Presets for the regulatory presets configuration.
REGULATORY_PRESETS: _RegulatoryPresets = _RegulatoryPresets()


@unique
class Regulatory(Enum):
    DEFAULT = "default"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the regions/genes category"""
        return getattr(REGULATORY_PRESETS, self.value)


@attrs.define(frozen=True)
class _TadPresets:
    default: typing.Dict[str, typing.Any] = {"tad_set": "hesc"}


#: Presets for the TAD configuration.
TAD_PRESETS: _TadPresets = _TadPresets()


@unique
class Tad(Enum):
    DEFAULT = "default"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the regions/genes category"""
        return getattr(TAD_PRESETS, self.value)


#: Inspired by ClinSV "High Confidence" Filter Settings
GT_CRITERIA_HIGH: typing.List[GenotypeCriteria] = [
    # The following are currently NOT SUPPORTED for structural variants because of the unnecessary complexity this
    # would cause.
    #
    # GenotypeCriteria(genotype=GenotypeChoice.NON_HOM)
    # GenotypeCriteria(genotype=GenotypeChoice.NON_REFERENCE)
    #
    # Further, you should not define any match for ``GenotypeCriteria(genotype=GenotypeChoice.ANY)`` as this is
    # implicit for applying no restriction on the genotype.
    #
    #
    # -- GenotypeChoice.REF -------------------------------------------------
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria High-CNV-1",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=100_000,
        max_rd_dev=0.1,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria High-CNV-2",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        select_sv_max_size=99_999,
        max_rd_dev=0.1,
        max_amq=55,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria High-Neutral",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        max_srpr_var=1,
        max_brk_segduprepeat=0,
    ),
    # -- GenotypeChoice.HET -------------------------------------------------
    GenotypeCriteria(
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=100_000,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        select_sv_max_size=99_999,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        min_amq=55,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        gt_one_of=["0/1", "0|1", "1/0", "0|1"],
        min_sr_var=1,
        min_pr_var=1,
        min_srpr_var=10,
        max_brk_segduprepeat=0,
    ),
    # -- GenotypeChoice.HOM -------------------------------------------------
    GenotypeCriteria(
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=100_000,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        select_sv_max_size=99_999,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        min_amq=55,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        gt_one_of=["1/1", "1|1"],
        min_sr_var=1,
        min_pr_var=1,
        min_srpr_var=10,
        max_brk_segduprepeat=0,
    ),
    # -- GenotypeChoice.VARIANT ---------------------------------------------
    GenotypeCriteria(
        comment="ClinSV Criteria High-CNV-1",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=100_000,
        min_rd_dev=0.2,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        comment="ClinSV Criteria High-CNV-2",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        select_sv_max_size=99_999,
        min_rd_dev=0.2,
        min_amq=55,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        comment="ClinSV Criteria High-Neutral",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        min_sr_var=1,
        min_pr_var=1,
        min_srpr_var=10,
        max_brk_segduprepeat=0,
    ),
    # -- GenotypeChoice.NON_VARIANT -----------------------------------------
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria High-CNV-1",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=100_000,
        max_rd_dev=0.1,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria High-CNV-2",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        select_sv_max_size=99_999,
        max_rd_dev=0.1,
        max_amq=55,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria High-Neutral",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        max_srpr_var=1,
        max_brk_segduprepeat=0,
    ),
]


#: Inspired by ClinSV "PASS" Filter Settings
GT_CRITERIA_PASS: typing.List[GenotypeCriteria] = [
    # The following are currently NOT SUPPORTED for structural variants because of the unnecessary complexity this
    # would cause.
    #
    # GenotypeCriteria(genotype=GenotypeChoice.NON_HOM)
    # GenotypeCriteria(genotype=GenotypeChoice.NON_REFERENCE)
    #
    # Further, you should not define any match for ``GenotypeCriteria(genotype=GenotypeChoice.ANY)`` as this is
    # implicit for applying no restriction on the genotype.
    #
    # -- GenotypeChoice.REF -------------------------------------------------
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria Pass-CNV-1",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        max_rd_dev=0.1,
        max_srpr_var=2,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria Pass-CNV-2",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_CNV,
        max_rd_dev=0.2,
        max_srpr_var=2,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria Pass-Neutral",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        max_srpr_var=2,
        max_brk_segduprepeat=1,
    ),
    # -- GenotypeChoice.HET -------------------------------------------------
    GenotypeCriteria(
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_CNV,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        min_srpr_var=10,
        max_brk_segduprepeat=1,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        gt_one_of=["0/1", "0|1", "1/0", "0|1"],
        min_srpr_var=6,
        max_brk_segduprepeat=1,
    ),
    # -- GenotypeChoice.HOM -------------------------------------------------
    GenotypeCriteria(
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_CNV,
        min_rd_dev=0.2,
        max_rd_dev=0.75,
        min_srpr_var=10,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        gt_one_of=["1/1", "1|1"],
        min_srpr_var=6,
        max_brk_segduprepeat=1,
    ),
    # -- GenotypeChoice.VARIANT ---------------------------------------------
    GenotypeCriteria(
        comment="ClinSV Criteria Pass-CNV-1",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        min_rd_dev=0.2,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        comment="ClinSV Criteria Pass-CNV-2",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        min_rd_dev=0.2,
        min_srpr_var=10,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        comment="ClinSV Criteria Pass-Neutral",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        min_srpr_var=2,
        max_brk_segduprepeat=1,
    ),
    # -- GenotypeChoice.NON_VARIANT -----------------------------------------
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria Pass-CNV-1",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        select_sv_min_size=10_000,
        max_rd_dev=0.2,
        max_srpr_var=2,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria Pass-CNV-2",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_CNV,
        max_rd_dev=0.2,
        max_srpr_var=2,
        max_brk_segduprepeat=2,
    ),
    GenotypeCriteria(
        comment="Opposite of ClinSV Criteria Pass-Neutral",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_NEUTRAL,
        max_srpr_var=2,
        max_brk_segduprepeat=1,
    ),
]

#: Just trust the genotypes
GT_CRITERIA_DEFAULT: typing.List[GenotypeCriteria] = [
    # The following are currently NOT SUPPORTED for structural variants because of the unnecessary complexity this
    # would cause.
    #
    # GenotypeCriteria(genotype=GenotypeChoice.NON_HOM)
    # GenotypeCriteria(genotype=GenotypeChoice.NON_REFERENCE)
    #
    # Further, you should not define any match for ``GenotypeCriteria(genotype=GenotypeChoice.ANY)`` as this is
    # implicit for applying no restriction on the genotype.
    #
    # -- GenotypeChoice.REF -------------------------------------------------
    GenotypeCriteria(
        comment="Trust the genotype to show the wild-type/reference",
        genotype=GenotypeChoice.REF,
        select_sv_sub_type=SVSUBTYPES_ALL,
        gt_one_of=["0/0", "0|0", "0", "./0", "0/.", "0|.", ".|0"],
        max_brk_segduprepeat=2,
    ),
    # -- GenotypeChoice.HET -------------------------------------------------
    GenotypeCriteria(
        comment="Trust the genotype to show the wild-type/reference",
        genotype=GenotypeChoice.HET,
        select_sv_sub_type=SVSUBTYPES_ALL,
        gt_one_of=["0/1", "1/0", "0|1", "1|0", "./1", "1/.", ".|1", "1|."],
        max_brk_segduprepeat=2,
    ),
    # -- GenotypeChoice.HOM -------------------------------------------------
    GenotypeCriteria(
        comment="Trust the genotype to show homozygous alternative genotype",
        genotype=GenotypeChoice.HOM,
        select_sv_sub_type=SVSUBTYPES_ALL,
        gt_one_of=["1/1", "1|1", "1"],
        max_brk_segduprepeat=2,
    ),
    # -- GenotypeChoice.VARIANT ---------------------------------------------
    GenotypeCriteria(
        comment="Trust the genotype to show variant genotype",
        genotype=GenotypeChoice.VARIANT,
        select_sv_sub_type=SVSUBTYPES_ALL,
        gt_one_of=["0/1", "1/0", "0|1", "1|0", "./1", "1/.", ".|1", "1|.", "1/1", "1|1", "1"],
        max_brk_segduprepeat=2,
    ),
    # -- GenotypeChoice.NON_VARIANT -----------------------------------------
    GenotypeCriteria(
        comment="Trust the genotype to show non-variant genotype",
        genotype=GenotypeChoice.NON_VARIANT,
        select_sv_sub_type=SVSUBTYPES_ALL,
        gt_one_of=["0/0", "0|0", "0", "./0", "0/.", "./."],
        max_brk_segduprepeat=2,
    ),
]


@attrs.define(frozen=True)
class _GenotypeCriteria:
    #: Clin-SV inspired high confidence filter criteria settings.
    svish_high: typing.List[GenotypeCriteria] = GT_CRITERIA_HIGH
    #: Clin-SV inspired pass filter criteria settings.
    svish_pass: typing.List[GenotypeCriteria] = GT_CRITERIA_PASS
    #: Default filters, using read pair signal only.
    default: typing.List[GenotypeCriteria] = GT_CRITERIA_DEFAULT


#: Presets for the filter criteria.
GENOTYPE_CRITERIA_DEFINITIONS: _GenotypeCriteria = _GenotypeCriteria()


@unique
class GenotypeCriteriaDefinitions(Enum):
    SVISH_HIGH = "svish_high"
    SVISH_PASS = "svish_pass"
    DEFAULT = "default"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the regions/genes category"""
        return getattr(GENOTYPE_CRITERIA_DEFINITIONS, self.value)


@attrs.define(frozen=True)
class QuickPresets:
    """Type for the global quick presets."""

    #: user-readable label
    label: str
    #: inheritance to use
    inheritance: Inheritance
    #: presets in category presets
    frequency: Frequency
    #: presets in category impact
    impact: Impact
    #: presets in category chromosomes
    chromosomes: Chromosomes
    #: regulatory configuration
    regulatory: Regulatory
    #: TAD setting
    tad: Tad
    #: settings for known pathogenic variants and ClinVar
    known_patho: KnownPatho
    #: genotype criteria set to use
    genotype_criteria: GenotypeCriteriaDefinitions
    #: database to use
    database: Database = Database.REFSEQ

    def to_settings(self, samples: typing.Iterable[PedigreeMember]) -> typing.Dict[str, typing.Any]:
        """Return the overall settings given the sample names"""
        assert len(set(s.family for s in samples)) == 1
        return {
            **self.frequency.to_settings(),
            **self.impact.to_settings(),
            **self.chromosomes.to_settings(),
            **self.tad.to_settings(),
            **self.known_patho.to_settings(),
            **{"genotype_criteria": self.genotype_criteria.to_settings()},
            **self.inheritance.to_settings(samples),
            **self.regulatory.to_settings(),
            "database": self.database.value,
        }


@attrs.define(frozen=True)
class _QuickPresetList:
    """Type for the top-level quick preset list."""

    #: default settings, all rare variants
    defaults: QuickPresets = QuickPresets(
        label="defaults",
        inheritance=Inheritance.ANY,
        frequency=Frequency.STRICT,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: de novo variant (similar to dominant, more strict on unaffected)
    de_novo: QuickPresets = QuickPresets(
        label="de novo",
        inheritance=Inheritance.DE_NOVO,
        frequency=Frequency.STRICT,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: dominant (present in affected, not present in unaffected)
    dominant: QuickPresets = QuickPresets(
        label="dominant",
        inheritance=Inheritance.DOMINANT,
        frequency=Frequency.STRICT,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: homozygous recessive (hom. in affected, het. in parents)
    homozygous_recessive: QuickPresets = QuickPresets(
        label="homozygous recessive",
        inheritance=Inheritance.HOMOZYGOUS_RECESSIVE,
        frequency=Frequency.RELAXED,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: Compound heterozygous recessive (het in affected, het. in ONE parent)
    compound_heterozygous: QuickPresets = QuickPresets(
        label="compound heterozygous",
        inheritance=Inheritance.COMPOUND_HETEROZYGOUS,
        frequency=Frequency.RELAXED,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: X-recessive
    x_recessive: QuickPresets = QuickPresets(
        label="X-recessive",
        inheritance=Inheritance.X_RECESSIVE,
        frequency=Frequency.RELAXED,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: clinVar pathogenic
    clinvar_pathogenic: QuickPresets = QuickPresets(
        label="ClinVar pathogenic",
        inheritance=Inheritance.AFFECTED_CARRIERS,
        frequency=Frequency.ANY,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: mitochondrial
    mitochondrial: QuickPresets = QuickPresets(
        label="mitochondrial",
        inheritance=Inheritance.AFFECTED_CARRIERS,
        frequency=Frequency.ANY,
        impact=Impact.ANY,
        chromosomes=Chromosomes.MT_CHROMOSOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )
    #: all variants
    whole_genome: QuickPresets = QuickPresets(
        label="whole genome",
        inheritance=Inheritance.ANY,
        frequency=Frequency.ANY,
        impact=Impact.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        regulatory=Regulatory.DEFAULT,
        tad=Tad.DEFAULT,
        known_patho=KnownPatho.DEFAULT,
        genotype_criteria=GenotypeCriteriaDefinitions.DEFAULT,
        database=Database.REFSEQ,
    )


#: Top level quick presets.
QUICK_PRESETS: _QuickPresetList = _QuickPresetList()
