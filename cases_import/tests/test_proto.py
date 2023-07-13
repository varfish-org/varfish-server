"""Tests for the ``proto`` module."""

import copy

from google.protobuf.json_format import ParseDict
from parameterized import parameterized
from phenopackets import Family
from test_plus import TestCase
import yaml

from cases_import.proto import FamilyValidator, MetaDataValidator, ProbandValidator


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
