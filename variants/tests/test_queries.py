"""Tests for the ``models_support`` module.

Remarks:

- VCF export is only tested for case one at the moment, as it shares a major part of the implementation with
  the render and tabular file export query.
"""

from clinvar.tests.factories import ClinvarFactory
from conservation.tests.factories import KnownGeneAAFactory
from hgmd.tests.factories import HgmdPublicLocusFactory
from variants.models import Case, ProjectCasesSmallVariantQuery
from variants.queries import (
    CasePrefetchQuery,
    CaseExportTableQuery,
    CaseExportVcfQuery,
    CaseLoadPrefetchedQuery,
    ClinvarReportPrefetchQuery,
    ClinvarReportLoadPrefetchedQuery,
    ProjectPrefetchQuery,
    ProjectLoadPrefetchedQuery,
    KnownGeneAAQuery,
)
from geneinfo.tests.factories import (
    HgncFactory,
    AcmgFactory,
    GeneIdToInheritanceFactory,
    GnomadConstraintsFactory,
    ExacConstraintsFactory,
)
from dbsnp.tests.factories import DbsnpFactory
from .factories import (
    SmallVariantFactory,
    SmallVariantSummaryFactory,
    ProjectFactory,
    ProjectCasesSmallVariantQueryFactory,
    SmallVariantQueryFactory,
    ClinvarQueryFactory,
    SmallVariantSetFactory,
)
from .helpers import TestBase, SupportQueryTestBase, SQLALCHEMY_ENGINE


# TODO: select correct cases from multiple ones
# TODO: prefetch from multiple cases


class TestCaseOneLoadSingletonResults(SupportQueryTestBase):
    def setUp(self):
        """Create a case and 3 variants, first one is linked to ACMG and has effect ambiguity.
        As we check the content of the results, make sure they are on the same chromosome to
        avoid ordering issues when we hit the change from chromosome Y to 1."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        case = variant_set.case
        self.acmg = AcmgFactory(entrez_id="1000")
        small_vars = [
            SmallVariantFactory(
                chromosome="1",
                ensembl_effect=["synonymous_variant"],
                refseq_effect=["stop_gained"],
                refseq_gene_id=self.acmg.entrez_id,
                variant_set=variant_set,
            ),
            SmallVariantFactory(chromosome="1", variant_set=variant_set),
            SmallVariantFactory(chromosome="1", variant_set=variant_set),
        ]
        # Prepare mode of inheritance
        self.modes_of_inheritance = [
            GeneIdToInheritanceFactory(
                ensembl_gene_id=small_vars[0].ensembl_gene_id,
                entrez_id=small_vars[0].refseq_gene_id,
                mode_of_inheritance="AD",
            ),
            GeneIdToInheritanceFactory(
                ensembl_gene_id=small_vars[0].ensembl_gene_id,
                entrez_id=small_vars[0].refseq_gene_id,
                mode_of_inheritance="AR",
            ),
        ]
        # Prepare constraints
        self.gnomad_constraints = GnomadConstraintsFactory(
            ensembl_gene_id=small_vars[0].ensembl_gene_id
        )
        self.exac_constraints = ExacConstraintsFactory(
            ensembl_transcript_id=small_vars[0].ensembl_transcript_id
        )
        # Prepare smallvariant query results
        self.smallvariantquery = SmallVariantQueryFactory(case=case)
        self.smallvariantquery.query_results.add(small_vars[0].id, small_vars[1].id)
        # Prepare projectcases smallvariant query results
        self.projectcasessmallvariantquery = ProjectCasesSmallVariantQueryFactory(
            project=case.project
        )
        self.projectcasessmallvariantquery.query_results.add(small_vars[0].id, small_vars[2].id)

    def test_load_prefetched_case_results(self):
        self.smallvariantquery.save()
        results = self.run_query(
            CaseLoadPrefetchedQuery, {"filter_job_id": self.smallvariantquery.id}, 2
        )
        self.assertEqual(results[0].acmg_symbol, self.acmg.symbol)
        self.assertIsNone(results[1].acmg_symbol)
        self.assertTrue(results[0].effect_ambiguity)
        self.assertFalse(results[1].effect_ambiguity)
        self.assertEqual(
            results[0].modes_of_inheritance,
            [
                self.modes_of_inheritance[0].mode_of_inheritance,
                self.modes_of_inheritance[1].mode_of_inheritance,
            ],
        )
        self.assertEqual(results[0].gnomad_pLI, self.gnomad_constraints.pLI)
        self.assertEqual(results[0].exac_pLI, self.exac_constraints.pLI)

    def test_load_prefetched_project_cases_results(self):
        results = self.run_query(
            ProjectLoadPrefetchedQuery,
            {"filter_job_id": self.projectcasessmallvariantquery.id},
            2,
            query_type="project",
        )
        self.assertEqual(results[0].acmg_symbol, self.acmg.symbol)
        self.assertIsNone(results[1].acmg_symbol)
        self.assertTrue(results[0].effect_ambiguity)
        self.assertFalse(results[1].effect_ambiguity)


class TestCaseOneQueryDatabaseSwitch(SupportQueryTestBase):
    """Test whether both RefSeq and ENSEMBL databases work."""

    def setUp(self):
        """Create a case with just one variant and HGNC record."""
        super().setUp()
        small_var = SmallVariantFactory()
        self.hgnc = HgncFactory(
            entrez_id=small_var.refseq_gene_id, ensembl_gene_id=small_var.ensembl_gene_id
        )

    def test_base_query_refseq_filter(self):
        self.run_query(CasePrefetchQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_export(self):
        self.run_query(CaseExportTableQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_vcf(self):
        self.run_query(CaseExportVcfQuery, {"database_select": "refseq"}, 1)

    def test_base_query_ensembl_filter(self):
        self.run_query(CasePrefetchQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_ensembl_export(self):
        self.run_query(CaseExportTableQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_ensembl_vcf(self):
        self.run_query(CaseExportVcfQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_refseq_check_gene_symbol(self):
        results = self.run_query(CasePrefetchQuery, {"database_select": "refseq"}, 1)
        self.assertEqual(results[0].symbol, self.hgnc.symbol)

    def test_base_query_ensembl_check_gene_symbol(self):
        results = self.run_query(CasePrefetchQuery, {"database_select": "ensembl"}, 1)
        self.assertEqual(results[0].symbol, self.hgnc.symbol)


class TestCaseOneQueryNotInDbsnp(SupportQueryTestBase):
    """Test whether both RefSeq and ENSEMBL databases work."""

    def setUp(self):
        """Create 3 variants and two dbSNP entries."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        small_vars = SmallVariantFactory.create_batch(3, variant_set=variant_set)
        DbsnpFactory(
            release=small_vars[0].release,
            chromosome=small_vars[0].chromosome,
            start=small_vars[0].start,
            end=small_vars[0].end,
            bin=small_vars[0].bin,
            reference=small_vars[0].reference,
            alternative=small_vars[0].alternative,
        )
        DbsnpFactory(
            release=small_vars[2].release,
            chromosome=small_vars[2].chromosome,
            start=small_vars[2].start,
            end=small_vars[2].end,
            bin=small_vars[2].bin,
            reference=small_vars[2].reference,
            alternative=small_vars[2].alternative,
        )

    def test_base_query_not_in_dbsnp_filter(self):
        self.run_query(CasePrefetchQuery, {"remove_if_in_dbsnp": True}, 1)

    def test_base_query_not_in_dbsnp_export(self):
        self.run_query(CaseExportTableQuery, {"remove_if_in_dbsnp": True}, 1)

    def test_base_query_not_in_dbsnp_vcf(self):
        self.run_query(CaseExportVcfQuery, {"remove_if_in_dbsnp": True}, 1)

    def test_base_query_filter(self):
        self.run_query(CasePrefetchQuery, {}, 3)

    def test_base_query_export(self):
        self.run_query(CaseExportTableQuery, {}, 3)

    def test_base_query_vcf(self):
        self.run_query(CaseExportVcfQuery, {}, 3)


class TestCaseOneQueryCase(SupportQueryTestBase):
    """Test with correct and incorrect case UUID"""

    def setUp(self):
        """Create case with just one variant."""
        super().setUp()
        SmallVariantFactory()

    def test_query_case_correct_filter(self):
        self.run_query(CasePrefetchQuery, {}, 1)

    def test_query_case_correct_export(self):
        self.run_query(CaseExportTableQuery, {}, 1)

    def test_query_case_correct_vcf(self):
        self.run_query(CaseExportVcfQuery, {}, 1)

    def test_query_case_incorrect_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )

    def test_query_case_incorrect_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )

    def test_query_case_incorrect_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )


class TestCaseOneQueryCaseFromTwoCases(SupportQueryTestBase):
    """Test with correct and incorrect case UUID"""

    def setUp(self):
        """Create case with just one variant."""
        super().setUp()
        self.variant_sets = SmallVariantSetFactory.create_batch(2)
        SmallVariantFactory(variant_set=self.variant_sets[0])
        SmallVariantFactory(variant_set=self.variant_sets[1])
        SmallVariantFactory(variant_set=self.variant_sets[1])

    def test_query_case1_correct_filter(self):
        self.run_query(CasePrefetchQuery, {"case_uuid": self.variant_sets[0].case.sodar_uuid}, 1)

    def test_query_case1_correct_export(self):
        self.run_query(CaseExportTableQuery, {"case_uuid": self.variant_sets[0].case.sodar_uuid}, 1)

    def test_query_case1_correct_vcf(self):
        self.run_query(CaseExportVcfQuery, {"case_uuid": self.variant_sets[0].case.sodar_uuid}, 1)

    def test_query_case2_correct_filter(self):
        self.run_query(CasePrefetchQuery, {"case_uuid": self.variant_sets[1].case.sodar_uuid}, 2)

    def test_query_case2_correct_export(self):
        self.run_query(CaseExportTableQuery, {"case_uuid": self.variant_sets[1].case.sodar_uuid}, 2)

    def test_query_case2_correct_vcf(self):
        self.run_query(CaseExportVcfQuery, {"case_uuid": self.variant_sets[1].case.sodar_uuid}, 2)


class TestCaseOneClinvarReportQueryCaseFromTwoCases(SupportQueryTestBase):
    """Test with correct and incorrect case UUID"""

    def setUp(self):
        """Create case with just one variant."""
        super().setUp()
        self.variant_sets = SmallVariantSetFactory.create_batch(2)
        small_vars = [
            SmallVariantFactory(variant_set=self.variant_sets[0], in_clinvar=True),
            SmallVariantFactory(variant_set=self.variant_sets[1], in_clinvar=True),
            SmallVariantFactory(variant_set=self.variant_sets[1], in_clinvar=True),
        ]
        for small_var in small_vars:
            ClinvarFactory(
                release=small_var.release,
                chromosome=small_var.chromosome,
                start=small_var.start,
                end=small_var.end,
                bin=small_var.bin,
                reference=small_var.reference,
                alternative=small_var.alternative,
            )

    def test_query_case1_correct_filter(self):
        self.run_query(
            ClinvarReportPrefetchQuery, {"case_uuid": self.variant_sets[0].case.sodar_uuid}, 1
        )

    def test_query_case2_correct_filter(self):
        self.run_query(
            ClinvarReportPrefetchQuery, {"case_uuid": self.variant_sets[1].case.sodar_uuid}, 2
        )


class TestCaseOneQueryVarTypeSwitch(SupportQueryTestBase):
    """Test switch for variant type (SNV, MNV, InDel)"""

    def setUp(self):
        """Create one case with 3 variants of different var_type."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        SmallVariantFactory(var_type="snv", variant_set=variant_set)
        SmallVariantFactory(var_type="mnv", variant_set=variant_set)
        SmallVariantFactory(var_type="indel", variant_set=variant_set)

    def test_var_type_none_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_none_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_none_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_mnv_filter(self):
        self.run_query(CasePrefetchQuery, {"var_type_snv": False, "var_type_indel": False}, 1)

    def test_var_type_mnv_export(self):
        self.run_query(CaseExportTableQuery, {"var_type_snv": False, "var_type_indel": False}, 1)

    def test_var_type_mnv_vcf(self):
        self.run_query(CaseExportVcfQuery, {"var_type_snv": False, "var_type_indel": False}, 1)

    def test_var_type_snv_filter(self):
        self.run_query(CasePrefetchQuery, {"var_type_mnv": False, "var_type_indel": False}, 1)

    def test_var_type_snv_export(self):
        self.run_query(CaseExportTableQuery, {"var_type_mnv": False, "var_type_indel": False}, 1)

    def test_var_type_snv_vcf(self):
        self.run_query(CaseExportVcfQuery, {"var_type_mnv": False, "var_type_indel": False}, 1)

    def test_var_type_indel_filter(self):
        self.run_query(CasePrefetchQuery, {"var_type_snv": False, "var_type_mnv": False}, 1)

    def test_var_type_indel_export(self):
        self.run_query(CaseExportTableQuery, {"var_type_snv": False, "var_type_mnv": False}, 1)

    def test_var_type_indel_vcf(self):
        self.run_query(CaseExportVcfQuery, {"var_type_snv": False, "var_type_mnv": False}, 1)

    def test_var_type_all_filter(self):
        self.run_query(CasePrefetchQuery, {}, 3)

    def test_var_type_all_export(self):
        self.run_query(CaseExportTableQuery, {}, 3)

    def test_var_type_all_vcf(self):
        self.run_query(CaseExportVcfQuery, {}, 3)


class TestCaseOneQueryFrequency(SupportQueryTestBase):
    """Test switch for all four frequency filters + frequency limits + homozygous limits

    Each limit is tested for lower, critical and higher values. The data is designed
    to cover this with one test function rather than having three test functions for this
    setting. 'None' is tested within the switch or the other function. This is the value
    when no value in the interface was entered.

    tested databases:
    - gnomad exomes, gnomad genomes, exac, thousand genomes
    """

    def setUp(self):
        """Create a case and 3 variants with different frequencies and count values and
        a corresponding variantsummary entry.
        """
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        for i in range(3):
            # this emulates 0.001, 0.01 and 0.1 frequency
            freq = 1 / 10 ** (3 - i)
            # this emulates increasing count starting from 1
            count = i + 1
            small_var = SmallVariantFactory(
                gnomad_genomes_frequency=freq,
                gnomad_genomes_heterozygous=count,
                gnomad_genomes_homozygous=count,
                gnomad_exomes_frequency=freq,
                gnomad_exomes_heterozygous=count,
                gnomad_exomes_homozygous=count,
                exac_frequency=freq,
                exac_heterozygous=count,
                exac_homozygous=count,
                thousand_genomes_frequency=freq,
                thousand_genomes_heterozygous=count,
                thousand_genomes_homozygous=count,
                variant_set=self.variant_set,
            )
            SmallVariantSummaryFactory(
                chromosome=small_var.chromosome,
                start=small_var.start,
                end=small_var.end,
                bin=small_var.bin,
                reference=small_var.reference,
                alternative=small_var.alternative,
                count_het=count,
                count_hom_alt=count,
            )

    def _setup_additional_variant_with_missing_inhouse_record(self):
        # Setup an additional variant and make sure it passes the default filter settings.
        freq = 1 / 10 ** 3  # 0.001
        count = 1
        SmallVariantFactory(
            gnomad_genomes_frequency=freq,
            gnomad_genomes_heterozygous=count,
            gnomad_genomes_homozygous=count,
            gnomad_exomes_frequency=freq,
            gnomad_exomes_heterozygous=count,
            gnomad_exomes_homozygous=count,
            exac_frequency=freq,
            exac_heterozygous=count,
            exac_homozygous=count,
            thousand_genomes_frequency=freq,
            thousand_genomes_heterozygous=count,
            thousand_genomes_homozygous=count,
            variant_set=self.variant_set,
        )

    def test_frequency_filters_disabled_filter(self):
        self.run_query(CasePrefetchQuery, {}, 3)

    def test_frequency_filters_disabled_export(self):
        self.run_query(CaseExportTableQuery, {}, 3)

    def test_frequency_filters_disabled_vcf(self):
        self.run_query(CaseExportVcfQuery, {}, 3)

    def test_frequency_thousand_genomes_enabled_filter(self):
        self.run_query(CasePrefetchQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_export(self):
        self.run_query(CaseExportTableQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_vcf(self):
        self.run_query(CaseExportVcfQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_exac_enabled_filter(self):
        self.run_query(CasePrefetchQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_export(self):
        self.run_query(CaseExportTableQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_vcf(self):
        self.run_query(CaseExportVcfQuery, {"exac_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_filter(self):
        self.run_query(CasePrefetchQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_export(self):
        self.run_query(CaseExportTableQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_vcf(self):
        self.run_query(CaseExportVcfQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_filter(self):
        self.run_query(CasePrefetchQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_export(self):
        self.run_query(CaseExportTableQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_vcf(self):
        self.run_query(CaseExportVcfQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_inhouse_enabled_filter(self):
        self.run_query(CasePrefetchQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_inhouse_enabled_export(self):
        self.run_query(CaseExportTableQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_inhouse_enabled_vcf(self):
        self.run_query(CaseExportVcfQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_thousand_genomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_thousand_genomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_thousand_genomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    # NB: we use carriers instead of carriers for in-house DB

    def test_carriers_inhouse_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_carriers_inhouse_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_carriers_inhouse_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_carriers_inhouse_limits_filter_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CasePrefetchQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            3,
        )

    def test_carriers_inhouse_limits_export_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CaseExportTableQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            3,
        )

    def test_carriers_inhouse_limits_vcf_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CaseExportVcfQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            3,
        )

    def test_homozygous_thousand_genomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_filter_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CasePrefetchQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            3,
        )

    def test_homozygous_inhouse_limits_export_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CaseExportTableQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            3,
        )

    def test_homozygous_inhouse_limits_vcf_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CaseExportVcfQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            3,
        )

    def test_heterozygous_thousand_genomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_filter_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CasePrefetchQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            3,
        )

    def test_heterozygous_inhouse_limits_export_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CaseExportTableQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            3,
        )

    def test_heterozygous_inhouse_limits_vcf_missing_inhouse_record(self):
        self._setup_additional_variant_with_missing_inhouse_record()
        self.run_query(
            CaseExportVcfQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            3,
        )


class TestCaseOneQueryEffects(SupportQueryTestBase):
    """Test effects settings (just an excerpt. everything else would be madness."""

    def setUp(self):
        """Create one case and 3 variants with different variant effects for refseq transcripts."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        case = variant_set.case
        SmallVariantFactory(
            refseq_effect=["missense_variant", "stop_lost"], variant_set=variant_set
        )
        SmallVariantFactory(
            refseq_effect=["missense_variant", "frameshift_variant"], variant_set=variant_set
        )
        SmallVariantFactory(refseq_effect=["frameshift_variant"], variant_set=variant_set)

    def test_effects_none_filter(self):
        self.run_query(CasePrefetchQuery, {"effects": []}, 0)

    def test_effects_none_export(self):
        self.run_query(CaseExportTableQuery, {"effects": []}, 0)

    def test_effects_none_vcf(self):
        self.run_query(CaseExportVcfQuery, {"effects": []}, 0)

    def test_effects_one_filter(self):
        self.run_query(CasePrefetchQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_export(self):
        self.run_query(CaseExportTableQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_vcf(self):
        self.run_query(CaseExportVcfQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_two_filter(self):
        self.run_query(CasePrefetchQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3)

    def test_effects_two_export(self):
        self.run_query(CaseExportTableQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3)

    def test_effects_two_vcf(self):
        self.run_query(CaseExportVcfQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3)

    def test_effects_all_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )

    def test_effects_all_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )

    def test_effects_all_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )


class TestCaseOneQueryTranscriptCoding(SupportQueryTestBase):
    def setUp(self):
        super().setUp()
        variant_set = SmallVariantSetFactory()
        case = variant_set.case
        SmallVariantFactory(
            refseq_transcript_coding=False, ensembl_transcript_coding=False, variant_set=variant_set
        )
        SmallVariantFactory(
            refseq_transcript_coding=True, ensembl_transcript_coding=True, variant_set=variant_set
        )

    def test_transcript_empty_refseq_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": False,
                "transcripts_noncoding": False,
            },
            0,
        )

    def test_transcript_empty_refseq_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": False,
                "transcripts_noncoding": False,
            },
            0,
        )

    def test_transcript_empty_refseq_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": False,
                "transcripts_noncoding": False,
            },
            0,
        )

    def test_transcript_empty_ensembl_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": False,
                "transcripts_noncoding": False,
            },
            0,
        )

    def test_transcript_empty_ensembl_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": False,
                "transcripts_noncoding": False,
            },
            0,
        )

    def test_transcript_empty_ensembl_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": False,
                "transcripts_noncoding": False,
            },
            0,
        )

    def test_transcript_coding_refseq_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": True,
                "transcripts_noncoding": False,
            },
            1,
        )

    def test_transcript_coding_refseq_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": True,
                "transcripts_noncoding": False,
            },
            1,
        )

    def test_transcript_coding_refseq_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": True,
                "transcripts_noncoding": False,
            },
            1,
        )

    def test_transcript_coding_ensembl_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": True,
                "transcripts_noncoding": False,
            },
            1,
        )

    def test_transcript_coding_ensembl_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": True,
                "transcripts_noncoding": False,
            },
            1,
        )

    def test_transcript_coding_ensembl_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": True,
                "transcripts_noncoding": False,
            },
            1,
        )

    def test_transcript_noncoding_refseq_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": False,
                "transcripts_noncoding": True,
            },
            1,
        )

    def test_transcript_noncoding_refseq_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": False,
                "transcripts_noncoding": True,
            },
            1,
        )

    def test_transcript_noncoding_refseq_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": False,
                "transcripts_noncoding": True,
            },
            1,
        )

    def test_transcript_noncoding_ensembl_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": False,
                "transcripts_noncoding": True,
            },
            1,
        )

    def test_transcript_noncoding_ensembl_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": False,
                "transcripts_noncoding": True,
            },
            1,
        )

    def test_transcript_noncoding_ensembl_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": False,
                "transcripts_noncoding": True,
            },
            1,
        )

    def test_transcript_coding_and_noncoding_refseq_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": True,
                "transcripts_noncoding": True,
            },
            2,
        )

    def test_transcript_coding_and_noncoding_refseq_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": True,
                "transcripts_noncoding": True,
            },
            2,
        )

    def test_transcript_coding_and_noncoding_refseq_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "refseq",
                "transcripts_coding": True,
                "transcripts_noncoding": True,
            },
            2,
        )

    def test_transcript_coding_and_noncoding_ensembl_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": True,
                "transcripts_noncoding": True,
            },
            2,
        )

    def test_transcript_coding_and_noncoding_ensembl_export_table(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": True,
                "transcripts_noncoding": True,
            },
            2,
        )

    def test_transcript_coding_and_noncoding_ensembl_export_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "database_select": "ensembl",
                "transcripts_coding": True,
                "transcripts_noncoding": True,
            },
            2,
        )


class TestCaseOneQueryGenotype(SupportQueryTestBase):
    """Test effects settings (just an excerpt. everything else would be madness."""

    def setUp(self):
        """Create case and 9 variants with different variant quality and genotype settings."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        case = variant_set.case
        self.patient = case.index
        SmallVariantFactory(
            genotype={self.patient: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 0, "dp": 30, "gq": 99, "gt": "0/0"}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 30, "dp": 30, "gq": 99, "gt": "1/1"}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 0, "dp": 10, "gq": 66, "gt": "./."}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 15, "dp": 20, "gq": 33, "gt": "1/0"}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 21, "dp": 30, "gq": 99, "gt": "0/1"}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 9, "dp": 30, "gq": 99, "gt": "0/1"}},
            variant_set=variant_set,
        )
        SmallVariantFactory(
            genotype={self.patient: {"ad": 6, "dp": 30, "gq": 99, "gt": "0/1"}},
            variant_set=variant_set,
        )

    def test_genotype_gt_any_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "any"}, 8)

    def test_genotype_gt_any_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "any"}, 8)

    def test_genotype_gt_any_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "any"}, 8)

    def test_genotype_gt_ref_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "ref"}, 1)

    def test_genotype_gt_ref_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "ref"}, 1)

    def test_genotype_gt_ref_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "ref"}, 1)

    def test_genotype_gt_het_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "het"}, 5)

    def test_genotype_gt_het_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "het"}, 5)

    def test_genotype_gt_het_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "het"}, 5)

    def test_genotype_gt_hom_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "hom"}, 1)

    def test_genotype_gt_hom_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "hom"}, 1)

    def test_genotype_gt_hom_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "hom"}, 1)

    def test_genotype_gt_variant_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "variant"}, 6)

    def test_genotype_gt_variant_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "variant"}, 6)

    def test_genotype_gt_variant_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "variant"}, 6)

    def test_genotype_gt_non_variant_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "non-variant"}, 2)

    def test_genotype_gt_non_variant_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "non-variant"}, 2)

    def test_genotype_gt_non_variant_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "non-variant"}, 2)

    def test_genotype_gt_non_reference_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_gt" % self.patient: "non-reference"}, 7)

    def test_genotype_gt_non_reference_export(self):
        self.run_query(CaseExportTableQuery, {"%s_gt" % self.patient: "non-reference"}, 7)

    def test_genotype_gt_non_reference_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_gt" % self.patient: "non-reference"}, 7)

    def test_genotype_ad_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_ad" % self.patient: 15},
            5,
        )

    def test_genotype_ad_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_ad" % self.patient: 15},
            5,
        )

    def test_genotype_ad_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_ad" % self.patient: 15},
            5,
        )

    def test_genotype_ab_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_ab" % self.patient: 0.3},
            6,
        )

    def test_genotype_ab_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_ab" % self.patient: 0.3},
            6,
        )

    def test_genotype_ab_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_ab" % self.patient: 0.3},
            6,
        )

    def test_genotype_dp_het_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_het" % self.patient: 21},
            7,
        )
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_het" % self.patient: 20},
            8,
        )

    def test_genotype_dp_het_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_het" % self.patient: 21},
            7,
        )
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_het" % self.patient: 20},
            8,
        )

    def test_genotype_dp_het_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_het" % self.patient: 21},
            7,
        )
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_het" % self.patient: 20},
            8,
        )

    def test_genotype_dp_hom_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_hom" % self.patient: 31},
            6,
        )
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_hom" % self.patient: 30},
            8,
        )

    def test_genotype_dp_hom_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_hom" % self.patient: 31},
            6,
        )
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_hom" % self.patient: 30},
            8,
        )

    def test_genotype_dp_hom_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_hom" % self.patient: 31},
            6,
        )
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_dp_hom" % self.patient: 30},
            8,
        )

    def test_genotype_gq_limits_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_gq" % self.patient: 66},
            7,
        )

    def test_genotype_gq_limits_export(self):
        self.run_query(
            CaseExportTableQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_gq" % self.patient: 66},
            7,
        )

    def test_genotype_gq_limits_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {"%s_fail" % self.patient: "drop-variant", "%s_gq" % self.patient: 66},
            7,
        )

    def test_genotype_fail_ignore_filter(self):
        self.run_query(CasePrefetchQuery, {"%s_fail" % self.patient: "ignore"}, 8)

    def test_genotype_fail_ignore_export(self):
        self.run_query(CaseExportTableQuery, {"%s_fail" % self.patient: "ignore"}, 8)

    def test_genotype_fail_ignore_vcf(self):
        self.run_query(CaseExportVcfQuery, {"%s_fail" % self.patient: "ignore"}, 8)

    def test_genotype_fail_drop_variant_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "%s_fail" % self.patient: "drop-variant",
                "%s_dp" % self.patient: 20,
                "%s_ab" % self.patient: 0.3,
                "%s_gq" % self.patient: 20,
                "%s_ad" % self.patient: 15,
            },
            4,
        )

    def test_genotype_fail_drop_variant_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "%s_fail" % self.patient: "drop-variant",
                "%s_dp" % self.patient: 20,
                "%s_ab" % self.patient: 0.3,
                "%s_gq" % self.patient: 20,
                "%s_ad" % self.patient: 15,
            },
            4,
        )

    def test_genotype_fail_drop_variant_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "%s_fail" % self.patient: "drop-variant",
                "%s_dp" % self.patient: 20,
                "%s_ab" % self.patient: 0.3,
                "%s_gq" % self.patient: 20,
                "%s_ad" % self.patient: 15,
            },
            4,
        )

    def test_genotype_fail_no_call_filter(self):
        self.run_query(
            CasePrefetchQuery,
            {
                "%s_fail" % self.patient: "no-call",
                "%s_dp" % self.patient: 20,
                "%s_ab" % self.patient: 0.3,
                "%s_gq" % self.patient: 20,
                "%s_ad" % self.patient: 15,
                "%s_gt" % self.patient: "het",
            },
            6,
        )

    def test_genotype_fail_no_call_export(self):
        self.run_query(
            CaseExportTableQuery,
            {
                "%s_fail" % self.patient: "no-call",
                "%s_dp" % self.patient: 20,
                "%s_ab" % self.patient: 0.3,
                "%s_gq" % self.patient: 20,
                "%s_ad" % self.patient: 15,
                "%s_gt" % self.patient: "het",
            },
            6,
        )

    def test_genotype_fail_no_call_vcf(self):
        self.run_query(
            CaseExportVcfQuery,
            {
                "%s_fail" % self.patient: "no-call",
                "%s_dp" % self.patient: 20,
                "%s_ab" % self.patient: 0.3,
                "%s_gq" % self.patient: 20,
                "%s_ad" % self.patient: 15,
                "%s_gt" % self.patient: "het",
            },
            6,
        )


class TestCaseOneWhitelistBlacklistRegionFilterQuery(SupportQueryTestBase):
    """Test whitelist, blacklist and genomic region filter settings."""

    def setUp(self):
        """Generate a case, 3 genes and variants: gene i has i variants."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        case = variant_set.case
        self.hgncs = HgncFactory.create_batch(3)
        for i, hgnc in enumerate(self.hgncs):
            SmallVariantFactory.create_batch(
                i + 1,
                chromosome="1",
                start=(i + 1) * 100 + i,
                refseq_gene_id=hgnc.entrez_id,
                ensembl_gene_id=hgnc.ensembl_gene_id,
                variant_set=variant_set,
            )

    def test_blacklist_empty(self):
        self.run_query(CasePrefetchQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_export(self):
        self.run_query(CaseExportTableQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_vcf(self):
        self.run_query(CaseExportVcfQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_one_filter(self):
        self.run_query(CasePrefetchQuery, {"gene_blacklist": [self.hgncs[0].symbol]}, 5)

    def test_blacklist_one_export(self):
        self.run_query(CaseExportTableQuery, {"gene_blacklist": [self.hgncs[0].symbol]}, 5)

    def test_blacklist_one_vcf(self):
        self.run_query(CaseExportVcfQuery, {"gene_blacklist": [self.hgncs[0].symbol]}, 5)

    def test_blacklist_two_filter(self):
        self.run_query(
            CasePrefetchQuery, {"gene_blacklist": [hgnc.symbol for hgnc in self.hgncs[:2]]}, 3
        )

    def test_blacklist_two_export(self):
        self.run_query(
            CaseExportTableQuery, {"gene_blacklist": [hgnc.symbol for hgnc in self.hgncs[:2]]}, 3
        )

    def test_blacklist_two_vcf(self):
        self.run_query(
            CaseExportVcfQuery, {"gene_blacklist": [hgnc.symbol for hgnc in self.hgncs[:2]]}, 3
        )

    def test_blacklist_all_filter(self):
        self.run_query(
            CasePrefetchQuery, {"gene_blacklist": [hgnc.symbol for hgnc in self.hgncs]}, 0
        )

    def test_blacklist_all_export(self):
        self.run_query(
            CaseExportTableQuery, {"gene_blacklist": [hgnc.symbol for hgnc in self.hgncs]}, 0
        )

    def test_blacklist_all_vcf(self):
        self.run_query(
            CaseExportVcfQuery, {"gene_blacklist": [hgnc.symbol for hgnc in self.hgncs]}, 0
        )

    def test_whitelist_empty(self):
        self.run_query(CasePrefetchQuery, {"gene_whitelist": []}, 6)

    def test_whitelist_empty_export(self):
        self.run_query(CaseExportTableQuery, {"gene_whitelist": []}, 6)

    def test_whitelist_empty_vcf(self):
        self.run_query(CaseExportVcfQuery, {"gene_whitelist": []}, 6)

    def test_whitelist_one_filter(self):
        self.run_query(CasePrefetchQuery, {"gene_whitelist": [self.hgncs[0].symbol]}, 1)

    def test_whitelist_one_export(self):
        self.run_query(CaseExportTableQuery, {"gene_whitelist": [self.hgncs[0].symbol]}, 1)

    def test_whitelist_one_vcf(self):
        self.run_query(CaseExportVcfQuery, {"gene_whitelist": [self.hgncs[0].symbol]}, 1)

    def test_whitelist_two_filter(self):
        self.run_query(
            CasePrefetchQuery, {"gene_whitelist": [hgnc.symbol for hgnc in self.hgncs[:2]]}, 3
        )

    def test_whitelist_two_export(self):
        self.run_query(
            CaseExportTableQuery, {"gene_whitelist": [hgnc.symbol for hgnc in self.hgncs[:2]]}, 3
        )

    def test_whitelist_two_vcf(self):
        self.run_query(
            CaseExportVcfQuery, {"gene_whitelist": [hgnc.symbol for hgnc in self.hgncs[:2]]}, 3
        )

    def test_whitelist_all_filter(self):
        self.run_query(
            CasePrefetchQuery, {"gene_whitelist": [hgnc.symbol for hgnc in self.hgncs]}, 6
        )

    def test_whitelist_all_export(self):
        self.run_query(
            CaseExportTableQuery, {"gene_whitelist": [hgnc.symbol for hgnc in self.hgncs]}, 6
        )

    def test_whitelist_all_vcf(self):
        self.run_query(
            CaseExportVcfQuery, {"gene_whitelist": [hgnc.symbol for hgnc in self.hgncs]}, 6
        )

    def test_genomic_region_empty_filter(self):
        self.run_query(CasePrefetchQuery, {"genomic_region": []}, 6)

    def test_genomic_region_empty_export(self):
        self.run_query(CaseExportTableQuery, {"genomic_region": []}, 6)

    def test_genomic_region_empty_vcf(self):
        self.run_query(CaseExportVcfQuery, {"genomic_region": []}, 6)

    def test_genomic_region_one_region_filter(self):
        self.run_query(CasePrefetchQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_one_region_export(self):
        self.run_query(CaseExportTableQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_one_region_vcf(self):
        self.run_query(CaseExportVcfQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_two_regions_filter(self):
        self.run_query(CasePrefetchQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4)

    def test_genomic_region_two_regions_export(self):
        self.run_query(
            CaseExportTableQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4
        )

    def test_genomic_region_two_regions_vcf(self):
        self.run_query(CaseExportVcfQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4)


# ---------------------------------------------------------------------------
# Tests for Case 2
# ---------------------------------------------------------------------------

# Case 2 is a trio with affected child and unaffected parents. We test that
# the query works for the dominant (de novo), homozygous recessive, and
# compound heterozygous recessive.


class TestCaseTwoDominantQuery(SupportQueryTestBase):
    """Test the queries for dominant/de novo hypothesis"""

    # setup_case_in_db = fixture_setup_case2

    def setUp(self):
        """Create a trio case with 4 variants."""
        super().setUp()
        self.variant_set = SmallVariantSetFactory(case__structure="trio")
        self.case = self.variant_set.case
        self.small_vars = [
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
            ),
        ]

    def test_query_de_novo_filter(self):
        res = self.run_query(
            CasePrefetchQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "het",
                "%s_gt" % self.case.pedigree[0]["father"]: "ref",
                "%s_gt" % self.case.pedigree[0]["mother"]: "ref",
            },
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[0].start)

    def test_query_de_novo_export_table(self):
        res = self.run_query(
            CaseExportTableQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "het",
                "%s_gt" % self.case.pedigree[0]["father"]: "ref",
                "%s_gt" % self.case.pedigree[0]["mother"]: "ref",
            },
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[0].start)

    def test_query_de_novo_export_vcf(self):
        res = self.run_query(
            CaseExportVcfQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "het",
                "%s_gt" % self.case.pedigree[0]["father"]: "ref",
                "%s_gt" % self.case.pedigree[0]["mother"]: "ref",
            },
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[0].start)


class TestCaseTwoRecessiveHomozygousQuery(SupportQueryTestBase):
    """Test the queries for recessive homozygous hypothesis"""

    def setUp(self):
        """Create a trio case with 4 variants."""
        super().setUp()
        self.variant_set = SmallVariantSetFactory(case__structure="trio")
        self.case = self.variant_set.case
        self.small_vars = [
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome="1",
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
            ),
        ]

    def test_query_recessive_hom_filter(self):
        res = self.run_query(
            CasePrefetchQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "hom",
                "%s_gt" % self.case.pedigree[0]["father"]: "het",
                "%s_gt" % self.case.pedigree[0]["mother"]: "het",
            },
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[1].start)

    def test_query_recessive_hom_export_table(self):
        res = self.run_query(
            CaseExportTableQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "hom",
                "%s_gt" % self.case.pedigree[0]["father"]: "het",
                "%s_gt" % self.case.pedigree[0]["mother"]: "het",
            },
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[1].start)

    def test_query_recessive_hom_export_vcf(self):
        res = self.run_query(
            CaseExportVcfQuery,
            {
                "%s_gt" % self.case.pedigree[0]["patient"]: "hom",
                "%s_gt" % self.case.pedigree[0]["father"]: "het",
                "%s_gt" % self.case.pedigree[0]["mother"]: "het",
            },
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[1].start)


class TestCaseTwoCompoundRecessiveHeterozygousQuery(SupportQueryTestBase):
    """Test the queries for compound recessive heterozygous hypothesis"""

    def setUp(self):
        """Create a trio case with 4 variants and make sure the coordinates in the same gene are on the same chromosome."""
        super().setUp()
        self.variant_set = SmallVariantSetFactory(case__structure="trio")
        self.case = self.variant_set.case
        self.small_vars = [
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                ensembl_gene_id="ENSG1",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="2",
                ensembl_gene_id="ENSG2",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
            ),
        ]

    def test_query_compound_het_prefetch_filter(self):
        res = self.run_query(
            CasePrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_compound_het_export_tsv(self):
        res = self.run_query(
            CaseExportTableQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_compound_het_export_vcf(self):
        res = self.run_query(
            CaseExportVcfQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_compound_het_load_prefetched_filter(self):
        # Generate results
        res = self.run_query(
            CasePrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        # Add results to variant query
        query = SmallVariantQueryFactory(case=self.case)
        query.query_results.add(res[0].id, res[1].id)
        # Load Prefetched results
        res = self.run_query(
            CaseLoadPrefetchedQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
                "filter_job_id": query.id,
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)


class TestCaseTwoCompoundRecessiveHeterozygousQueryQuartet(SupportQueryTestBase):
    """Test the queries for compound recessive heterozygous hypothesis with siblings."""

    def setUp(self):
        """Create a quartet case with 4 variants and make sure the coordinates in the same gene are on the same chromosome."""
        super().setUp()
        self.variant_set = SmallVariantSetFactory(case__structure="quartet")
        self.case = self.variant_set.case
        self.small_vars = [
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                ensembl_gene_id="ENSG1",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="2",
                ensembl_gene_id="ENSG2",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
            ),
            SmallVariantFactory(
                chromosome=4,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="4",
                ensembl_gene_id="ENSG4",
                variant_set=self.variant_set,
            ),
            SmallVariantFactory(
                chromosome=4,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                variant_set=self.variant_set,
                refseq_gene_id="4",
                ensembl_gene_id="ENSG4",
            ),
        ]

    def test_query_index_compound_het_prefetch_filter(self):
        res = self.run_query(
            CasePrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_index_compound_het_prefetch_export_tsv(self):
        res = self.run_query(
            CaseExportTableQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_index_compound_het_prefetch_export_vcf(self):
        res = self.run_query(
            CaseExportVcfQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_index_compound_het_load_prefetched_filter(self):
        # Generate results
        res = self.run_query(
            CasePrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        # Add results to variant query
        query = SmallVariantQueryFactory(case=self.case)
        query.query_results.add(res[0].id, res[1].id)
        # Load Prefetched results
        res = self.run_query(
            CaseLoadPrefetchedQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
                "filter_job_id": query.id,
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_sibling_compound_het_prefetch_filter(self):
        res = self.run_query(
            CasePrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[4].start)
        self.assertEqual(res[1].start, self.small_vars[5].start)

    def test_query_sibling_compound_het_prefetch_export_tsv(self):
        res = self.run_query(
            CaseExportTableQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[4].start)
        self.assertEqual(res[1].start, self.small_vars[5].start)

    def test_query_sibling_compound_het_prefetch_export_vcf(self):
        res = self.run_query(
            CaseExportVcfQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[4].start)
        self.assertEqual(res[1].start, self.small_vars[5].start)

    def test_query_sibling_compound_het_load_prefetched_filter(self):
        # Generate results
        res = self.run_query(
            CasePrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
            },
            2,
        )
        # Add results to variant query
        query = SmallVariantQueryFactory(case=self.case)
        query.query_results.add(res[0].id, res[1].id)
        # Load Prefetched results
        res = self.run_query(
            CaseLoadPrefetchedQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
                "filter_job_id": query.id,
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[4].start)
        self.assertEqual(res[1].start, self.small_vars[5].start)


# ---------------------------------------------------------------------------
# Tests for Case 3
# ---------------------------------------------------------------------------

# Case 3 is a singleton test case and meant for testing the Clinvar
# membership queries.  We create a new test case for this as we might be able
# to allow the user to filter out benign variants or variants of unknown
# significance.


class CaseThreeClinvarMembershipFilterTestMixin:
    """Base class for testing query with ClinvarMembership filter."""

    query_class = None
    run_query_function = None

    def setUp(self):
        super().setUp()
        variant_set = SmallVariantSetFactory(case__structure="trio")
        self.small_vars = [
            SmallVariantFactory(chromosome="1", in_clinvar=True, variant_set=variant_set),
            SmallVariantFactory(chromosome="1", in_clinvar=False, variant_set=variant_set),
        ]
        patho_keys = (
            "pathogenic",
            "likely_pathogenic",
            "uncertain_significance",
            "likely_benign",
            "benign",
        )
        for key in patho_keys:
            self.small_vars.append(
                SmallVariantFactory(
                    refseq_gene_id="2",
                    ensembl_gene_id="ENSG2",
                    in_clinvar=True,
                    variant_set=variant_set,
                )
            )
            ClinvarFactory(
                release=self.small_vars[-1].release,
                chromosome=self.small_vars[-1].chromosome,
                start=self.small_vars[-1].start,
                end=self.small_vars[-1].end,
                bin=self.small_vars[-1].bin,
                reference=self.small_vars[-1].reference,
                alternative=self.small_vars[-1].alternative,
                clinical_significance=key,
                clinical_significance_ordered=[key],
                review_status="practice guideline",
                review_status_ordered=["practice guideline"],
                **{key: 1},
            )

    def test_render_query_do_not_require_membership(self):
        self.run_query_function(self.query_class, {}, 7)

    def test_render_query_require_membership_include_none(self):
        self.run_query_function(self.query_class, {"require_in_clinvar": True}, 6)

    def test_render_query_require_membership_include_pathogenic(self):
        res = self.run_query_function(
            self.query_class, {"require_in_clinvar": True, "clinvar_include_pathogenic": True}, 1
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)

    def test_render_query_require_membership_include_likely_pathogenic(self):
        res = self.run_query_function(
            self.query_class,
            {"require_in_clinvar": True, "clinvar_include_likely_pathogenic": True},
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[3].start)

    def test_render_query_require_membership_include_uncertain_significance(self):
        res = self.run_query_function(
            self.query_class,
            {"require_in_clinvar": True, "clinvar_include_uncertain_significance": True},
            1,
        )
        self.assertEqual(res[0].start, self.small_vars[4].start)

    def test_render_query_require_membership_include_likely_benign(self):
        res = self.run_query_function(
            self.query_class, {"require_in_clinvar": True, "clinvar_include_likely_benign": True}, 1
        )
        self.assertEqual(res[0].start, self.small_vars[5].start)

    def test_render_query_require_membership_include_benign(self):
        res = self.run_query_function(
            self.query_class, {"require_in_clinvar": True, "clinvar_include_benign": True}, 1
        )
        self.assertEqual(res[0].start, self.small_vars[6].start)


class RenderQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, SupportQueryTestBase
):
    """Test clinvar membership using RenderFilterQuery."""

    query_class = CasePrefetchQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_query


class ExportFileFilterQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, SupportQueryTestBase
):
    """Test clinvar membership using ExportFileFilterQuery."""

    query_class = CaseExportTableQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_query


class ExportVcfFilterQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, SupportQueryTestBase
):
    """Test clinvar membership using ExportFileFilterQuery."""

    query_class = CaseExportVcfQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_query


# ---------------------------------------------------------------------------
# ClinvarReportQuery: Case 4
# ---------------------------------------------------------------------------

# We use the singleton case 1 and construct different cases with clinvar annotation.


# TODO exports are missing
class TestHgmdMembershipQuery(SupportQueryTestBase):
    """Tests for the HGMD membership query."""

    def setUp(self):
        """Create a case and two variants: one in HGMD, the other not."""
        super().setUp()
        variant_set = SmallVariantSetFactory()
        self.small_vars = [
            SmallVariantFactory(variant_set=variant_set),
            SmallVariantFactory(variant_set=variant_set),
        ]
        self.hgmd = HgmdPublicLocusFactory(
            chromosome=self.small_vars[1].chromosome,
            start=self.small_vars[1].start - 1,
            end=self.small_vars[1].start,
        )

    def test_no_hgmd_query(self):
        self.run_query(
            CasePrefetchQuery,
            {"require_in_hgmd_public": False, "display_hgmd_public_membership": False},
            2,
        )

    def test_require_in_hgmd_query(self):
        self.run_query(
            CasePrefetchQuery,
            {"require_in_hgmd_public": True, "display_hgmd_public_membership": False},
            1,
        )

    def test_display_hgmd_membership_query(self):
        res = self.run_query(
            CasePrefetchQuery,
            {"require_in_hgmd_public": False, "display_hgmd_public_membership": True},
            2,
        )
        self.assertEqual(res[1].hgmd_accession, self.hgmd.variation_name)

    def test_require_in_hgmd_and_display_membership_query(self):
        res = self.run_query(
            CasePrefetchQuery,
            {"require_in_hgmd_public": True, "display_hgmd_public_membership": True},
            1,
        )
        self.assertEqual(res[0].hgmd_accession, self.hgmd.variation_name)


# TODO clinvar doesn't test genotype
class ClinvarReportQueryTestCaseFour(SupportQueryTestBase):
    def setUp(self):
        super().setUp()
        self.small_var = SmallVariantFactory(in_clinvar=True)

    def _setup_clinvar_entry(self, clinvar_patch={}):
        """Setup patched Clinvar entry with values from ``clinvar_patch``.

        This function will take care of patching the correct position into the defaults.
        """
        patched_data = {
            "review_status": "practice guideline",
            "review_status_ordered": ["practice guideline"],
            **clinvar_patch,
        }
        ClinvarFactory(
            release=self.small_var.release,
            chromosome=self.small_var.chromosome,
            start=self.small_var.start,
            end=self.small_var.end,
            bin=self.small_var.bin,
            reference=self.small_var.reference,
            alternative=self.small_var.alternative,
            **patched_data,
        )

    # TODO: conver to use ``test_snake_case``

    def testEnsemblTranscripts(self):
        self._setup_clinvar_entry()
        self.run_query(ClinvarReportPrefetchQuery, {"database_select": "ensembl"}, 1)

    def testPathogenicInclude(self):
        self._setup_clinvar_entry({"pathogenic": 1})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_pathogenic": True}, 1)

    def testPathogenicNoInclude(self):
        self._setup_clinvar_entry()
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_pathogenic": True}, 0)

    def testLikelyPathogenicInclude(self):
        self._setup_clinvar_entry({"likely_pathogenic": 1})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_likely_pathogenic": True}, 1)

    def testLikelyPathogenicNoInclude(self):
        self._setup_clinvar_entry()
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_likely_pathogenic": True}, 0)

    def testUncertainSignificanceInclude(self):
        self._setup_clinvar_entry({"uncertain_significance": 1})
        self.run_query(
            ClinvarReportPrefetchQuery, {"clinvar_include_uncertain_significance": True}, 1
        )

    def testUncertainSignificanceNoInclude(self):
        self._setup_clinvar_entry()
        self.run_query(
            ClinvarReportPrefetchQuery, {"clinvar_include_uncertain_significance": True}, 0
        )

    def testLikelyBenignInclude(self):
        self._setup_clinvar_entry({"likely_benign": 1})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_likely_benign": True}, 1)

    def testLikelyBenignNoInclude(self):
        self._setup_clinvar_entry()
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_likely_benign": True}, 0)

    def testBenignInclude(self):
        self._setup_clinvar_entry({"benign": 1})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_benign": True}, 1)

    def testBenignNoInclude(self):
        self._setup_clinvar_entry()
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_include_benign": True}, 0)

    def testGermlineInclude(self):
        self._setup_clinvar_entry({"origin": ["germline"]})
        self.run_query(
            ClinvarReportPrefetchQuery,
            {"clinvar_origin_germline": True, "clinvar_origin_somatic": False},
            1,
        )

    def testGermlineNoInclude(self):
        self._setup_clinvar_entry({"origin": ["germline"]})
        self.run_query(
            ClinvarReportPrefetchQuery,
            {"clinvar_origin_germline": False, "clinvar_origin_somatic": True},
            0,
        )

    def testSomaticInclude(self):
        self._setup_clinvar_entry({"origin": ["somatic"]})
        self.run_query(
            ClinvarReportPrefetchQuery,
            {"clinvar_origin_germline": False, "clinvar_origin_somatic": True},
            1,
        )

    def testSomaticNoInclude(self):
        self._setup_clinvar_entry({"origin": ["somatic"]})
        self.run_query(
            ClinvarReportPrefetchQuery,
            {"clinvar_origin_germline": True, "clinvar_origin_somatic": False},
            0,
        )

    def testPracticeGuidelineInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["practice guideline"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_practice_guideline": True}, 1)

    def testPracticeGuidelineNoInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["practice guideline"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_practice_guideline": False}, 0)

    def testExpertPanelInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["reviewed by expert panel"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_expert_panel": True}, 1)

    def testExpertPanelNoInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["reviewed by expert panel"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_expert_panel": False}, 0)

    def testMultipleNoConflictInclude(self):
        self._setup_clinvar_entry(
            {"review_status_ordered": ["criteria provided, multiple submitters, no conflicts"]}
        )
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_multiple_no_conflict": True}, 1)

    def testMultipleNoConflictNoInclude(self):
        self._setup_clinvar_entry(
            {"review_status_ordered": ["criteria provided, multiple submitters, no conflicts"]}
        )
        self.run_query(
            ClinvarReportPrefetchQuery, {"clinvar_status_multiple_no_conflict": False}, 0
        )

    def testSingleInclude(self):
        self._setup_clinvar_entry(
            {"review_status_ordered": ["criteria provided, single submitter"]}
        )
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_single": True}, 1)

    def testSingleNoInclude(self):
        self._setup_clinvar_entry(
            {"review_status_ordered": ["criteria provided, single submitter"]}
        )
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_single": False}, 0)

    def testConflictInclude(self):
        self._setup_clinvar_entry(
            {"review_status_ordered": ["criteria provided, conflicting interpretations"]}
        )
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_conflict": True}, 1)

    def testConflictNoInclude(self):
        self._setup_clinvar_entry(
            {"review_status_ordered": ["criteria provided, conflicting interpretations"]}
        )
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_conflict": False}, 0)

    def testNoCriteriaInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["no assertion criteria provided"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_no_criteria": True}, 1)

    def testNoCriteriaNoInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["no assertion criteria provided"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_no_criteria": False}, 0)

    def testNoAssertionInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["no assertion provided"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_no_assertion": True}, 1)

    def testNoAssertionNoInclude(self):
        self._setup_clinvar_entry({"review_status_ordered": ["no assertion provided"]})
        self.run_query(ClinvarReportPrefetchQuery, {"clinvar_status_no_assertion": False}, 0)


class TestCaseFourClinvarLoadPrefetchedQuery(SupportQueryTestBase):
    """Test the load prefetched functionality of clinvar report."""

    def setUp(self):
        super().setUp()
        variant_set = SmallVariantSetFactory()
        self.small_vars = list()
        for i in range(3):
            self.small_vars.append(SmallVariantFactory(in_clinvar=True, variant_set=variant_set))
            ClinvarFactory(
                release=self.small_vars[-1].release,
                chromosome=self.small_vars[-1].chromosome,
                start=self.small_vars[-1].start,
                end=self.small_vars[-1].end,
                bin=self.small_vars[-1].bin,
                reference=self.small_vars[-1].reference,
                alternative=self.small_vars[-1].alternative,
                review_status="practice guideline",
                review_status_ordered=["practice guideline"],
            )
        self.clinvarquery = ClinvarQueryFactory(case=variant_set.case)
        self.clinvarquery.query_results.add(self.small_vars[0].id, self.small_vars[2].id)

    def test_load_prefetched_clinvar_query(self):
        self.run_query(ClinvarReportLoadPrefetchedQuery, {"filter_job_id": self.clinvarquery.id}, 2)


class TestClinvarCompHetQuery(SupportQueryTestBase):
    """Test the Clinvar Report in compound heterozygous mode."""

    def setUp(self):
        """Create a case and smallvars with clinvar entries."""
        super().setUp()
        variant_set = SmallVariantSetFactory(case__structure="trio")
        self.case = variant_set.case
        self.small_vars = [
            # Create a de novo variant that is in clinvar
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                ensembl_gene_id="ENSG1",
                variant_set=variant_set,
                in_clinvar=True,
            ),
            # Create a recessive variant that is not in clinvar
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="2",
                ensembl_gene_id="ENSG2",
                variant_set=variant_set,
                in_clinvar=False,
            ),
            # Create a pair of comp het variants that are in clinvar
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
                variant_set=variant_set,
                in_clinvar=True,
            ),
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
                variant_set=variant_set,
                in_clinvar=True,
            ),
            # Create a pair of comp het variants that are not in clinvar
            SmallVariantFactory(
                chromosome=4,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="4",
                ensembl_gene_id="ENSG4",
                variant_set=variant_set,
                in_clinvar=False,
            ),
            SmallVariantFactory(
                chromosome=4,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                refseq_gene_id="4",
                ensembl_gene_id="ENSG4",
                variant_set=variant_set,
                in_clinvar=False,
            ),
        ]
        for small_var in self.small_vars:
            if small_var.in_clinvar:
                ClinvarFactory(
                    release=small_var.release,
                    chromosome=small_var.chromosome,
                    start=small_var.start,
                    end=small_var.end,
                    bin=small_var.bin,
                    reference=small_var.reference,
                    alternative=small_var.alternative,
                )

    def test_query_compound_het_prefetch_filter(self):
        res = self.run_query(
            ClinvarReportPrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)

    def test_query_compound_het_load_prefetched_filter(self):
        # Generate results
        res = self.run_query(
            ClinvarReportPrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        # Add results to variant query
        query = ClinvarQueryFactory(case=self.case)
        query.query_results.add(res[0].id, res[1].id)
        # Load Prefetched results
        res = self.run_query(
            ClinvarReportLoadPrefetchedQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
                "filter_job_id": query.id,
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[2].start)
        self.assertEqual(res[1].start, self.small_vars[3].start)


class TestClinvarCompHetQueryQuartet(SupportQueryTestBase):
    """Test the Clinvar Report in compound heterozygous mode."""

    def setUp(self):
        """Create a case and smallvars with clinvar entries."""
        super().setUp()
        self.variant_set = SmallVariantSetFactory(case__structure="quartet")
        self.case = self.variant_set.case
        self.small_vars = [
            # Create a de novo variant that is in clinvar
            SmallVariantFactory(
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                ensembl_gene_id="ENSG1",
                variant_set=self.variant_set,
                in_clinvar=True,
            ),
            # Create a pair of comp het variants that are in clinvar
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
                variant_set=self.variant_set,
                in_clinvar=True,
            ),
            SmallVariantFactory(
                chromosome=3,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                refseq_gene_id="3",
                ensembl_gene_id="ENSG3",
                variant_set=self.variant_set,
                in_clinvar=True,
            ),
            # Create a pair of comp het variants that are not in clinvar
            SmallVariantFactory(
                chromosome=4,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                refseq_gene_id="4",
                ensembl_gene_id="ENSG4",
                variant_set=self.variant_set,
                in_clinvar=True,
            ),
            SmallVariantFactory(
                chromosome=4,
                genotype={
                    self.case.pedigree[0]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    self.case.pedigree[1]["patient"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["father"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    self.case.pedigree[0]["mother"]: {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                refseq_gene_id="4",
                ensembl_gene_id="ENSG4",
                variant_set=self.variant_set,
                in_clinvar=True,
            ),
        ]
        for small_var in self.small_vars:
            if small_var.in_clinvar:
                ClinvarFactory(
                    release=small_var.release,
                    chromosome=small_var.chromosome,
                    start=small_var.start,
                    end=small_var.end,
                    bin=small_var.bin,
                    reference=small_var.reference,
                    alternative=small_var.alternative,
                )

    def test_query_index_compound_het_prefetch_filter(self):
        res = self.run_query(
            ClinvarReportPrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[1].start)
        self.assertEqual(res[1].start, self.small_vars[2].start)

    def test_query_index_compound_het_load_prefetched_filter(self):
        # Generate results
        res = self.run_query(
            ClinvarReportPrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
            },
            2,
        )
        # Add results to variant query
        query = ClinvarQueryFactory(case=self.case)
        query.query_results.add(res[0].id, res[1].id)
        # Load Prefetched results
        res = self.run_query(
            ClinvarReportLoadPrefetchedQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[0]["patient"],
                "filter_job_id": query.id,
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[1].start)
        self.assertEqual(res[1].start, self.small_vars[2].start)

    def test_query_sibling_compound_het_prefetch_filter(self):
        res = self.run_query(
            ClinvarReportPrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[3].start)
        self.assertEqual(res[1].start, self.small_vars[4].start)

    def test_query_sibling_compound_het_load_prefetched_filter(self):
        # Generate results
        res = self.run_query(
            ClinvarReportPrefetchQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
            },
            2,
        )
        # Add results to variant query
        query = ClinvarQueryFactory(case=self.case)
        query.query_results.add(res[0].id, res[1].id)
        # Load Prefetched results
        res = self.run_query(
            ClinvarReportLoadPrefetchedQuery,
            {
                "compound_recessive_enabled": True,
                "compound_recessive_index": self.case.pedigree[1]["patient"],
                "filter_job_id": query.id,
            },
            2,
        )
        self.assertEqual(res[0].start, self.small_vars[3].start)
        self.assertEqual(res[1].start, self.small_vars[4].start)


class TestCaseFiveQueryProject(SupportQueryTestBase):
    def setUp(self):
        super().setUp()
        project = ProjectFactory()
        variant_sets = [
            SmallVariantSetFactory(case__project=project),
            SmallVariantSetFactory(case__project=project),
        ]
        small_vars = [
            SmallVariantFactory(variant_set=variant_sets[0]),
            SmallVariantFactory(variant_set=variant_sets[1]),
            SmallVariantFactory(variant_set=variant_sets[1]),
        ]
        projectcasessmallvariantquery = ProjectCasesSmallVariantQueryFactory(project=project)
        projectcasessmallvariantquery.query_results.add(small_vars[0], small_vars[2])

    def test_query_project_with_two_cases(self):
        self.run_query(ProjectPrefetchQuery, {}, 3, query_type="project")

    def test_load_project_prefetched_two_cases(self):
        query_job = ProjectCasesSmallVariantQuery.objects.first()
        self.run_query(
            ProjectLoadPrefetchedQuery, {"filter_job_id": query_job.id}, 2, query_type="project"
        )


class TestKnownGeneAAQuery(TestBase):
    """Test the knowngeneaa query."""

    def run_query(self, query_class, kwargs, length):
        query = query_class(SQLALCHEMY_ENGINE)
        results = list(query.run(kwargs))
        self.assertEqual(len(results), length)

    def setUp(self):
        super().setUp()
        self.knowngene = KnownGeneAAFactory(chromosome="1", start=100)

    def test_query_pre_triplet(self):
        self.run_query(
            KnownGeneAAQuery,
            {
                "release": self.knowngene.release,
                "chromosome": self.knowngene.chromosome,
                "start": self.knowngene.start - 1,
                "end": self.knowngene.end - 1,
                "reference": "A",
            },
            0,
        )

    def test_query_first_triplet(self):
        self.run_query(
            KnownGeneAAQuery,
            {
                "release": self.knowngene.release,
                "chromosome": self.knowngene.chromosome,
                "start": self.knowngene.start,
                "end": self.knowngene.start,
                "reference": "A",
            },
            1,
        )

    def test_query_second_triplet(self):
        self.run_query(
            KnownGeneAAQuery,
            {
                "release": self.knowngene.release,
                "chromosome": self.knowngene.chromosome,
                "start": self.knowngene.start + 1,
                "end": self.knowngene.end + 1,
                "reference": "A",
            },
            1,
        )

    def test_query_third_triplet(self):
        self.run_query(
            KnownGeneAAQuery,
            {
                "release": self.knowngene.release,
                "chromosome": self.knowngene.chromosome,
                "start": self.knowngene.start + 2,
                "end": self.knowngene.start + 2,
                "reference": "A",
            },
            1,
        )

    def test_query_post_triplet(self):
        self.run_query(
            KnownGeneAAQuery,
            {
                "release": self.knowngene.release,
                "chromosome": self.knowngene.chromosome,
                "start": self.knowngene.start + 3,
                "end": self.knowngene.end + 3,
                "reference": "A",
            },
            0,
        )
