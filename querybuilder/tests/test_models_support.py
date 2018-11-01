import aldjemy.core
from django.test import TestCase

from variants.models import SmallVariant, Case
from projectroles.models import Project

from ..models_support import ExportFileFilterQuery, CountOnlyFilterQuery, RenderFilterQuery

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()

# ---------------------------------------------------------------------------
# Test Helpers and Generic Test Data
# ---------------------------------------------------------------------------


class FilterTestBase(TestCase):
    """Base class for running the test for the ``SmallVariant`` filter queries.
    """

    #: Callable that sets up the database with the case to use in the test
    setup_case_in_db = None
    #: Set this value to the base cleaned data to patch
    base_cleaned_data = None

    def setUp(self):
        self.maxDiff = None  # show full diff
        self.__class__.setup_case_in_db()

    def _get_fetch_and_query(self, query_class, cleaned_data_patch):
        connection = SQLALCHEMY_ENGINE.connect()
        patched_cleaned_data = {**self.base_cleaned_data, **cleaned_data_patch}

        def fetch_case_and_query():
            """Helper function that fetches the ``case`` by UUID and then generates the
            appropriate query.
            """
            case = Case.objects.get(sodar_uuid=patched_cleaned_data["case_uuid"])
            return query_class(case, connection).run(patched_cleaned_data)

        return fetch_case_and_query

    def run_filter_query(self, query_class, cleaned_data_patch, length, assert_raises=None):
        """Run query returning a collection of filtration results with ``query_class``.

        This is a helper to be called in all ``test_*()`` functions.  It is a shortcut
        to the following:

        - Create a query kwargs ``dict`` by patching ``self.__class__.base_cleaned_data``
          with ``patch_cleaned_data``.
        - Perform the query.
        - Assert that exactly ``length`` elements are returned (and return list of these
          elements for further testing).
        - If ``assert_raises`` evaluates as ``True`` then instead of checking the result
          length and returning a list of elements, assert that an exception of type
          ``assert_raises`` is raised.
        """
        fetch_case_and_query = self._get_fetch_and_query(query_class, cleaned_data_patch)
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            results = list(fetch_case_and_query())
            self.assertEquals(length, len(results))
            return results

    def run_count_query(self, query_class, kwargs_patch, length, assert_raises=None):
        """Run query returning a result record count instead of result records."""
        fetch_case_and_query = self._get_fetch_and_query(query_class, kwargs_patch)
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            result = fetch_case_and_query()
            self.assertEquals(length, result)
            return result


#: Shared data for ``Project`` to use for all test cases.
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}

# ---------------------------------------------------------------------------
# Tests for Case 1
# ---------------------------------------------------------------------------

# Case 1 is a singleton with a single variant.  Here, we perform tests for
# the basic queries.


def fixture_setup_case1():
    """Setup test case 1 -- a singleton with one variant only."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
    )
    SmallVariant.objects.create(
        case_id=case.pk,
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        var_type="snv",
        genotype={"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        in_clinvar=False,
        # frequencies
        exac_frequency=0.01,
        exac_homozygous=0,
        exac_heterozygous=0,
        exac_hemizygous=0,
        thousand_genomes_frequency=0.01,
        thousand_genomes_homozygous=0,
        thousand_genomes_heterozygous=0,
        thousand_genomes_hemizygous=0,
        gnomad_exomes_frequency=0.01,
        gnomad_exomes_homozygous=0,
        gnomad_exomes_heterozygous=0,
        gnomad_exomes_hemizygous=0,
        gnomad_genomes_frequency=0.01,
        gnomad_genomes_homozygous=0,
        gnomad_genomes_heterozygous=0,
        gnomad_genomes_hemizygous=0,
        # RefSeq
        refseq_gene_id="1234",
        refseq_transcript_id="NR_00001.1",
        refseq_transcript_coding=False,
        refseq_hgvs_c="n.111+2T>C",
        refseq_hgvs_p="p.=",
        refseq_effect=["synonymous_variant"],
        # ENSEMBL
        ensembl_gene_id="ENGS00001",
        ensembl_transcript_id="ENST00001",
        ensembl_transcript_coding=False,
        ensembl_hgvs_c="n.111+2T>C",
        ensembl_hgvs_p="p.=",
        ensembl_effect=["synonymous_variant"],
    )


#: A value for filtration form ``cleaned_data`` to be used for "Case 1" that lets
#: all variants through.
INCLUSIVE_CLEANED_DATA_CASE1 = {
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "effects": ["synonymous_variant"],
    "gene_blacklist": [],
    "database_select": "refseq",
    "var_type_snv": True,
    "var_type_mnv": True,
    "var_type_indel": True,
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 0.0,
    "gnomad_exomes_heterozygous": 0,
    "gnomad_exomes_homozygous": 0,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 0.0,
    "gnomad_genomes_heterozygous": 0,
    "gnomad_genomes_homozygous": 0,
    "exac_enabled": False,
    "exac_frequency": 0.0,
    "exac_heterozygous": 0,
    "exac_homozygous": 0,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 0.0,
    "thousand_genomes_heterozygous": 0,
    "thousand_genomes_homozygous": 0,
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp": 0,
    "A_ab": 0,
    "A_gq": 0,
    "A_ad": 0,
}


class TestCaseOneQueryDatabaseSwitch(FilterTestBase):
    """Test whether both RefSeq and ENSEMBL databases work."""

    setup_case_in_db = fixture_setup_case1
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_base_query_refseq_filter(self):
        self.run_filter_query(RenderFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_ensembl_filter(self):
        self.run_filter_query(RenderFilterQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_ensembl_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_ensembl_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"database_select": "ensembl"}, 1)


class TestCaseOneQueryCase(FilterTestBase):
    """Test with correct and incorrect case UUID"""

    setup_case_in_db = fixture_setup_case1
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_query_case_correct_filter(self):
        self.run_filter_query(RenderFilterQuery, {}, 1)

    def test_query_case_correct_export(self):
        self.run_filter_query(ExportFileFilterQuery, {}, 1)

    def test_query_case_correct_count(self):
        self.run_count_query(CountOnlyFilterQuery, {}, 1)

    def test_query_case_incorrect_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )

    def test_query_case_incorrect_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )

    def test_query_case_incorrect_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )


# TODO: there's no tests like more tests for case 1


# ---------------------------------------------------------------------------
# Tests for Case 2
# ---------------------------------------------------------------------------

# Case 2 is a trio with affected child and unaffected parents. We test that
# the query works for the dominant (de novo), homozygous recessive, and
# compound heterozygous recessive.


def fixture_setup_case2():
    """Setup test case 2 -- a trio."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="C",
        index="C",
        pedigree=[
            {"sex": 1, "father": "F", "mother": "M", "patient": "C", "affected": 2},
            {"sex": 1, "father": "0", "mother": "0", "patient": "F", "affected": 1},
            {"sex": 2, "father": "0", "mother": "0", "patient": "M", "affected": 1},
        ],
    )
    # Basic variant settings.
    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": None,
        "in_clinvar": False,
        # frequencies
        "exac_frequency": 0.01,
        "exac_homozygous": 0,
        "exac_heterozygous": 0,
        "exac_hemizygous": 0,
        "thousand_genomes_frequency": 0.01,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 0,
        "thousand_genomes_hemizygous": 0,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 0,
        "gnomad_exomes_hemizygous": 0,
        "gnomad_genomes_frequency": 0.01,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 0,
        "gnomad_genomes_hemizygous": 0,
        # RefSeq
        "refseq_gene_id": None,
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": None,
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }
    # Variant that should be passing for dominant/de novo filter settings.
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 100,
                "genotype": {
                    "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    "F": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    "M": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                "refseq_gene_id": "1",
                "ensembl_gene_id": "ENGS1",
            },
        }
    )
    # Variant that should be passing for homozygous recessive filter settings.
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 101,
                "genotype": {
                    "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "1/1"},
                    "F": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    "M": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                "refseq_gene_id": "2",
                "ensembl_gene_id": "ENGS2",
            },
        }
    )
    # Two variants that should be passing for compound recessive filter settings.
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 102,
                "genotype": {
                    "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    "F": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                    "M": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                },
                "refseq_gene_id": "3",
                "ensembl_gene_id": "ENGS3",
            },
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 103,
                "genotype": {
                    "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    "F": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                    "M": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/0"},
                },
                "refseq_gene_id": "3",
                "ensembl_gene_id": "ENGS3",
            },
        }
    )


#: A value for filtration form ``cleaned_data`` to be used for "Case 1" that lets
#: all variants through.
INCLUSIVE_CLEANED_DATA_CASE2 = {
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "effects": ["synonymous_variant"],
    "gene_blacklist": [],
    "database_select": "refseq",
    "var_type_snv": True,
    "var_type_mnv": True,
    "var_type_indel": True,
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 0.0,
    "gnomad_exomes_heterozygous": 0,
    "gnomad_exomes_homozygous": 0,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 0.0,
    "gnomad_genomes_heterozygous": 0,
    "gnomad_genomes_homozygous": 0,
    "exac_enabled": False,
    "exac_frequency": 0.0,
    "exac_heterozygous": 0,
    "exac_homozygous": 0,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 0.0,
    "thousand_genomes_heterozygous": 0,
    "thousand_genomes_homozygous": 0,
    "C_fail": "drop-variant",
    "C_gt": "any",  # ensure complex queries are used
    "C_dp": 0,
    "C_ab": 0,
    "C_gq": 0,
    "C_ad": 0,
    "F_fail": "drop-variant",  # ensure complex queries are used
    "F_gt": "any",
    "F_dp": 0,
    "F_ab": 0,
    "F_gq": 0,
    "F_ad": 0,
    "M_fail": "drop-variant",  # ensure complex queries are used
    "M_gt": "any",
    "M_dp": 0,
    "M_ab": 0,
    "M_gq": 0,
    "M_ad": 0,
}


class TestCaseTwoDominantQuery(FilterTestBase):
    """Test the queries for dominant/de novo hypothesis"""

    setup_case_in_db = fixture_setup_case2
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE2

    cleaned_data_patch = {"C_gt": "het", "F_gt": "ref", "M_gt": "ref"}

    def test_query_de_novo_filter(self):
        res = self.run_filter_query(RenderFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 100)

    def test_query_de_novo_export(self):
        res = self.run_filter_query(ExportFileFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 100)

    def test_query_de_novo_count(self):
        self.run_count_query(CountOnlyFilterQuery, self.cleaned_data_patch, 1)


class TestCaseTwoRecessiveHomozygousQuery(FilterTestBase):
    """Test the queries for recessive homozygous hypothesis"""

    setup_case_in_db = fixture_setup_case2
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE2

    cleaned_data_patch = {"C_gt": "hom", "F_gt": "het", "M_gt": "het"}

    def test_query_recessive_hom_filter(self):
        res = self.run_filter_query(RenderFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 101)

    def test_query_recessive_hom_export(self):
        res = self.run_filter_query(ExportFileFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 101)

    def test_query_recessive_hom_count(self):
        self.run_count_query(CountOnlyFilterQuery, self.cleaned_data_patch, 1)


class TestCaseTwoCompoundRecessiveHeterozygousQuery(FilterTestBase):
    """Test the queries for compound recessive heterozygous hypothesis"""

    setup_case_in_db = fixture_setup_case2
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE2

    cleaned_data_patch = {"compound_recessive_enabled": True}

    def test_query_compound_het_filter(self):
        res = self.run_filter_query(RenderFilterQuery, self.cleaned_data_patch, 2)
        self.assertEqual(res[0].position, 102)
        self.assertEqual(res[1].position, 103)

    def test_query_compound_het_export(self):
        res = self.run_filter_query(ExportFileFilterQuery, self.cleaned_data_patch, 2)
        self.assertEqual(res[0].position, 102)
        self.assertEqual(res[1].position, 103)

    def test_query_compound_het_count(self):
        self.run_count_query(CountOnlyFilterQuery, self.cleaned_data_patch, 2)
