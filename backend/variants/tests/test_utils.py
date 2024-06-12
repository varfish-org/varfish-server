"""Tests for ``variants.utils``."""

import json

from django.forms import model_to_dict
from test_plus.test import TestCase

from svs.models import (
    StructuralVariant,
    StructuralVariantComment,
    StructuralVariantFlags,
    SvQueryResultRow,
    SvQueryResultSet,
)
from svs.tests.factories import (
    StructuralVariantCommentFactory,
    StructuralVariantFactory,
    StructuralVariantFlagsFactory,
    StructuralVariantSetFactory,
    SvQueryFactory,
    SvQueryResultRowFactory,
    SvQueryResultSetFactory,
)
from variants.models import (
    AcmgCriteriaRating,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQueryResultRow,
    SmallVariantQueryResultSet,
)
from variants.tests.factories import (
    AcmgCriteriaRatingFactory,
    CaseFactory,
    ProjectFactory,
    SmallVariantCommentFactory,
    SmallVariantFactory,
    SmallVariantFlagsFactory,
    SmallVariantQueryFactory,
    SmallVariantQueryResultRowFactory,
    SmallVariantQueryResultSetFactory,
    SmallVariantSetFactory,
)
from variants.utils import (
    clear_sm_queryresultset,
    clear_sv_queryresultset,
    create_queryresultset,
    fill_sm_queryresultset,
    fill_sv_queryresultset,
)
from variants.views import UUIDEncoder


def create_expected_skeleton_sm():
    # Set expectations
    expected_count = {
        "added": 0,
        "removed": 0,
        "salvable": {
            "comments": 0,
            "flags": 0,
            "acmg_ratings": 0,
        },
        "lost": {
            "comments": 0,
            "flags": 0,
            "acmg_ratings": 0,
        },
    }
    expected_salvable = []
    expected_duplicates = []
    expected_orphans = {
        "flags": [],
        "comments": [],
        "acmg_ratings": [],
    }
    return expected_count, expected_salvable, expected_duplicates, expected_orphans


def create_expected_skeleton_sv():
    # Set expectations
    expected_count = {
        "added": 0,
        "removed": 0,
        "salvable": {
            "comments": 0,
            "flags": 0,
        },
        "lost": {
            "comments": 0,
            "flags": 0,
        },
    }
    expected_salvable = []
    expected_duplicates = []
    expected_orphans = {
        "flags": [],
        "comments": [],
    }
    return expected_count, expected_salvable, expected_duplicates, expected_orphans


def create_expected_skeleton(uuids=None):
    # Set expectations
    if uuids is None:
        uuids = []
    (
        expected_count_sm,
        _,
        expected_duplicates_sm,
        expected_orphans_sm,
    ) = create_expected_skeleton_sm()
    (
        expected_count_sv,
        _,
        expected_duplicates_sv,
        expected_orphans_sv,
    ) = create_expected_skeleton_sv()
    expected_count = {
        "svqueryresultset": 0,
        "smallvariantqueryresultset": 0,
        "svs": expected_count_sv,
        "sms": expected_count_sm,
    }
    expected_salvable = {}
    expected_duplicates = {"sms": expected_duplicates_sm, "svs": expected_duplicates_sv}
    expected_orphans = {
        "sms": expected_orphans_sm,
        "svs": expected_orphans_sv,
    }
    return expected_count, expected_salvable, expected_duplicates, expected_orphans


class TestCreateQueryResultSet(TestCase):
    """Basic tests for the ``SmallVariantFlags`` class."""

    def setUp(self):
        super().setUp()
        self.project1 = ProjectFactory()
        self.project2 = ProjectFactory()
        self.project1_case1 = CaseFactory(project=self.project1)
        self.project1_case2 = CaseFactory(project=self.project1)
        self.project2_case1 = CaseFactory(project=self.project2)
        self.project1_smallvariantset1 = SmallVariantSetFactory(case=self.project1_case1)
        self.project1_smallvariantset2 = SmallVariantSetFactory(case=self.project1_case2)
        self.project2_smallvariantset1 = SmallVariantSetFactory(case=self.project2_case1)
        self.project1_structuralvariantset1 = StructuralVariantSetFactory(case=self.project1_case1)
        self.project1_structuralvariantset2 = StructuralVariantSetFactory(case=self.project1_case2)
        self.project2_structuralvariantset1 = StructuralVariantSetFactory(case=self.project2_case1)

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
        count, salvable, duplicates, orphans = create_queryresultset(all=True)

        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
                self.project1_case2.sodar_uuid,
                self.project2_case1.sodar_uuid,
            ]
        )
        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            smallvariantqueryresultset11,
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            smallvariantqueryresultset12,
        )
        self.assertEqual(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            smallvariantqueryresultset21,
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            svqueryresultset11,
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.filter(svquery=None).first(),
            svqueryresultset12,
        )
        self.assertEqual(
            self.project2_case1.svqueryresultset_set.filter(svquery=None).first(),
            svqueryresultset21,
        )

    def test_create_result_sets_for_case(self):
        # Run
        count, salvable, duplicates, orphans = create_queryresultset(
            case_uuid=self.project1_case1.sodar_uuid
        )

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
            ]
        )
        expected_count["smallvariantqueryresultset"] = 1
        expected_count["svqueryresultset"] = 1

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertFalse(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(self.project1_case2.svqueryresultset_set.filter(svquery=None).exists())
        self.assertFalse(self.project2_case1.svqueryresultset_set.filter(svquery=None).exists())

    def test_create_small_variant_result_sets_for_case(self):
        # Prepare
        svqueryresultset11 = SvQueryResultSetFactory(case=self.project1_case1, svquery=None)

        # Run
        count, salvable, duplicates, orphans = create_queryresultset(
            case_uuid=self.project1_case1.sodar_uuid
        )

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
            ]
        )
        expected_count["smallvariantqueryresultset"] = 1

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertFalse(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            svqueryresultset11,
        )
        self.assertFalse(self.project1_case2.svqueryresultset_set.filter(svquery=None).exists())
        self.assertFalse(self.project2_case1.svqueryresultset_set.filter(svquery=None).exists())

    def test_create_structural_variant_result_sets_for_case(self):
        # Prepare
        smallvariantqueryresultset11 = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=None
        )

        # Run
        count, salvable, duplicates, orphans = create_queryresultset(
            case_uuid=self.project1_case1.sodar_uuid
        )

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
            ]
        )
        expected_count["svqueryresultset"] = 1

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            smallvariantqueryresultset11,
        )
        self.assertFalse(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertFalse(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertFalse(self.project1_case2.svqueryresultset_set.filter(svquery=None).exists())
        self.assertFalse(self.project2_case1.svqueryresultset_set.filter(svquery=None).exists())

    def test_create_result_sets_for_project(self):
        # Run
        count, salvable, duplicates, orphans = create_queryresultset(
            project_uuid=self.project1.sodar_uuid
        )

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
                self.project1_case2.sodar_uuid,
            ]
        )
        expected_count["smallvariantqueryresultset"] = 2
        expected_count["svqueryresultset"] = 2

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(self.project2_case1.svqueryresultset_set.filter(svquery=None).exists())

    def test_create_result_sets_for_project_partly(self):
        # Prepare
        svqueryresultset11 = SvQueryResultSetFactory(case=self.project1_case1, svquery=None)
        smallvariantqueryresultset11 = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=None
        )

        # Run
        count, salvable, duplicates, orphans = create_queryresultset(
            project_uuid=self.project1.sodar_uuid
        )

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
                self.project1_case2.sodar_uuid,
            ]
        )
        expected_count["svqueryresultset"] = 1
        expected_count["smallvariantqueryresultset"] = 1

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            smallvariantqueryresultset11,
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).exists()
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            svqueryresultset11,
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertFalse(self.project2_case1.svqueryresultset_set.filter(svquery=None).exists())

    def test_create_result_sets_for_all(self):
        # Run
        count, salvable, duplicates, orphans = create_queryresultset(all=True)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
                self.project1_case2.sodar_uuid,
                self.project2_case1.sodar_uuid,
            ]
        )
        expected_count["smallvariantqueryresultset"] = 3
        expected_count["svqueryresultset"] = 3

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertEqual(
            self.project2_case1.smallvariantqueryresultset_set.filter(
                smallvariantquery=None
            ).first(),
            SmallVariantQueryResultSet.objects.get(case=self.project2_case1),
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case1),
        )
        self.assertEqual(
            self.project1_case2.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project1_case2),
        )
        self.assertEqual(
            self.project2_case1.svqueryresultset_set.filter(svquery=None).first(),
            SvQueryResultSet.objects.get(case=self.project2_case1),
        )

    def test_create_sets_fill_annotations_simple(self):
        # Prepare
        small_vars = SmallVariantFactory.create_batch(
            2,
            case_id=self.project1_case1.id,
            case=self.project1_case1,
            variant_set=self.project1_smallvariantset1,
        )
        svs = StructuralVariantFactory.create_batch(
            2,
            case_id=self.project1_case1.id,
            case=self.project1_case1,
            variant_set=self.project1_smallvariantset1,
        )
        sm_query = SmallVariantQueryFactory(case=self.project1_case1)
        sm_result_set = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=sm_query
        )
        sv_query = SvQueryFactory(case=self.project1_case1)
        sv_result_set = SvQueryResultSetFactory(case=self.project1_case1, svquery=sv_query)
        sm_flag = SmallVariantFlagsFactory(
            case=self.project1_case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        sm_row = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=sm_result_set,
            release=sm_flag.release,
            chromosome=sm_flag.chromosome,
            start=sm_flag.start,
            end=sm_flag.end,
            reference=sm_flag.reference,
            alternative=sm_flag.alternative,
        )
        sv_flag = StructuralVariantFlagsFactory(
            case=self.project1_case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        sv_row = SvQueryResultRowFactory(
            svqueryresultset=sv_result_set,
            release=sv_flag.release,
            chromosome=sv_flag.chromosome,
            start=sv_flag.start,
            end=sv_flag.end,
            sv_type=sv_flag.sv_type,
            sv_sub_type=sv_flag.sv_sub_type,
        )

        # Run
        count, salvable, duplicates, orphans = create_queryresultset(all=True)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
                self.project1_case2.sodar_uuid,
                self.project2_case1.sodar_uuid,
            ]
        )
        expected_count["smallvariantqueryresultset"] = 3
        expected_count["svqueryresultset"] = 3
        expected_count["sms"]["added"] = 1
        expected_count["svs"]["added"] = 1

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertNotEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(smallvariantquery=None)
            .first()
            .smallvariantqueryresultrow_set.first(),
            sm_row,
        )
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.filter(smallvariantquery=None)
            .first()
            .smallvariantqueryresultrow_set.first()
            .payload,
            sm_row.payload,
        )
        self.assertNotEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None)
            .first()
            .svqueryresultrow_set.first(),
            sv_row,
        )
        self.assertEqual(
            self.project1_case1.svqueryresultset_set.filter(svquery=None)
            .first()
            .svqueryresultrow_set.first()
            .payload,
            sv_row.payload,
        )

    def test_create_sets_sm_annotations_complete(self):
        # Prepare
        smallvariantqueryresultset11 = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=None
        )
        small_vars = SmallVariantFactory.create_batch(
            2,
            case_id=self.project1_case1.id,
            case=self.project1_case1,
            variant_set=self.project1_smallvariantset1,
        )
        sm_query = SmallVariantQueryFactory(case=self.project1_case1)
        sm_result_set = SmallVariantQueryResultSetFactory(
            case=self.project1_case1, smallvariantquery=sm_query
        )
        sm_flag_add = SmallVariantFlagsFactory(
            case=self.project1_case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        sm_flag_salvable = SmallVariantFlagsFactory(
            case=self.project1_case1,
            release=small_vars[1].release,
            chromosome=small_vars[1].chromosome,
            start=small_vars[1].start,
            end=small_vars[1].end,
            reference=small_vars[1].reference,
            alternative=small_vars[1].alternative,
        )
        sm_flag_lost = SmallVariantFlagsFactory(
            case=self.project1_case1,
        )
        sm_row_add = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=sm_result_set,
            release=sm_flag_add.release,
            chromosome=sm_flag_add.chromosome,
            start=sm_flag_add.start,
            end=sm_flag_add.end,
            reference=sm_flag_add.reference,
            alternative=sm_flag_add.alternative,
        )
        sm_row_remove = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=smallvariantqueryresultset11,
            release=sm_flag_lost.release,
            chromosome=sm_flag_lost.chromosome,
            start=sm_flag_lost.start,
            end=sm_flag_lost.end,
            reference=sm_flag_lost.reference,
            alternative=sm_flag_lost.alternative,
        )

        # Run
        count, salvable, duplicates, orphans = create_queryresultset(all=True)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton(
            [
                self.project1_case1.sodar_uuid,
                self.project1_case2.sodar_uuid,
                self.project2_case1.sodar_uuid,
            ]
        )
        expected_count["smallvariantqueryresultset"] = 2
        expected_count["svqueryresultset"] = 3
        expected_count["sms"]["added"] = 1
        expected_count["sms"]["removed"] = 1
        expected_count["sms"]["salvable"]["flags"] = 1
        expected_count["sms"]["lost"]["flags"] = 1
        expected_salvable[str(self.project1_case1.sodar_uuid)] = {
            "sms": ["{chromosome}:{start}-{end}".format(**sm_flag_salvable.__dict__)],
            "svs": [],
        }
        expected_orphans["sms"]["flags"] = [
            {
                "case_uuid": str(self.project1_case1.sodar_uuid),
                "case_name": self.project1_case1.name,
                "project": self.project1_case1.project.full_title,
                "chromosome": sm_flag_lost.chromosome,
                "start": sm_flag_lost.start,
                "end": sm_flag_lost.end,
                "lost": True,
                "json": json.dumps(model_to_dict(sm_flag_lost, exclude=("id",)), cls=UUIDEncoder),
            },
            {
                "case_uuid": str(self.project1_case1.sodar_uuid),
                "case_name": self.project1_case1.name,
                "project": self.project1_case1.project.full_title,
                "chromosome": sm_flag_salvable.chromosome,
                "start": sm_flag_salvable.start,
                "end": sm_flag_salvable.end,
                "lost": False,
                "json": json.dumps(
                    model_to_dict(sm_flag_salvable, exclude=("id",)), cls=UUIDEncoder
                ),
            },
        ]

        # Refresh
        self.project1_case1.refresh_from_db()
        self.project1_case2.refresh_from_db()
        self.project2_case1.refresh_from_db()

        # Assert
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.get(
                smallvariantquery=None
            ).smallvariantqueryresultrow_set.count(),
            1,
        )
        row_added = model_to_dict(
            self.project1_case1.smallvariantqueryresultset_set.get(
                smallvariantquery=None
            ).smallvariantqueryresultrow_set.first(),
            exclude=("id", "sodar_uuid", "smallvariantqueryresultset"),
        )
        self.assertNotEqual(
            row_added,
            model_to_dict(
                sm_row_remove, exclude=("id", "sodar_uuid", "smallvariantqueryresultset")
            ),
        )
        self.assertEqual(
            row_added,
            model_to_dict(sm_row_add, exclude=("id", "sodar_uuid", "smallvariantqueryresultset")),
        )
        self.assertEqual(
            self.project1_case1.smallvariantqueryresultset_set.get(smallvariantquery=None)
            .smallvariantqueryresultrow_set.first()
            .smallvariantqueryresultset,
            smallvariantqueryresultset11,
        )


class TestFillSmQueryResultSet(TestCase):
    def setUp(self):
        super().setUp()
        self.case1 = CaseFactory()
        self.case2 = CaseFactory(project=self.case1.project)
        self.case3 = CaseFactory()

    def test_sms_nothing_to_fill(self):
        # Prepare
        small_vars = SmallVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SmallVariantQueryFactory(case=self.case1)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case1, smallvariantquery=query
        )
        flag = SmallVariantFlagsFactory(
            case=self.case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            reference=flag.reference,
            alternative=flag.alternative,
        )
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            reference=flag.reference,
            alternative=flag.alternative,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)

    def test_sms_fill_comment_flags_acmg(self):
        # Prepare
        small_vars = SmallVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SmallVariantQueryFactory(case=self.case1)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case1, smallvariantquery=query
        )
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        SmallVariantFlagsFactory(
            case=self.case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        SmallVariantFlagsFactory(
            case=self.case1,
            release=small_vars[1].release,
            chromosome=small_vars[1].chromosome,
            start=small_vars[1].start,
            end=small_vars[1].end,
            reference=small_vars[1].reference,
            alternative=small_vars[1].alternative,
        )
        SmallVariantCommentFactory(
            case=self.case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        AcmgCriteriaRatingFactory(
            case=self.case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        row1 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        row2 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=small_vars[1].release,
            chromosome=small_vars[1].chromosome,
            start=small_vars[1].start,
            end=small_vars[1].end,
            reference=small_vars[1].reference,
            alternative=small_vars[1].alternative,
        )

        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)
        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Refresh
        case_result_set.refresh_from_db()

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        expected_count["added"] = 2
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 2)
        self.assertNotEqual(
            case_result_set.smallvariantqueryresultrow_set.all().order_by("id")[0], row1
        )
        self.assertEqual(
            case_result_set.smallvariantqueryresultrow_set.all().order_by("id")[0].payload,
            row1.payload,
        )
        self.assertNotEqual(
            case_result_set.smallvariantqueryresultrow_set.all().order_by("id")[1], row2
        )
        self.assertEqual(
            case_result_set.smallvariantqueryresultrow_set.all().order_by("id")[1].payload,
            row2.payload,
        )

    def test_sms_salvable_no_query(self):
        # Prepare
        small_vars = SmallVariantFactory.create_batch(2, case_id=self.case1.id)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(
            case=self.case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        expected_count["salvable"]["flags"] = 1
        expected_salvable = ["{chromosome}:{start}-{end}".format(**flag.__dict__)]
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": False,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_sms_salvable_no_row(self):
        # Prepare
        # Do not create: rows for query_result_set
        small_vars = SmallVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SmallVariantQueryFactory(case=self.case1)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case1, smallvariantquery=query
        )
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(
            case=self.case1,
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )

        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        expected_count["salvable"]["flags"] = 1
        expected_salvable = ["{chromosome}:{start}-{end}".format(**flag.__dict__)]
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": False,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_sms_lost_no_var_with_query(self):
        # Prepare
        query = SmallVariantQueryFactory(case=self.case1)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case1, smallvariantquery=query
        )
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            reference=flag.reference,
            alternative=flag.alternative,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Refresh
        case_result_set.refresh_from_db()

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        expected_count["lost"]["flags"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_sms_lost_no_var_no_query_no_caseresultrow(self):
        # Prepare
        # Do not create: svs, query, query_result_set, rows for query_result_set
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)

        # Run
        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Refresh
        case_result_set.refresh_from_db()

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        expected_count["lost"]["flags"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)

    def test_sms_lost_no_var_no_query_with_caseresultrow(self):
        # Prepare
        # Do not create: svs, query, query_result_set, rows for query_result_set
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case1, smallvariantquery=None)
        flag = SmallVariantFlagsFactory(case=self.case1)
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            reference=flag.reference,
            alternative=flag.alternative,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sm_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sm()
        expected_count["lost"]["flags"] = 1
        expected_count["removed"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.smallvariantqueryresultrow_set.count(), 0)


class TestFillSvQueryResultSet(TestCase):
    def setUp(self):
        super().setUp()
        self.case1 = CaseFactory()
        self.case2 = CaseFactory(project=self.case1.project)
        self.case3 = CaseFactory()

    def test_svs_nothing_to_fill(self):
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SvQueryFactory(case=self.case1)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case1, svquery=query)
        flag = StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            sv_type=flag.sv_type,
            sv_sub_type=flag.sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            sv_type=flag.sv_type,
            sv_sub_type=flag.sv_sub_type,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)

    def test_svs_fill_comment_flags(self):
        # Prepare
        # Do not create: rows for case_result_set.
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=self.case1, svquery=query)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[1].release,
            chromosome=svs[1].chromosome,
            start=svs[1].start,
            end=svs[1].end,
            sv_type=svs[1].sv_type,
            sv_sub_type=svs[1].sv_sub_type,
        )
        StructuralVariantCommentFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        row1 = SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        row2 = SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[1].release,
            chromosome=svs[1].chromosome,
            start=svs[1].start,
            end=svs[1].end,
            sv_type=svs[1].sv_type,
            sv_sub_type=svs[1].sv_sub_type,
        )

        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["added"] = 2
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 2)
        self.assertNotEqual(case_result_set.svqueryresultrow_set.all().order_by("id")[0], row1)
        self.assertEqual(
            case_result_set.svqueryresultrow_set.all().order_by("id")[0].payload, row1.payload
        )
        self.assertNotEqual(case_result_set.svqueryresultrow_set.all().order_by("id")[1], row2)
        self.assertEqual(
            case_result_set.svqueryresultrow_set.all().order_by("id")[1].payload, row2.payload
        )

    def test_svs_salvable_no_query(self):
        # Prepare
        # Do not create: query, query_result_set, rows for query_result_set, rows for case_result_set
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case1.id)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["salvable"]["flags"] = 1
        expected_salvable = ["{chromosome}:{start}-{end}".format(**flag.__dict__)]
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": False,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_svs_salvable_no_row(self):
        # Prepare
        # Do not create: rows for query_result_set
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=self.case1, svquery=query)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["salvable"]["flags"] = 1
        expected_salvable = ["{chromosome}:{start}-{end}".format(**flag.__dict__)]
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": False,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_svs_lost_no_var_with_query(self):
        # Prepare
        # Do not create: svs, rows for case_result_set
        query = SvQueryFactory(case=self.case1)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case1, svquery=query)
        flag = StructuralVariantFlagsFactory(case=self.case1)
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            sv_type=flag.sv_type,
            sv_sub_type=flag.sv_sub_type,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["lost"]["flags"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_svs_lost_no_var_no_query_no_caseresultrow(self):
        # Prepare
        # Do not create: svs, query, query_result_set, rows for query_result_set
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(case=self.case1)

        # Run
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["lost"]["flags"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)

    def test_svs_lost_no_var_no_query_with_caseresultrow(self):
        # Prepare
        # Do not create: svs
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        flag = StructuralVariantFlagsFactory(case=self.case1)
        SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            sv_type=flag.sv_type,
            sv_sub_type=flag.sv_sub_type,
        )

        # Run
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["lost"]["flags"] = 1
        expected_count["removed"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(SvQueryResultRow.objects.count(), 0)

    def test_svs_var_overlap_above_80(self):
        # Prepare
        # Do not create: rows for case_result_set.
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=self.case1, svquery=query)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        shift = int((svs[0].end - svs[0].start + 1) * 0.1)
        StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        row = SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["added"] = 1
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 1)
        self.assertNotEqual(case_result_set.svqueryresultrow_set.all().order_by("id")[0], row)
        self.assertEqual(
            case_result_set.svqueryresultrow_set.all().order_by("id")[0].payload, row.payload
        )

    def test_svs_var_overlap_below_80(self):
        # Prepare
        # Do not create: rows for case_result_set.
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case1.id)
        query = SvQueryFactory(case=self.case1)
        query_result_set = SvQueryResultSetFactory(case=self.case1, svquery=query)
        case_result_set = SvQueryResultSetFactory(case=self.case1, svquery=None)
        shift = int((svs[0].end - svs[0].start + 1) * 0.9)
        flag = StructuralVariantFlagsFactory(
            case=self.case1,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)
        count, salvable, duplicates, orphans = fill_sv_queryresultset(case_result_set)

        # Set expectations
        (
            expected_count,
            expected_salvable,
            expected_duplicates,
            expected_orphans,
        ) = create_expected_skeleton_sv()
        expected_count["lost"]["flags"] = 1
        expected_orphans["flags"] = [
            {
                "case_uuid": str(self.case1.sodar_uuid),
                "case_name": self.case1.name,
                "project": self.case1.project.full_title,
                "chromosome": flag.chromosome,
                "start": flag.start,
                "end": flag.end,
                "lost": True,
                "json": json.dumps(model_to_dict(flag, exclude=("id",)), cls=UUIDEncoder),
            }
        ]
        self.assertEqual(count, expected_count)
        self.assertEqual(salvable, expected_salvable)
        self.assertEqual(duplicates, expected_duplicates)
        self.assertEqual(orphans, expected_orphans)
        self.assertEqual(case_result_set.svqueryresultrow_set.count(), 0)


class TestClearSvQueryResultSet(TestCase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()

    def _test_svs_case_resultrows_with_annotation(self, anno_type):
        if anno_type == "flags":
            anno_model = StructuralVariantFlags
            anno_factory = StructuralVariantFlagsFactory
        else:
            anno_model = StructuralVariantComment
            anno_factory = StructuralVariantCommentFactory
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case.id)
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case, svquery=query)
        flag = anno_factory(
            case=self.case,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            sv_type=flag.sv_type,
            sv_sub_type=flag.sv_sub_type,
        )
        case_row = SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=flag.release,
            chromosome=flag.chromosome,
            start=flag.start,
            end=flag.end,
            sv_type=flag.sv_type,
            sv_sub_type=flag.sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 0)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 1)
        self.assertEqual(rows_expected[0], case_row)
        self.assertEqual(anno_model.objects.count(), 1)
        self.assertEqual(anno_model.objects.first(), flag)
        svs_expected = StructuralVariant.objects.all().order_by("id")
        self.assertEqual(svs_expected.count(), 2)
        self.assertEqual(svs_expected[0], svs[0])
        self.assertEqual(svs_expected[0], svs[0])

    def test_svs_case_resultrows_with_flags(self):
        self._test_svs_case_resultrows_with_annotation("flags")

    def test_svs_case_resultrows_with_comments(self):
        self._test_svs_case_resultrows_with_annotation("comments")

    def test_svs_case_resultrows_no_annotation(self):
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case.id)
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        SvQueryResultSetFactory(case=self.case, svquery=query)
        SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 1)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 0)
        self.assertEqual(StructuralVariantFlags.objects.count(), 0)
        self.assertEqual(StructuralVariantComment.objects.count(), 0)
        svs_expected = StructuralVariant.objects.all().order_by("id")
        self.assertEqual(svs_expected.count(), 2)
        self.assertEqual(svs_expected[0], svs[0])
        self.assertEqual(svs_expected[0], svs[0])

    def _test_svs_case_resultrows_no_var(self, anno_type):
        if anno_type == "flags":
            anno_model = StructuralVariantFlags
            anno_factory = StructuralVariantFlagsFactory
        else:
            anno_model = StructuralVariantComment
            anno_factory = StructuralVariantCommentFactory
        # Prepare
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case, svquery=query)
        anno = anno_factory(
            case=self.case,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=anno.release,
            chromosome=anno.chromosome,
            start=anno.start,
            end=anno.end,
            sv_type=anno.sv_type,
            sv_sub_type=anno.sv_sub_type,
        )
        case_row = SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=anno.release,
            chromosome=anno.chromosome,
            start=anno.start,
            end=anno.end,
            sv_type=anno.sv_type,
            sv_sub_type=anno.sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 1)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 0)
        self.assertEqual(anno_model.objects.count(), 1)
        self.assertEqual(anno_model.objects.first(), anno)

    def test_svs_case_resultrows_no_var_with_flags(self):
        self._test_svs_case_resultrows_no_var("flags")

    def test_svs_case_resultrows_no_var_with_comment(self):
        self._test_svs_case_resultrows_no_var("comments")

    def test_svs_case_resultrows_complete(self):
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case.id)
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case, svquery=query)
        flag1 = StructuralVariantFlagsFactory(
            case=self.case,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        comment1 = StructuralVariantCommentFactory(
            case=self.case,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            sv_type=flag1.sv_type,
            sv_sub_type=flag1.sv_sub_type,
        )
        flag2 = StructuralVariantFlagsFactory(case=self.case)
        comment2 = StructuralVariantCommentFactory(
            case=self.case,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            sv_type=flag2.sv_type,
            sv_sub_type=flag2.sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            sv_type=flag1.sv_type,
            sv_sub_type=flag1.sv_sub_type,
        )
        case_row1 = SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            sv_type=flag1.sv_type,
            sv_sub_type=flag1.sv_sub_type,
        )
        case_row2 = SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            sv_type=flag2.sv_type,
            sv_sub_type=flag2.sv_sub_type,
        )
        case_row3 = SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=svs[1].release,
            chromosome=svs[1].chromosome,
            start=svs[1].start,
            end=svs[1].end,
            sv_type=svs[1].sv_type,
            sv_sub_type=svs[1].sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 2)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 1)
        self.assertEqual(rows_expected[0], case_row1)
        flags_expected = StructuralVariantFlags.objects.all().order_by("id")
        self.assertEqual(flags_expected.count(), 2)
        self.assertEqual(flags_expected[0], flag1)
        self.assertEqual(flags_expected[1], flag2)
        comments_expected = StructuralVariantComment.objects.all().order_by("id")
        self.assertEqual(comments_expected.count(), 2)
        self.assertEqual(comments_expected[0], comment1)
        self.assertEqual(comments_expected[1], comment2)
        svs_expected = StructuralVariant.objects.all().order_by("id")
        self.assertEqual(svs_expected.count(), 2)
        self.assertEqual(svs_expected[0], svs[0])
        self.assertEqual(svs_expected[0], svs[0])

    def test_svs_case_resultrows_overlap_below_80(self):
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case.id)
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case, svquery=query)
        shift = int((svs[0].end - svs[0].start + 1) * 0.9)
        flag = StructuralVariantFlagsFactory(
            case=self.case,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 1)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 0)
        flags_expected = StructuralVariantFlags.objects.all().order_by("id")
        self.assertEqual(flags_expected.count(), 1)
        self.assertEqual(flags_expected[0], flag)
        svs_expected = StructuralVariant.objects.all().order_by("id")
        self.assertEqual(svs_expected.count(), 2)
        self.assertEqual(svs_expected[0], svs[0])
        self.assertEqual(svs_expected[0], svs[0])

    def test_svs_case_annotation_overlap_below_80(self):
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case.id)
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case, svquery=query)
        shift = int((svs[0].end - svs[0].start + 1) * 0.9)
        flag = StructuralVariantFlagsFactory(
            case=self.case,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 1)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 0)
        flags_expected = StructuralVariantFlags.objects.all().order_by("id")
        self.assertEqual(flags_expected.count(), 1)
        self.assertEqual(flags_expected[0], flag)
        svs_expected = StructuralVariant.objects.all().order_by("id")
        self.assertEqual(svs_expected.count(), 2)
        self.assertEqual(svs_expected[0], svs[0])
        self.assertEqual(svs_expected[0], svs[0])

    def test_svs_case_resultrows_overlap_above_80(self):
        # Prepare
        svs = StructuralVariantFactory.create_batch(2, case_id=self.case.id)
        query = SvQueryFactory(case=self.case)
        case_result_set = SvQueryResultSetFactory(case=self.case, svquery=None)
        query_result_set = SvQueryResultSetFactory(case=self.case, svquery=query)
        shift = int((svs[0].end - svs[0].start + 1) * 0.1)
        flag = StructuralVariantFlagsFactory(
            case=self.case,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start,
            end=svs[0].end,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        SvQueryResultRowFactory(
            svqueryresultset=query_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )
        row = SvQueryResultRowFactory(
            svqueryresultset=case_result_set,
            release=svs[0].release,
            chromosome=svs[0].chromosome,
            start=svs[0].start + shift,
            end=svs[0].end + shift,
            sv_type=svs[0].sv_type,
            sv_sub_type=svs[0].sv_sub_type,
        )

        # Run
        count = clear_sv_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 0)
        rows_expected = SvQueryResultRow.objects.filter(svqueryresultset=case_result_set)
        self.assertEqual(rows_expected.count(), 1)
        self.assertEqual(rows_expected.first(), row)
        flags_expected = StructuralVariantFlags.objects.all().order_by("id")
        self.assertEqual(flags_expected.count(), 1)
        self.assertEqual(flags_expected[0], flag)
        svs_expected = StructuralVariant.objects.all().order_by("id")
        self.assertEqual(svs_expected.count(), 2)
        self.assertEqual(svs_expected[0], svs[0])
        self.assertEqual(svs_expected[0], svs[0])


class TestClearSmQueryResultSet(TestCase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()

    def _test_sms_case_resultrows_with_annotation(self, anno_type):
        if anno_type == "flags":
            anno_model = SmallVariantFlags
            anno_factory = SmallVariantFlagsFactory
        elif anno_type == "comments":
            anno_model = SmallVariantComment
            anno_factory = SmallVariantCommentFactory
        else:
            anno_model = AcmgCriteriaRating
            anno_factory = AcmgCriteriaRatingFactory
        # Prepare
        sms = SmallVariantFactory.create_batch(2, case_id=self.case.id)
        query = SmallVariantQueryFactory(case=self.case)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case, smallvariantquery=None)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case, smallvariantquery=query
        )
        anno = anno_factory(
            case=self.case,
            release=sms[0].release,
            chromosome=sms[0].chromosome,
            start=sms[0].start,
            end=sms[0].end,
            reference=sms[0].reference,
            alternative=sms[0].alternative,
        )
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=anno.release,
            chromosome=anno.chromosome,
            start=anno.start,
            end=anno.end,
            reference=anno.reference,
            alternative=anno.alternative,
        )
        case_row = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=anno.release,
            chromosome=anno.chromosome,
            start=anno.start,
            end=anno.end,
            reference=anno.reference,
            alternative=anno.alternative,
        )

        # Run
        count = clear_sm_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 0)
        rows_expected = SmallVariantQueryResultRow.objects.filter(
            smallvariantqueryresultset=case_result_set
        )
        self.assertEqual(rows_expected.count(), 1)
        self.assertEqual(rows_expected[0], case_row)
        self.assertEqual(anno_model.objects.count(), 1)
        self.assertEqual(anno_model.objects.first(), anno)
        sms_expected = SmallVariant.objects.all().order_by("id")
        self.assertEqual(sms_expected.count(), 2)
        self.assertEqual(sms_expected[0], sms[0])
        self.assertEqual(sms_expected[0], sms[0])

    def test_sms_case_resultrows_with_flags(self):
        self._test_sms_case_resultrows_with_annotation("flags")

    def test_sms_case_resultrows_with_comments(self):
        self._test_sms_case_resultrows_with_annotation("comments")

    def test_sms_case_resultrows_with_acmg_rating(self):
        self._test_sms_case_resultrows_with_annotation("acmg_rating")

    def test_sms_case_resultrows_no_annotation(self):
        # Prepare
        sms = SmallVariantFactory.create_batch(2, case_id=self.case.id)
        query = SmallVariantQueryFactory(case=self.case)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case, smallvariantquery=None)
        SmallVariantQueryResultSetFactory(case=self.case, smallvariantquery=query)
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=sms[0].release,
            chromosome=sms[0].chromosome,
            start=sms[0].start,
            end=sms[0].end,
            reference=sms[0].reference,
            alternative=sms[0].alternative,
        )

        # Run
        count = clear_sm_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 1)
        rows_expected = SmallVariantQueryResultRow.objects.filter(
            smallvariantqueryresultset=case_result_set
        )
        self.assertEqual(rows_expected.count(), 0)
        self.assertEqual(SmallVariantFlags.objects.count(), 0)
        self.assertEqual(SmallVariantComment.objects.count(), 0)
        self.assertEqual(AcmgCriteriaRating.objects.count(), 0)
        sms_expected = SmallVariant.objects.all().order_by("id")
        self.assertEqual(sms_expected.count(), 2)
        self.assertEqual(sms_expected[0], sms[0])
        self.assertEqual(sms_expected[0], sms[0])

    def _test_sms_case_resultrows_no_var(self, anno_type):
        if anno_type == "flags":
            anno_model = SmallVariantFlags
            anno_factory = SmallVariantFlagsFactory
        elif anno_type == "comments":
            anno_model = SmallVariantComment
            anno_factory = SmallVariantCommentFactory
        else:
            anno_model = AcmgCriteriaRating
            anno_factory = AcmgCriteriaRatingFactory
        # Prepare
        query = SmallVariantQueryFactory(case=self.case)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case, smallvariantquery=None)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case, smallvariantquery=query
        )
        anno = anno_factory(
            case=self.case,
        )
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=anno.release,
            chromosome=anno.chromosome,
            start=anno.start,
            end=anno.end,
            reference=anno.reference,
            alternative=anno.alternative,
        )
        case_row = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=anno.release,
            chromosome=anno.chromosome,
            start=anno.start,
            end=anno.end,
            reference=anno.reference,
            alternative=anno.alternative,
        )

        # Run
        count = clear_sm_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 1)
        rows_expected = SmallVariantQueryResultRow.objects.filter(
            smallvariantqueryresultset=case_result_set
        )
        self.assertEqual(rows_expected.count(), 0)
        self.assertEqual(anno_model.objects.count(), 1)
        self.assertEqual(anno_model.objects.first(), anno)

    def test_sms_case_resultrows_no_var_with_flags(self):
        self._test_sms_case_resultrows_no_var("flags")

    def test_sms_case_resultrows_no_var_with_comment(self):
        self._test_sms_case_resultrows_no_var("comments")

    def test_sms_case_resultrows_no_var_with_acmg_rating(self):
        self._test_sms_case_resultrows_no_var("acmg_rating")

    def test_sms_case_resultrows_complete(self):
        # Prepare
        sms = SmallVariantFactory.create_batch(2, case_id=self.case.id)
        query = SmallVariantQueryFactory(case=self.case)
        case_result_set = SmallVariantQueryResultSetFactory(case=self.case, smallvariantquery=None)
        query_result_set = SmallVariantQueryResultSetFactory(
            case=self.case, smallvariantquery=query
        )
        flag1 = SmallVariantFlagsFactory(
            case=self.case,
            release=sms[0].release,
            chromosome=sms[0].chromosome,
            start=sms[0].start,
            end=sms[0].end,
            reference=sms[0].reference,
            alternative=sms[0].alternative,
        )
        comment1 = SmallVariantCommentFactory(
            case=self.case,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        acmg_rating1 = AcmgCriteriaRatingFactory(
            case=self.case,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        flag2 = SmallVariantFlagsFactory(case=self.case)
        comment2 = SmallVariantCommentFactory(
            case=self.case,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            reference=flag2.reference,
            alternative=flag2.alternative,
        )
        acmg_rating2 = AcmgCriteriaRatingFactory(
            case=self.case,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            reference=flag2.reference,
            alternative=flag2.alternative,
        )
        SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=query_result_set,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        case_row1 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=flag1.release,
            chromosome=flag1.chromosome,
            start=flag1.start,
            end=flag1.end,
            reference=flag1.reference,
            alternative=flag1.alternative,
        )
        case_row2 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=flag2.release,
            chromosome=flag2.chromosome,
            start=flag2.start,
            end=flag2.end,
            reference=flag2.reference,
            alternative=flag2.alternative,
        )
        case_row3 = SmallVariantQueryResultRowFactory(
            smallvariantqueryresultset=case_result_set,
            release=sms[1].release,
            chromosome=sms[1].chromosome,
            start=sms[1].start,
            end=sms[1].end,
            reference=sms[1].reference,
            alternative=sms[1].alternative,
        )

        # Run
        count = clear_sm_queryresultset(case_result_set)

        # Assert
        self.assertEqual(count, 2)
        rows_expected = SmallVariantQueryResultRow.objects.filter(
            smallvariantqueryresultset=case_result_set
        )
        self.assertEqual(rows_expected.count(), 1)
        self.assertEqual(rows_expected[0], case_row1)
        flags_expected = SmallVariantFlags.objects.all().order_by("id")
        self.assertEqual(flags_expected.count(), 2)
        self.assertEqual(flags_expected[0], flag1)
        self.assertEqual(flags_expected[1], flag2)
        comments_expected = SmallVariantComment.objects.all().order_by("id")
        self.assertEqual(comments_expected.count(), 2)
        self.assertEqual(comments_expected[0], comment1)
        self.assertEqual(comments_expected[1], comment2)
        acmg_rating_expected = AcmgCriteriaRating.objects.all().order_by("id")
        self.assertEqual(acmg_rating_expected.count(), 2)
        self.assertEqual(acmg_rating_expected[0], acmg_rating1)
        self.assertEqual(acmg_rating_expected[1], acmg_rating2)
        sms_expected = SmallVariant.objects.all().order_by("id")
        self.assertEqual(sms_expected.count(), 2)
        self.assertEqual(sms_expected[0], sms[0])
        self.assertEqual(sms_expected[0], sms[0])
