import aldjemy.core
from django.test import TestCase

from clinvar.models import Clinvar
from frequencies.models import Exac, ThousandGenomes, GnomadExomes, GnomadGenomes
from geneinfo.models import Hgnc, Mim2geneMedgen, Hpo
from pathways.models import KeggInfo, EnsemblToKegg, RefseqToKegg
from projectroles.models import Project
from variants.models import SmallVariant, Case

from ..models_support import ExportFileFilterQuery, CountOnlyFilterQuery, RenderFilterQuery

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()

# ---------------------------------------------------------------------------
# Test Helpers and Generic Test Data
# ---------------------------------------------------------------------------


class TestBase(TestCase):
    #: Callable that sets up the database with the case to use in the test
    setup_case_in_db = None
    #: Set this value to the base cleaned data to patch
    base_cleaned_data = None

    def setUp(self):
        self.maxDiff = None  # show full diff
        self.__class__.setup_case_in_db()


class FilterTestBase(TestBase):
    """Base class for running the test for the ``SmallVariant`` filter queries.
    """

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


class QueryTestBase(TestBase):
    def run_get_query(self, model, cleaned_data_patch, assert_raises=None):
        patched_data = {**self.base_cleaned_data, **cleaned_data_patch}
        if assert_raises:
            with self.assertRaises(assert_raises):
                model.objects.get(**patched_data)
        else:
            return model.objects.get(**patched_data)

    def run_filter_query(self, model, cleaned_data_patch, length):
        results = model.objects.filter(**{**self.base_cleaned_data, **cleaned_data_patch})
        self.assertEquals(length, len(results))
        return results


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


def fixture_setup_case1_simple():
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


def fixture_setup_case1_var_type():
    """Setup test case 1 -- a singleton with variants for var type filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
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
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
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
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    # Variant that should be passing var_type SNV setting
    SmallVariant.objects.create(**{**basic_var, **{"position": 100, "var_type": "snv"}})
    # Variant that should be passing var_type MNV setting
    SmallVariant.objects.create(**{**basic_var, **{"position": 200, "var_type": "mnv"}})
    # Variant that should be passing var_type InDel setting
    SmallVariant.objects.create(**{**basic_var, **{"position": 300, "var_type": "indel"}})


def fixture_setup_case1_frequency():
    """Setup test case 1 -- a singleton with variants for frequency filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
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
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
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
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    # Variant that should be passing gnomad genomes frequency enabled setting
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 100,
                "gnomad_genomes_frequency": 0.001,
                "gnomad_genomes_heterozygous": 1,
                "gnomad_genomes_homozygous": 1,
                "gnomad_exomes_frequency": 0.001,
                "gnomad_exomes_heterozygous": 1,
                "gnomad_exomes_homozygous": 1,
                "exac_frequency": 0.001,
                "exac_heterozygous": 1,
                "exac_homozygous": 1,
                "thousand_genomes_frequency": 0.001,
                "thousand_genomes_heterozygous": 1,
                "thousand_genomes_homozygous": 1,
            },
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 200,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_heterozygous": 2,
                "gnomad_genomes_homozygous": 2,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_heterozygous": 2,
                "gnomad_exomes_homozygous": 2,
                "exac_frequency": 0.01,
                "exac_heterozygous": 2,
                "exac_homozygous": 2,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_heterozygous": 2,
                "thousand_genomes_homozygous": 2,
            },
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 300,
                "gnomad_genomes_frequency": 0.1,
                "gnomad_genomes_heterozygous": 3,
                "gnomad_genomes_homozygous": 3,
                "gnomad_exomes_frequency": 0.1,
                "gnomad_exomes_heterozygous": 3,
                "gnomad_exomes_homozygous": 3,
                "exac_frequency": 0.1,
                "exac_heterozygous": 3,
                "exac_homozygous": 3,
                "thousand_genomes_frequency": 0.1,
                "thousand_genomes_heterozygous": 3,
                "thousand_genomes_homozygous": 3,
            },
        }
    )


def fixture_setup_case1_effects():
    """Setup test case 1 -- a singleton with variants for effects filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
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
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
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
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    # Variant that should be passing gnomad genomes frequency enabled setting
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 100, "refseq_effect": ["missense_variant", "stop_lost"]}}
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 200, "refseq_effect": ["missense_variant", "frameshift_variant"]},
        }
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 300, "refseq_effect": ["frameshift_variant"]}}
    )


def fixture_setup_case1_effects():
    """Setup test case 1 -- a singleton with variants for effects filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
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
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
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
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    # Variant that should be passing gnomad genomes frequency enabled setting
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 100, "refseq_effect": ["missense_variant", "stop_lost"]}}
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 200, "refseq_effect": ["missense_variant", "frameshift_variant"]},
        }
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 300, "refseq_effect": ["frameshift_variant"]}}
    )


def fixture_setup_case1_genotype():
    """Setup test case 1 -- a singleton with variants for genotype filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
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
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 100, "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 200, "genotype": {"A": {"ad": 0, "dp": 30, "gq": 99, "gt": "0/0"}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 300, "genotype": {"A": {"ad": 30, "dp": 30, "gq": 99, "gt": "1/1"}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 400, "genotype": {"A": {"ad": 0, "dp": 10, "gq": 66, "gt": "./."}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 500, "genotype": {"A": {"ad": 15, "dp": 20, "gq": 33, "gt": "1/0"}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 600, "genotype": {"A": {"ad": 21, "dp": 30, "gq": 99, "gt": "0/1"}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 700, "genotype": {"A": {"ad": 9, "dp": 30, "gq": 99, "gt": "0/1"}}},
        }
    )
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{"position": 800, "genotype": {"A": {"ad": 6, "dp": 30, "gq": 99, "gt": "0/1"}}},
        }
    )


def fixture_setup_case1_blacklist():
    """Setup test case 1 -- a singleton with variants for gene blacklist filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
    )
    Hgnc.objects.create(hgnc_id="HGNC:1", symbol="AAA", name="AAA gene", entrez_id="123")
    Hgnc.objects.create(hgnc_id="HGNC:2", symbol="BBB", name="CCC gene", entrez_id="456")
    Hgnc.objects.create(hgnc_id="HGNC:3", symbol="CCC", name="BBB gene", entrez_id="789")
    # Basic variant settings.
    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
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
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    SmallVariant.objects.create(**{**basic_var, **{"position": 100, "refseq_gene_id": "123"}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 200, "refseq_gene_id": "456"}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 201, "refseq_gene_id": "456"}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 300, "refseq_gene_id": "789"}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 301, "refseq_gene_id": "789"}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 302, "refseq_gene_id": "789"}})


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
    "exac_enabled": False,
    "exac_frequency": 0.0,
    "exac_heterozygous": 0,
    "exac_homozygous": 0,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 0.0,
    "thousand_genomes_heterozygous": 0,
    "thousand_genomes_homozygous": 0,
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 0.0,
    "gnomad_exomes_heterozygous": 0,
    "gnomad_exomes_homozygous": 0,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 0.0,
    "gnomad_genomes_heterozygous": 0,
    "gnomad_genomes_homozygous": 0,
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_ab": 0,
    "A_gq": 0,
    "A_ad": 0,
    "transcripts_coding": True,
    "transcripts_noncoding": True,
    "require_in_clinvar": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
}


class TestCaseOneQueryDatabaseSwitch(FilterTestBase):
    """Test whether both RefSeq and ENSEMBL databases work."""

    setup_case_in_db = fixture_setup_case1_simple
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

    setup_case_in_db = fixture_setup_case1_simple
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


class TestCaseOneVarTypeSwitch(FilterTestBase):
    """Test switch for variant type (SNV, MNV, InDel)"""

    setup_case_in_db = fixture_setup_case1_var_type
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_var_type_none_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_none_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_none_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_mnv_filter(self):
        self.run_filter_query(
            RenderFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_mnv_export(self):
        self.run_filter_query(
            ExportFileFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_mnv_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_filter(self):
        self.run_filter_query(
            RenderFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_export(self):
        self.run_filter_query(
            ExportFileFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_indel_filter(self):
        self.run_filter_query(RenderFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1)

    def test_var_type_indel_export(self):
        self.run_filter_query(
            ExportFileFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1
        )

    def test_var_type_indel_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1
        )

    def test_var_type_all_filter(self):
        self.run_filter_query(RenderFilterQuery, {}, 3)

    def test_var_type_all_export(self):
        self.run_filter_query(ExportFileFilterQuery, {}, 3)

    def test_var_type_all_count(self):
        self.run_count_query(CountOnlyFilterQuery, {}, 3)


class TestCaseOneQueryFrequency(FilterTestBase):
    """Test switch for all four frequency filters + frequency limits + homozygous limits

    Each limit is tested for lower, critical and higher values. The data is designed
    to cover this with one test function rather than having three test functions for this
    setting. 'None' is tested within the switch or the other function. This is the value
    when no value in the interface was entered.

    tested databases:
    - gnomad exomes, gnomad genomes, exac, thousand genomes
    """

    setup_case_in_db = fixture_setup_case1_frequency
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_frequency_filters_disabled_filter(self):
        self.run_filter_query(RenderFilterQuery, {}, 3)

    def test_frequency_filters_disabled_export(self):
        self.run_filter_query(ExportFileFilterQuery, {}, 3)

    def test_frequency_filters_disabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {}, 3)

    def test_frequency_thousand_genomes_enabled_filter(self):
        self.run_filter_query(RenderFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_exac_enabled_filter(self):
        self.run_filter_query(RenderFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_filter(self):
        self.run_filter_query(RenderFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_filter(self):
        self.run_filter_query(RenderFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_thousand_genomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_thousand_genomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_genomes_limits_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_genomes_limits_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_genomes_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": 2,
            },
            2,
        )


class TestCaseOneQueryEffects(FilterTestBase):
    """Test effects settings (just an excerpt. everything else would be madness."""

    setup_case_in_db = fixture_setup_case1_effects
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_effects_none_filter(self):
        self.run_filter_query(RenderFilterQuery, {"effects": []}, 0)

    def test_effects_none_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"effects": []}, 0)

    def test_effects_none_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"effects": []}, 0)

    def test_effects_one_filter(self):
        self.run_filter_query(RenderFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_two_filter(self):
        self.run_filter_query(
            RenderFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_two_export(self):
        self.run_filter_query(
            ExportFileFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_two_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_all_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )

    def test_effects_all_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )

    def test_effects_all_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )


class TestCaseOneQueryGenotype(FilterTestBase):
    """Test effects settings (just an excerpt. everything else would be madness."""

    setup_case_in_db = fixture_setup_case1_genotype
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_genotype_gt_any_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_any_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_any_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_ref_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_ref_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_ref_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_het_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_het_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_het_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_hom_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_hom_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_hom_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_variant_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_variant_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_variant_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_non_variant_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_variant_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_variant_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_reference_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_gt_non_reference_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_gt_non_reference_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_ad_limits_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ad_limits_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ad_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ab_limits_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6)

    def test_genotype_ab_limits_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6)

    def test_genotype_ab_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6)

    def test_genotype_dp_het_limits_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7)
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8)

    def test_genotype_dp_het_limits_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7)
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8)

    def test_genotype_dp_het_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7)
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8)

    def test_genotype_dp_hom_limits_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6)
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8)

    def test_genotype_dp_hom_limits_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6)
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8)

    def test_genotype_dp_hom_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6)
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8)

    def test_genotype_gq_limits_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_gq_limits_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_gq_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_fail_ignore_filter(self):
        self.run_filter_query(RenderFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_ignore_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_ignore_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_drop_variant_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {"A_fail": "drop-variant", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15},
            4,
        )

    def test_genotype_fail_drop_variant_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {"A_fail": "drop-variant", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15},
            4,
        )

    def test_genotype_fail_drop_variant_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {"A_fail": "drop-variant", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15},
            4,
        )

    def test_genotype_fail_no_call_filter(self):
        self.run_filter_query(
            RenderFilterQuery,
            {"A_fail": "no-call", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15, "A_gt": "het"},
            6,
        )

    def test_genotype_fail_no_call_export(self):
        self.run_filter_query(
            ExportFileFilterQuery,
            {"A_fail": "no-call", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15, "A_gt": "het"},
            6,
        )

    def test_genotype_fail_no_call_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {"A_fail": "no-call", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15, "A_gt": "het"},
            6,
        )


class TestCaseOneQueryBlacklist(FilterTestBase):
    """Test effects settings (just an excerpt. everything else would be madness."""

    setup_case_in_db = fixture_setup_case1_blacklist
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_blacklist_empty_filter(self):
        self.run_filter_query(RenderFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_one_filter(self):
        self.run_filter_query(RenderFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_one_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_one_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_two_filter(self):
        self.run_filter_query(RenderFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_two_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_two_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_all_filter(self):
        self.run_filter_query(RenderFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0)

    def test_blacklist_all_export(self):
        self.run_filter_query(ExportFileFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0)

    def test_blacklist_all_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0)


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


#: A value for filtration form ``cleaned_data`` to be used for "Case 2" that lets
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
    "C_dp_het": 0,
    "C_dp_hom": 0,
    "C_ab": 0,
    "C_gq": 0,
    "C_ad": 0,
    "F_fail": "drop-variant",  # ensure complex queries are used
    "F_gt": "any",
    "F_dp_het": 0,
    "F_dp_hom": 0,
    "F_ab": 0,
    "F_gq": 0,
    "F_ad": 0,
    "M_fail": "drop-variant",  # ensure complex queries are used
    "M_gt": "any",
    "M_dp_het": 0,
    "M_dp_hom": 0,
    "M_ab": 0,
    "M_gq": 0,
    "M_ad": 0,
    "transcripts_coding": True,
    "transcripts_noncoding": True,
    "require_in_clinvar": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
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


# ---------------------------------------------------------------------------
# Tests for Case 3
# ---------------------------------------------------------------------------

# Case 3 is a singleton test case and meant for testing the Clinvar
# membership queries.  We create a new test case for this as we might be able
# to allow the user to filter out benign variants or variants of unknown
# significance.


def fixture_setup_case3():
    """Setup test case 3 -- for clinvar testing."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
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
    # Variant that should be passing for clinvar membership but has no Clinvar entry.
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 100,
                "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
                "refseq_gene_id": "1",
                "ensembl_gene_id": "ENGS1",
                "in_clinvar": True,
            },
        }
    )
    # Variant that should not be passing for clinvar membership
    SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 101,
                "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
                "refseq_gene_id": "2",
                "ensembl_gene_id": "ENGS2",
            },
        }
    )

    # Variants that have Clinvar entries with different pathogenicities
    basic_clinvar = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "start": None,
        "stop": None,
        "strand": "+",
        "variation_type": "Variant",
        "variation_id": 12345,
        "rcv": "RCV12345",
        "scv": ["RCV12345"],
        "allele_id": 12345,
        "symbol": "ENSG2",
        "hgvs_c": "some-hgvs-c",
        "hgvs_p": "home-hgvs-p",
        "molecular_consequence": "some-molecular-consequence",
        "clinical_significance": None,
        "clinical_significance_ordered": None,
        "pathogenic": 0,
        "likely_pathogenic": 0,
        "uncertain_significance": 0,
        "likely_benign": 0,
        "benign": 0,
        "review_status": "single submitter",
        "review_status_ordered": ["criteria provided"],
        "last_evaluated": "2016-06-14",
        "all_submitters": ["Some Submitter"],
        "submitters_ordered": ["Some Submitter"],
        "all_traits": ["Some trait"],
        "all_pmids": [12345],
        "inheritance_modes": "",
        "age_of_onset": "",
        "prevalence": "",
        "disease_mechanism": "",
        "origin": ["germline"],
        "xrefs": ["Some xref"],
        "dates_ordered": ["2016-06-14"],
        "multi": 1,
    }
    patho_keys = (
        "pathogenic",
        "likely_pathogenic",
        "uncertain_significance",
        "likely_benign",
        "benign",
    )
    for i, key in enumerate(patho_keys):
        SmallVariant.objects.create(
            **{
                **basic_var,
                **{
                    "position": 102 + i,
                    "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
                    "refseq_gene_id": "2",
                    "ensembl_gene_id": "ENGS2",
                    "in_clinvar": True,
                },
            }
        )
        Clinvar.objects.create(
            **{
                **basic_clinvar,
                **{
                    "position": 102 + i,
                    "start": 102 + i,
                    "stop": 102 + i,
                    "clinical_significance": key,
                    "clinical_significance_ordered": [key],
                    key: 1,
                },
            }
        )


#: A value for filtration form ``cleaned_data`` to be used for "Case 3" that lets
#: all variants through.
INCLUSIVE_CLEANED_DATA_CASE3 = {
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "effects": ["synonymous_variant"],
    "gene_blacklist": [],
    "database_select": "refseq",
    "var_type_snv": True,
    "var_type_mnv": True,
    "var_type_indel": True,
    "exac_enabled": False,
    "exac_frequency": 0.0,
    "exac_heterozygous": 0,
    "exac_homozygous": 0,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 0.0,
    "thousand_genomes_heterozygous": 0,
    "thousand_genomes_homozygous": 0,
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 0.0,
    "gnomad_exomes_heterozygous": 0,
    "gnomad_exomes_homozygous": 0,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 0.0,
    "gnomad_genomes_heterozygous": 0,
    "gnomad_genomes_homozygous": 0,
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_ab": 0,
    "A_gq": 0,
    "A_ad": 0,
    "transcripts_coding": True,
    "transcripts_noncoding": True,
    "require_in_clinvar": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": False,
    "clinvar_include_pathogenic": False,
}


class CaseThreeClinvarMembershipFilterTestMixin:
    """Base class for testing query with ClinvarMembership filter."""

    #: Tests should be run on sub classes
    __test__ = False

    setup_case_in_db = fixture_setup_case3
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE3

    check_result_rows = None
    query_class = None
    run_query_function = None

    def test_render_query_do_not_require_membership(self):
        self.run_query_function(self.query_class, {}, 7)

    def test_render_query_require_membership_include_none(self):
        self.run_query_function(self.query_class, {"require_in_clinvar": True}, 6)

    def test_render_query_require_membership_include_pathogenic(self):
        res = self.run_query_function(
            self.query_class, {"require_in_clinvar": True, "clinvar_include_pathogenic": True}, 1
        )
        if self.check_result_rows:
            self.assertEqual(res[0].position, 102)

    def test_render_query_require_membership_include_likely_pathogenic(self):
        res = self.run_query_function(
            self.query_class,
            {"require_in_clinvar": True, "clinvar_include_likely_pathogenic": True},
            1,
        )
        if self.check_result_rows:
            self.assertEqual(res[0].position, 103)

    def test_render_query_require_membership_include_uncertain_significance(self):
        res = self.run_query_function(
            self.query_class,
            {"require_in_clinvar": True, "clinvar_include_uncertain_significance": True},
            1,
        )
        if self.check_result_rows:
            self.assertEqual(res[0].position, 104)

    def test_render_query_require_membership_include_likely_benign(self):
        res = self.run_query_function(
            self.query_class, {"require_in_clinvar": True, "clinvar_include_likely_benign": True}, 1
        )
        if self.check_result_rows:
            self.assertEqual(res[0].position, 105)

    def test_render_query_require_membership_include_benign(self):
        res = self.run_query_function(
            self.query_class, {"require_in_clinvar": True, "clinvar_include_benign": True}, 1
        )
        if self.check_result_rows:
            self.assertEqual(res[0].position, 106)


class RenderQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, FilterTestBase
):
    """Test clinvar membership using RenderFilterQuery."""

    check_result_rows = True
    query_class = RenderFilterQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_filter_query


class ExportFileFilterQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, FilterTestBase
):
    """Test clinvar membership using ExportFileFilterQuery."""

    check_result_rows = True
    query_class = ExportFileFilterQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_filter_query


class CountOnlyFilterQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, FilterTestBase
):
    """Test clinvar membership using CountOnlyFilterQuery."""

    check_result_rows = False
    query_class = CountOnlyFilterQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_count_query


# ---------------------------------------------------------------------------
# Tests for querying frequency tables
# ---------------------------------------------------------------------------


def fixture_setup_frequency():
    """Setup test case 1 -- a singleton with variants for gene blacklist filter."""
    # Basic variant settings.
    basic_var = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
        "ac": None,
        "ac_afr": 1,
        "ac_amr": 0,
        "ac_eas": 0,
        "ac_fin": 0,
        "ac_nfe": 0,
        "ac_oth": 0,
        "an": None,
        "an_afr": 8726,
        "an_amr": 838,
        "an_eas": 1620,
        "an_fin": 3464,
        "an_nfe": 14996,
        "an_oth": 982,
        "hemi": None,
        "hemi_afr": None,
        "hemi_amr": None,
        "hemi_eas": None,
        "hemi_fin": None,
        "hemi_nfe": None,
        "hemi_oth": None,
        "hom": 0,
        "hom_afr": 0,
        "hom_amr": 0,
        "hom_eas": 0,
        "hom_fin": 0,
        "hom_nfe": 0,
        "hom_oth": 0,
        "popmax": "AFR",
        "ac_popmax": 1,
        "an_popmax": 8726,
        "af_popmax": 0.0001146,
        "hemi_popmax": None,
        "hom_popmax": 0,
        "af": None,
        "af_afr": 0.0001146,
        "af_amr": 0.0,
        "af_eas": 0.0,
        "af_fin": 0.0,
        "af_nfe": 0.0,
        "af_oth": 0.0,
    }

    Exac.objects.create(
        **{
            **basic_var,
            **{"ac_sas": 0, "an_sas": 323, "hemi_sas": None, "hom_sas": 0, "af_sas": 0.0},
        }
    )
    ThousandGenomes.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        ac=3,
        an=5008,
        het=3,
        hom=0,
        af=0.000058,
        af_afr=0.0,
        af_amr=0.0054,
        af_eas=0.0,
        af_eur=0.0,
        af_sas=0.0,
    )
    GnomadExomes.objects.create(
        **{
            **basic_var,
            **{
                "ac_asj": 0,
                "ac_sas": 0,
                "an_asj": 323,
                "an_sas": 932,
                "hemi_asj": None,
                "hemi_sas": None,
                "hom_asj": 0,
                "hom_sas": 0,
                "af_asj": 0.0,
                "af_sas": 0.0,
            },
        }
    )
    GnomadGenomes.objects.create(
        **{
            **basic_var,
            **{"ac_asj": 0, "an_asj": 323, "hemi_asj": None, "hom_asj": 0, "af_asj": 0.0},
        }
    )


class TestFrequencyQuery(QueryTestBase):
    """Test the queries for compound recessive heterozygous hypothesis"""

    setup_case_in_db = fixture_setup_frequency
    base_cleaned_data = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
    }

    def test_frequency_exac(self):
        obj = self.run_get_query(Exac, {})
        self.assertEquals(obj.position, 100)

    def test_frequency_exac_fail(self):
        self.run_get_query(Exac, {"position": 200}, Exac.DoesNotExist)

    def test_frequency_thousand_genomes(self):
        obj = self.run_get_query(ThousandGenomes, {})
        self.assertEquals(obj.position, 100)

    def test_frequency_thousand_genomes_fail(self):
        self.run_get_query(ThousandGenomes, {"position": 200}, ThousandGenomes.DoesNotExist)

    def test_frequency_gnomad_exomes(self):
        obj = self.run_get_query(GnomadExomes, {})
        self.assertEquals(obj.position, 100)

    def test_frequency_gnomad_exomes_fail(self):
        self.run_get_query(GnomadExomes, {"position": 200}, GnomadExomes.DoesNotExist)

    def test_frequency_gnomad_genomes(self):
        obj = self.run_get_query(GnomadGenomes, {})
        self.assertEquals(obj.position, 100)

    def test_frequency_gnomad_genomes_fail(self):
        self.run_get_query(GnomadGenomes, {"position": 200}, GnomadGenomes.DoesNotExist)


def fixture_setup_clinvar():
    # Variants that have Clinvar entries with different pathogenicities
    basic_clinvar = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "start": None,
        "stop": None,
        "strand": "+",
        "variation_type": "Variant",
        "variation_id": 12345,
        "rcv": "RCV12345",
        "scv": ["RCV12345"],
        "allele_id": 12345,
        "symbol": "ENSG2",
        "hgvs_c": "some-hgvs-c",
        "hgvs_p": "home-hgvs-p",
        "molecular_consequence": "some-molecular-consequence",
        "clinical_significance": "benign",
        "clinical_significance_ordered": ["benign"],
        "pathogenic": 0,
        "likely_pathogenic": 0,
        "uncertain_significance": 0,
        "likely_benign": 0,
        "benign": 0,
        "review_status": "single submitter",
        "review_status_ordered": ["criteria provided"],
        "last_evaluated": "2016-06-14",
        "all_submitters": ["Some Submitter"],
        "submitters_ordered": ["Some Submitter"],
        "all_traits": ["Some trait"],
        "all_pmids": [12345],
        "inheritance_modes": "",
        "age_of_onset": "",
        "prevalence": "",
        "disease_mechanism": "",
        "origin": ["germline"],
        "xrefs": ["Some xref"],
        "dates_ordered": ["2016-06-14"],
        "multi": 1,
    }
    Clinvar.objects.create(**{**basic_clinvar, **{"position": 100, "start": 100, "stop": 100}})
    Clinvar.objects.create(**{**basic_clinvar, **{"position": 200, "start": 200, "stop": 200}})


class TestClinvarQuery(QueryTestBase):
    """Test querying for clinvar"""

    setup_case_in_db = fixture_setup_clinvar
    base_cleaned_data = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
    }

    def test_clinvar_query(self):
        obj = self.run_get_query(Clinvar, {})
        self.assertEquals(obj.position, 100)

    def test_clinvar_query_fail(self):
        self.run_get_query(Clinvar, {"position": 300}, Clinvar.DoesNotExist)


def fixture_setup_geneinfo():
    Hgnc.objects.create(
        hgnc_id="HGNC:1", symbol="AAA", name="AAA gene", entrez_id="123", ensembl_gene_id="ENSG1"
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:2", symbol="BBB", name="CCC gene", entrez_id="456", ensembl_gene_id="ENSG2"
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:3", symbol="CCC", name="BBB gene", entrez_id="789", ensembl_gene_id="ENSG3"
    )
    Mim2geneMedgen.objects.create(omim_id=1, entrez_id="123")
    Mim2geneMedgen.objects.create(omim_id=2, entrez_id="123")
    Mim2geneMedgen.objects.create(omim_id=3, entrez_id="789")
    Hpo.objects.create(database_id="OMIM:1", hpo_id="HP:001")
    Hpo.objects.create(database_id="OMIM:1", hpo_id="HP:002")
    Hpo.objects.create(database_id="OMIM:3", hpo_id="HP:003")


class TestGeneinfoQuery(QueryTestBase):
    """Test querying Hgnc"""

    setup_case_in_db = fixture_setup_geneinfo
    base_cleaned_data = {}

    def test_hgnc_query_refseq(self):
        """Test hgnc query with refseq id"""
        obj = self.run_get_query(Hgnc, {"entrez_id": "123"})
        self.assertEquals(obj.symbol, "AAA")

    def test_hgnc_query_refseq_fail(self):
        """Test hgnc query with refseq id failing"""
        self.run_get_query(Hgnc, {"entrez_id": "000"}, Hgnc.DoesNotExist)

    def test_hgnc_query_ensembl(self):
        """Test hgnc query with ensembl gene id"""
        obj = self.run_get_query(Hgnc, {"ensembl_gene_id": "ENSG1"})
        self.assertEquals(obj.symbol, "AAA")

    def test_hgnc_query_ensembl_fail(self):
        """Test hgnc query with ensembl gene id failing"""
        self.run_get_query(Hgnc, {"ensembl_gene_id": "ENSG0"}, Hgnc.DoesNotExist)

    def test_mim2genemedgen(self):
        """Test mim2gene medgen query. only works with refseq id"""
        self.run_filter_query(Mim2geneMedgen, {"entrez_id": "123"}, 2)

    def test_mim2genemedgen_empty_list(self):
        """Test mem2gene medgen query with no results"""
        self.run_filter_query(Mim2geneMedgen, {"entrez_id": "000"}, 0)

    def test_hpo(self):
        """Test hpo query"""
        self.run_filter_query(Hpo, {"database_id": "OMIM:1"}, 2)

    def test_hpo_empty(self):
        """Test hpo query with empty results"""
        self.run_filter_query(Hpo, {"database_id": "OMIM:2"}, 0)


def fixture_setup_pathways():
    """Setup case for pathway tests"""
    kegginfo1 = KeggInfo.objects.create(kegg_id="hsa1", name="Pathway1")
    kegginfo2 = KeggInfo.objects.create(kegg_id="hsa2", name="Pathway2")
    EnsemblToKegg.objects.create(gene_id="ENSG1", kegginfo_id=kegginfo1.pk)
    EnsemblToKegg.objects.create(gene_id="ENSG1", kegginfo_id=kegginfo2.pk)
    EnsemblToKegg.objects.create(gene_id="ENSG2", kegginfo_id=kegginfo2.pk)
    RefseqToKegg.objects.create(gene_id="123", kegginfo_id=kegginfo1.pk)
    RefseqToKegg.objects.create(gene_id="456", kegginfo_id=kegginfo1.pk)
    RefseqToKegg.objects.create(gene_id="456", kegginfo_id=kegginfo2.pk)


class TestPathwayQuery(QueryTestBase):
    """Test pathways query"""

    setup_case_in_db = fixture_setup_pathways
    base_cleaned_data = {}

    def test_ensembltokegg_query(self):
        self.run_filter_query(EnsemblToKegg, {"gene_id": "ENSG1"}, 2)

    def test_ensembltokegg_empty(self):
        self.run_filter_query(EnsemblToKegg, {"gene_id": "ENSG0"}, 0)

    def test_refseqtokegg_query(self):
        self.run_filter_query(RefseqToKegg, {"gene_id": "123"}, 1)

    def test_refseqtokegg_empty(self):
        self.run_filter_query(RefseqToKegg, {"gene_id": "000"}, 0)

    def test_kegginfo_ensembl_query(self):
        ensemblkegg = EnsemblToKegg.objects.filter(gene_id="ENSG1").first()
        obj = self.run_get_query(KeggInfo, {"id": ensemblkegg.kegginfo_id})
        self.assertEquals(obj.name, "Pathway1")

    def test_kegginfo_refseq_query(self):
        refseqkegg = RefseqToKegg.objects.filter(gene_id="456")
        obj = self.run_get_query(KeggInfo, {"id": refseqkegg[0].kegginfo_id})
        self.assertEquals(obj.name, "Pathway1")
        obj = self.run_get_query(KeggInfo, {"id": refseqkegg[1].kegginfo_id})
        self.assertEquals(obj.name, "Pathway2")

    def test_kegginfo_fail(self):
        self.run_get_query(KeggInfo, {"id": 12345678}, KeggInfo.DoesNotExist)
