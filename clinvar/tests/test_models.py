"""Tests for Modle queries to the ``clinvar`` models."""

from variants.tests.helpers import QueryTestBase

from ..models import Clinvar
from .factories import ClinvarFactory


class ClinvarQuery(QueryTestBase):
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

    def test_clinvar_query(self):
        created, query = self.create(ClinvarFactory)
        obj = self.run_get_query(Clinvar, query)
        self.assertEquals(obj.position, created.position)

    def test_clinvar_query_fail(self):
        created, query = self.create(ClinvarFactory)
        self.run_get_query(
            Clinvar, {**query, **{"position": created.position + 1}}, Clinvar.DoesNotExist
        )
