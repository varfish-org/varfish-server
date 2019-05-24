"""Factory Boy factory classes for ``clinvar``."""
import typing

import attr
import factory

from ..models import Clinvar


class ClinvarFactory(factory.django.DjangoModelFactory):
    """Factory for ``Clinvar`` records."""

    class Meta:
        model = Clinvar

    release = "GRCh37"
    chromosome = factory.Iterator((list(map(str, range(1, 23))) + ["X", "Y"]))
    position = factory.Sequence(lambda n: (n + 1) * 100)
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    start = factory.SelfAttribute("position")
    stop = factory.LazyAttribute(lambda o: o.position + len(o.reference) - len(o.alternative))

    strand = "+"
    variation_type = "Variant"
    variation_id = factory.Sequence(lambda n: 12345 + n)
    rcv = factory.Sequence(lambda n: "RCV%d" % (12345 + n))
    scv = factory.Sequence(lambda n: ["RCV%d" % (12345 + n)])
    allele_id = factory.Sequence(lambda n: 12345 + n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
    hgvs_c = "c.123C>T"
    hgvs_p = "p.I2T"
    molecular_consequence = "some-molecular-consequence"
    clinical_significance = ""
    clinical_significance_ordered = []
    pathogenic = 0
    likely_pathogenic = 0
    uncertain_significance = 0
    likely_benign = 0
    benign = 0
    review_status = "practice guideline"
    review_status_ordered = ["practice guideline"]
    last_evaluated = "2016-06-14"
    all_submitters = ["Some Submitter"]
    submitters_ordered = ["Some Submitter"]
    all_traits = ["Some trait"]
    all_pmids = [12345]
    inheritance_modes = ""
    age_of_onset = ""
    prevalence = ""
    disease_mechanism = ""
    origin = ["germline"]
    xrefs = ["Some xref"]
    dates_ordered = ["2016-06-14"]
    multi = 1


@attr.s(auto_attribs=True)
class ClinvarFormDataFactory:
    # Testbase should add %s_gt % patient !!!
    # no need for this data outside clinvar queries.
    # Pathogenicity
    clinvar_include_benign: bool = False
    clinvar_include_likely_benign: bool = False
    clinvar_include_uncertain_significance: bool = False
    clinvar_include_likely_pathogenic: bool = False
    clinvar_include_pathogenic: bool = False
    # Origin
    clinvar_origin_germline: bool = True
    clinvar_origin_somatic: bool = False
    # Reliability
    clinvar_status_practice_guideline: bool = True
    clinvar_status_expert_panel: bool = True
    clinvar_status_multiple_no_conflict: bool = True
    clinvar_status_conflict: bool = True
    clinvar_status_single: bool = True
    clinvar_status_no_criteria: bool = True
    clinvar_status_no_assertion: bool = True
    # Database
    database_select: str = "refseq"
    # Genotypes
    compound_recessive_enabled: bool = False
    # Limit on number of rows
    result_rows_limit: int = 500
    # Filter selection for form.
    flag_bookmarked: bool = True
    flag_candidate: bool = True
    flag_final_causative: bool = True
    flag_for_validation: bool = True
    flag_phenotype_match_empty: bool = True
    flag_phenotype_match_negative: bool = True
    flag_phenotype_match_positive: bool = True
    flag_phenotype_match_uncertain: bool = True
    flag_simple_empty: bool = True
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
    # Clinvar/HGMD
    require_in_clinvar: bool = False
    remove_if_in_dbsnp: bool = False
    require_in_hgmd_public: bool = False
    display_hgmd_public_membership: bool = True


@attr.s(auto_attribs=True)
class ProcessedClinvarFormDataFactory:
    # Pathogenicity
    clinvar_include_benign: bool = False
    clinvar_include_likely_benign: bool = False
    clinvar_include_uncertain_significance: bool = False
    clinvar_include_likely_pathogenic: bool = False
    clinvar_include_pathogenic: bool = False
    # Origin
    clinvar_origin_germline: bool = True
    clinvar_origin_somatic: bool = False
    # Reliability
    clinvar_status_practice_guideline: bool = True
    clinvar_status_expert_panel: bool = True
    clinvar_status_multiple_no_conflict: bool = True
    clinvar_status_conflict: bool = True
    clinvar_status_single: bool = True
    clinvar_status_no_criteria: bool = True
    clinvar_status_no_assertion: bool = True
    # Database
    database_select: str = "refseq"
    # Genotypes
    compound_recessive_enabled: bool = False
    # Filter selection for form.
    flag_bookmarked: bool = True
    flag_candidate: bool = True
    flag_final_causative: bool = True
    flag_for_validation: bool = True
    flag_phenotype_match_empty: bool = True
    flag_phenotype_match_negative: bool = True
    flag_phenotype_match_positive: bool = True
    flag_phenotype_match_uncertain: bool = True
    flag_simple_empty: bool = True
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
    # Clinvar/HGMD
    require_in_clinvar: bool = False
    remove_if_in_dbsnp: bool = False
    require_in_hgmd_public: bool = False
    display_hgmd_public_membership: bool = True

    # This is a dummy attribute to generate the name-dependent fields.
    # It is removed after initialization.
    names: typing.List[str] = []

    def __attrs_post_init__(self):
        for name in self.names:
            self.__dict__.update(
                {
                    "%s_fail" % name: "ignore",
                    "%s_gt" % name: "any",
                    "%s_dp_het" % name: 0,
                    "%s_dp_hom" % name: 0,
                    "%s_ab" % name: 0,
                    "%s_gq" % name: 0,
                    "%s_ad" % name: 0,
                }
            )
        delattr(self, "names")


@attr.s(auto_attribs=True)
class ClinvarFormDataFactory(ProcessedClinvarFormDataFactory):
    result_rows_limit: int = 500
    submit: str = "display"

    def __attrs_post_init__(self):
        for name in self.names:
            self.__dict__.update({"%s_export" % name: True})
        super().__attrs_post_init__()


@attr.s(auto_attribs=True)
class ResubmitClinvarFormDataFactory(ClinvarFormDataFactory):
    pass
