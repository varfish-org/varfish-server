"""Tests for the factory_defaults module.

Note that we use snapshot tests here to ensure that that the UUID and dates
from the factory defaults remain constant.
"""

from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from seqvars.factory_defaults import (
    create_presetsset_short_read_exome_legacy,
    create_presetsset_short_read_exome_modern,
    create_presetsset_short_read_genome,
)
from seqvars.serializers import QueryPresetsSetDetailsSerializer


def canonicalize_dicts(arg: dict) -> dict:
    """Replace all OrderedDicts in value with dicts."""
    result = {}
    for key, value in arg.items():
        if isinstance(value, dict):
            result[key] = canonicalize_dicts(value)
        elif isinstance(value, list):
            result[key] = [
                canonicalize_dicts(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            result[key] = value
    return result


class CreatePresetsSetTest(TestCaseSnapshot, TestCase):
    def test_create_presetsset_short_read_exome_legacy(self):
        presetsset = create_presetsset_short_read_exome_legacy()
        result = QueryPresetsSetDetailsSerializer(presetsset).data
        self.assertMatchSnapshot(canonicalize_dicts(result))

    def test_create_presetsset_short_read_exome_modern(self):
        presetsset = create_presetsset_short_read_exome_modern()
        result = QueryPresetsSetDetailsSerializer(presetsset).data
        self.assertMatchSnapshot(canonicalize_dicts(result))

    def test_create_presetsset_short_read_genome(self):
        presetsset = create_presetsset_short_read_genome()
        result = QueryPresetsSetDetailsSerializer(presetsset).data
        self.assertMatchSnapshot(canonicalize_dicts(result))
