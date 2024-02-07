"""Utility code for query schemas."""

import copy
from enum import Enum, unique
import json
import os.path
import re
import typing

import attr
import attrs
import cattr
from jsonschema import Draft7Validator, validators

from variants.forms import FILTER_FORM_TRANSLATE_EFFECTS
from variants.models import Case


def extend_with_default(validator_class):
    """Helper function to create a jsonschema validator class that uses default value for unset values."""
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for key, sub_schema in properties.items():
            if "default" in sub_schema:
                instance.setdefault(key, sub_schema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            yield error

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


def load_json(path):
    """Helper function to load JSON file relative to project root directory."""
    full_path = os.path.join(os.path.dirname(__file__), "..", path)
    with open(full_path, "rt") as inputf:
        return json.load(inputf)


#: Query schema v1
SCHEMA_QUERY_V1 = load_json("variants/schemas/case-query-v1.json")


#: JSON draft 7 validator that uses default values.
DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


@unique
class EffectsV1(Enum):
    THREE_PRIME_UTR_EXON_VARIANT = "3_prime_UTR_exon_variant"
    THREE_PRIME_UTR_INTRON_VARIANT = "3_prime_UTR_intron_variant"
    FIVE_PRIME_UTR_EXON_VARIANT = "5_prime_UTR_exon_variant"
    FIVE_PRIME_UTR_INTRON_VARIANT = "5_prime_UTR_intron_variant"
    CODING_TRANSCRIPT_INTRON_VARIANT = "coding_transcript_intron_variant"
    COMPLEX_SUBSTITUTION = "complex_substitution"
    DIRECT_TANDEM_DUPLICATION = "direct_tandem_duplication"
    DISRUPTIVE_INFRAME_DELETION = "disruptive_inframe_deletion"
    DISRUPTIVE_INFRAME_INSERTION = "disruptive_inframe_insertion"
    DOWNSTREAM_GENE_VARIANT = "downstream_gene_variant"
    EXON_LOSS_VARIANT = "exon_loss_variant"
    FEATURE_TRUNCATION = "feature_truncation"
    FRAMESHIFT_ELONGATION = "frameshift_elongation"
    FRAMESHIFT_TRUNCATION = "frameshift_truncation"
    FRAMESHIFT_VARIANT = "frameshift_variant"
    INFRAME_DELETION = "inframe_deletion"
    INFRAME_INSERTION = "inframe_insertion"
    INTERGENIC_VARIANT = "intergenic_variant"
    INTERNAL_FEATURE_ELONGATION = "internal_feature_elongation"
    MAX_EXON_DIST = "max_exon_dist"
    MISSENSE_VARIANT = "missense_variant"
    MNV = "mnv"
    NON_CODING_TRANSCRIPT_EXON_VARIANT = "non_coding_transcript_exon_variant"
    NON_CODING_TRANSCRIPT_INTRON_VARIANT = "non_coding_transcript_intron_variant"
    SLICE_ACCEPTOR_VARIANT = "splice_acceptor_variant"
    SPLICE_DONOR_VARIANT = "splice_donor_variant"
    SPLICE_REGION_VARIANT = "splice_region_variant"
    START_LOST = "start_lost"
    STOP_GAINED = "stop_gained"
    STOP_LOST = "stop_lost"
    STOP_RETAINED_VARIANT = "stop_retained_variant"
    STRUCTURAL_VARIANT = "structural_variant"
    SYNONYMOUS_VARIANT = "synonymous_variant"
    TRANSCRIPT_ABLATION = "transcript_ablation"
    UPSTREAM_GENE_VARIANT = "upstream_gene_variant"


@unique
class RecessiveModeV1(Enum):
    RECESSIVE = "recessive"
    COMPOUND_RECESSIVE = "compound-recessive"


@attr.s(auto_attribs=True, frozen=True)
class FailChoiceV1(Enum):
    IGNORE = "ignore"
    DROP_VARIANT = "drop-variant"
    NO_CALL = "no-call"


@unique
class GenotypeChoiceV1(Enum):
    ANY = "any"
    REF = "ref"
    HET = "het"
    HOM = "hom"
    NON_HOM = "non-hom"
    VARIANT = "variant"
    NON_VARIANT = "non-variant"
    NON_REFERENCE = "non-reference"
    COMPHET_INDEX = "comphet-index"
    RECESSIVE_INDEX = "recessive-index"
    RECESSIVE_PARENT = "recessive-parent"


@attr.s(auto_attribs=True, frozen=True)
class QualitySettingsV1:
    """Data structure to hold the information for quality settings"""

    dp_het: typing.Optional[int] = None
    dp_hom: typing.Optional[int] = None
    number: typing.Optional[float] = None
    gq: typing.Optional[int] = None
    ab: typing.Optional[float] = None
    ad: typing.Optional[int] = None
    ad_max: typing.Optional[int] = None
    fail: FailChoiceV1 = FailChoiceV1.IGNORE


@attr.s(auto_attribs=True, frozen=True)
class RangeV1:
    """Data structure to hold a range"""

    start: int
    end: int


@attr.s(auto_attribs=True, frozen=True)
class GenomicRegionV1:
    """Data structure eto hold the information for genomic regions."""

    chromosome: str
    range: typing.Optional[RangeV1] = None

    def with_chr_stripped(self):
        chromosome = self.chromosome
        if chromosome.startswith("chr"):
            chromosome = chromosome[len("chr") :]
        return GenomicRegionV1(chromosome, self.range)

    def to_str(self):
        if not self.range:
            return self.chromosome
        return "%s:%d-%d" % (self.chromosome, self.range.start, self.range.end)


def convert_genomic_region_v1(region: GenomicRegionV1):
    if region.range:
        return (region.chromosome, region.range.start, region.range.end)
    else:
        return (region.chromosome, None, None)


@attr.s(auto_attribs=True, frozen=True)
class CaseQueryV1:
    """Data structure to hold the information for a single case query"""

    database: str

    effects: typing.List[EffectsV1]

    exac_enabled: bool
    gnomad_exomes_enabled: bool
    gnomad_genomes_enabled: bool
    thousand_genomes_enabled: bool
    inhouse_enabled: bool
    mtdb_enabled: bool
    helixmtdb_enabled: bool
    mitomap_enabled: bool

    quality: typing.Dict[str, QualitySettingsV1]
    genotype: typing.Dict[str, typing.Optional[GenotypeChoiceV1]]

    transcripts_coding: bool = True
    transcripts_noncoding: bool = False

    var_type_snv: bool = True
    var_type_indel: bool = True
    var_type_mnv: bool = True

    max_exon_dist: typing.Optional[int] = None

    flag_simple_empty: bool = True
    flag_bookmarked: bool = True
    flag_candidate: bool = True
    flag_doesnt_segregate: bool = True
    flag_final_causative: bool = True
    flag_for_validation: bool = True
    flag_no_disease_association: bool = True
    flag_segregates: bool = True

    flag_molecular_empty: bool = True
    flag_molecular_negative: bool = True
    flag_molecular_positive: bool = True
    flag_molecular_uncertain: bool = True

    flag_phenotype_empty: bool = True
    flag_phenotype_negative: bool = True
    flag_phenotype_positive: bool = True
    flag_phenotype_uncertain: bool = True

    flag_summary_empty: bool = True
    flag_summary_negative: bool = True
    flag_summary_positive: bool = True
    flag_summary_uncertain: bool = True

    flag_validation_empty: bool = True
    flag_validation_negative: bool = True
    flag_validation_positive: bool = True
    flag_validation_uncertain: bool = True

    flag_visual_empty: bool = True
    flag_visual_negative: bool = True
    flag_visual_positive: bool = True
    flag_visual_uncertain: bool = True

    gene_allowlist: typing.Optional[typing.List[str]] = None
    gene_blocklist: typing.Optional[typing.List[str]] = None
    genomic_region: typing.Optional[typing.List[GenomicRegionV1]] = None

    remove_if_in_dbsnp: bool = False

    require_in_hgmd_public: bool = False
    require_in_clinvar: bool = False
    clinvar_include_benign: bool = True
    clinvar_include_pathogenic: bool = True
    clinvar_include_likely_benign: bool = True
    clinvar_include_likely_pathogenic: bool = True
    clinvar_include_uncertain_significance: bool = True

    patho_enabled: bool = False
    patho_score: typing.Optional[str] = None

    prio_enabled: bool = False
    prio_algorithm: typing.Optional[str] = None
    prio_hpo_terms: typing.Optional[typing.List[str]] = None

    recessive_mode: typing.Optional[RecessiveModeV1] = None
    recessive_index: typing.Optional[str] = None

    exac_frequency: typing.Optional[float] = None
    exac_heterozygous: typing.Optional[int] = None
    exac_homozygous: typing.Optional[int] = None
    exac_hemizygous: typing.Optional[int] = None

    gnomad_exomes_frequency: typing.Optional[float] = None
    gnomad_exomes_heterozygous: typing.Optional[int] = None
    gnomad_exomes_homozygous: typing.Optional[int] = None
    gnomad_exomes_hemizygous: typing.Optional[int] = None

    gnomad_genomes_frequency: typing.Optional[float] = None
    gnomad_genomes_heterozygous: typing.Optional[int] = None
    gnomad_genomes_homozygous: typing.Optional[int] = None
    gnomad_genomes_hemizygous: typing.Optional[int] = None

    thousand_genomes_frequency: typing.Optional[float] = None
    thousand_genomes_heterozygous: typing.Optional[int] = None
    thousand_genomes_homozygous: typing.Optional[int] = None
    thousand_genomes_hemizygous: typing.Optional[int] = None

    inhouse_carriers: typing.Optional[int] = None
    inhouse_heterozygous: typing.Optional[int] = None
    inhouse_homozygous: typing.Optional[int] = None
    inhouse_hemizygous: typing.Optional[int] = None

    mtdb_count: typing.Optional[int] = None
    mtdb_frequency: typing.Optional[float] = None

    helixmtdb_frequency: typing.Optional[float] = None
    helixmtdb_het_count: typing.Optional[int] = None
    helixmtdb_hom_count: typing.Optional[int] = None

    mitomap_count: typing.Optional[int] = None
    mitomap_frequency: typing.Optional[float] = None


class QueryJsonToFormConverter:
    """Helper class"""

    def convert(self, case: Case, query: CaseQueryV1) -> typing.Dict[str, typing.Any]:
        result = {
            "database_select": query.database,
            "var_type_snv": query.var_type_snv,
            "var_type_mnv": query.var_type_mnv,
            "var_type_indel": query.var_type_indel,
            "exac_enabled": query.exac_enabled,
            "exac_frequency": query.exac_frequency,
            "exac_heterozygous": query.exac_heterozygous,
            "exac_homozygous": query.exac_homozygous,
            "thousand_genomes_enabled": query.thousand_genomes_enabled,
            "thousand_genomes_frequency": query.thousand_genomes_frequency,
            "thousand_genomes_heterozygous": query.thousand_genomes_heterozygous,
            "thousand_genomes_homozygous": query.thousand_genomes_homozygous,
            "gnomad_exomes_enabled": query.gnomad_exomes_enabled,
            "gnomad_exomes_frequency": query.gnomad_exomes_frequency,
            "gnomad_exomes_heterozygous": query.gnomad_exomes_heterozygous,
            "gnomad_exomes_homozygous": query.gnomad_exomes_homozygous,
            "gnomad_genomes_enabled": query.gnomad_genomes_enabled,
            "gnomad_genomes_frequency": query.gnomad_genomes_frequency,
            "gnomad_genomes_heterozygous": query.gnomad_genomes_heterozygous,
            "gnomad_genomes_homozygous": query.gnomad_genomes_homozygous,
            "inhouse_enabled": query.inhouse_enabled,
            "inhouse_carriers": query.inhouse_carriers,
            "inhouse_heterozygous": query.inhouse_heterozygous,
            "inhouse_homozygous": query.inhouse_homozygous,
            "max_exon_dist": query.max_exon_dist,
            "mtdb_enabled": query.mtdb_enabled,
            "mtdb_count": query.mtdb_count,
            "mtdb_frequency": query.mtdb_frequency,
            "helixmtdb_enabled": query.helixmtdb_enabled,
            "helixmtdb_hom_count": query.helixmtdb_hom_count,
            "helixmtdb_het_count": query.helixmtdb_het_count,
            "helixmtdb_frequency": query.helixmtdb_frequency,
            "mitomap_enabled": query.mitomap_enabled,
            "mitomap_count": query.mitomap_count,
            "transcripts_coding": query.transcripts_coding,
            "transcripts_noncoding": query.transcripts_noncoding,
            "remove_if_in_dbsnp": query.remove_if_in_dbsnp,
            "require_in_hgmd_public": query.require_in_hgmd_public,
            "require_in_clinvar": query.require_in_clinvar,
            "clinvar_include_benign": query.clinvar_include_benign,
            "clinvar_include_likely_benign": query.clinvar_include_likely_benign,
            "clinvar_include_uncertain_significance": query.clinvar_include_uncertain_significance,
            "clinvar_include_likely_pathogenic": query.clinvar_include_likely_pathogenic,
            "clinvar_include_pathogenic": query.clinvar_include_pathogenic,
            "flag_simple_empty": query.flag_simple_empty,
            "flag_bookmarked": query.flag_bookmarked,
            "flag_candidate": query.flag_candidate,
            "flag_doesnt_segregate": query.flag_doesnt_segregate,
            "flag_final_causative": query.flag_final_causative,
            "flag_for_validation": query.flag_for_validation,
            "flag_no_disease_association": query.flag_no_disease_association,
            "flag_segregates": query.flag_segregates,
            "flag_molecular_empty": query.flag_molecular_empty,
            "flag_molecular_negative": query.flag_molecular_negative,
            "flag_molecular_positive": query.flag_molecular_positive,
            "flag_molecular_uncertain": query.flag_molecular_uncertain,
            "flag_phenotype_empty": query.flag_phenotype_empty,
            "flag_phenotype_negative": query.flag_phenotype_negative,
            "flag_phenotype_positive": query.flag_phenotype_positive,
            "flag_phenotype_uncertain": query.flag_phenotype_uncertain,
            "flag_summary_empty": query.flag_summary_empty,
            "flag_summary_negative": query.flag_summary_negative,
            "flag_summary_positive": query.flag_summary_positive,
            "flag_summary_uncertain": query.flag_summary_uncertain,
            "flag_validation_empty": query.flag_validation_empty,
            "flag_validation_negative": query.flag_validation_negative,
            "flag_validation_positive": query.flag_validation_positive,
            "flag_validation_uncertain": query.flag_validation_uncertain,
            "flag_visual_empty": query.flag_visual_empty,
            "flag_visual_negative": query.flag_visual_negative,
            "flag_visual_positive": query.flag_visual_positive,
            "flag_visual_uncertain": query.flag_visual_uncertain,
            "gene_blocklist": query.gene_blocklist,
            "gene_allowlist": query.gene_allowlist,
            "genomic_region": list(map(convert_genomic_region_v1, query.genomic_region)),
            "prio_enabled": query.prio_enabled,
            "prio_algorithm": query.prio_algorithm,
            "prio_hpo_terms": query.prio_hpo_terms,
            "patho_enabled": query.patho_enabled,
            "patho_score": query.patho_score,
            "effects": [e.value for e in query.effects],
            # Add static values that are not relevant for the API use case
            "submit": "display",
            "export_comments": True,
            "export_flags": True,
            "file_type": "xlsx",
            "training_mode": False,
            "result_rows_limit": 200,
        }

        # add effect_* fields
        effects = {e.value for e in query.effects}
        for flat, entry in FILTER_FORM_TRANSLATE_EFFECTS.items():
            result[flat] = entry in effects

        # add recessive information
        result["compound_recessive_indices"] = {}
        result["recessive_indices"] = {}
        if query.recessive_mode == RecessiveModeV1.RECESSIVE and query.recessive_index:
            result["recessive_indices"] = {case.name: query.recessive_index}
        elif query.recessive_mode == RecessiveModeV1.COMPOUND_RECESSIVE and query.recessive_index:
            result["compound_recessive_indices"] = {case.name: query.recessive_index}

        case_samples = {p["patient"] for p in case.pedigree}
        quality_samples = set(query.quality.keys())
        if case_samples != quality_samples:
            raise ValueError(
                f"Case and quality samples are not equal: {case_samples} vs {quality_samples}"
            )
        genotype_samples = set(query.genotype.keys())
        if case_samples != quality_samples:
            raise ValueError(
                f"Case and genotype samples are not equal: {case_samples} vs {genotype_samples}"
            )

        # add genotype fields for each sample
        for sample in case_samples:
            if sample in result["recessive_indices"].values():
                result["%s_gt" % sample] = "recessive-index"
            elif sample in result["compound_recessive_indices"].values():
                result["%s_gt" % sample] = "index"
            else:
                gt = query.genotype.get(sample, GenotypeChoiceV1.ANY)
                if gt:
                    result["%s_gt" % sample] = gt.value
        # add quality field for each sample
        for sample in case_samples:
            value = query.quality.get(sample, QualitySettingsV1())
            if value and value.fail:
                result["%s_fail" % sample] = value.fail.value
            else:
                result["%s_fail" % sample] = None
            for field in ("dp_het", "dp_hom", "ab", "gq", "ad", "ad_max"):
                result["%s_%s" % (sample, field)] = (
                    None if not value else getattr(value, field, None)
                )

        return result


def convert_query_json_to_small_variant_filter_form_v1(
    case: Case, query_json: typing.Dict[str, typing.Any]
):
    """Helper function that converts case query JSON to form data for ``small_variant_filter_form`` in version 1."""
    tmp = copy.deepcopy(query_json)
    DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(tmp)
    query = cattr.structure(tmp, CaseQueryV1)
    if query.genomic_region:
        query = attrs.evolve(
            query,
            genomic_region=list(map(GenomicRegionV1.with_chr_stripped, query.genomic_region)),
        )
    return QueryJsonToFormConverter().convert(case, query)


def _structure_genomic_region(s, _):
    if not re.match("^[a-zA-Z0-9]+(:(\\d+(,\\d+)*)-(\\d+(,\\d+)*))?$", s):
        raise RuntimeError("Invalid genomic region string: %s" % repr(s))
    if ":" not in s:
        return GenomicRegionV1(chromosome=s)
    chrom, range_str = s.split(":")
    start, end = range_str.split("-")
    return GenomicRegionV1(
        chromosome=chrom, range=RangeV1(int(start.replace(",", "")), int(end.replace(",", "")))
    )


cattr.register_structure_hook(GenomicRegionV1, _structure_genomic_region)


cattr.register_unstructure_hook(GenomicRegionV1, GenomicRegionV1.to_str)
