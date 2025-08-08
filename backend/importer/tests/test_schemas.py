"""Tests for the JSON schemas"""

import jsonschema
from test_plus.test import TestCase

from importer.qc_schemas import SCHEMA_QC_V1, load_json


class TestQuerySchema(TestCase):
    """Smoke test for the case QC JSON schema."""

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValidationTrioV1(self):
        obj = load_json("importer/schemas/examples/trio.json")
        jsonschema.Draft7Validator(SCHEMA_QC_V1).validate(obj)
