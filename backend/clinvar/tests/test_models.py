"""Tests for Modle queries to the ``clinvar`` models."""

import binning

from variants.tests.helpers import QueryTestBase

from ..models import Clinvar
from .factories import ClinvarFactory


class ClinvarQuery(QueryTestBase):
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

    def test_clinvar_query(self):
        created, query = self.create(ClinvarFactory)
        obj = self.run_get_query(Clinvar, query)
        self.assertEquals(obj.start, created.start)

    def test_clinvar_query_fail(self):
        created, query = self.create(ClinvarFactory)
        self.run_get_query(
            Clinvar,
            {
                **query,
                **{
                    "start": created.start + 1,
                    "end": created.end + 1,
                    "bin": binning.assign_bin(created.start, created.end + 1),
                },
            },
            Clinvar.DoesNotExist,
        )
