"""Tests for var_stats_qc module, focusing on chromosome naming compatibility."""

import unittest

from var_stats_qc.qc import (
    VALID_CHROMOSOMES_GRCH37,
    VALID_CHROMOSOMES_GRCH38,
    normalize_chromosome_for_build,
    validate_chromosome_for_build,
)


class ChromosomeNamingTestCase(unittest.TestCase):
    """Test chromosome naming functions for GRCh37/GRCh38 compatibility."""

    def test_valid_chromosomes_constants(self):
        """Test that chromosome constant sets are correct."""
        # GRCh37 should have no chr prefix
        self.assertIn("1", VALID_CHROMOSOMES_GRCH37)
        self.assertIn("X", VALID_CHROMOSOMES_GRCH37)
        self.assertIn("MT", VALID_CHROMOSOMES_GRCH37)
        self.assertNotIn("chr1", VALID_CHROMOSOMES_GRCH37)

        # GRCh38 should have chr prefix (except MT -> chrM)
        self.assertIn("chr1", VALID_CHROMOSOMES_GRCH38)
        self.assertIn("chrX", VALID_CHROMOSOMES_GRCH38)
        self.assertIn("chrM", VALID_CHROMOSOMES_GRCH38)
        self.assertNotIn("1", VALID_CHROMOSOMES_GRCH38)
        self.assertNotIn("MT", VALID_CHROMOSOMES_GRCH38)

    def test_normalize_chromosome_grch37(self):
        """Test chromosome normalization for GRCh37."""
        # Autosomes
        self.assertEqual(normalize_chromosome_for_build("1", "GRCh37"), "1")
        self.assertEqual(normalize_chromosome_for_build("chr1", "GRCh37"), "1")
        self.assertEqual(normalize_chromosome_for_build("22", "GRCh37"), "22")

        # Sex chromosomes
        self.assertEqual(normalize_chromosome_for_build("X", "GRCh37"), "X")
        self.assertEqual(normalize_chromosome_for_build("chrX", "GRCh37"), "X")
        self.assertEqual(normalize_chromosome_for_build("Y", "GRCh37"), "Y")

        # Mitochondrial
        self.assertEqual(normalize_chromosome_for_build("MT", "GRCh37"), "MT")
        self.assertEqual(normalize_chromosome_for_build("M", "GRCh37"), "MT")
        self.assertEqual(normalize_chromosome_for_build("chrM", "GRCh37"), "MT")

    def test_normalize_chromosome_grch38(self):
        """Test chromosome normalization for GRCh38."""
        # Autosomes
        self.assertEqual(normalize_chromosome_for_build("1", "GRCh38"), "chr1")
        self.assertEqual(normalize_chromosome_for_build("chr1", "GRCh38"), "chr1")
        self.assertEqual(normalize_chromosome_for_build("22", "GRCh38"), "chr22")

        # Sex chromosomes
        self.assertEqual(normalize_chromosome_for_build("X", "GRCh38"), "chrX")
        self.assertEqual(normalize_chromosome_for_build("chrX", "GRCh38"), "chrX")
        self.assertEqual(normalize_chromosome_for_build("Y", "GRCh38"), "chrY")

        # Mitochondrial
        self.assertEqual(normalize_chromosome_for_build("MT", "GRCh38"), "chrM")
        self.assertEqual(normalize_chromosome_for_build("M", "GRCh38"), "chrM")
        self.assertEqual(normalize_chromosome_for_build("chrM", "GRCh38"), "chrM")

    def test_validate_chromosome_for_build(self):
        """Test chromosome validation for different builds."""
        # GRCh37 validation
        self.assertTrue(validate_chromosome_for_build("1", "GRCh37"))
        self.assertTrue(validate_chromosome_for_build("X", "GRCh37"))
        self.assertTrue(validate_chromosome_for_build("MT", "GRCh37"))
        self.assertFalse(validate_chromosome_for_build("chr1", "GRCh37"))
        self.assertFalse(validate_chromosome_for_build("chrX", "GRCh37"))

        # GRCh38 validation
        self.assertTrue(validate_chromosome_for_build("chr1", "GRCh38"))
        self.assertTrue(validate_chromosome_for_build("chrX", "GRCh38"))
        self.assertTrue(validate_chromosome_for_build("chrM", "GRCh38"))
        self.assertFalse(validate_chromosome_for_build("1", "GRCh38"))
        self.assertFalse(validate_chromosome_for_build("X", "GRCh38"))
        self.assertFalse(validate_chromosome_for_build("MT", "GRCh38"))

    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        # Invalid genome build
        with self.assertRaises(ValueError):
            normalize_chromosome_for_build("1", "InvalidBuild")

        with self.assertRaises(ValueError):
            validate_chromosome_for_build("1", "InvalidBuild")

        # Invalid chromosome
        with self.assertRaises(ValueError):
            normalize_chromosome_for_build("25", "GRCh37")

        with self.assertRaises(ValueError):
            normalize_chromosome_for_build("Z", "GRCh38")

    def test_edge_cases(self):
        """Test edge cases and unusual inputs."""
        # Multiple chr prefixes should be handled
        self.assertEqual(normalize_chromosome_for_build("chrchr1", "GRCh37"), "1")

        # Case sensitivity shouldn't matter for basic chromosomes
        # Note: The current implementation doesn't handle case, but we document expected behavior
        with self.assertRaises(ValueError):
            normalize_chromosome_for_build("x", "GRCh37")  # lowercase should fail


if __name__ == "__main__":
    unittest.main()
