"""Tests for the JSON schemas"""

import json

import jsonschema
from jsonschema.exceptions import ValidationError
from test_plus.test import TestCase

from variants.query_schemas import (
    SCHEMA_QUERY,
    DefaultValidatingDraft7Validator,
    FormToQueryJsonConverter,
    convert_query_json_to_small_variant_filter_form,
    load_json,
)

from .data.query_settings import QUERY_SETTINGS, QUERY_SETTINGS_CONVERTED
from .factories import CaseFactory


class TestQuerySchema(TestCase):
    """Tests for the query schema file"""

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValidationFailure(self):
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            obj = {}
            jsonschema.Draft7Validator(SCHEMA_QUERY).validate(obj)

    def testValidateSimpleV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-01-minimal.json")
        jsonschema.Draft7Validator(SCHEMA_QUERY).validate(obj)

    def testValidateSingletonV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-02-singleton.json")
        jsonschema.Draft7Validator(SCHEMA_QUERY).validate(obj)

    def testDefaultSimpleV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-01-minimal.json")
        DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(obj)
        expected = load_json(
            "variants/schemas/examples/case-query-v1-01-minimal-with-defaults.json"
        )
        self.assertEqual(obj, expected)

    def testDefaultSingletonV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-02-singleton.json")
        DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(obj)
        with open("/tmp/b.txt", "wt") as outputf:
            json.dump(obj, outputf, indent="  ")
        expected = load_json(
            "variants/schemas/examples/case-query-v1-02-singleton-with-defaults.json"
        )
        self.assertEqual(obj, expected)

    def testWithMaxExonDist25(self):
        """Test with ``max_exon_dist`` set to 25."""
        obj = load_json("variants/schemas/examples/case-query-v1-01-minimal.json")
        obj["max_exon_dist"] = 25
        DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(obj)
        expected = load_json(
            "variants/schemas/examples/case-query-v1-01-minimal-with-defaults.json"
        )
        expected["max_exon_dist"] = 25
        self.assertEqual(obj, expected)

    def testWithMaxExonDist25Str(self):
        """Test with ``max_exon_dist`` set to str '25'."""
        obj = load_json("variants/schemas/examples/case-query-v1-01-minimal.json")
        obj["max_exon_dist"] = "25"
        with self.assertRaises(ValidationError):
            DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(obj)

    def test_conversion_json_to_filter_form(self):
        """Test conversion from query settings to small variant filter form"""
        self.maxDiff = None
        case = CaseFactory(name="Case_1", index="Case_1_index-N1-DNA1-WGS1")
        result, version = convert_query_json_to_small_variant_filter_form(case, QUERY_SETTINGS)
        self.assertEqual(result, QUERY_SETTINGS_CONVERTED)
        self.assertEqual(version.major, 0)
        self.assertEqual(version.minor, 0)

    def test_form_to_query_json_converter(self):
        """Test conversion from query settings to small variant filter form"""
        result = FormToQueryJsonConverter().convert(QUERY_SETTINGS_CONVERTED)
        self.assertEqual(result, QUERY_SETTINGS)
