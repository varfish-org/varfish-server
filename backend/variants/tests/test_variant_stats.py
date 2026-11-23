"""Tests for ``variants.variant_stats``."""

from test_plus.test import TestCase

from variants.tests.factories import SmallVariantFactory, SmallVariantSetFactory
from variants.variant_stats import gather_variant_stats

#: Effect terms that mehari writes since v0.51.0.
MEHARI_0_51_EFFECTS = (
    "bidirectional_gene_fusion",
    "copy_number_change",
    "copy_number_increase",
    "five_prime_duplicated_transcript",
    "frameshift_unidirectional_gene_fusion",
    "gene_fusion",
    "inframe_unidirectional_gene_fusion",
    "three_prime_duplicated_transcript",
    "transcript_fusion",
    "unidirectional_gene_fusion",
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
