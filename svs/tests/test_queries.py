"""Tests for the complex queries through the ``svs`` module."""

from geneinfo.tests.factories import HgncFactory
from genomicfeatures.tests.factories import (
    EnsemblRegulatoryFeatureFactory,
    GeneIntervalFactory,
    TadSetFactory,
    TadIntervalFactory,
    TadBoundaryIntervalFactory,
    VistaEnhancerFactory,
)
from svdbs.tests.factories import GnomAdSvFactory
from variants.tests.factories import CaseFactory
from .factories import (
    StructuralVariantFactory,
    StructuralVariantGeneAnnotationFactory,
    StructuralVariantSetFactory,
)
from .helpers import QueryTestBase
from ..models import SV_TYPE_CHOICES, SV_SUB_TYPE_CHOICES, StructuralVariant
from ..queries import SingleCaseFilterQuery


class SvsInCaseWithDeNovoGenotypeFilterQueryTest(QueryTestBase):
    """Test for a case with a de novo SV inheritance pattern."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]

    def testQueryAnyGenotype(self):
        results = self.run_query(SingleCaseFilterQuery, {}, 1)
        self.assertEqual(self.svs[0].sv_uuid, results[0].sv_uuid)

    def testQueryDeNovo(self):
        results = self.run_query(
            SingleCaseFilterQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "ref",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
            },
            1,
        )
        self.assertEqual(self.svs[0].sv_uuid, results[0].sv_uuid)

    def testQueryDominant(self):
        self.run_query(
            SingleCaseFilterQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
            },
            0,
        )


class GenotypeQualityFilterQueryTest(QueryTestBase):
    """Test for the quality filter."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]
        self.genotype = self.svs[0].genotype

    def testPassGqFilterFailsGenotypeFilter(self):
        gq = self.genotype.get(self.case.pedigree[1]["patient"])["gq"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_gq_min" % self.case.pedigree[1]["patient"]): gq,
            },
            0,
        )

    def testFailGqFilterPassesGenotypeFilter(self):
        gq = self.genotype.get(self.case.pedigree[1]["patient"])["gq"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_gq_min" % self.case.pedigree[1]["patient"]): gq + 1,
            },
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassSrcFilterFailsGenotypeFilter(self):
        src = self.genotype.get(self.case.pedigree[1]["patient"])["src"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_src_min" % self.case.pedigree[1]["patient"]): src,
            },
            0,
        )

    def testPassSrcFilterPassesGenotypeFilter(self):
        src = self.genotype.get(self.case.pedigree[1]["patient"])["src"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_src_min" % self.case.pedigree[1]["patient"]): src + 1,
            },
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassSrvMinFilterFailsGenotypeFilter(self):
        srv = self.genotype.get(self.case.pedigree[1]["patient"])["srv"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_srv_min" % self.case.pedigree[1]["patient"]): srv,
            },
            0,
        )

    def testFailSrvMinFilterFailsGenotypeFilter2(self):
        srv = self.genotype.get(self.case.pedigree[1]["patient"])["srv"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 but GT is hom. ref. => filtered out
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_srv_min" % self.case.pedigree[1]["patient"]): srv + 1,
            },
            0,
        )

    def testPassSrvMaxFilterFailsGenotypeFilter(self):
        srv = self.genotype.get(self.case.pedigree[1]["patient"])["srv"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for domaxant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_srv_max" % self.case.pedigree[1]["patient"]): srv,
            },
            0,
        )

    def testFailSrvMaxFilterPassesGenotypeFilter(self):
        srv = self.genotype.get(self.case.pedigree[1]["patient"])["srv"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for domaxant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_srv_max" % self.case.pedigree[1]["patient"]): srv - 1,
            },
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassPecMinFilterFailsGenotypeFilter(self):
        pec = self.genotype.get(self.case.pedigree[1]["patient"])["pec"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for domaxant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_pec_min" % self.case.pedigree[1]["patient"]): pec,
            },
            0,
        )

    def testFailPecMinFilterPassesGenotypeFilter(self):
        pec = self.genotype.get(self.case.pedigree[1]["patient"])["pec"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for domaxant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_pec_min" % self.case.pedigree[1]["patient"]): pec + 1,
            },
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassPevMinFilterFailsGenotypeFilter(self):
        pev = self.genotype.get(self.case.pedigree[1]["patient"])["pev"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_pev_min" % self.case.pedigree[1]["patient"]): pev,
            },
            0,
        )

    def testFailPevMinFilterPassesGenotypeFilter(self):
        pev = self.genotype.get(self.case.pedigree[1]["patient"])["pev"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 but GT is hom. ref. => filtered out
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_pev_min" % self.case.pedigree[1]["patient"]): pev + 1,
            },
            0,
        )

    def testPassPevMaxFilterFailsGenotypeFilter(self):
        pev = self.genotype.get(self.case.pedigree[1]["patient"])["pev"]
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for domaxant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_pev_max" % self.case.pedigree[1]["patient"]): pev,
            },
            0,
        )

    def testFailPevMaxFilterPassesGenotypeFilter(self):
        pev = self.genotype.get(self.case.pedigree[1]["patient"])["pev"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for domaxant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_pev_max" % self.case.pedigree[1]["patient"]): pev - 1,
            },
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassCovMinFilterFailsGenotypeFilter(self):
        cov = (
            self.genotype.get(self.case.pedigree[1]["patient"])["pec"]
            + self.genotype.get(self.case.pedigree[1]["patient"])["src"]
        )
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_cov_min" % self.case.pedigree[1]["patient"]): cov,
            },
            0,
        )

    def testFailCovMinFilterPassesGenotypeFilter(self):
        cov = (
            self.genotype.get(self.case.pedigree[1]["patient"])["pec"]
            + self.genotype.get(self.case.pedigree[1]["patient"])["src"]
        )
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_cov_min" % self.case.pedigree[1]["patient"]): cov + 1,
            },
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassVarMinFilterFailsGenotypeFilter(self):
        var = (
            self.genotype.get(self.case.pedigree[1]["patient"])["pev"]
            + self.genotype.get(self.case.pedigree[1]["patient"])["srv"]
        )
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality passes for sample2 => filtered out.
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_var_min" % self.case.pedigree[1]["patient"]): var,
            },
            0,
        )

    def testFailVarMinFilterFailsGenotypeFilter(self):
        var = (
            self.genotype.get(self.case.pedigree[1]["patient"])["pev"]
            + self.genotype.get(self.case.pedigree[1]["patient"])["srv"]
        )
        self.run_query(
            SingleCaseFilterQuery,
            {
                # Query is for dominant variants, pattern in data is de novo.
                "%s_gt" % self.case.pedigree[0]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[1]["patient"]: "variant",
                "%s_gt" % self.case.pedigree[2]["patient"]: "ref",
                # Quality fails for sample2 => passes
                ("%s_fail" % self.case.pedigree[1]["patient"]): "no-call",
                ("%s_var_min" % self.case.pedigree[1]["patient"]): var + 1,
            },
            0,
        )


class SvTypeFilterQueryTest(QueryTestBase):
    """Tests for filtration by ``sv_type`` and ``sv_sub_type`` attributes."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]
        self.genotype = self.svs[0].genotype

    def testQueryVariantTypeMatch(self):
        result = self.run_query(SingleCaseFilterQuery, {"sv_sub_type": []}, 1)
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testQueryVariantTypeNoMatch(self):
        sv_types = [var_type for var_type, _ in SV_TYPE_CHOICES if not var_type.startswith("DEL")]
        self.run_query(SingleCaseFilterQuery, {"sv_type": sv_types, "sv_sub_type": []}, 0)

    def testQueryVariantSubTypeMatch(self):
        result = self.run_query(SingleCaseFilterQuery, {"sv_type": []}, 1)
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testQueryVariantSubTypeNoMatch(self):
        sv_sub_types = [
            var_type for var_type, _ in SV_SUB_TYPE_CHOICES if not var_type.startswith("DEL")
        ]
        self.run_query(SingleCaseFilterQuery, {"sv_type": [], "sv_sub_type": sv_sub_types}, 0)


class SvCohortFrequencyFilterQueryTest(QueryTestBase):
    """Test for filtration with the frequencies within the analysis cohort/collective."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]
        self.genotype = self.svs[0].genotype

    def testPassMinAffectedCarriers(self):
        count = self.svs[0].info["affectedCarriers"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_affected_carriers_min": count},
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMinAffectedCarriers(self):
        count = self.svs[0].info["affectedCarriers"]
        self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_affected_carriers_min": count + 1},
            0,
        )

    def testPassMaxAffectedCarriers(self):
        count = self.svs[0].info["affectedCarriers"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_affected_carriers_max": count},
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMaxAffectedCarriers(self):
        count = self.svs[0].info["affectedCarriers"]
        self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_affected_carriers_max": count - 1},
            0,
        )

    def testPassMinUnaffectedCarriers(self):
        count = self.svs[0].info["unaffectedCarriers"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_unaffected_carriers_min": count},
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMinUnaffectedCarriers(self):
        count = self.svs[0].info["unaffectedCarriers"]
        self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_unaffected_carriers_min": count + 1},
            0,
        )

    def testPassMaxUnaffectedCarriers(self):
        count = self.svs[0].info["unaffectedCarriers"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_unaffected_carriers_max": count},
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMaxUnaffectedCarriers(self):
        count = self.svs[0].info["unaffectedCarriers"]
        self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_unaffected_carriers_max": count - 1},
            0,
        )

    def testPassMinBackgroundCarriers(self):
        count = self.svs[0].info["backgroundCarriers"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_background_carriers_min": count},
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMinBackgroundCarriers(self):
        count = self.svs[0].info["backgroundCarriers"]
        self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_background_carriers_min": count + 1},
            0,
        )

    def testPassMaxBackgroundCarriers(self):
        count = self.svs[0].info["backgroundCarriers"]
        result = self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_background_carriers_max": count},
            1,
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMaxBackgroundCarriers(self):
        count = self.svs[0].info["backgroundCarriers"]
        self.run_query(
            SingleCaseFilterQuery,
            {"collective_enabled": True, "cohort_background_carriers_max": count - 1},
            0,
        )


class SvDatabaseFrequencyFilterQueryTest(QueryTestBase):
    """Test for filtration with database frequencies."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv = StructuralVariantFactory(variant_set=self.variant_set)
        GnomAdSvFactory(
            release=self.sv.release,
            chromosome=self.sv.chromosome,
            start=self.sv.start + (self.sv.end - self.sv.start) * 0.20,
            end=self.sv.end + (self.sv.end - self.sv.start) * 0.20,
        )

    def testPassesFrequencyFilterBelowThreshold(self):
        result = self.run_query(
            SingleCaseFilterQuery,
            {"gnomad_enabled": True, "gnomad_min_overlap": 0.50, "gnomad_max_carriers": 1},
            1,
        )
        self.assertEquals(result[0].sv_uuid, self.sv.sv_uuid)

    def testPassesFrequencyFilterNoOverlap(self):
        result = self.run_query(
            SingleCaseFilterQuery,
            {"gnomad_enabled": True, "gnomad_min_overlap": 0.99, "gnomad_max_carriers": 0},
            1,
        )
        self.assertEquals(result[0].sv_uuid, self.sv.sv_uuid)

    def testFailsFrequencyFilter(self):
        self.run_query(
            SingleCaseFilterQuery,
            {"gnomad_enabled": True, "gnomad_min_overlap": 0.50, "gnomad_max_carriers": 0},
            0,
        )

    def testPassesFrequencyFilterIfDisabled(self):
        result = self.run_query(
            SingleCaseFilterQuery,
            {"gnomad_enabled": False, "gnomad_min_overlap": 0.50, "gnomad_max_carriers": 0},
            1,
        )
        self.assertEquals(result[0].sv_uuid, self.sv.sv_uuid)


class SvDatabaseFrequencyAnnotationTest(QueryTestBase):
    """Test for annotation with database entries."""

    # TODO: tests for other databases as well?

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv = StructuralVariantFactory(variant_set=self.variant_set)
        GnomAdSvFactory(
            release=self.sv.release,
            chromosome=self.sv.chromosome,
            start=self.sv.start + (self.sv.end - self.sv.start) * 0.20,
            end=self.sv.end + (self.sv.end - self.sv.start) * 0.20,
        )

    def testGnomadAnnotationWithOverlap(self):
        result = self.run_query(SingleCaseFilterQuery, {"gnomad_min_overlap": 0.50}, 1)
        self.assertEquals(result[0].sv_uuid, self.sv.sv_uuid)
        self.assertEquals(result[0].gnomad_overlap_count, 1)

    def testGnomadAnnotationWithoutOverlap(self):
        result = self.run_query(SingleCaseFilterQuery, {"gnomad_min_overlap": 0.99}, 1)
        self.assertEquals(result[0].sv_uuid, self.sv.sv_uuid)
        self.assertEquals(result[0].gnomad_overlap_count, 0)


class RegionFilterQueryTest(QueryTestBase):
    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]

    def testPassRegionsChr(self):
        chrom = "chr" + self.svs[0].chromosome.replace("chr", "")
        start = self.svs[0].start
        end = self.svs[0].end
        result = self.run_query(SingleCaseFilterQuery, {"genomic_region": [(chrom, start, end)]}, 1)
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testPassRegionsNoChr(self):
        chrom = self.svs[0].chromosome.replace("chr", "")
        start = self.svs[0].start
        end = self.svs[0].end
        result = self.run_query(SingleCaseFilterQuery, {"genomic_region": [(chrom, start, end)]}, 1)
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailRegions(self):
        chrom = self.svs[0].chromosome
        start = self.svs[0].end + 100
        end = start + 100
        self.run_query(SingleCaseFilterQuery, {"genomic_region": [(chrom, start, end)]}, 0)


class GeneListsFilterQueryTest(QueryTestBase):
    def setUp(self):
        super().setUp()
        self.hgnc = HgncFactory()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]
        StructuralVariantGeneAnnotationFactory(
            ensembl_gene_id=self.hgnc.ensembl_gene_id, sv_uuid=self.svs[0].sv_uuid
        )

    # # TODO FIXME XXX
    # def testPassGeneWhiteList(self):
    #     result = self.run_query(SingleCaseFilterQuery, {"gene_whitelist": [self.hgnc.symbol]}, 1)
    #     result = list(result)
    #     self.assertEqual(len(result), 1)
    #     self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailGeneWhiteList(self):
        self.run_query(SingleCaseFilterQuery, {"gene_whitelist": [self.hgnc.symbol + "XXX"]}, 0)

    def testPassGeneBlackList(self):
        result = self.run_query(
            SingleCaseFilterQuery, {"gene_blacklist": [self.hgnc.symbol + "XXX"]}, 1
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailGeneBlackList(self):
        self.run_query(SingleCaseFilterQuery, {"gene_blacklist": [self.hgnc.symbol]}, 0)


class GeneInIntervalsAnnotationQueryTest(QueryTestBase):
    """Test of annotation of genes in intervals."""

    def setUp(self):
        super().setUp()
        self.tad_set = TadSetFactory()
        self.tad = TadIntervalFactory(tad_set=self.tad_set, start=100_000, end=200_000)
        self.tad_boundaries = (
            TadBoundaryIntervalFactory(
                tad_set=self.tad_set,
                release=self.tad.release,
                chromosome=self.tad.chromosome,
                start=self.tad.start - 10000,
                end=self.tad.start + 10000,
            ),
            TadBoundaryIntervalFactory(
                tad_set=self.tad_set,
                release=self.tad.release,
                chromosome=self.tad.chromosome,
                start=self.tad.end - 10000,
                end=self.tad.end + 10000,
            ),
        )
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [
            StructuralVariantFactory(
                variant_set=self.variant_set,
                release=self.tad.release,
                chromosome=self.tad.chromosome,
                start=self.tad.start + 10000,
                end=self.tad.start + 15000,
            )
        ]

    def testNoTadSet(self):
        result = self.run_query(SingleCaseFilterQuery, {"tad_set_uuid": None}, 1)
        result = list(result)
        self.assertIsNone(getattr(result[0], "itv_shared_gene_ids", None))
        self.assertIsNone(getattr(result[0], "itv_shared_gene_symbols", None))

    def testRefSeqGeneInTad(self):
        gene = GeneIntervalFactory(
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad.start + 20000,
            end=self.tad.start + 25000,
            database="refseq",
        )
        hgnc = HgncFactory(entrez_id=gene.gene_id)
        result = self.run_query(
            SingleCaseFilterQuery, {"database_select": "refseq"}, 1, tad_set=self.tad_set
        )
        result = list(result)
        self.assertEquals([hgnc.entrez_id], result[0].itv_shared_gene_ids)
        self.assertEquals([hgnc.symbol], result[0].itv_shared_gene_symbols)

    def testRefSeqGeneInTad2(self):
        gene = GeneIntervalFactory(
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad.start + 20000,
            end=self.tad.start + 25000,
            database="refseq",
        )
        hgnc = HgncFactory(entrez_id=gene.gene_id)
        result = self.run_query(
            SingleCaseFilterQuery, {"database_select": "refseq"}, 1, tad_set=self.tad_set
        )
        result = list(result)
        self.assertEquals([hgnc.entrez_id], result[0].itv_shared_gene_ids)
        self.assertEquals([hgnc.symbol], result[0].itv_shared_gene_symbols)

    def testEnsemblGeneInTad(self):
        gene = GeneIntervalFactory(
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad.start + 20000,
            end=self.tad.start + 25000,
            database="ensembl",
        )
        hgnc = HgncFactory(ensembl_gene_id=gene.gene_id)
        result = self.run_query(
            SingleCaseFilterQuery, {"database_select": "ensembl"}, 1, tad_set=self.tad_set
        )
        result = list(result)
        self.assertEquals([hgnc.ensembl_gene_id], result[0].itv_shared_gene_ids)
        self.assertEquals([hgnc.symbol], result[0].itv_shared_gene_symbols)

    def testEnsemblGeneInTad2(self):
        gene = GeneIntervalFactory(
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad.start + 20000,
            end=self.tad.start + 25000,
            database="ensembl",
        )
        hgnc = HgncFactory(ensembl_gene_id=gene.gene_id)
        result = self.run_query(
            SingleCaseFilterQuery, {"database_select": "ensembl"}, 1, tad_set=self.tad_set
        )
        result = list(result)
        self.assertEquals([hgnc.ensembl_gene_id], result[0].itv_shared_gene_ids)
        self.assertEquals([hgnc.symbol], result[0].itv_shared_gene_symbols)

    def testNoGeneInTad(self):
        GeneIntervalFactory(
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad.end + 20000,
            end=self.tad.end + 25000,
        )
        result = self.run_query(SingleCaseFilterQuery, {}, 1, tad_set=self.tad_set)
        result = list(result)
        self.assertEquals(None, result[0].itv_shared_gene_ids)
        self.assertEquals(None, result[0].itv_shared_gene_symbols)


class DistanceToTadBoundaryAnnotationQueryTest(QueryTestBase):
    """Test annotation with distance to TAD boundary."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.tad_set = TadSetFactory()
        self.tad = TadIntervalFactory(tad_set=self.tad_set, start=100_000, end=200_000)
        self.tad_boundaries = (
            TadBoundaryIntervalFactory(
                tad_set=self.tad_set,
                release=self.tad.release,
                chromosome=self.tad.chromosome,
                start=self.tad.start - 10000,
                end=self.tad.start + 10000,
            ),
            TadBoundaryIntervalFactory(
                tad_set=self.tad_set,
                release=self.tad.release,
                chromosome=self.tad.chromosome,
                start=self.tad.end - 10000,
                end=self.tad.end + 10000,
            ),
        )

    def testFarAway(self):
        StructuralVariantFactory(
            variant_set=self.variant_set,
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad_boundaries[0].start - 20000,
            end=self.tad_boundaries[0].start - 20000 + 10,
        )
        result = self.run_query(SingleCaseFilterQuery, {}, 1, tad_set=self.tad_set)
        result = list(result)
        self.assertEqual(-1, result[0].distance_to_center)

    def testOverlapping(self):
        StructuralVariantFactory(
            variant_set=self.variant_set,
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad_boundaries[0].start,
            end=self.tad_boundaries[0].start + 5000,
        )
        result = self.run_query(SingleCaseFilterQuery, {}, 1, tad_set=self.tad_set)
        result = list(result)
        self.assertEqual(5000, result[0].distance_to_center)

    def testOnBoundary(self):
        StructuralVariantFactory(
            variant_set=self.variant_set,
            release=self.tad.release,
            chromosome=self.tad.chromosome,
            start=self.tad_boundaries[0].start + 5000,
            end=self.tad_boundaries[0].start + 15000,
        )
        result = self.run_query(SingleCaseFilterQuery, {}, 1, tad_set=self.tad_set)
        result = list(result)
        self.assertEqual(0, result[0].distance_to_center)


class SvSizeFilterQueryTest(QueryTestBase):
    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]

    def testPassMinSize(self):
        result = self.run_query(
            SingleCaseFilterQuery, {"sv_size_min": self.svs[0].end - self.svs[0].start - 2}, 1
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMinSize(self):
        self.run_query(
            SingleCaseFilterQuery, {"sv_size_min": self.svs[0].end - self.svs[0].start + 2}, 0
        )

    def testPassMaxSize(self):
        result = self.run_query(
            SingleCaseFilterQuery, {"sv_size_max": self.svs[0].end - self.svs[0].start + 2}, 1
        )
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailMaxSize(self):
        self.run_query(
            SingleCaseFilterQuery, {"sv_size_max": self.svs[0].end - self.svs[0].start - 2}, 0
        )


class BndSizeFilterQueryTest(QueryTestBase):
    """BNDs have to be handled special for size limits."""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [
            StructuralVariantFactory(
                variant_set=self.variant_set, sv_type="BND", sv_sub_type="BND", start=1000, end=1000
            )
        ]

    def testPassAnyMinSize(self):
        self.run_query(SingleCaseFilterQuery, {"sv_size_min": -1}, 1)
        self.run_query(SingleCaseFilterQuery, {"sv_size_min": 0}, 1)
        result = self.run_query(SingleCaseFilterQuery, {"sv_size_min": 1}, 1)
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailAnyMaxSize(self):
        self.run_query(SingleCaseFilterQuery, {"sv_size_max": -1}, 0)
        self.run_query(SingleCaseFilterQuery, {"sv_size_max": 0}, 0)
        self.run_query(SingleCaseFilterQuery, {"sv_size_max": 10_000_000}, 0)


class SvTranscriptCodingFilterQueryTest(QueryTestBase):
    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.svs = [StructuralVariantFactory(variant_set=self.variant_set)]
        StructuralVariantGeneAnnotationFactory(
            sv_uuid=self.svs[0].sv_uuid,
            refseq_transcript_coding=True,
            ensembl_transcript_coding=True,
        )

    def testIncludeTranscriptCoding(self):
        result = self.run_query(SingleCaseFilterQuery, {"transcripts_coding": True}, 1)
        result = list(result)
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testExcludeTranscriptCoding(self):
        self.run_query(SingleCaseFilterQuery, {"transcripts_coding": False}, 0)


class _VariantEffectTestBase(QueryTestBase):

    #: The selected database.
    database_select = None

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv_annos = [
            StructuralVariantGeneAnnotationFactory(
                sv__variant_set=self.variant_set,
                refseq_transcript_coding=True,
                refseq_effect=["transcript_ablation", "coding_transcript_variant"],
                ensembl_transcript_coding=True,
                ensembl_effect=["transcript_ablation", "coding_transcript_variant"],
            )
        ]
        self.svs = [
            StructuralVariant.objects.get(sv_uuid=self.sv_annos[0].sv_uuid),
            StructuralVariantFactory(variant_set=self.variant_set),
        ]

    def testPassVariantEffect(self):
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                "database_select": self.database_select,
                "require_transcript_overlap": True,
                "effects": ["transcript_ablation"],
            },
            1,
        )
        self.assertEqual(self.svs[0].sv_uuid, result[0]["sv_uuid"])

    def testFailVariantEffect(self):
        self.run_query(
            SingleCaseFilterQuery,
            {
                "database_select": self.database_select,
                "require_transcript_overlap": True,
                "effects": [],
            },
            0,
        )

    def testPassNoVariantEffect(self):
        result = self.run_query(
            SingleCaseFilterQuery,
            {
                "database_select": self.database_select,
                "require_transcript_overlap": False,
                "effects": [],
            },
            1,
        )
        self.assertEqual(self.svs[1].sv_uuid, result[0]["sv_uuid"])

    def testFailNoVariantEffect(self):
        self.run_query(
            SingleCaseFilterQuery,
            {
                "database_select": self.database_select,
                "require_transcript_overlap": True,
                "effects": [],
            },
            0,
        )


class RefSeqVariantEffectFilterQueryTest(QueryTestBase):
    database_select = "refseq"


class EnsemblVariantEffectFilterQueryTest(QueryTestBase):
    database_select = "ensembl"


class EnsemblRegulatoryOverlapFilterQueryTest(QueryTestBase):
    """Test filtration query result with ENSEMBL regulatory regions"""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv = StructuralVariantFactory(variant_set=self.variant_set)
        self.region = EnsemblRegulatoryFeatureFactory(
            release=self.sv.release,
            chromosome=self.sv.chromosome,
            start=self.sv.start,
            end=self.sv.start + 10,
        )

    def testAnyFeaturePasses(self):
        result = self.run_query(SingleCaseFilterQuery, {"regulatory_ensembl": ["any_feature"]}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])

    def testEnhancerPasses(self):
        result = self.run_query(SingleCaseFilterQuery, {"regulatory_ensembl": ["enhancer"]}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])

    def testOpenChromatinRegionFails(self):
        self.run_query(SingleCaseFilterQuery, {"regulatory_ensembl": ["open_chromatin_region"]}, 0)

    def testAnyFeatureNoOverlapFails(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        self.run_query(SingleCaseFilterQuery, {"regulatory_ensembl": ["any_feature"]}, 0)

    def testEnhancerNoOverlapFails(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        self.run_query(SingleCaseFilterQuery, {"regulatory_ensembl": ["enhancer"]}, 0)

    def testNoOverlapPasses(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        result = self.run_query(SingleCaseFilterQuery, {"regulatory_ensembl": []}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])


class EnsemblRegulatoryOverlapAnnotationQueryTest(QueryTestBase):
    """Test annotation of query result with ENSEMBL regulatory regions"""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv = StructuralVariantFactory(variant_set=self.variant_set)
        self.region = EnsemblRegulatoryFeatureFactory(
            release=self.sv.release,
            chromosome=self.sv.chromosome,
            start=self.sv.start,
            end=self.sv.start + 10,
        )

    def testOverlap(self):
        result = self.run_query(SingleCaseFilterQuery, {}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(0, result[0].ensembl_CTCF_binding_site_count)
        self.assertEqual(1, result[0].ensembl_enhancer_count)
        self.assertEqual(0, result[0].ensembl_open_chromatin_region_count)
        self.assertEqual(0, result[0].ensembl_promoter_count)
        self.assertEqual(0, result[0].ensembl_promoter_flanking_region_count)
        self.assertEqual(0, result[0].ensembl_TF_binding_site_count)
        self.assertEqual(0, result[0].ensembl_CTCF_binding_site_count)
        self.assertEqual(0, result[0].ensembl_CTCF_binding_site_count)

    def testNoOverlap(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        result = self.run_query(SingleCaseFilterQuery, {}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(0, result[0].ensembl_CTCF_binding_site_count)
        self.assertEqual(0, result[0].ensembl_enhancer_count)
        self.assertEqual(0, result[0].ensembl_open_chromatin_region_count)
        self.assertEqual(0, result[0].ensembl_promoter_count)
        self.assertEqual(0, result[0].ensembl_promoter_flanking_region_count)
        self.assertEqual(0, result[0].ensembl_TF_binding_site_count)
        self.assertEqual(0, result[0].ensembl_CTCF_binding_site_count)
        self.assertEqual(0, result[0].ensembl_CTCF_binding_site_count)


class VistaOverlapFilterQueryTest(QueryTestBase):
    """Test filtration query result with Vista regions"""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv = StructuralVariantFactory(variant_set=self.variant_set)
        self.region = VistaEnhancerFactory(
            release=self.sv.release,
            chromosome=self.sv.chromosome,
            start=self.sv.start,
            end=self.sv.start + 10,
        )

    def testOverlapPositivePasses(self):
        self.region.validation_result = "positive"
        self.region.save()
        result = self.run_query(SingleCaseFilterQuery, {"regulatory_vista": ["positive"]}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(1, result[0].vista_positive_count)
        self.assertEqual(0, result[0].vista_negative_count)

    def testOverlapPositiveFails(self):
        self.region.validation_result = "negative"
        self.region.save()
        self.run_query(SingleCaseFilterQuery, {"regulatory_vista": ["positive"]}, 0)

    def testOverlapAnyValidationPasses(self):
        self.region.validation_result = "negative"
        self.region.save()
        result = self.run_query(SingleCaseFilterQuery, {"regulatory_vista": ["any_validation"]}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(0, result[0].vista_positive_count)
        self.assertEqual(1, result[0].vista_negative_count)

    def testNoOverlapPasses(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        result = self.run_query(SingleCaseFilterQuery, {"regulatory_vista": []}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(0, result[0].vista_positive_count)
        self.assertEqual(0, result[0].vista_negative_count)

    def testNoOverlapFails(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        self.run_query(SingleCaseFilterQuery, {"regulatory_vista": ["any_validation"]}, 0)


class VistaOverlapAnnotationQueryTest(QueryTestBase):
    """Test annotation of query result with Vista regions"""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.case = self.variant_set.case
        self.sv = StructuralVariantFactory(variant_set=self.variant_set)
        self.region = VistaEnhancerFactory(
            release=self.sv.release,
            chromosome=self.sv.chromosome,
            start=self.sv.start,
            end=self.sv.start + 10,
        )

    def testOverlap(self):
        result = self.run_query(SingleCaseFilterQuery, {}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(1, result[0].vista_positive_count)
        self.assertEqual(0, result[0].vista_negative_count)

    def testNoOverlap(self):
        self.region.start = self.sv.end + 10
        self.region.end = self.region.start + 20
        self.region.save()
        result = self.run_query(SingleCaseFilterQuery, {}, 1)
        self.assertEqual(self.sv.sv_uuid, result[0]["sv_uuid"])
        self.assertEqual(0, result[0].vista_positive_count)
        self.assertEqual(0, result[0].vista_negative_count)
