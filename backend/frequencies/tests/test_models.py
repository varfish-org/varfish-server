"""Tests for Model queries to the ``frequencies`` models."""

from variants.tests.helpers import QueryTestBase

from ..models import Exac, GnomadExomes, GnomadGenomes, ThousandGenomes
from .factories import (
    ExacFactory,
    GnomadExomesFactory,
    GnomadGenomesFactory,
    ThousandGenomesFactory,
)

#: Symbol of gene to query the variants for.
SYMBOL = "LAMA1"


class TestFrequencyQuery(QueryTestBase):
    def create(self, factory_cls):
        obj = factory_cls.create()
        query = {
            "release": obj.release,
            "chromosome": obj.chromosome,
            "start": obj.start,
            "end": obj.end,
            "bin": obj.bin,
            "reference": obj.reference,
            "alternative": obj.alternative,
        }
        return obj, query

    def test_frequency_exac(self):
        created, query = self.create(ExacFactory)
        obj = self.run_get_query(Exac, query)
        self.assertEquals(obj.start, created.start)

    def test_frequency_exac_fail(self):
        created, query = self.create(ExacFactory)
        self.run_get_query(
            Exac,
            {**query, **{"start": created.start + 1, "end": created.end + 1}},
            Exac.DoesNotExist,
        )

    def test_frequency_thousand_genomes(self):
        created, query = self.create(ThousandGenomesFactory)
        obj = self.run_get_query(ThousandGenomes, query)
        self.assertEquals(obj.start, created.start)

    def test_frequency_thousand_genomes_fail(self):
        created, query = self.create(ThousandGenomesFactory)
        self.run_get_query(
            ThousandGenomes,
            {**query, **{"start": created.start + 1, "end": created.end + 1}},
            ThousandGenomes.DoesNotExist,
        )

    def test_frequency_gnomad_exomes(self):
        created, query = self.create(GnomadExomesFactory)
        obj = self.run_get_query(GnomadExomes, query)
        self.assertEquals(obj.start, created.start)

    def test_frequency_gnomad_exomes_fail(self):
        created, query = self.create(GnomadExomesFactory)
        self.run_get_query(
            GnomadExomes,
            {**query, **{"start": created.start + 1, "end": created.end + 1}},
            GnomadExomes.DoesNotExist,
        )

    def test_frequency_gnomad_genomes(self):
        created, query = self.create(GnomadGenomesFactory)
        obj = self.run_get_query(GnomadGenomes, query)
        self.assertEquals(obj.start, created.start)

    def test_frequency_gnomad_genomes_fail(self):
        created, query = self.create(GnomadGenomesFactory)
        self.run_get_query(
            GnomadGenomes,
            {**query, **{"start": created.start + 1, "end": created.end + 1}},
            GnomadGenomes.DoesNotExist,
        )
