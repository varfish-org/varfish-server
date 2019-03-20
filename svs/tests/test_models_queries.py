"""Tests for performing queries with the ``models_queries`` module."""

from variants.models import Case

from ._fixtures import (
    fixture_setup_case1_simple,
    BASE_CLEANED_DATA_CASE_1,
    DGV_SV_DICT,
    DGV_SV_GS_DICT,
    G1K_DICT,
    EXAC_CNV_DICT,
    DB_VAR_DICT,
    GNOMAD_SV_DICT,
)
from ._helpers import TestBase, SQLALCHEMY_ENGINE

from ..models_queries import SingleCaseFilterQuery
from svdbs.models import DgvSvs, DgvGoldStandardSvs, ExacCnv, ThousandGenomesSv, DbVarSv, GnomAdSv
from .. import models


class SvGenotypeQueryTest(TestBase):
    """Tests for filtration by genotype."""

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testQueryAnyGenotype(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(self.base_cleaned_data)
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testQueryDeNovo(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "ref",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testQueryDominant(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                },
            }
        )
        result = list(result)
        self.assertEqual(result, [])


class GenotypeQualityTest(TestBase):

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassGqFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_gq_min": 10,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testFailGqFilterPassesGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 => kept
                    "sample2-N1-DNA1-WGS1_gq_min": 11,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassSrcFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_src_min": 10,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassSrcFilterPassesGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 but GT is hom. ref. => discarded
                    "sample2-N1-DNA1-WGS1_src_min": 11,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassSrvMinFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_srv_min": 5,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testFailSrvMinFilterFailsGenotypeFilter2(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 but GT is hom. ref. => discarded
                    "sample2-N1-DNA1-WGS1_srv_min": 6,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassSrvMaxFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_srv_max": 5,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testFailSrvMaxFilterPassesGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 => kept
                    "sample2-N1-DNA1-WGS1_srv_max": 4,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassPecFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_pec_min": 10,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testFailPecFilterPassesGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 => kept
                    "sample2-N1-DNA1-WGS1_pec_min": 11,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassPevMinFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_pev_min": 5,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassPevMinFilterFailsGenotypeFilter2(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 but GT is hom. ref. => discarded
                    "sample2-N1-DNA1-WGS1_pev_min": 6,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassPevMaxFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_pev_max": 5,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testFailPevMaxFilterPassesGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 => kept
                    "sample2-N1-DNA1-WGS1_pev_max": 4,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassCovFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_cov_min": 15,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testFailCovFilterPassesGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 => kept
                    "sample2-N1-DNA1-WGS1_cov_min": 21,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassVarMinFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 but GT is hom. ref. => discarded
                    "sample2-N1-DNA1-WGS1_var_min": 9,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassVarMinFilterFailsGenotypeFilter2(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 but GT is hom. ref. => discarded
                    "sample2-N1-DNA1-WGS1_var_min": 11,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassVarMaxFilterFailsGenotypeFilter(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality passes for sample2 => filtered out.
                    "sample2-N1-DNA1-WGS1_var_max": 15,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassVarMaxFilterFailsGenotypeFilter2(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{
                    # Query is for dominant variants, pattern in data is de novo.
                    "sample1-N1-DNA1-WGS1_gt": "het",
                    "sample2-N1-DNA1-WGS1_gt": "het",
                    "sample3-N1-DNA1-WGS1_gt": "ref",
                    # Quality fails for sample2 but GT is hom. ref. => discarded
                    "sample2-N1-DNA1-WGS1_var_max": 11,
                },
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)


class SvVariantTypeQueryTest(TestBase):
    """Tests for filtration by ``sv_type`` and ``sv_sub_type`` attributes."""

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testQueryVariantTypeMatch(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, "sv_sub_type": []})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testQueryVariantTypeNoMatch(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        sv_types = [
            var_type for var_type, _ in models.SV_TYPE_CHOICES if not var_type.startswith("DEL")
        ]
        result = query.run({**self.base_cleaned_data, **{"sv_type": sv_types, "sv_sub_type": []}})
        result = list(result)
        self.assertEqual(len(result), 0)

    def testQueryVariantSubTypeMatch(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"sv_type": []}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testQueryVariantSubTypeNoMatch(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        sv_sub_types = [
            sub_type for sub_type, _ in models.SV_TYPE_CHOICES if not sub_type.startswith("DEL")
        ]
        result = query.run(
            {**self.base_cleaned_data, **{"sv_type": [], "sv_sub_type": sv_sub_types}}
        )
        result = list(result)
        self.assertEqual(len(result), 0)


class SvCohortFrequencyTest(TestBase):
    """Test for filtration with the frequencies within the analysis cohort/collective.
    """

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassMinAffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_affected_carriers_min": 1},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMinAffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_affected_carriers_min": 2},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxAffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_affected_carriers_max": 1},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_affected_carriers_max": 0},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMinUnaffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_unaffected_carriers_min": 1},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMinUnaffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_unaffected_carriers_min": 2},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxUnaffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_unaffected_carriers_max": 1},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxUnaffectedCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_unaffected_carriers_max": 0},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMinBackgroundCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_background_carriers_min": 1},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMinBackgroundCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_background_carriers_min": 2},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxBackgroundCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_background_carriers_max": 1},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxBackgroundCarriers(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"collective_enabled": True, "cohort_background_carriers_max": 0},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 0)


class SvDatabaseFrequencyTest(TestBase):
    """Test for filtration with the frequencies from the SV databases.
    """

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassMaxAffectedCarriersDgv(self):
        # Prepare overlapping DGV entry
        DgvSvs.objects.create(**DGV_SV_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"dgv_max_carriers": 1}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriersDgv(self):
        # Prepare overlapping DGV entry
        DgvSvs.objects.create(**DGV_SV_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"dgv_max_carriers": 0}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxAffectedCarriersDgvGoldStandard(self):
        # Prepare overlapping DGV entry
        DgvGoldStandardSvs.objects.create(**DGV_SV_GS_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"dgv_gs_max_carriers": 1}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriersDgvGoldStandard(self):
        # Prepare overlapping DGV entry
        DgvGoldStandardSvs.objects.create(**DGV_SV_GS_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"dgv_gs_max_carriers": 0}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxAffectedCarriersThousandGenomes(self):
        # Prepare overlapping DGV entry
        ThousandGenomesSv.objects.create(**G1K_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"g1k_max_carriers": 1}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriersThousandGenomes(self):
        # Prepare overlapping DGV entry
        ThousandGenomesSv.objects.create(**G1K_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"g1k_max_carriers": 0}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxAffectedCarriersExacCnv(self):
        # Prepare overlapping DGV entry
        ExacCnv.objects.create(**EXAC_CNV_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"exac_max_carriers": 1}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriersExacCnv(self):
        # Prepare overlapping DGV entry
        ExacCnv.objects.create(**EXAC_CNV_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"exac_max_carriers": 0}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxAffectedCarriersDbVar(self):
        # Prepare overlapping DGV entry
        DbVarSv.objects.create(**DB_VAR_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"dbvar_max_carriers": 1}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriersDbVar(self):
        # Prepare overlapping DGV entry
        DbVarSv.objects.create(**DB_VAR_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"dbvar_max_carriers": 0}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxAffectedCarriersGnomadSv(self):
        # Prepare overlapping DGV entry
        GnomAdSv.objects.create(**GNOMAD_SV_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"gnomad_max_carriers": 1}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxAffectedCarriersGnomadSv(self):
        # Prepare overlapping DGV entry
        GnomAdSv.objects.create(**GNOMAD_SV_DICT)
        # Perform query
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"gnomad_max_carriers": 0}})
        # Check result
        result = list(result)
        self.assertEqual(len(result), 0)


class RegionTest(TestBase):

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassRegionsChr(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {**self.base_cleaned_data, **{"region_whitelist": [("chr7", 155_579_762, 155_628_829)]}}
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassRegionsNoChr(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {**self.base_cleaned_data, **{"region_whitelist": [("7", 155_579_762, 155_628_829)]}}
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailRegions(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {**self.base_cleaned_data, **{"region_whitelist": [("chr1", 55_579_762, 55_628_829)]}}
        )
        result = list(result)
        self.assertEqual(len(result), 0)


class GeneListsTest(TestBase):

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassGeneWhiteList(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"gene_blacklist": ["SHH"]}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailGeneWhiteList(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"gene_blacklist": ["KYNU"]}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testPassGeneBlackList(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"gene_blacklist": ["KYNU"]}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailGeneBlackList(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"gene_blacklist": ["SHH"]}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)


class SvSizeTest(TestBase):

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassMinSize(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"sv_size_min": 10000}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMinSize(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"sv_size_min": 50000}})
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassMaxSize(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"sv_size_max": 50000}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailMaxSize(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"sv_size_max": 10000}})
        result = list(result)
        self.assertEqual(len(result), 0)


class TranscriptCodingTest(TestBase):

    # TODO: no fixture yet for non-coding, thus no test

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testIncludeTranscriptCoding(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"transcripts_coding": True}})
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testExcludeTranscriptCoding(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run({**self.base_cleaned_data, **{"transcripts_coding": False}})
        result = list(result)
        self.assertEqual(len(result), 0)


class VariantEffectTest(TestBase):

    # TODO: no fixture yet for non-coding, thus no test

    debug_sql = False
    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = BASE_CLEANED_DATA_CASE_1

    def testPassVariantEffect(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {
                **self.base_cleaned_data,
                **{"require_transcript_overlap": True, "effects": ["transcript_ablation"]},
            }
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_579_762)
        self.assertEqual(result[0]["end"], 155_628_829)

    def testFailVariantEffect(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {**self.base_cleaned_data, **{"require_transcript_overlap": True, "effects": []}}
        )
        result = list(result)
        self.assertEqual(len(result), 0)

    def testPassNoVariantEffect(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {**self.base_cleaned_data, **{"require_transcript_overlap": False, "effects": []}}
        )
        result = list(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 155_580_774)
        self.assertEqual(result[0]["end"], 155_585_255)

    def testFailNoVariantEffect(self):
        query = SingleCaseFilterQuery(Case.objects.first(), SQLALCHEMY_ENGINE, self.debug_sql)
        result = query.run(
            {**self.base_cleaned_data, **{"require_transcript_overlap": True, "effects": []}}
        )
        result = list(result)
        self.assertEqual(len(result), 0)
