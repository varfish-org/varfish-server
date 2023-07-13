"""Tests for the ``proto`` module."""

import copy

from google.protobuf.json_format import ParseDict
from parameterized import parameterized
from phenopackets import Family
from test_plus import TestCase
import yaml

from cases_import.proto import (
    Assay,
    FamilyValidator,
    FileDesignation,
    MetaDataValidator,
    ProbandValidator,
)


class AssayTest(TestCase):
    def test_is_value(self):
        self.assertTrue(Assay.is_value("NCIT:C158253"))
        self.assertTrue(Assay.is_value("NCIT:C101295"))
        self.assertTrue(Assay.is_value("NCIT:C101294"))
        self.assertFalse(Assay.is_value("xyz"))

    def test_all_values(self):
        self.assertEqual(
            Assay.all_values(),
            [
                "NCIT:C158253",
                "NCIT:C101295",
                "NCIT:C101294",
            ],
        )

    def test_get_label(self):
        self.assertEqual(
            Assay.PANEL_SEQ.get_label(),
            "Targeted Genome Sequencing",
        )
        self.assertEqual(
            Assay.WES.get_label(),
            "Whole Exome Sequencing",
        )
        self.assertEqual(
            Assay.WGS.get_label(),
            "Whole Genome Sequencing",
        )


class FileDesignationTest(TestCase):
    def test_is_value(self):
        self.assertTrue(FileDesignation.is_value("sequencing_targets"))
        self.assertTrue(FileDesignation.is_value("read_alignments"))
        self.assertTrue(FileDesignation.is_value("variant_calls"))
        self.assertTrue(FileDesignation.is_value("other"))

    def test_all_values(self):
        self.assertEqual(
            FileDesignation.all_values(),
            [
                "sequencing_targets",
                "read_alignments",
                "variant_calls",
                "other",
            ],
        )


class FamilyValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            FamilyValidator(family).validate(),
            [],
        )

    @parameterized.expand(
        [
            ["proband", 5],
            ["pedigree", 4],
            ["metaData", 1],
        ]
    )
    def test_validate_fails(self, key, expected_res_len):
        js_dict = copy.deepcopy(self.fam_dict["family"])
        js_dict.pop(key)
        family: Family = ParseDict(js_dict=js_dict, message=Family())
        res = FamilyValidator(family).validate()
        self.assertEqual(len(res), expected_res_len, res)


class MetaDataValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            MetaDataValidator(family.meta_data).validate(),
            [],
        )

    @parameterized.expand(
        [
            ["created", None],
            ["createdBy", None],
            ["resources", None],
            ["phenopacketSchemaVersion", "1.0"],
            ["phenopacketSchemaVersion", "3.0"],
        ]
    )
    def test_validate_fails_knockout_top(self, key, value):
        """Test that validation fails by knocking out top level elements."""
        js_dict = copy.deepcopy(self.fam_dict["family"])
        if value is None:
            js_dict["metaData"].pop(key)
        else:
            js_dict["metaData"][key] = value
        family: Family = ParseDict(js_dict=js_dict, message=Family())
        res = MetaDataValidator(family.meta_data).validate()
        self.assertEqual(
            len(res),
            1,
        )

    @parameterized.expand(
        [
            ["id"],
            ["name"],
            ["namespacePrefix"],
            ["url"],
            ["version"],
            ["iriPrefix"],
        ]
    )
    def test_validate_fails_knockout_resource_fields(self, key):
        """Test that validation fails by knocking out resource fields."""
        js_dict = copy.deepcopy(self.fam_dict["family"])
        js_dict["metaData"]["resources"][0].pop(key)
        family: Family = ParseDict(js_dict=js_dict, message=Family())
        res = MetaDataValidator(family.meta_data).validate()
        self.assertEqual(
            len(res),
            1,
        )


class PhenopacketValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)


class ProbandValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            ProbandValidator(family.proband, sample_names={"index", "mother", "father"}).validate(),
            [],
        )


class ProbandValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)


class RelativeValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)


class PedigreeValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)


class FileValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)
