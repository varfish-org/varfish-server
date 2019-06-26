"""Tests for ``variants.models``."""
import binning

from .helpers import TestBase
from ._fixtures import fixture_setup_case1_simple

from ..models import Case, SmallVariantFlags


class TestSmallVariantFlags(TestBase):
    """Basic tests for the ``SmallVariantFlags`` class."""

    #: We use the simple common Case #1.
    setup_case_in_db = fixture_setup_case1_simple

    #: Cleaned data that we will use for setting up the ``SmallVariantFlags`` instances.
    base_cleaned_data = {
        # Coordinates
        "release": "GRCh37",
        "chromosome": "1",
        "start": 100,
        "end": 100,
        "bin": binning.assign_bin(99, 100),
        "reference": "A",
        "alternative": "G",
        # Related case
        "case_id": None,
        # Flags
        "flag_bookmarked": True,
        "flag_candidate": True,
        "flag_final_causative": True,
        "flag_for_validation": True,
        "flag_visual": "empty",
        "flag_validation": "empty",
        "flag_phenotype_match": "empty",
    }

    def testCreate(self):
        data = {**self.base_cleaned_data, "case_id": Case.objects.first().pk}
        self.assertEquals(SmallVariantFlags.objects.count(), 0)
        SmallVariantFlags.objects.create(**data)
        self.assertEquals(SmallVariantFlags.objects.count(), 1)
