"""Factory Boy factory classes for ``clinvar``."""
import typing

import attr
import binning
import factory

from ..models import Clinvar


class ClinvarFactory(factory.django.DjangoModelFactory):
    """Factory for ``Clinvar`` records."""

    class Meta:
        model = Clinvar

    release = "GRCh37"
    chromosome = factory.Iterator((list(map(str, range(1, 23))) + ["X", "Y"]))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
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

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
