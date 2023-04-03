from django.forms import model_to_dict
from test_plus import TestCase

from cases.serializers import (
    CaseAlignmentStatsSerializer,
    CaseCommentSerializer,
    CaseGeneAnnotationSerializer,
    CaseSerializer,
    PedigreeRelatednessSerializer,
    SampleVariantStatisticsSerializer,
)
from cases.tests.factories import CaseAlignmentStatsFactory, PedigreeRelatednessFactory
from variants.tests.factories import (
    CaseCommentsFactory,
    CaseFactory,
    CaseGeneAnnotationEntryFactory,
    CaseWithVariantSetFactory,
    SampleVariantStatisticsFactory,
)
from variants.tests.test_views_api import transmogrify_pedigree

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestCaseCommentSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.case_comment = CaseCommentsFactory()

    def testSerializeExisting(self):
        serializer = CaseCommentSerializer(self.case_comment)
        expected = model_to_dict(self.case_comment)
        expected.pop("id")
        expected["case"] = self.case_comment.case.sodar_uuid
        expected["date_created"] = self.case_comment.date_created.strftime(TIMEF)
        expected["date_modified"] = self.case_comment.date_modified.strftime(TIMEF)
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        self.assertDictEqual(serializer.data, expected)


class TestCaseGeneAnnotationSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.entry = CaseGeneAnnotationEntryFactory()

    def testSerializeExisting(self):
        serializer = CaseGeneAnnotationSerializer(self.entry)
        expected = model_to_dict(self.entry, exclude=("id",))
        expected["case"] = self.entry.case.sodar_uuid
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        self.assertDictEqual(serializer.data, expected)


class TestCaseSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()
        self.maxDiff = None

    def testSerializeExisting(self):
        serializer = CaseSerializer(self.case)
        expected = model_to_dict(
            self.case,
            fields=(
                "sodar_uuid",
                "project",
                "sex_errors",
                "release",
                "name",
                "index",
                "pedigree",
                "notes",
                "status",
                "tags",
                "date_created",
                "date_modified",
                "num_small_vars",
                "num_svs",
            ),
        )
        expected["pedigree"] = transmogrify_pedigree(expected["pedigree"])
        expected["project"] = self.case.project.sodar_uuid
        expected["sodar_uuid"] = str(self.case.sodar_uuid)
        expected["sex_errors"] = {}
        expected["date_created"] = self.case.date_created.strftime(TIMEF)
        expected["date_modified"] = self.case.date_modified.strftime(TIMEF)
        self.assertDictEqual(serializer.data, expected)


class TestCaseAlignmentStatsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.casealignmentstats = CaseAlignmentStatsFactory()
        self.maxDiff = None

    def testSerializeExisting(self):
        serializer = CaseAlignmentStatsSerializer(self.casealignmentstats)
        expected = model_to_dict(
            self.casealignmentstats,
            fields=(
                "case",
                "variantset",
                "bam_stats",
            ),
        )
        expected["case"] = self.casealignmentstats.case.sodar_uuid
        self.assertDictEqual(serializer.data, expected)


class TestSampleVariantStatisticsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        (
            self.case,
            self.latest_variant_set,
            self.latest_structural_variant_set,
        ) = CaseWithVariantSetFactory.get()
        self.samplevariantstatistics = SampleVariantStatisticsFactory(
            variant_set=self.latest_variant_set
        )

    def testSerializeExisting(self):
        serializer = SampleVariantStatisticsSerializer(self.samplevariantstatistics)
        expected = model_to_dict(
            self.samplevariantstatistics,
            fields=(
                "case",
                "sample_name",
                "ontarget_transitions",
                "ontarget_transversions",
                "ontarget_snvs",
                "ontarget_indels",
                "ontarget_mnvs",
                "ontarget_effect_counts",
                "ontarget_indel_sizes",
                "ontarget_dps",
                "ontarget_dp_quantiles",
                "het_ratio",
                "chrx_het_hom",
                "ontarget_ts_tv_ratio",
            ),
        )
        expected["ontarget_ts_tv_ratio"] = self.samplevariantstatistics.ontarget_ts_tv_ratio()
        expected["case"] = self.case.sodar_uuid
        self.assertDictEqual(serializer.data, expected)


class TestPedigreeRelatednessSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.pedigreerelatedness = PedigreeRelatednessFactory()

    def testSerializeExisting(self):
        serializer = PedigreeRelatednessSerializer(self.pedigreerelatedness)
        expected = model_to_dict(
            self.pedigreerelatedness,
            fields=(
                "case",
                "sample1",
                "sample2",
                "het_1_2",
                "het_1",
                "het_2",
                "n_ibs0",
                "n_ibs1",
                "n_ibs2",
                "relatedness",
            ),
        )
        expected["relatedness"] = self.pedigreerelatedness.relatedness()
        expected["case"] = self.pedigreerelatedness.stats.variant_set.case.sodar_uuid
        self.assertDictEqual(serializer.data, expected)
