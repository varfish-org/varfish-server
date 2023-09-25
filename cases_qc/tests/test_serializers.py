from unittest.mock import patch

from freezegun import freeze_time
from parameterized import parameterized
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.serializers import (
    CraminoMetricsSerializer,
    DragenCnvMetricsSerializer,
    DragenFragmentLengthHistogramSerializer,
    DragenMappingMetricsSerializer,
    DragenPloidyEstimationMetricsSerializer,
    DragenRegionCoverageMetricsSerializer,
    DragenRegionFineHistSerializer,
    DragenRegionHistSerializer,
    DragenRegionOverallMeanCovSerializer,
    DragenRohMetricsSerializer,
    DragenSvMetricsSerializer,
    DragenTimeMetricsSerializer,
    DragenTrimmerMetricsSerializer,
    DragenVcHethomRatioMetricsSerializer,
    DragenVcMetricsSerializer,
    DragenWgsContigMeanCovMetricsSerializer,
    DragenWgsCoverageMetricsSerializer,
    DragenWgsFineHistSerializer,
    DragenWgsHistSerializer,
    DragenWgsOverallMeanCovSerializer,
    NgsbitsMappingqcMetricsSerializer,
    SamtoolsFlagstatMetricsSerializer,
    SamtoolsIdxstatsMetricsSerializer,
    SamtoolsStatsMainMetricsSerializer,
    SamtoolsStatsSupplementaryMetricsSerializer,
    VarfishStatsSerializer,
)
from cases_qc.tests import helpers
from cases_qc.tests.factories import (
    CraminoMetricsFactory,
    DragenCnvMetricsFactory,
    DragenFragmentLengthHistogramFactory,
    DragenMappingMetricsFactory,
    DragenPloidyEstimationMetricsFactory,
    DragenRegionCoverageMetricsFactory,
    DragenRegionFineHistFactory,
    DragenRegionHistFactory,
    DragenRegionOverallMeanCovFactory,
    DragenRohMetricsFactory,
    DragenSvMetricsFactory,
    DragenTimeMetricsFactory,
    DragenTrimmerMetricsFactory,
    DragenVcHethomRatioMetricsFactory,
    DragenVcMetricsFactory,
    DragenWgsContigMeanCovMetricsFactory,
    DragenWgsCoverageMetricsFactory,
    DragenWgsFineHistFactory,
    DragenWgsHistFactory,
    DragenWgsOverallMeanCovFactory,
    NgsbitsMappingqcMetricsFactory,
    SamtoolsFlagstatMetricsFactory,
    SamtoolsIdxstatsMetricsFactory,
    SamtoolsStatsMainMetricsFactory,
    SamtoolsStatsSupplementaryMetricsFactory,
    VarfishStatsFactory,
)


@freeze_time("2012-01-14 12:00:01")
class SerializerTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    @parameterized.expand(
        [
            [DragenFragmentLengthHistogramFactory, DragenFragmentLengthHistogramSerializer],
            [DragenCnvMetricsFactory, DragenCnvMetricsSerializer],
            [DragenMappingMetricsFactory, DragenMappingMetricsSerializer],
            [DragenPloidyEstimationMetricsFactory, DragenPloidyEstimationMetricsSerializer],
            [DragenRegionCoverageMetricsFactory, DragenRegionCoverageMetricsSerializer],
            [DragenRegionFineHistFactory, DragenRegionFineHistSerializer],
            [DragenRegionHistFactory, DragenRegionHistSerializer],
            [DragenRegionOverallMeanCovFactory, DragenRegionOverallMeanCovSerializer],
            [DragenRohMetricsFactory, DragenRohMetricsSerializer],
            [DragenVcMetricsFactory, DragenVcMetricsSerializer],
            [DragenSvMetricsFactory, DragenSvMetricsSerializer],
            [DragenTimeMetricsFactory, DragenTimeMetricsSerializer],
            [DragenTrimmerMetricsFactory, DragenTrimmerMetricsSerializer],
            [DragenVcHethomRatioMetricsFactory, DragenVcHethomRatioMetricsSerializer],
            [DragenWgsContigMeanCovMetricsFactory, DragenWgsContigMeanCovMetricsSerializer],
            [DragenWgsCoverageMetricsFactory, DragenWgsCoverageMetricsSerializer],
            [DragenWgsFineHistFactory, DragenWgsFineHistSerializer],
            [DragenWgsHistFactory, DragenWgsHistSerializer],
            [DragenWgsOverallMeanCovFactory, DragenWgsOverallMeanCovSerializer],
            [SamtoolsStatsMainMetricsFactory, SamtoolsStatsMainMetricsSerializer],
            [SamtoolsStatsSupplementaryMetricsFactory, SamtoolsStatsSupplementaryMetricsSerializer],
            [SamtoolsFlagstatMetricsFactory, SamtoolsFlagstatMetricsSerializer],
            [SamtoolsIdxstatsMetricsFactory, SamtoolsIdxstatsMetricsSerializer],
            [CraminoMetricsFactory, CraminoMetricsSerializer],
            [NgsbitsMappingqcMetricsFactory, NgsbitsMappingqcMetricsSerializer],
            [VarfishStatsFactory, VarfishStatsSerializer],
        ]
    )
    @patch("faker.providers.misc.Provider.uuid4", new_callable=helpers.determined_uuids)
    @patch("faker.providers.lorem.Provider.word", new_callable=helpers.determined_words)
    def test_load(self, factory_class, serializer_class, _mock_uuid, _mock_word):
        obj = factory_class()
        serializer = serializer_class(obj)
        self.assertMatchSnapshot(dict(serializer.data))
