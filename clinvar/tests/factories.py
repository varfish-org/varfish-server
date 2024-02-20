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
    clinvar_version = "99991122.1"
    variation_type = "snv"
    set_type = "variant"
    symbols = factory.Sequence(lambda n: ["SYMBOL%d" % n])
    hgnc_ids = factory.Sequence(lambda n: ["HGNC:%d" % n])
    vcv = factory.Sequence(lambda n: "VCV%d" % (12345 + n))
    summary_clinvar_review_status_label = "criteria provided, single committer"
    summary_clinvar_pathogenicity_label = "likely pathogenic"
    summary_clinvar_pathogenicity = ["likely pathogenic"]
    summary_clinvar_gold_stars = 1
    summary_paranoid_review_status_label = "criteria provided, single committer"
    summary_paranoid_pathogenicity_label = "likely pathogenic"
    summary_paranoid_pathogenicity = ["likely pathogenic"]
    summary_paranoid_gold_stars = 1
    details = []

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
