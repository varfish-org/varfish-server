"""Tests for the JSON schemas"""

import json

import jsonschema
from jsonschema.exceptions import ValidationError
from test_plus.test import TestCase

from variants.forms import FilterForm
from variants.query_schemas import (
    SCHEMA_QUERY_V1,
    DefaultValidatingDraft7Validator,
    convert_query_json_to_small_variant_filter_form_v1,
    load_json,
)
from variants.tests.factories import CaseWithVariantSetFactory


class TestQuerySchema(TestCase):
    """Tests for the query schema file"""

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValidationFailure(self):
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            obj = {}
            jsonschema.Draft7Validator(SCHEMA_QUERY_V1).validate(obj)

    def testValidateSimpleV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-01-minimal.json")
        jsonschema.Draft7Validator(SCHEMA_QUERY_V1).validate(obj)

    def testValidateSingletonV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-02-singleton.json")
        jsonschema.Draft7Validator(SCHEMA_QUERY_V1).validate(obj)

    def testDefaultSimpleV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-01-minimal.json")
        DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(obj)
        expected = load_json(
            "variants/schemas/examples/case-query-v1-01-minimal-with-defaults.json"
        )
        self.assertEqual(obj, expected)

    def testDefaultSingletonV1(self):
        obj = load_json("variants/schemas/examples/case-query-v1-02-singleton.json")
        DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(obj)
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
        DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(obj)
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
            DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(obj)


class TestQuerySchemaConversion(TestCase):
    """Test conversion from query schema to form data"""

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testConversionOfSimpleV1(self):
        case, _, _ = CaseWithVariantSetFactory.get("small")

        json_data = {
            "effects": ["missense_variant"],
            "quality": {case.index: {"dp_het": 10, "dp_hom": 5, "ab": 0.3, "gq": 20, "ad": 3}},
            "genotype": {case.index: "variant"},
        }
        DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(json_data)

        form_data = convert_query_json_to_small_variant_filter_form_v1(case, json_data)
        form = FilterForm(form_data, case=case, user=0)
        is_valid = form.is_valid()
        self.assertTrue(is_valid, form.errors)
