"""Tests for the factory_defaults module.

Note that we use snapshot tests here to ensure that that the UUID and dates
from the factory defaults remain constant.
"""

from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from seqvars.factory_defaults import (
    create_seqvarspresetsset_short_read_exome_legacy,
    create_seqvarspresetsset_short_read_exome_modern,
    create_seqvarspresetsset_short_read_genome,
    store_factory_defaults,
)
from seqvars.models.base import (
    SeqvarsPredefinedQuery,
    SeqvarsQueryPresetsFrequency,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
)
from seqvars.serializers import SeqvarsQueryPresetsSetDetailsSerializer


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
        presetsset = create_seqvarspresetsset_short_read_exome_legacy()
        result = SeqvarsQueryPresetsSetDetailsSerializer(presetsset).data
        self.assertMatchSnapshot(canonicalize_dicts(result))

    def test_create_presetsset_short_read_exome_modern(self):
        presetsset = create_seqvarspresetsset_short_read_exome_modern()
        result = SeqvarsQueryPresetsSetDetailsSerializer(presetsset).data
        self.assertMatchSnapshot(canonicalize_dicts(result))

    def test_create_presetsset_short_read_genome(self):
        presetsset = create_seqvarspresetsset_short_read_genome()
        result = SeqvarsQueryPresetsSetDetailsSerializer(presetsset).data
        self.assertMatchSnapshot(canonicalize_dicts(result))


class StoreFactoryDefaultsTest(TestCase):
    def test_run_once(self):
        self.assertEqual(
            SeqvarsQueryPresetsSet.objects.count(),
            0,
        )
        self.assertEqual(
            SeqvarsQueryPresetsSetVersion.objects.count(),
            0,
        )
        self.assertEqual(
            SeqvarsPredefinedQuery.objects.count(),
            0,
        )
        self.assertEqual(
            SeqvarsQueryPresetsFrequency.objects.count(),
            0,
        )

        store_factory_defaults()

        self.assertEqual(
            SeqvarsQueryPresetsSet.objects.count(),
            3,
        )
        self.assertEqual(
            SeqvarsQueryPresetsSetVersion.objects.count(),
            3,
        )
        self.assertEqual(
            SeqvarsPredefinedQuery.objects.count(),
            30,
        )
        self.assertEqual(
            SeqvarsQueryPresetsFrequency.objects.count(),
            18,
        )

    def test_run_twice(self):
        store_factory_defaults()
        store_factory_defaults()

        self.assertEqual(
            SeqvarsQueryPresetsSet.objects.count(),
            3,
        )
        self.assertEqual(
            SeqvarsQueryPresetsSetVersion.objects.count(),
            3,
        )
        self.assertEqual(
            SeqvarsPredefinedQuery.objects.count(),
            30,
        )
        self.assertEqual(
            SeqvarsQueryPresetsFrequency.objects.count(),
            18,
        )
