"""Tests for ``varannos.queries``.

We use white-box testing with mocks for now as we do not have the test harness infrastructure in place to test
separate ``ExtendQueryPartsBase`` subclasses yet.
"""

from unittest.mock import MagicMock

from sqlalchemy import true
from test_plus import TestCase

from varannos.queries import ExtendQueryPartsVarAnnosJoin
from variants.tests.factories import CaseFactory


class TestExtendQueryPartsVarAnnosJoin(TestCase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()
        self.kwargs = {}
        self.maxDiff = None

    def test_construction(self):
        obj = ExtendQueryPartsVarAnnosJoin(self.kwargs, self.case)
        expected = (
            """LATERAL (SELECT DISTINCT count(*) AS varannos_varannosetentry_count_inner\n"""
            """FROM variants_smallvariant, varannos_varannosetentry\n"""
            """WHERE variants_smallvariant.release = varannos_varannosetentry.release AND """
            """variants_smallvariant.chromosome = varannos_varannosetentry.chromosome AND """
            """variants_smallvariant.start = varannos_varannosetentry.start AND """
            """variants_smallvariant."end" = varannos_varannosetentry."end" AND """
            """variants_smallvariant.reference = varannos_varannosetentry.reference AND """
            """variants_smallvariant.alternative = varannos_varannosetentry.alternative)"""
        )
        result = "\n".join(line.strip() for line in str(obj.subquery).splitlines())
        self.assertEqual(result, expected)

    def test_extend_selectable(self):
        obj = ExtendQueryPartsVarAnnosJoin(self.kwargs, self.case)
        query_parts = MagicMock()
        result = obj.extend_selectable(query_parts)
        query_parts.selectable.outerjoin.assert_called_with(obj.subquery, true())
        self.assertTrue("name='mock.selectable.outerjoin()'" in str(result))

    def test_extend_fields(self):
        obj = ExtendQueryPartsVarAnnosJoin(self.kwargs, self.case)
        result = obj.extend_fields(None)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            str(result[0]),
            "coalesce(varannos_subquery.varannos_varannosetentry_count_inner, :coalesce_1)",
        )
