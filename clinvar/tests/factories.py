"""Factory Boy factory classes for ``clinvar``."""

import factory

from variants.tests.factories_data import SMALL_VARS, small_var_iterator, small_var_attribute

from ..models import Clinvar

#: The gene to create the frequencies for.
SYMBOL = "LAMA1"

#: Base data for ClinVar by gene.
CLINVAR_VARS = {SYMBOL: {"strand": "+"}}


def clin_var_attribute(gene, attribute):
    """Return attribute value for the given gene and attribute"""
    return CLINVAR_VARS[gene][attribute]


class ClinvarFactory(factory.django.DjangoModelFactory):
    """Factory for ``Clinvar`` records."""

    class Meta:
        model = Clinvar

    release = small_var_attribute(SYMBOL, "release")
    chromosome = small_var_attribute(SYMBOL, "chromosome")
    position = small_var_iterator(SYMBOL, "position")
    reference = small_var_iterator(SYMBOL, "reference")
    alternative = small_var_iterator(SYMBOL, "alternative")

    start = small_var_iterator(SYMBOL, "position")
    stop = factory.Sequence(
        lambda n: SMALL_VARS[SYMBOL]["position"][n]
        + len(SMALL_VARS[SYMBOL]["reference"][n])
        - len(SMALL_VARS[SYMBOL]["alternative"][n])
    )

    strand = clin_var_attribute(SYMBOL, "strand")
    variation_type = "Variant"
    variation_id = factory.Sequence(lambda n: 12345 + n)
    rcv = factory.Sequence(lambda n: "RCV%d" % (12345 + n))
    scv = factory.Sequence(lambda n: ["RCV%d" % (12345 + n)])
    allele_id = factory.Sequence(lambda n: 12345 + n)
    symbol = SYMBOL
    hgvs_c = small_var_iterator(SYMBOL, "refseq_hgvs_c")
    hgvs_p = small_var_iterator(SYMBOL, "refseq_hgvs_p")
    molecular_consequence = "some-molecular-consequence"
    clinical_significance = "benign"
    clinical_significance_ordered = ["benign"]
    pathogenic = 0
    likely_pathogenic = 0
    uncertain_significance = 0
    likely_benign = 0
    benign = 0
    review_status = "single submitter"
    review_status_ordered = ["criteria provided"]
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
