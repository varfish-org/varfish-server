"""Tests for the ``proto`` module."""

import copy

from parameterized import parameterized
import yaml
from test_plus import TestCase
from google.protobuf.json_format import ParseDict
from phenopackets import Family

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
            ["proband"],
            # ["relatives"],
            # ['pedigree'],
            # ["files"],
            ["meta_data"],
        ]
    )
    def test_validate_fails(self, key):
        js_dict = copy.deepcopy(self.fam_dict["family"])
        js_dict.pop(key)
        family: Family = ParseDict(js_dict=js_dict, message=Family())
        res = FamilyValidator(family).validate()
        self.assertEqual(
            len(res),
            1,
        )


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


class ProbandValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            ProbandValidator(family.proband).validate(),
            [],
        )
