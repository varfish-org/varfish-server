"""Presets for small variant query configuration

The presets are organized on three levels

- Top level presets in ``QUICK_PRESETS`` select the ``_QuickPresets``
- Each `_QuickPresets` defines per category presets in each of the categories
- For each category, there is a `_CategoryPresets` type for the corresponding
  ``CATEGORY_PRESETS`` constant that defines the presets
"""

from enum import Enum, unique
import itertools
import typing

import attrs


@unique
class Sex(Enum):
    """Represents the sex in a ``PedigreeMember``."""

    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


@unique
class DiseaseState(Enum):
    """Represents the disease status in a ``PedigreeMember``"""

    UNKNOWN = 0
    UNAFFECTED = 1
    AFFECTED = 2


#: Value to code for "no father/mother"
NOBODY = "0"


@attrs.frozen
class PedigreeMember:
    """Member in a pedigree"""

    family: typing.Optional[str]
    name: str
    father: str
    mother: str
    sex: Sex
    disease_state: DiseaseState

    def has_both_parents(self):
        return self.father != NOBODY and self.mother != NOBODY

    def is_singleton(self):
        return self.father == NOBODY and self.mother == NOBODY

    def has_single_parent(self):
        return not self.has_both_parents() and not self.is_singleton()

    def is_affected(self):
        return self.disease_state == DiseaseState.AFFECTED


@unique
class GenotypeChoice(Enum):
    ANY = "any"
    REF = "ref"
    HET = "het"
    HOM = "hom"
    NON_HOM = "non-hom"
    VARIANT = "variant"
    NON_VARIANT = "non-variant"
    NON_REFERENCE = "non-reference"

    def to_vcf_gt_values(self):
        """Convert to values that would appear as ``GT`` in a VCF file"""
        return {
            GenotypeChoice.ANY: [
                "0",
                "1",
                "0/0",
                "0|0",
                "0/1",
                "0/1",
                "1/0",
                "1|0",
                "1/1",
                "1|1",
                ".",
                "./.",
            ],
            GenotypeChoice.REF: ["0", "0/0", "0|0"],
            GenotypeChoice.HET: ["0/1", "0/1", "1/0", "1|0"],
            GenotypeChoice.HOM: ["0", "1", "0/0", "0|0", "1/1", "1|1"],
            GenotypeChoice.NON_HOM: ["0/1", "0/1", "1/0", "1|0", ".", "./."],
            GenotypeChoice.VARIANT: ["1", "0/1", "0/1", "1/0", "1|0", "1/1", "1|1"],
            GenotypeChoice.NON_VARIANT: ["0", "0/0", "0|0", ".", "./."],
            GenotypeChoice.NON_REFERENCE: [
                "1",
                "0/1",
                "0/1",
                "1/0",
                "1|0",
                "1/1",
                "1|1",
                ".",
                "./.",
            ],
        }[self]


def genotype_choice_value_to_genotype(value):
    for c in GenotypeChoice:
        if c.value == value:
            return c
    raise ValueError(f"Not a valid genotype value: {value}")


@unique
class Inheritance(Enum):
    """Preset options for category inheritance"""

    ANY = "any"
    DE_NOVO = "de_novo"
    DOMINANT = "dominant"
    HOMOZYGOUS_RECESSIVE = "homozygous_recessive"
    COMPOUND_HETEROZYGOUS = "compound_heterozygous"
    RECESSIVE = "recessive"
    X_RECESSIVE = "x_recessive"
    AFFECTED_CARRIERS = "affected_carriers"
    CUSTOM = "custom"

    def _is_recessive(self):
        return self in (
            Inheritance.HOMOZYGOUS_RECESSIVE,
            Inheritance.COMPOUND_HETEROZYGOUS,
            Inheritance.RECESSIVE,
        )

    def to_settings(
        self, samples: typing.Iterable[PedigreeMember], index: typing.Optional[str] = None
    ) -> typing.Dict[str, typing.Any]:
        """Return settings for the inheritance

        All sample names must be of the same family.
        """
        assert len(set(s.family for s in samples)) == 1

        samples_by_name = {s.name: s for s in samples}

        # Select first affected invididual that has both parents set, fall back to first affected otherwise
        affected_samples = [s for s in samples if s.is_affected()]
        index_candidates = list(
            itertools.chain(
                [s for s in affected_samples if s.has_both_parents()],
                [s for s in affected_samples if s.has_single_parent()],
                affected_samples,
                samples,
            )
        )

        if self._is_recessive():
            return self._to_settings_recessive(affected_samples, index, index_candidates, samples)
        elif self == Inheritance.X_RECESSIVE:
            return self._to_settings_x_recessive(index_candidates, samples, samples_by_name)
        elif self == Inheritance.AFFECTED_CARRIERS:
            return {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    s.name: (
                        GenotypeChoice.VARIANT.value
                        if s.is_affected()
                        else GenotypeChoice.ANY.value
                    )
                    for s in samples
                },
            }
        elif self == Inheritance.DE_NOVO:
            return {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    s.name: (
                        GenotypeChoice.VARIANT.value
                        if s.name == index_candidates[0].name
                        else GenotypeChoice.REF.value
                    )
                    for s in samples
                },
            }
        elif self == Inheritance.DOMINANT:
            return {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    s.name: (
                        GenotypeChoice.HET.value if s.is_affected() else GenotypeChoice.REF.value
                    )
                    for s in samples
                },
            }
        elif self == Inheritance.ANY:
            return {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {s.name: GenotypeChoice.ANY.value for s in samples},
            }
        else:
            raise ValueError(f"Cannot generate settings for inheritance {self}")

    def _to_settings_x_recessive(self, index_candidates, samples, samples_by_name):
        male_index_candidates = list(
            itertools.chain(
                [s for s in index_candidates if s.sex == Sex.MALE],
                [s for s in index_candidates if s.sex == Sex.UNKNOWN],
                index_candidates,
                samples,
            )
        )
        recessive_index = male_index_candidates[0]
        index_father = samples_by_name.get(recessive_index.father, None)
        index_mother = samples_by_name.get(recessive_index.mother, None)
        others = [
            s
            for s in samples
            if s.name not in (recessive_index.name, recessive_index.father, recessive_index.mother)
        ]
        genotype = {recessive_index.name: GenotypeChoice.HOM}
        if index_father and index_father.is_affected():
            genotype[recessive_index.father] = GenotypeChoice.HOM
            if index_mother:
                genotype[recessive_index.mother] = GenotypeChoice.REF
        elif index_father and not index_father.is_affected():
            genotype[recessive_index.father] = GenotypeChoice.REF
            if index_mother:
                genotype[recessive_index.mother] = GenotypeChoice.HET
        elif index_mother:  # and not index_father
            genotype[recessive_index.mother] = GenotypeChoice.ANY
        for other in others:
            genotype[other.name] = GenotypeChoice.ANY
        result = {
            "recessive_index": recessive_index.name,
            "recessive_mode": None,
            "genotype": {k: e.value for k, e in genotype.items()},
        }
        return result

    def _to_settings_recessive(self, affected_samples, index, index_candidates, samples):
        # Get index, parents, and others (not index, not parents) individuals
        recessive_index = index_candidates[0]
        if index is None:
            index = index_candidates[0].name
        parents = [s for s in samples if s.name in (recessive_index.father, recessive_index.mother)]
        parent_names = {p.name for p in parents}
        others = {s for s in affected_samples if s.name != index and s.name not in parent_names}
        # Fill ``genotype`` for the index
        if self == Inheritance.HOMOZYGOUS_RECESSIVE:
            genotype = {recessive_index.name: GenotypeChoice.HOM.value}
            mode = {"recessive_mode": None}
        elif self == Inheritance.COMPOUND_HETEROZYGOUS:
            genotype = {recessive_index.name: None}
            mode = {"recessive_mode": "compound-recessive"}
        elif self == Inheritance.RECESSIVE:
            genotype = {recessive_index.name: None}
            mode = {"recessive_mode": "recessive"}
        else:  # pragma: no cover
            raise RuntimeError(f"Unexpected recessive mode of inheritance: {self}")
        # Fill ``genotype`` for parents and others
        if self == Inheritance.HOMOZYGOUS_RECESSIVE:
            affected_parents = len([p for p in parents if p.is_affected()])
            for parent in parents:
                if parent.is_affected():
                    genotype[parent.name] = GenotypeChoice.HOM.value
                else:
                    if affected_parents > 0:
                        genotype[parent.name] = GenotypeChoice.REF.value
                    else:
                        genotype[parent.name] = GenotypeChoice.HET.value
        else:
            for parent in parents:
                genotype[parent.name] = None
        for other in others:
            genotype[other.name] = GenotypeChoice.ANY.value
        # Compose the dict with recessive index, recessive mode, and genotype
        result = {
            "recessive_index": recessive_index.name,
            "genotype": {k: e for k, e in genotype.items()},
            **mode,
        }
        return result


@attrs.frozen
class _FrequencyPresets:
    """Type for providing immutable frequency presets"""

    #: Presets for "dominant super strict" frequency
    dominant_super_strict: typing.Dict[str, typing.Any] = {
        "thousand_genomes_enabled": True,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 1,
        "thousand_genomes_hemizygous": None,
        "thousand_genomes_frequency": 0.002,
        "exac_enabled": True,
        "exac_homozygous": 0,
        "exac_heterozygous": 1,
        "exac_hemizygous": None,
        "exac_frequency": 0.002,
        "gnomad_exomes_enabled": True,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 1,
        "gnomad_exomes_hemizygous": None,
        "gnomad_exomes_frequency": 0.002,
        "gnomad_genomes_enabled": True,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 1,
        "gnomad_genomes_hemizygous": None,
        "gnomad_genomes_frequency": 0.002,
        "inhouse_enabled": True,
        "inhouse_homozygous": None,
        "inhouse_heterozygous": None,
        "inhouse_hemizygous": None,
        "inhouse_carriers": 20,
        "mtdb_enabled": False,
        "mtdb_count": None,
        "mtdb_frequency": None,
        "helixmtdb_enabled": False,
        "helixmtdb_het_count": None,
        "helixmtdb_hom_count": None,
        "helixmtdb_frequency": None,
        "mitomap_enabled": False,
        "mitomap_count": None,
        "mitomap_frequency": None,
    }
    #: Presets for "dominant strict" frequency
    dominant_strict: typing.Dict[str, typing.Any] = {
        "thousand_genomes_enabled": True,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 4,
        "thousand_genomes_hemizygous": None,
        "thousand_genomes_frequency": 0.002,
        "exac_enabled": True,
        "exac_homozygous": 0,
        "exac_heterozygous": 10,
        "exac_hemizygous": None,
        "exac_frequency": 0.002,
        "gnomad_exomes_enabled": True,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 20,
        "gnomad_exomes_hemizygous": None,
        "gnomad_exomes_frequency": 0.002,
        "gnomad_genomes_enabled": True,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 4,
        "gnomad_genomes_hemizygous": None,
        "gnomad_genomes_frequency": 0.002,
        "inhouse_enabled": True,
        "inhouse_homozygous": None,
        "inhouse_heterozygous": None,
        "inhouse_hemizygous": None,
        "inhouse_carriers": 20,
        "mtdb_enabled": True,
        "mtdb_count": 10,
        "mtdb_frequency": 0.01,
        "helixmtdb_enabled": True,
        "helixmtdb_hom_count": 200,
        "helixmtdb_het_count": None,
        "helixmtdb_frequency": 0.01,
        "mitomap_enabled": False,
        "mitomap_count": None,
        "mitomap_frequency": None,
    }
    #: Presets for "dominant relaxed" frequency
    dominant_relaxed: typing.Dict[str, typing.Any] = {
        "thousand_genomes_enabled": True,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 10,
        "thousand_genomes_hemizygous": None,
        "thousand_genomes_frequency": 0.01,
        "exac_enabled": True,
        "exac_homozygous": 0,
        "exac_heterozygous": 25,
        "exac_hemizygous": None,
        "exac_frequency": 0.01,
        "gnomad_exomes_enabled": True,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 50,
        "gnomad_exomes_hemizygous": None,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_genomes_enabled": True,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 20,
        "gnomad_genomes_hemizygous": None,
        "gnomad_genomes_frequency": 0.01,
        "inhouse_enabled": True,
        "inhouse_homozygous": None,
        "inhouse_heterozygous": None,
        "inhouse_hemizygous": None,
        "inhouse_carriers": 20,
        "mtdb_enabled": True,
        "mtdb_count": 50,
        "mtdb_frequency": 0.15,
        "helixmtdb_enabled": True,
        "helixmtdb_het_count": None,
        "helixmtdb_hom_count": 400,
        "helixmtdb_frequency": 0.15,
        "mitomap_enabled": False,
        "mitomap_count": None,
        "mitomap_frequency": None,
    }
    #: Presets for "recessive strict" frequency
    recessive_strict: typing.Dict[str, typing.Any] = {
        "thousand_genomes_enabled": True,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 24,
        "thousand_genomes_hemizygous": None,
        "thousand_genomes_frequency": 0.001,
        "exac_enabled": True,
        "exac_homozygous": 0,
        "exac_heterozygous": 60,
        "exac_hemizygous": None,
        "exac_frequency": 0.001,
        "gnomad_exomes_enabled": True,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 120,
        "gnomad_exomes_hemizygous": None,
        "gnomad_exomes_frequency": 0.001,
        "gnomad_genomes_enabled": True,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 15,
        "gnomad_genomes_hemizygous": None,
        "gnomad_genomes_frequency": 0.001,
        "inhouse_enabled": True,
        "inhouse_homozygous": None,
        "inhouse_heterozygous": None,
        "inhouse_hemizygous": None,
        "inhouse_carriers": 20,
        "mtdb_enabled": False,
        "mtdb_count": None,
        "mtdb_frequency": None,
        "helixmtdb_enabled": False,
        "helixmtdb_het_count": None,
        "helixmtdb_hom_count": None,
        "helixmtdb_frequency": None,
        "mitomap_enabled": False,
        "mitomap_count": None,
        "mitomap_frequency": None,
    }
    #: Presets for "recessive relaxed" frequency
    recessive_relaxed: typing.Dict[str, typing.Any] = {
        "thousand_genomes_enabled": True,
        "thousand_genomes_homozygous": 4,
        "thousand_genomes_heterozygous": 240,
        "thousand_genomes_hemizygous": None,
        "thousand_genomes_frequency": 0.01,
        "exac_enabled": True,
        "exac_homozygous": 10,
        "exac_heterozygous": 600,
        "exac_hemizygous": None,
        "exac_frequency": 0.01,
        "gnomad_exomes_enabled": True,
        "gnomad_exomes_homozygous": 20,
        "gnomad_exomes_heterozygous": 1200,
        "gnomad_exomes_hemizygous": None,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_genomes_enabled": True,
        "gnomad_genomes_homozygous": 4,
        "gnomad_genomes_heterozygous": 150,
        "gnomad_genomes_hemizygous": None,
        "gnomad_genomes_frequency": 0.01,
        "inhouse_enabled": True,
        "inhouse_homozygous": None,
        "inhouse_heterozygous": None,
        "inhouse_hemizygous": None,
        "inhouse_carriers": 20,
        "mtdb_enabled": False,
        "mtdb_count": None,
        "mtdb_frequency": None,
        "helixmtdb_enabled": False,
        "helixmtdb_het_count": None,
        "helixmtdb_hom_count": None,
        "helixmtdb_frequency": None,
        "mitomap_enabled": False,
        "mitomap_count": None,
        "mitomap_frequency": None,
    }
    #: Presets for "any" frequency
    any: typing.Dict[str, typing.Any] = {
        "thousand_genomes_enabled": False,
        "thousand_genomes_homozygous": None,
        "thousand_genomes_heterozygous": None,
        "thousand_genomes_hemizygous": None,
        "thousand_genomes_frequency": None,
        "exac_enabled": False,
        "exac_homozygous": None,
        "exac_heterozygous": None,
        "exac_hemizygous": None,
        "exac_frequency": None,
        "gnomad_exomes_enabled": False,
        "gnomad_exomes_homozygous": None,
        "gnomad_exomes_heterozygous": None,
        "gnomad_exomes_hemizygous": None,
        "gnomad_exomes_frequency": None,
        "gnomad_genomes_enabled": False,
        "gnomad_genomes_homozygous": None,
        "gnomad_genomes_heterozygous": None,
        "gnomad_genomes_hemizygous": None,
        "gnomad_genomes_frequency": None,
        "inhouse_enabled": False,
        "inhouse_homozygous": None,
        "inhouse_heterozygous": None,
        "inhouse_carriers": None,
        "mtdb_enabled": False,
        "mtdb_count": None,
        "mtdb_frequency": None,
        "helixmtdb_enabled": False,
        "helixmtdb_het_count": None,
        "helixmtdb_hom_count": None,
        "helixmtdb_frequency": None,
        "mitomap_enabled": False,
        "mitomap_count": None,
        "mitomap_frequency": None,
    }


#: Presets for the impact related settings by frequency preset option
FREQUENCY_PRESETS: _FrequencyPresets = _FrequencyPresets()


@unique
class Frequency(Enum):
    """Preset options for category frequency"""

    DOMINANT_SUPER_STRICT = "dominant_super_strict"
    DOMINANT_STRICT = "dominant_strict"
    DOMINANT_RELAXED = "dominant_relaxed"
    RECESSIVE_STRICT = "recessive_strict"
    RECESSIVE_RELAXED = "recessive_relaxed"
    CUSTOM = "custom"
    ANY = "any"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the frequency category"""
        return getattr(FREQUENCY_PRESETS, self.value)


@attrs.frozen
class _ImpactPresets:
    """Type for providing immutable impact presets"""

    #: Presets for "null variant" impact
    null_variant: typing.Dict[str, typing.Any] = {
        "var_type_snv": True,
        "var_type_mnv": True,
        "var_type_indel": True,
        "transcripts_coding": True,
        "transcripts_noncoding": False,
        "max_exon_dist": None,
        "effects": [
            "exon_loss_variant",
            "feature_elongation",
            "feature_truncation",
            "frameshift_elongation",
            "frameshift_truncation",
            "frameshift_variant",
            "internal_feature_elongation",
            "splice_acceptor_variant",
            "splice_donor_variant",
            "start_lost",
            "stop_gained",
            "stop_lost",
            "structural_variant",
            "transcript_ablation",
            "transcript_amplification",
        ],
    }
    #: Presets for "amino acid change and splicing" impact
    aa_change_splicing: typing.Dict[str, typing.Any] = {
        "var_type_snv": True,
        "var_type_mnv": True,
        "var_type_indel": True,
        "transcripts_coding": True,
        "transcripts_noncoding": False,
        "max_exon_dist": None,
        "effects": [
            "complex_substitution",
            "conservative_inframe_deletion",
            "conservative_inframe_insertion",
            "direct_tandem_duplication",
            "disruptive_inframe_deletion",
            "disruptive_inframe_insertion",
            "exon_loss_variant",
            "exonic_splice_region_variant",
            "feature_elongation",
            "feature_truncation",
            "frameshift_elongation",
            "frameshift_truncation",
            "frameshift_variant",
            "inframe_deletion",
            "inframe_insertion",
            "internal_feature_elongation",
            "missense_variant",
            "mnv",
            "protein_altering_variant",
            "rare_amino_acid_variant",
            "splice_acceptor_variant",
            "splice_donor_5th_base_variant",
            "splice_donor_region_variant",
            "splice_donor_variant",
            "splice_polypyrimidine_tract_variant",
            "splice_region_variant",
            "start_lost",
            "stop_gained",
            "stop_lost",
            "structural_variant",
            "transcript_ablation",
            "transcript_amplification",
        ],
    }
    #: Presets for "all coding and deep intronic" impact
    all_coding_deep_intronic: typing.Dict[str, typing.Any] = {
        "var_type_snv": True,
        "var_type_mnv": True,
        "var_type_indel": True,
        "transcripts_coding": True,
        "transcripts_noncoding": False,
        "max_exon_dist": None,
        "effects": [
            "coding_sequence_variant",
            "coding_transcript_intron_variant",
            "complex_substitution",
            "conservative_inframe_deletion",
            "conservative_inframe_insertion",
            "direct_tandem_duplication",
            "disruptive_inframe_deletion",
            "disruptive_inframe_insertion",
            "exon_loss_variant",
            "exonic_splice_region_variant",
            "feature_elongation",
            "feature_truncation",
            "frameshift_elongation",
            "frameshift_truncation",
            "frameshift_variant",
            "inframe_deletion",
            "inframe_insertion",
            "internal_feature_elongation",
            "intron_variant",
            "missense_variant",
            "mnv",
            "protein_altering_variant",
            "rare_amino_acid_variant",
            "splice_acceptor_variant",
            "splice_donor_5th_base_variant",
            "splice_donor_region_variant",
            "splice_donor_variant",
            "splice_polypyrimidine_tract_variant",
            "splice_region_variant",
            "start_lost",
            "start_retained_variant",
            "stop_gained",
            "stop_lost",
            "stop_retained_variant",
            "structural_variant",
            "synonymous_variant",
            "transcript_ablation",
            "transcript_amplification",
        ],
    }
    #: Presets for "whole transcript" impact
    whole_transcript: typing.Dict[str, typing.Any] = {
        "var_type_snv": True,
        "var_type_mnv": True,
        "var_type_indel": True,
        "transcripts_coding": True,
        "transcripts_noncoding": True,
        "max_exon_dist": None,
        "effects": [
            "3_prime_UTR_exon_variant",
            "3_prime_UTR_intron_variant",
            "5_prime_UTR_exon_variant",
            "5_prime_UTR_intron_variant",
            "coding_sequence_variant",
            "coding_transcript_intron_variant",
            "complex_substitution",
            "conservative_inframe_deletion",
            "conservative_inframe_insertion",
            "direct_tandem_duplication",
            "disruptive_inframe_deletion",
            "disruptive_inframe_insertion",
            "downstream_gene_variant",
            "exon_loss_variant",
            "exonic_splice_region_variant",
            "feature_elongation",
            "feature_truncation",
            "frameshift_elongation",
            "frameshift_truncation",
            "frameshift_variant",
            "inframe_deletion",
            "inframe_insertion",
            "internal_feature_elongation",
            "intron_variant",
            "missense_variant",
            "mnv",
            "non_coding_transcript_exon_variant",
            "non_coding_transcript_intron_variant",
            "protein_altering_variant",
            "rare_amino_acid_variant",
            "splice_acceptor_variant",
            "splice_donor_5th_base_variant",
            "splice_donor_region_variant",
            "splice_donor_variant",
            "splice_polypyrimidine_tract_variant",
            "splice_region_variant",
            "start_lost",
            "start_retained_variant",
            "stop_gained",
            "stop_lost",
            "stop_retained_variant",
            "structural_variant",
            "synonymous_variant",
            "transcript_ablation",
            "transcript_amplification",
            "upstream_gene_variant",
        ],
    }
    #: Presets for "any" impact
    any: typing.Dict[str, typing.Any] = {
        "var_type_snv": True,
        "var_type_mnv": True,
        "var_type_indel": True,
        "transcripts_coding": True,
        "transcripts_noncoding": True,
        "max_exon_dist": None,
        "effects": [
            "3_prime_UTR_exon_variant",
            "3_prime_UTR_intron_variant",
            "5_prime_UTR_exon_variant",
            "5_prime_UTR_intron_variant",
            "coding_sequence_variant",
            "coding_transcript_intron_variant",
            "complex_substitution",
            "conservative_inframe_deletion",
            "conservative_inframe_insertion",
            "direct_tandem_duplication",
            "disruptive_inframe_deletion",
            "disruptive_inframe_insertion",
            "downstream_gene_variant",
            "exon_loss_variant",
            "exonic_splice_region_variant",
            "feature_elongation",
            "feature_truncation",
            "frameshift_elongation",
            "frameshift_truncation",
            "frameshift_variant",
            "gene_variant",
            "inframe_deletion",
            "inframe_insertion",
            "intergenic_variant",
            "internal_feature_elongation",
            "intron_variant",
            "missense_variant",
            "mnv",
            "non_coding_transcript_exon_variant",
            "non_coding_transcript_intron_variant",
            "protein_altering_variant",
            "rare_amino_acid_variant",
            "splice_acceptor_variant",
            "splice_donor_5th_base_variant",
            "splice_donor_region_variant",
            "splice_donor_variant",
            "splice_polypyrimidine_tract_variant",
            "splice_region_variant",
            "start_lost",
            "start_retained_variant",
            "stop_gained",
            "stop_lost",
            "stop_retained_variant",
            "structural_variant",
            "synonymous_variant",
            "transcript_ablation",
            "transcript_amplification",
            "upstream_gene_variant",
        ],
    }


#: Presets for the impact related settings by impact preset option
IMPACT_PRESETS: _ImpactPresets = _ImpactPresets()


@unique
class Impact(Enum):
    """Preset options for category impact"""

    NULL_VARIANT = "null_variant"
    AA_CHANGE_SPLICING = "aa_change_splicing"
    ALL_CODING_DEEP_INTRONIC = "all_coding_deep_intronic"
    WHOLE_TRANSCRIPT = "whole_transcript"
    CUSTOM = "custom"
    ANY = "any"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for the impact category"""
        return getattr(IMPACT_PRESETS, self.value)


@unique
class _QualityFail(Enum):
    """Enum for representing the action on variant call quality fail"""

    #: Drop variant
    DROP_VARIANT = "drop-variant"
    #: Ignore failure
    IGNORE = "ignore"
    #: Interpret as "no-call"
    NO_CALL = "no-call"


@attrs.frozen
class _QualityPresets:
    """Type for providing immutable quality presets"""

    #: Presets for "super strict" quality settings
    super_strict: typing.Dict[str, typing.Any] = {
        "dp_het": 10,
        "dp_hom": 5,
        "ab": 0.3,
        "gq": 30,
        "ad": 3,
        "ad_max": None,
        "fail": _QualityFail.DROP_VARIANT.value,
    }
    #: Presets for the "strict" quality settings
    strict: typing.Dict[str, typing.Any] = {
        "dp_het": 10,
        "dp_hom": 5,
        "ab": 0.2,
        "gq": 10,
        "ad": 3,
        "ad_max": None,
        "fail": _QualityFail.DROP_VARIANT.value,
    }
    #: Presets for the "relaxed" quality settings
    relaxed: typing.Dict[str, typing.Any] = {
        "dp_het": 8,
        "dp_hom": 4,
        "ab": 0.1,
        "gq": 10,
        "ad": 2,
        "ad_max": None,
        "fail": _QualityFail.DROP_VARIANT.value,
    }
    #: Presets for the "any" quality settings
    any: typing.Dict[str, typing.Any] = {
        "dp_het": 0,
        "dp_hom": 0,
        "ab": 0.0,
        "gq": 0,
        "ad": 0,
        "ad_max": None,
        "fail": _QualityFail.IGNORE.value,
    }


#: Presets for the quality related settings, by quality preset option
QUALITY_PRESETS: _QualityPresets = _QualityPresets()


@unique
class Quality(Enum):
    """Preset options for category quality"""

    ANY = "any"
    SUPER_STRICT = "super_strict"
    STRICT = "strict"
    RELAXED = "relaxed"
    CUSTOM = "custom"

    def to_settings(self, samples: typing.Iterable[PedigreeMember]) -> typing.Dict[str, typing.Any]:
        """Return settings for the quality category

        Returns a ``dict`` with the key ``quality`` that contains one entry for each sample from ``sample_names``
        that contains the quality filter settings for the given sample.

        All sample names must be of the same family.
        """
        assert len(set(s.family for s in samples)) == 1
        return {
            "quality": {
                sample.name: dict(getattr(QUALITY_PRESETS, self.value)) for sample in samples
            }
        }


@attrs.frozen
class _ChromosomePresets:
    """Type for providing immutable chromosome/region/gene presets"""

    #: Presets for the "whole genome" chromosome/region/gene settings
    whole_genome: typing.Dict[str, typing.Any] = {
        "genomic_region": [],
        "gene_allowlist": [],
        "gene_blocklist": [],
    }
    #: Presets for the "autosomes" chromosome/region/gene settings
    autosomes: typing.Dict[str, typing.Any] = {
        "genomic_region": list(f"{num}" for num in range(1, 23)),
        "gene_allowlist": [],
        "gene_blocklist": [],
    }
    #: Presets for the "X-chromosome" chromosome/region/gene settings
    x_chromosome: typing.Dict[str, typing.Any] = {
        "genomic_region": [
            "X",
        ],
        "gene_allowlist": [],
        "gene_blocklist": [],
    }
    #: Presets for the "Y-chromosomes" chromosome/region/gene settings
    y_chromosome: typing.Dict[str, typing.Any] = {
        "genomic_region": [
            "Y",
        ],
        "gene_allowlist": [],
        "gene_blocklist": [],
    }
    #: Presets for the "mitochondrial" chromosome/region/gene settings
    mt_chromosome: typing.Dict[str, typing.Any] = {
        "genomic_region": [
            "MT",
        ],
        "gene_allowlist": [],
        "gene_blocklist": [],
    }


#: Presets for the chromosome/region/gene related settings, by chromosome preset option
CHROMOSOME_PRESETS: _ChromosomePresets = _ChromosomePresets()


@unique
class Chromosomes(Enum):
    """Presets options for category chromosomes"""

    WHOLE_GENOME = "whole_genome"
    AUTOSOMES = "autosomes"
    X_CHROMOSOME = "x_chromosome"
    Y_CHROMOSOME = "y_chromosome"
    MT_CHROMOSOME = "mt_chromosome"
    CUSTOM = "custom"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for this flags etc. category"""
        return getattr(CHROMOSOME_PRESETS, self.value)


@attrs.frozen
class _FlagsEtcPresets:
    """Type for providing immutable chromosome/region/gene presets"""

    #: Presets for the "defaults" flags etc. settings
    defaults: typing.Dict[str, typing.Any] = {
        "clinvar_include_benign": False,
        "clinvar_include_likely_benign": False,
        "clinvar_include_likely_pathogenic": True,
        "clinvar_include_pathogenic": True,
        "clinvar_include_uncertain_significance": False,
        "clinvar_include_conflicting": False,
        "flag_bookmarked": True,
        "flag_incidental": True,
        "flag_candidate": True,
        "flag_doesnt_segregate": True,
        "flag_final_causative": True,
        "flag_for_validation": True,
        "flag_no_disease_association": True,
        "flag_molecular_empty": True,
        "flag_molecular_negative": True,
        "flag_molecular_positive": True,
        "flag_molecular_uncertain": True,
        "flag_phenotype_match_empty": True,
        "flag_phenotype_match_negative": True,
        "flag_phenotype_match_positive": True,
        "flag_phenotype_match_uncertain": True,
        "flag_segregates": True,
        "flag_simple_empty": True,
        "flag_summary_empty": True,
        "flag_summary_negative": True,
        "flag_summary_positive": True,
        "flag_summary_uncertain": True,
        "flag_validation_empty": True,
        "flag_validation_negative": True,
        "flag_validation_positive": True,
        "flag_validation_uncertain": True,
        "flag_visual_empty": True,
        "flag_visual_negative": True,
        "flag_visual_positive": True,
        "flag_visual_uncertain": True,
        "require_in_clinvar": False,
        "clinvar_paranoid_mode": False,
    }
    #: Presets for the "Clinvar only" flags etc. settings
    clinvar_only: typing.Dict[str, typing.Any] = {
        "flag_bookmarked": True,
        "flag_incidental": True,
        "flag_candidate": True,
        "flag_doesnt_segregate": True,
        "flag_final_causative": True,
        "flag_for_validation": True,
        "flag_no_disease_association": True,
        "flag_molecular_empty": True,
        "flag_molecular_negative": True,
        "flag_molecular_positive": True,
        "flag_molecular_uncertain": True,
        "flag_phenotype_match_empty": True,
        "flag_phenotype_match_negative": True,
        "flag_phenotype_match_positive": True,
        "flag_phenotype_match_uncertain": True,
        "flag_segregates": True,
        "flag_simple_empty": True,
        "flag_summary_empty": True,
        "flag_summary_negative": True,
        "flag_summary_positive": True,
        "flag_summary_uncertain": True,
        "flag_validation_empty": True,
        "flag_validation_negative": True,
        "flag_validation_positive": True,
        "flag_validation_uncertain": True,
        "flag_visual_empty": True,
        "flag_visual_negative": True,
        "flag_visual_positive": True,
        "flag_visual_uncertain": True,
        "require_in_clinvar": True,
        "clinvar_paranoid_mode": False,
    }
    #: Presets for the "user flagged" flags etc. settings
    user_flagged: typing.Dict[str, typing.Any] = {
        "clinvar_include_benign": False,
        "clinvar_include_likely_benign": False,
        "clinvar_include_likely_pathogenic": True,
        "clinvar_include_pathogenic": True,
        "clinvar_include_uncertain_significance": False,
        "flag_bookmarked": True,
        "flag_incidental": True,
        "flag_candidate": True,
        "flag_doesnt_segregate": True,
        "flag_final_causative": True,
        "flag_for_validation": True,
        "flag_no_disease_association": True,
        "flag_molecular_empty": False,
        "flag_molecular_negative": True,
        "flag_molecular_positive": True,
        "flag_molecular_uncertain": True,
        "flag_phenotype_match_empty": False,
        "flag_phenotype_match_negative": True,
        "flag_phenotype_match_positive": True,
        "flag_phenotype_match_uncertain": True,
        "flag_segregates": True,
        "flag_simple_empty": False,
        "flag_summary_empty": False,
        "flag_summary_negative": True,
        "flag_summary_positive": True,
        "flag_summary_uncertain": True,
        "flag_validation_empty": False,
        "flag_validation_negative": True,
        "flag_validation_positive": True,
        "flag_validation_uncertain": True,
        "flag_visual_empty": False,
        "flag_visual_negative": True,
        "flag_visual_positive": True,
        "flag_visual_uncertain": True,
        "require_in_clinvar": False,
        "clinvar_paranoid_mode": False,
    }


#: Presets for the chromosome/region/gene related settings, by chromosome preset option
FLAGSETC_PRESETS: _FlagsEtcPresets = _FlagsEtcPresets()


@unique
class FlagsEtc(Enum):
    """Preset options for category flags etc."""

    DEFAULTS = "defaults"
    CLINVAR_ONLY = "clinvar_only"
    USER_FLAGGED = "user_flagged"
    CUSTOM = "custom"

    def to_settings(self) -> typing.Dict[str, typing.Any]:
        """Return settings for this flags etc. category"""
        return getattr(FLAGSETC_PRESETS, self.value)


@unique
class Database(Enum):
    REFSEQ = "refseq"
    ENSEMBL = "ensembl"


@attrs.frozen
class Version:
    """Type for the version of the query settings"""

    #: major version of the query settings
    major: int
    #: minor version of the query settings
    minor: int


@attrs.frozen
class QuickPresets:
    """Type for the global quick presets"""

    #: a user-readable label
    label: str
    #: presets in category inheritance
    inheritance: Inheritance
    #: presets in category frequency
    frequency: Frequency
    #: presets in category impact
    impact: Impact
    #: presets in category quality
    quality: Quality
    #: presets in category chromosomes
    chromosomes: Chromosomes
    #: presets in category flags etc.
    flagsetc: FlagsEtc
    #: database to use
    database: Database = Database.REFSEQ

    def to_settings(self, samples: typing.Iterable[PedigreeMember]) -> typing.Dict[str, typing.Any]:
        """Return the overall settings given the sample names"""
        assert len(set(s.family for s in samples)) == 1
        return {
            **self.inheritance.to_settings(samples),
            **self.frequency.to_settings(),
            **self.impact.to_settings(),
            **self.quality.to_settings(samples),
            **self.chromosomes.to_settings(),
            **self.flagsetc.to_settings(),
            "database": self.database.value,
        }


@attrs.frozen
class _QuickPresetList:
    """Type for the top-level quick preset list"""

    #: default presets
    defaults: QuickPresets = QuickPresets(
        label="defaults",
        inheritance=Inheritance.ANY,
        frequency=Frequency.DOMINANT_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: *de novo* presets
    de_novo: QuickPresets = QuickPresets(
        label="de novo",
        inheritance=Inheritance.DE_NOVO,
        frequency=Frequency.DOMINANT_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.SUPER_STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: dominant presets
    dominant: QuickPresets = QuickPresets(
        label="dominant",
        inheritance=Inheritance.DOMINANT,
        frequency=Frequency.DOMINANT_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: homozygous recessive presets
    homozygous_recessive: QuickPresets = QuickPresets(
        label="homozygous recessive",
        inheritance=Inheritance.HOMOZYGOUS_RECESSIVE,
        frequency=Frequency.RECESSIVE_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: compound recessive recessive presets
    compound_recessive: QuickPresets = QuickPresets(
        label="compound recessive",
        inheritance=Inheritance.COMPOUND_HETEROZYGOUS,
        frequency=Frequency.RECESSIVE_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: recessive presets
    recessive: QuickPresets = QuickPresets(
        label="recessive",
        inheritance=Inheritance.RECESSIVE,
        frequency=Frequency.RECESSIVE_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: X-recessive presets
    x_recessive: QuickPresets = QuickPresets(
        label="X-recessive",
        inheritance=Inheritance.X_RECESSIVE,
        frequency=Frequency.RECESSIVE_STRICT,
        impact=Impact.AA_CHANGE_SPLICING,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.X_CHROMOSOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: Clinvar pathogenic presets
    clinvar_pathogenic: QuickPresets = QuickPresets(
        label="ClinVar pathogenic",
        inheritance=Inheritance.AFFECTED_CARRIERS,
        frequency=Frequency.ANY,
        impact=Impact.ANY,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.CLINVAR_ONLY,
    )
    #: mitochondrial recessive presets
    mitochondrial: QuickPresets = QuickPresets(
        label="mitochondrial",
        inheritance=Inheritance.AFFECTED_CARRIERS,
        frequency=Frequency.DOMINANT_STRICT,
        impact=Impact.ANY,
        quality=Quality.STRICT,
        chromosomes=Chromosomes.MT_CHROMOSOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )
    #: whole exome recessive presets
    whole_exome: QuickPresets = QuickPresets(
        label="whole exome",
        inheritance=Inheritance.ANY,
        frequency=Frequency.ANY,
        impact=Impact.ANY,
        quality=Quality.ANY,
        chromosomes=Chromosomes.WHOLE_GENOME,
        flagsetc=FlagsEtc.DEFAULTS,
    )


#: Top level quick presets.
QUICK_PRESETS: _QuickPresetList = _QuickPresetList()
