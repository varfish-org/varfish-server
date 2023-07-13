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
    FileValidator,
    MetaDataValidator,
    PedigreeValidator,
    PhenopacketValidator,
    ProbandValidator,
    RelativeValidator,
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
            ["phenopacketSchemaVersion", None],
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

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            PhenopacketValidator(
                family.proband, sample_names={"index", "mother", "father"}
            ).validate(),
            [],
        )

    @parameterized.expand(
        [
            ["id", "InVaLiD"],
            ["subject", {"id": "InVaLiD", "sex": "MALE", "karyotypicSex": "XY"}],
            ["measurements", [[], []]],
            ["measurements", [{"assay": {"id": "InVaLiD"}}]],
            ["files", []],
            [
                "files",
                [
                    {
                        "uri": "s3://whatever",
                        "individualToFileIdentifiers": {"index": "index"},
                        "fileAttributes": {
                            "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                            "designation": "read_alignments",
                            "genome_assembly": "GRCh38",
                            "file_format": "text/x-bed+x-bgzip",
                        },
                    }
                ],
            ],
        ]
    )
    def test_validate_knockout(self, key, value):
        """Test validation fails due to inconsistent family name."""
        self.fam_dict["family"]["proband"][key] = value
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            len(
                PhenopacketValidator(
                    family.proband, sample_names={"index", "mother", "father"}
                ).validate()
            ),
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
            ProbandValidator(family.proband, sample_names={"index", "mother", "father"}).validate(),
            [],
        )


class RelativeValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            RelativeValidator(
                family.proband, sample_names={"index", "mother", "father"}
            ).validate(),
            [],
        )


class PedigreeValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            PedigreeValidator(
                family.pedigree, sample_names={"index", "mother", "father"}
            ).validate(),
            [],
        )

    def test_validate_inconsistent_family_name(self):
        """Test validation fails due to inconsistent family name."""
        self.fam_dict["family"]["pedigree"]["persons"][0]["familyId"] = "InVaLiD"
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            len(
                PedigreeValidator(
                    family.pedigree, sample_names={"index", "mother", "father"}
                ).validate()
            ),
            1,
        )

    @parameterized.expand(
        [
            ["paternalId", "InVaLiD"],
            ["maternalId", "InVaLiD"],
        ]
    )
    def test_validate_inconsistent_parent_name(self, key, value):
        """Test validation fails due to inconsistent family name."""
        self.fam_dict["family"]["pedigree"]["persons"][0][key] = value
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            len(
                PedigreeValidator(
                    family.pedigree, sample_names={"index", "mother", "father"}
                ).validate()
            ),
            1,
        )

    @parameterized.expand(
        [
            ["father", "FEMALE"],
            ["mother", "MALE"],
        ]
    )
    def test_validate_inconsistent_parent_sexes(self, name, value):
        """Test validation fails due to inconsistent sex of parents."""
        for person in self.fam_dict["family"]["pedigree"]["persons"]:
            if person["individualId"] == name:
                person["sex"] = value
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            len(
                PedigreeValidator(
                    family.pedigree, sample_names={"index", "mother", "father"}
                ).validate()
            ),
            1,
        )


class FileValidatorTest(TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_validate_ok(self):
        """Test validation succeeds."""
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        self.assertEqual(
            FileValidator(
                family.proband.files[0], sample_names=["index", "mother", "father"]
            ).validate(),
            [],
        )

    @parameterized.expand(
        [
            ["uri", None],
            ["individualToFileIdentifiers", {"unknown": "unknown"}],
            ["fileAttributes", {"designation": "sequencing_targets"}],
            ["fileAttributes", {"checksum": "sha256:"}],
            ["fileAttributes", {"checksum": "foo", "designation": "sequencing_targets"}],
            ["fileAttributes", {"checksum": "sha256:", "designation": "unknown"}],
        ]
    )
    def test_validate_fails_knockout(self, key, value):
        """Test that validation fails by knocking out elements."""
        js_dict = copy.deepcopy(self.fam_dict["family"])
        if value is None:
            js_dict["proband"]["files"][0].pop(key)
        else:
            js_dict["proband"]["files"][0][key] = value
        family: Family = ParseDict(js_dict=js_dict, message=Family())
        res = FileValidator(
            family.proband.files[0], sample_names=["index", "mother", "father"]
        ).validate()
        self.assertEqual(
            len(res),
            1,
            f"{key}={value}",
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
