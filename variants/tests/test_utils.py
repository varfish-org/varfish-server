"""Tests for ``variants.utils``."""

from test_plus.test import TestCase

from svs.models import SvQueryResultSet
from svs.tests.factories import (
    StructuralVariantCommentFactory,
    StructuralVariantFlagsFactory,
    SvQueryFactory,
    SvQueryResultRowFactory,
    SvQueryResultSetFactory,
)
from variants.models import SmallVariantQueryResultSet
from variants.tests.factories import (
    AcmgCriteriaRatingFactory,
    CaseFactory,
    ProjectFactory,
    SmallVariantCommentFactory,
    SmallVariantFlagsFactory,
    SmallVariantQueryFactory,
    SmallVariantQueryResultRowFactory,
    SmallVariantQueryResultSetFactory,
)
from variants.utils import create_queryresultset, fill_queryresultset


class TestCreateQueryResultSet(TestCase):
    """Basic tests for the ``SmallVariantFlags`` class."""

    def setUp(self):
        super().setUp()
        self.project1 = ProjectFactory()
        self.project1_case1 = CaseFactory(project=self.project1)
        self.project1_case2 = CaseFactory(project=self.project1)
        self.project2 = ProjectFactory()
        self.project2_case1 = CaseFactory(project=self.project2)

    def test_no_resultset_to_create(self):
        # Prepare
        svqueryresultset11 = SvQueryResultSetFactory(case=self.project1_case1, svquery=None)
        svqueryresultset12 = SvQueryResultSetFactory(case=self.project1_case2, svquery=None)
        svqueryresultset21 = SvQueryResultSetFactory(case=self.project2_case1, svquery=None)
        smallvariantqueryresultset11 = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=None
        )
        smallvariantqueryresultset12 = SmallVariantQueryResultSetFactory(
            case=self.project1_case2, smallvariantquery=None
        )
        smallvariantqueryresultset21 = SmallVariantQueryResultSetFactory(
            case=self.project2_case1, smallvariantquery=None
        )

        # Run
        count, fill_count = create_queryresultset(all=True)

        # Set expectations
        expected_count = {
            "svqueryresultset": 0,
            "smallvariantqueryresultset": 0,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(), smallvariantqueryresultset11
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.first(), smallvariantqueryresultset12
        )
        self.assertEqual(
            self.project2_case1.smallvariantqueryresultset_set.first(), smallvariantqueryresultset21
        )
        self.assertEqual(self.project1_case1.svqueryresultset_set.first(), svqueryresultset11)
        self.assertEqual(self.project1_case2.svqueryresultset_set.first(), svqueryresultset12)
        self.assertEqual(self.project2_case1.svqueryresultset_set.first(), svqueryresultset21)

    def test_create_result_sets_for_case(self):
        # Run
        count, fill_count = create_queryresultset(case_uuid=self.project1_case1.sodar_uuid)

        # Set expectations
        expected_count = {
            "svqueryresultset": 1,
            "smallvariantqueryresultset": 1,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(self.project1_case2.smallvariantqueryresultset_set.exists())
        self.assertFalse(self.project2_case1.smallvariantqueryresultset_set.exists())
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(self.project1_case2.svqueryresultset_set.exists())
        self.assertFalse(self.project2_case1.svqueryresultset_set.exists())

    def test_create_small_variant_result_sets_for_case(self):
        # Prepare
        svqueryresultset11 = SvQueryResultSetFactory(case=self.project1_case1, svquery=None)

        # Run
        count, fill_count = create_queryresultset(case_uuid=self.project1_case1.sodar_uuid)

        # Set expectations
        expected_count = {
            "svqueryresultset": 0,
            "smallvariantqueryresultset": 1,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(self.project1_case2.smallvariantqueryresultset_set.exists())
        self.assertFalse(self.project2_case1.smallvariantqueryresultset_set.exists())
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.first(),
            svqueryresultset11,
        )
        self.assertFalse(self.project1_case2.svqueryresultset_set.exists())
        self.assertFalse(self.project2_case1.svqueryresultset_set.exists())

    def test_create_structural_variant_result_sets_for_case(self):
        # Prepare
        smallvariantqueryresultset11 = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=None
        )

        # Run
        count, fill_count = create_queryresultset(case_uuid=self.project1_case1.sodar_uuid)

        # Set expectations
        expected_count = {
            "svqueryresultset": 1,
            "smallvariantqueryresultset": 0,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(),
            smallvariantqueryresultset11,
        )
        self.assertFalse(self.project1_case2.smallvariantqueryresultset_set.exists())
        self.assertFalse(self.project2_case1.smallvariantqueryresultset_set.exists())
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(self.project1_case2.svqueryresultset_set.exists())
        self.assertFalse(self.project2_case1.svqueryresultset_set.exists())

    def test_create_result_sets_for_project(self):
        # Run
        count, fill_count = create_queryresultset(project_uuid=self.project1.sodar_uuid)

        # Set expectations
        expected_count = {
            "svqueryresultset": 2,
            "smallvariantqueryresultset": 2,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(self.project2_case1.smallvariantqueryresultset_set.exists())
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(self.project2_case1.svqueryresultset_set.exists())

    def test_create_result_sets_for_project_partly(self):
        # Prepare
        svqueryresultset11 = SvQueryResultSetFactory(case=self.project1_case1, svquery=None)
        smallvariantqueryresultset11 = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=None
        )

        # Run
        count, fill_count = create_queryresultset(project_uuid=self.project1.sodar_uuid)

        # Set expectations
        expected_count = {
            "svqueryresultset": 1,
            "smallvariantqueryresultset": 1,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(),
            smallvariantqueryresultset11,
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(self.project2_case1.smallvariantqueryresultset_set.exists())
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.first(),
            svqueryresultset11,
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(self.project2_case1.svqueryresultset_set.exists())

    def test_create_result_sets_for_all(self):
        # Run
        count, fill_count = create_queryresultset(all=True)

        # Set expectations
        expected_count = {
            "svqueryresultset": 3,
            "smallvariantqueryresultset": 3,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertEqual(
            self.project2_case1.smallvariantqueryresultset_set.first(),
            SmallVariantQueryResultSet.objects.get(case=self.project2_case1),
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertEqual(
            self.project2_case1.svqueryresultset_set.first(),
            SvQueryResultSet.objects.get(case=self.project2_case1),
        )

    def test_create_sets_with_annotations_simple(self):
        # Prepare
        query = SmallVariantQueryFactory(case=self.project1_case1)
        result_set = SmallVariantQueryResultSetFactory(case=None, smallvariantquery=query)
        flag = SmallVariantFlagsFactory(case=self.project1_case1)
        row = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            reference=flag.reference,
            alternative=flag.alternative,
        )

        # Run
        count, fill_count = create_queryresultset(all=True)

        # Set expectations
        expected_count = {
            "svqueryresultset": 3,
            "smallvariantqueryresultset": 3,
        }
        expected_fill_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 1,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(fill_count, expected_fill_count)
        self.assertNotEqual(
            self.project1_case1.smallvariantqueryresultset_set.first().smallvariantqueryresultrow_set.first(),
            row,
        )
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.first()
            .smallvariantqueryresultrow_set.first()
            .payload,
            row.payload,
        )


class TestFillQueryResultSet(TestCase):
    def setUp(self):
        super().setUp()
        self.case1 = CaseFactory()
        self.case2 = CaseFactory(project=self.case1.project)
        self.case3 = CaseFactory()

    def test_nothing_to_fill(self):
        # Prepare
        SmallVariantQueryFactory(case=self.case1)
        result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            reference=flag.reference,
            alternative=flag.alternative,
        )

        # Run
        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)

    def test_structural_variants_comments_flags(self):
        # Prepare
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=None, svquery=query)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag1 = StructuralVariantFlagsFactory(case=self.case1)
        flag2 = StructuralVariantFlagsFactory(case=self.case1)
        comment = StructuralVariantCommentFactory(
            case=self.case1,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            sv_type=flag1.sv_type,
            sv_sub_type=flag1.sv_sub_type,
        )
        row1 = SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            sv_type=flag1.sv_type,
            sv_sub_type=flag1.sv_sub_type,
        )
        row2 = SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            sv_type=flag2.sv_type,
            sv_sub_type=flag2.sv_sub_type,
        )

        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)
        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 2,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 2)
        self.assertNotEqual(case_result_set.svqueryresultrow_set.all()[0], row1)
        self.assertEqual(case_result_set.svqueryresultrow_set.all()[0].payload, row1.payload)
        self.assertNotEqual(case_result_set.svqueryresultrow_set.all()[1], row2)
        self.assertEqual(case_result_set.svqueryresultrow_set.all()[1].payload, row2.payload)

    def test_structural_variants_orphaned_no_query(self):
        # Prepare
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 1,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_structural_variants_orphaned_no_row(self):
        # Prepare
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=None, svquery=query)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 1,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_structural_variants_no_query_result_set(self):
        # Prepare
        query = SvQueryFactory(case=self.case1)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 1,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_structural_variants_no_case_result_set(self):
        # Prepare
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=None, svquery=query)
        flag = StructuralVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Refresh
        self.case1.refresh_from_db()

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 1,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(self.case1.svqueryresultset_set.count(), 0)

    def test_small_variants_comment_flag_acmg(self):
        # Prepare
        query = SmallVariantQueryFactory(case=self.case1)
        query_result_set = SmallVariantQueryResultSetFactory(case=None, smallvariantquery=query)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag1 = SmallVariantFlagsFactory(case=self.case1)
        flag2 = SmallVariantFlagsFactory(case=self.case1)
        comment = SmallVariantCommentFactory(
            case=self.case1,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        acmg = AcmgCriteriaRatingFactory(
            case=self.case1,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        row1 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        row2 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            reference=flag2.reference,
            alternative=flag2.alternative,
        )

        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)
        count = fill_queryresultset(self.case1)

        # Refresh
        case_result_set.refresh_from_db()

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 2,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 2)
        self.assertNotEqual(case_result_set.smallvariantqueryresultrow_set.all()[0], row1)
        self.assertEqual(
            case_result_set.smallvariantqueryresultrow_set.all()[0].payload, row1.payload
        )
        self.assertNotEqual(case_result_set.smallvariantqueryresultrow_set.all()[1], row2)
        self.assertEqual(
            case_result_set.smallvariantqueryresultrow_set.all()[1].payload, row2.payload
        )

    def test_small_variants_orphaned_no_query(self):
        # Prepare
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 1,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_small_variants_orphaned_no_row(self):
        # Prepare
        query = SmallVariantQueryFactory(case=self.case1)
        query_result_set = SmallVariantQueryResultSetFactory(case=None, smallvariantquery=query)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 1,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_small_variants_no_query_result_set(self):
        # Prepare
        query = SmallVariantQueryFactory(case=self.case1)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 1,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_small_variants_no_case_result_set(self):
        # Prepare
        query = SmallVariantQueryFactory(case=self.case1)
        query_result_set = SmallVariantQueryResultSetFactory(case=None, smallvariantquery=query)
        flag = SmallVariantFlagsFactory(case=self.case1)

        count = fill_queryresultset(self.case1)

        # Refresh
        self.case1.refresh_from_db()

        # Set expectations
        expected_count = {
            "structural_variants": 0,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 0,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 1,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(self.case1.smallvariantqueryresultset_set.count(), 0)

    def test_small_and_structural_result_set(self):
        # Prepare
        sv_query = SvQueryFactory(case=self.case1)
        sv_query_result_set = SvQueryResultSetFactory(case=None, svquery=sv_query)
        sv_case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        sv_flag1 = StructuralVariantFlagsFactory(case=self.case1)
        sv_flag2 = StructuralVariantFlagsFactory(case=self.case1)
        sv_comment = StructuralVariantCommentFactory(
            case=self.case1,
            release=sv_flag1.release,
            chromosome=sv_flag1.chromosome,
            start=sv_flag1.start,
            end=sv_flag1.end,
            sv_type=sv_flag1.sv_type,
            sv_sub_type=sv_flag1.sv_sub_type,
        )
        sv_row1 = SvQueryResultRowFactory(
            svqueryresultset=sv_query_result_set,
            release=sv_flag1.release,
            chromosome=sv_flag1.chromosome,
            start=sv_flag1.start,
            end=sv_flag1.end,
            sv_type=sv_flag1.sv_type,
            sv_sub_type=sv_flag1.sv_sub_type,
        )
        sv_row2 = SvQueryResultRowFactory(
            svqueryresultset=sv_query_result_set,
            release=sv_flag2.release,
            chromosome=sv_flag2.chromosome,
            start=sv_flag2.start,
            end=sv_flag2.end,
            sv_type=sv_flag2.sv_type,
            sv_sub_type=sv_flag2.sv_sub_type,
        )
        variant_query = SmallVariantQueryFactory(case=self.case1)
        variant_query_result_set = SmallVariantQueryResultSetFactory(
            case=None, smallvariantquery=variant_query
        )
        variant_case_result_set = SmallVariantQueryResultSetFactory(
            case=self.case1, smallvariantquery=None
        )
        variant_flag1 = SmallVariantFlagsFactory(case=self.case1)
        variant_flag2 = SmallVariantFlagsFactory(case=self.case1)
        variant_comment = SmallVariantCommentFactory(
            case=self.case1,
            release=variant_flag1.release,
            chromosome=variant_flag1.chromosome,
            start=variant_flag1.start,
            end=variant_flag1.end,
            reference=variant_flag1.reference,
            alternative=variant_flag1.alternative,
        )
        variant_acmg = AcmgCriteriaRatingFactory(
            case=self.case1,
            release=variant_flag1.release,
            chromosome=variant_flag1.chromosome,
            start=variant_flag1.start,
            end=variant_flag1.end,
            reference=variant_flag1.reference,
            alternative=variant_flag1.alternative,
        )
        variant_row1 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=variant_query_result_set,
            release=variant_flag1.release,
            chromosome=variant_flag1.chromosome,
            start=variant_flag1.start,
            end=variant_flag1.end,
            reference=variant_flag1.reference,
            alternative=variant_flag1.alternative,
        )
        variant_row2 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=variant_query_result_set,
            release=variant_flag2.release,
            chromosome=variant_flag2.chromosome,
            start=variant_flag2.start,
            end=variant_flag2.end,
            reference=variant_flag2.reference,
            alternative=variant_flag2.alternative,
        )

        self.assertEqual(sv_case_result_set.svqueryresultrow_set.count(), 0)
        self.assertEqual(variant_case_result_set.smallvariantqueryresultrow_set.count(), 0)
        count = fill_queryresultset(self.case1)

        # Refresh
        sv_case_result_set.refresh_from_db()
        variant_case_result_set.refresh_from_db()

        # Set expectations
        expected_count = {
            "structural_variants": 2,
            "structural_variants_orphaned": 0,
            "structural_variants_no_query_result_set": 0,
            "structural_variants_no_case_result_set": 0,
            "small_variants": 2,
            "small_variants_orphaned": 0,
            "small_variants_no_query_result_set": 0,
            "small_variants_no_case_result_set": 0,
        }
        self.assertEqual(count, expected_count)
        self.assertEqual(sv_case_result_set.svqueryresultrow_set.count(), 2)
        self.assertNotEqual(sv_case_result_set.svqueryresultrow_set.all()[0], sv_row1)
        self.assertEqual(sv_case_result_set.svqueryresultrow_set.all()[0].payload, sv_row1.payload)
        self.assertNotEqual(sv_case_result_set.svqueryresultrow_set.all()[1], sv_row2)
        self.assertEqual(sv_case_result_set.svqueryresultrow_set.all()[1].payload, sv_row2.payload)
        self.assertEqual(variant_case_result_set.smallvariantqueryresultrow_set.count(), 2)
        self.assertNotEqual(
            variant_case_result_set.smallvariantqueryresultrow_set.all()[0], variant_row1
        )
        self.assertEqual(
            variant_case_result_set.smallvariantqueryresultrow_set.all()[0].payload,
            variant_row1.payload,
        )
        self.assertNotEqual(
            variant_case_result_set.smallvariantqueryresultrow_set.all()[1], variant_row2
        )
        self.assertEqual(
            variant_case_result_set.smallvariantqueryresultrow_set.all()[1].payload,
            variant_row2.payload,
        )
