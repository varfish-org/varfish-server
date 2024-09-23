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
from variants.query_presets import Version


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
SCHEMA_QUERY = load_json("variants/schemas/case-query-v1.json")


#: JSON draft 7 validator that uses default values.
DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


@unique
class Effects(Enum):
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
class RecessiveMode(Enum):
    RECESSIVE = "recessive"
    COMPOUND_RECESSIVE = "compound-recessive"


@attr.s(auto_attribs=True, frozen=True)
class FailChoice(Enum):
    IGNORE = "ignore"
    DROP_VARIANT = "drop-variant"
    NO_CALL = "no-call"


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
    COMPHET_INDEX = "comphet-index"
    RECESSIVE_INDEX = "recessive-index"
    RECESSIVE_PARENT = "recessive-parent"


@attr.s(auto_attribs=True, frozen=True)
class QualitySettings:
    """Data structure to hold the information for quality settings"""

    dp_het: typing.Optional[int] = None
    dp_hom: typing.Optional[int] = None
    number: typing.Optional[float] = None
    gq: typing.Optional[int] = None
    ab: typing.Optional[float] = None
    ad: typing.Optional[int] = None
    ad_max: typing.Optional[int] = None
    fail: FailChoice = FailChoice.IGNORE


@attr.s(auto_attribs=True, frozen=True)
class Range:
    """Data structure to hold a range"""

    start: int
    end: int


@attr.s(auto_attribs=True, frozen=True)
class GenomicRegion:
    """Data structure eto hold the information for genomic regions."""

    chromosome: str
    range: typing.Optional[Range] = None

    def with_chr_stripped(self):
        chromosome = self.chromosome
        if chromosome.startswith("chr"):
            chromosome = chromosome[len("chr") :]
        return GenomicRegion(chromosome, self.range)

    def to_str(self):
        if not self.range:
            return self.chromosome
        return "%s:%d-%d" % (self.chromosome, self.range.start, self.range.end)


def convert_genomic_region(region: GenomicRegion):
    if region.range:
        return (region.chromosome, region.range.start, region.range.end)
    else:
        return (region.chromosome, None, None)


@attr.s(auto_attribs=True, frozen=True)
class CaseQuery:
    """Data structure to hold the information for a single case query"""

    database: str

    effects: typing.List[Effects]

    exac_enabled: bool
    gnomad_exomes_enabled: bool
    gnomad_genomes_enabled: bool
    thousand_genomes_enabled: bool
    inhouse_enabled: bool
    mtdb_enabled: bool
    helixmtdb_enabled: bool
    mitomap_enabled: bool

    quality: typing.Dict[str, QualitySettings]
    genotype: typing.Dict[str, typing.Optional[GenotypeChoice]]

    # Variables with default values
    # -----------------------------

    #: Version of the query schema.
    VERSION: Version = Version(major=0, minor=0)  # noqa

    transcripts_coding: bool = True
    transcripts_noncoding: bool = False

    var_type_snv: bool = True
    var_type_indel: bool = True
    var_type_mnv: bool = True

    max_exon_dist: typing.Optional[int] = None

    flag_simple_empty: bool = True
    flag_bookmarked: bool = True
    flag_incidental: bool = True
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

    flag_phenotype_match_empty: bool = True
    flag_phenotype_match_negative: bool = True
    flag_phenotype_match_positive: bool = True
    flag_phenotype_match_uncertain: bool = True

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
    genomic_region: typing.Optional[typing.List[GenomicRegion]] = None

    require_in_clinvar: bool = False
    clinvar_include_benign: bool = True
    clinvar_include_pathogenic: bool = True
    clinvar_include_likely_benign: bool = True
    clinvar_include_likely_pathogenic: bool = True
    clinvar_include_uncertain_significance: bool = True

    patho_enabled: bool = False
    patho_score: typing.Optional[str] = None

    prio_enabled: bool = False
    gm_enabled: bool = False
    pedia_enabled: bool = False
    prio_algorithm: typing.Optional[str] = None
    prio_hpo_terms: typing.Optional[typing.List[str]] = None
    prio_gm: typing.Optional[str] = None
    photo_file: typing.Optional[str] = None

    recessive_mode: typing.Optional[RecessiveMode] = None
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

    def convert(self, case: Case, query: CaseQuery) -> typing.Dict[str, typing.Any]:
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
            "require_in_clinvar": query.require_in_clinvar,
            "clinvar_include_benign": query.clinvar_include_benign,
            "clinvar_include_likely_benign": query.clinvar_include_likely_benign,
            "clinvar_include_uncertain_significance": query.clinvar_include_uncertain_significance,
            "clinvar_include_likely_pathogenic": query.clinvar_include_likely_pathogenic,
            "clinvar_include_pathogenic": query.clinvar_include_pathogenic,
            "flag_simple_empty": query.flag_simple_empty,
            "flag_bookmarked": query.flag_bookmarked,
            "flag_incidental": query.flag_incidental,
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
            "flag_phenotype_match_empty": query.flag_phenotype_match_empty,
            "flag_phenotype_match_negative": query.flag_phenotype_match_negative,
            "flag_phenotype_match_positive": query.flag_phenotype_match_positive,
            "flag_phenotype_match_uncertain": query.flag_phenotype_match_uncertain,
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
            "genomic_region": list(map(convert_genomic_region, query.genomic_region)),
            "prio_enabled": query.prio_enabled,
            "prio_algorithm": query.prio_algorithm,
            "prio_hpo_terms": query.prio_hpo_terms,
            "prio_gm": query.prio_gm,
            "photo_file": query.photo_file,
            "patho_enabled": query.patho_enabled,
            "gm_enabled": query.gm_enabled,
            "pedia_enabled": query.pedia_enabled,
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
        if query.recessive_mode == RecessiveMode.RECESSIVE and query.recessive_index:
            result["recessive_indices"] = {case.name: query.recessive_index}
        elif query.recessive_mode == RecessiveMode.COMPOUND_RECESSIVE and query.recessive_index:
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
                gt = query.genotype.get(sample, GenotypeChoice.ANY)
                if gt:
                    result["%s_gt" % sample] = gt.value
        # add quality field for each sample
        for sample in case_samples:
            value = query.quality.get(sample, QualitySettings())
            if value and value.fail:
                result["%s_fail" % sample] = value.fail.value
            else:
                result["%s_fail" % sample] = None
            for field in ("dp_het", "dp_hom", "ab", "gq", "ad", "ad_max"):
                result["%s_%s" % (sample, field)] = (
                    None if not value else getattr(value, field, None)
                )

        return result, query.VERSION


def genomic_region_to_str(region: typing.Tuple[str, typing.Optional[int], typing.Optional[int]]):
    chromosome, start, end = region
    if start is None and end is None:
        return chromosome
    return "%s:%s-%s" % (chromosome, start, end)


class FormToQueryJsonConverter:
    """Helper class"""

    def convert(self, form: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        result = {
            "database": form.get("database_select"),  # OK
            "var_type_snv": form.get("var_type_snv"),  # OK
            "var_type_mnv": form.get("var_type_mnv"),  # OK
            "var_type_indel": form.get("var_type_indel"),  # OK
            "exac_enabled": form.get("exac_enabled"),  # OK
            "exac_frequency": form.get("exac_frequency"),  # OK
            "exac_heterozygous": form.get("exac_heterozygous"),  # OK
            "exac_homozygous": form.get("exac_homozygous"),  # OK
            "exac_hemizygous": form.get("exac_hemizygous"),  # OK
            "thousand_genomes_enabled": form.get("thousand_genomes_enabled"),  # OK
            "thousand_genomes_frequency": form.get("thousand_genomes_frequency"),  # OK
            "thousand_genomes_heterozygous": form.get("thousand_genomes_heterozygous"),  # OK
            "thousand_genomes_homozygous": form.get("thousand_genomes_homozygous"),  # OK
            "thousand_genomes_hemizygous": form.get("thousand_genomes_hemizygous"),  # OK
            "gnomad_exomes_enabled": form.get("gnomad_exomes_enabled"),  # OK
            "gnomad_exomes_frequency": form.get("gnomad_exomes_frequency"),  # OK
            "gnomad_exomes_heterozygous": form.get("gnomad_exomes_heterozygous"),  # OK
            "gnomad_exomes_homozygous": form.get("gnomad_exomes_homozygous"),  # OK
            "gnomad_exomes_hemizygous": form.get("gnomad_exomes_hemizygous"),  # OK
            "gnomad_genomes_enabled": form.get("gnomad_genomes_enabled"),  # OK
            "gnomad_genomes_frequency": form.get("gnomad_genomes_frequency"),  # OK
            "gnomad_genomes_heterozygous": form.get("gnomad_genomes_heterozygous"),  # OK
            "gnomad_genomes_homozygous": form.get("gnomad_genomes_homozygous"),  # OK
            "gnomad_genomes_hemizygous": form.get("gnomad_genomes_hemizygous"),  # OK
            "inhouse_enabled": form.get("inhouse_enabled"),  # OK
            "inhouse_carriers": form.get("inhouse_carriers"),  # OK
            "inhouse_heterozygous": form.get("inhouse_heterozygous"),  # OK
            "inhouse_homozygous": form.get("inhouse_homozygous"),  # OK
            "inhouse_hemizygous": form.get("inhouse_hemizygous"),  # OK
            "max_exon_dist": form.get("max_exon_dist"),  # OK
            "mtdb_enabled": form.get("mtdb_enabled"),  # OK
            "mtdb_count": form.get("mtdb_count"),  # OK
            "mtdb_frequency": form.get("mtdb_frequency"),  # OK
            "helixmtdb_enabled": form.get("helixmtdb_enabled"),  # OK
            "helixmtdb_hom_count": form.get("helixmtdb_hom_count"),  # OK
            "helixmtdb_het_count": form.get("helixmtdb_het_count"),  # OK
            "helixmtdb_frequency": form.get("helixmtdb_frequency"),  # OK
            "mitomap_enabled": form.get("mitomap_enabled"),  # OK
            "mitomap_count": form.get("mitomap_count"),  # OK
            "mitomap_frequency": form.get("mitomap_frequency"),  # OK
            "transcripts_coding": form.get("transcripts_coding"),  # OK
            "transcripts_noncoding": form.get("transcripts_noncoding"),  # OK
            "require_in_clinvar": form.get("require_in_clinvar"),  # OK
            "clinvar_include_benign": form.get("clinvar_include_benign"),  # OK
            "clinvar_include_likely_benign": form.get("clinvar_include_likely_benign"),  # OK
            "clinvar_include_uncertain_significance": form.get(
                "clinvar_include_uncertain_significance"
            ),  # OK
            "clinvar_include_likely_pathogenic": form.get(
                "clinvar_include_likely_pathogenic"
            ),  # OK
            "clinvar_include_pathogenic": form.get("clinvar_include_pathogenic"),  # OK
            "clinvar_paranoid_mode": form.get("clinvar_paranoid_mode", False),  # OK
            "flag_simple_empty": form.get("flag_simple_empty"),  # OK
            "flag_bookmarked": form.get("flag_bookmarked"),  # OK
            "flag_incidental": form.get("flag_incidental"),  # OK
            "flag_candidate": form.get("flag_candidate"),  # OK
            "flag_doesnt_segregate": form.get("flag_doesnt_segregate"),  # OK
            "flag_final_causative": form.get("flag_final_causative"),  # OK
            "flag_for_validation": form.get("flag_for_validation"),  # OK
            "flag_no_disease_association": form.get("flag_no_disease_association"),  # OK
            "flag_segregates": form.get("flag_segregates"),  # OK
            "flag_molecular_empty": form.get("flag_molecular_empty"),  # OK
            "flag_molecular_negative": form.get("flag_molecular_negative"),  # OK
            "flag_molecular_positive": form.get("flag_molecular_positive"),  # OK
            "flag_molecular_uncertain": form.get("flag_molecular_uncertain"),  # OK
            "flag_phenotype_match_empty": form.get("flag_phenotype_match_empty"),  # OK
            "flag_phenotype_match_negative": form.get("flag_phenotype_match_negative"),  # OK
            "flag_phenotype_match_positive": form.get("flag_phenotype_match_positive"),  # OK
            "flag_phenotype_match_uncertain": form.get("flag_phenotype_match_uncertain"),  # OK
            "flag_summary_empty": form.get("flag_summary_empty"),  # OK
            "flag_summary_negative": form.get("flag_summary_negative"),  # OK
            "flag_summary_positive": form.get("flag_summary_positive"),  # OK
            "flag_summary_uncertain": form.get("flag_summary_uncertain"),  # OK
            "flag_validation_empty": form.get("flag_validation_empty"),  # OK
            "flag_validation_negative": form.get("flag_validation_negative"),  # OK
            "flag_validation_positive": form.get("flag_validation_positive"),  # OK
            "flag_validation_uncertain": form.get("flag_validation_uncertain"),  # OK
            "flag_visual_empty": form.get("flag_visual_empty"),  # OK
            "flag_visual_negative": form.get("flag_visual_negative"),  # OK
            "flag_visual_positive": form.get("flag_visual_positive"),  # OK
            "flag_visual_uncertain": form.get("flag_visual_uncertain"),  # OK
            "gene_blocklist": form.get("gene_blocklist"),  # OK
            "gene_allowlist": form.get("gene_allowlist"),  # OK
            "genomic_region": [genomic_region_to_str(r) for r in form.get("genomic_region")],  # OK
            "prio_enabled": form.get("prio_enabled"),  # OK
            "prio_algorithm": form.get("prio_algorithm"),  # OK
            "prio_hpo_terms": form.get("prio_hpo_terms"),  # OK
            "patho_enabled": form.get("patho_enabled"),  # OK
            "patho_score": form.get("patho_score"),  # OK
            "effects": form.get("effects"),  # OK
            "recessive_mode": None,
            "recessive_index": None,
            "quality": {},
            "genotype": {},
        }

        # transform fields
        for e in form.keys():
            # turn genotype information into dictionary
            if e.endswith("_gt"):
                sample = e[:-3]
                gt = form[e]
                if sample not in result["quality"]:
                    result["quality"][sample] = {}
                if gt == "recessive-index":
                    result["recessive_index"] = sample
                    result["recessive_mode"] = RecessiveMode.RECESSIVE.value
                elif gt == "index":
                    gt = "recessive-index"
                    result["recessive_index"] = sample
                    result["recessive_mode"] = RecessiveMode.COMPOUND_RECESSIVE.value
                result["genotype"][sample] = gt

            # turn quality information into dictionary
            for field in ("dp_het", "dp_hom", "ab", "gq", "ad", "ad_max", "fail"):
                if e.endswith("_%s" % field):
                    sample = e[: -len(field) - 1]
                    if sample not in result["quality"]:
                        result["quality"][sample] = {}
                    result["quality"][sample][field] = form[e]

        return result


def convert_query_json_to_small_variant_filter_form(
    case: Case, query_json: typing.Dict[str, typing.Any]
):
    """Helper function that converts case query JSON to form data for ``small_variant_filter_form`` in version 1."""
    tmp = copy.deepcopy(query_json)
    DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(tmp)
    query = cattr.structure(tmp, CaseQuery)
    if query.genomic_region:
        query = attrs.evolve(
            query,
            genomic_region=list(map(GenomicRegion.with_chr_stripped, query.genomic_region)),
        )
    return QueryJsonToFormConverter().convert(case, query)


def _structure_genomic_region(s, _):
    if not re.match("^[a-zA-Z0-9]+(:(\\d+(,\\d+)*)-(\\d+(,\\d+)*))?$", s):
        raise RuntimeError("Invalid genomic region string: %s" % repr(s))
    if ":" not in s:
        return GenomicRegion(chromosome=s)
    chrom, range_str = s.split(":")
    start, end = range_str.split("-")
    return GenomicRegion(
        chromosome=chrom, range=Range(int(start.replace(",", "")), int(end.replace(",", "")))
    )


cattr.register_structure_hook(GenomicRegion, _structure_genomic_region)


cattr.register_unstructure_hook(GenomicRegion, GenomicRegion.to_str)
