"""Tests for ``variants.variant_stats``."""

from test_plus.test import TestCase

from variants.tests.factories import SmallVariantFactory, SmallVariantSetFactory
from variants.variant_stats import gather_variant_stats

#: Effect terms that mehari writes for sequence alleles since v0.51.0.
MEHARI_0_51_EFFECTS = (
    "five_prime_duplicated_transcript",
    "three_prime_duplicated_transcript",
)


class TestGatherVariantStats(TestCase):
    def test_counts_effects_of_mehari_0_51(self):
        for effect in MEHARI_0_51_EFFECTS:
            with self.subTest(effect=effect):
                variant_set = SmallVariantSetFactory()
                SmallVariantFactory(variant_set=variant_set, ensembl_effect=[effect])
                sample = variant_set.case.pedigree[0]["patient"]

                effect_counts = gather_variant_stats(variant_set)[5]

                self.assertEqual(effect_counts[sample][effect], 1)
