"""Tests for Model queries to the ``frequencies`` models."""

from variants.tests.helpers import QueryTestBase
from variants.tests.factories_data import SMALL_VARS

from ..models import Exac, ThousandGenomes, GnomadExomes, GnomadGenomes
from .factories import (
    ExacFrequenciesFactory,
    ThousandGenomesFactory,
    GnomadExomesFactory,
    GnomadGenomesFactory,
)

#: Symbol of gene to query the variants for.
SYMBOL = "LAMA1"


class TestFrequencyQuery(QueryTestBase):
    def create(self, factory_cls):
        obj = factory_cls.create()
        query = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "position": obj.position,
            "reference": obj.reference,
            "alternative": obj.alternative,
        }
        return obj, query

    def test_frequency_exac(self):
        created, query = self.create(ExacFrequenciesFactory)
        obj = self.run_get_query(Exac, query)
        self.assertEquals(obj.position, created.position)

    def test_frequency_exac_fail(self):
        created, query = self.create(ExacFrequenciesFactory)
        self.run_get_query(Exac, {**query, **{"position": created.position + 1}}, Exac.DoesNotExist)

    def test_frequency_thousand_genomes(self):
        created, query = self.create(ThousandGenomesFactory)
        obj = self.run_get_query(ThousandGenomes, query)
        self.assertEquals(obj.position, created.position)

    def test_frequency_thousand_genomes_fail(self):
        created, query = self.create(ThousandGenomesFactory)
        self.run_get_query(
            ThousandGenomes,
            {**query, **{"position": created.position + 1}},
            ThousandGenomes.DoesNotExist,
        )

    def test_frequency_gnomad_exomes(self):
        created, query = self.create(GnomadExomesFactory)
        obj = self.run_get_query(GnomadExomes, query)
        self.assertEquals(obj.position, created.position)

    def test_frequency_gnomad_exomes_fail(self):
        created, query = self.create(GnomadExomesFactory)
        self.run_get_query(
            GnomadExomes, {**query, **{"position": created.position + 1}}, GnomadExomes.DoesNotExist
        )

    def test_frequency_gnomad_genomes(self):
        created, query = self.create(GnomadGenomesFactory)
        obj = self.run_get_query(GnomadGenomes, query)
        self.assertEquals(obj.position, created.position)

    def test_frequency_gnomad_genomes_fail(self):
        created, query = self.create(GnomadGenomesFactory)
        self.run_get_query(
            GnomadGenomes,
            {**query, **{"position": created.position + 1}},
            GnomadGenomes.DoesNotExist,
        )
