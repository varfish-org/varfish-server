"""Tests for the ``models_support`` module.

Remarks:

- VCF export is only tested for case one at the moment, as it shares a major part of the implementation with
  the render and tabular file export query.
"""

from clinvar.models import Clinvar
from geneinfo.models import Hgnc, Acmg
from projectroles.models import Project
from variants.models import (
    SmallVariant,
    Case,
    CaseAwareProject,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
    SmallVariantSummary,
)
from dbsnp.models import Dbsnp

from ._helpers import TestBase, SQLALCHEMY_ENGINE
from ._fixtures import (
    PROJECT_DICT,
    fixture_setup_case1_simple,
    SMALL_VARIANT_CASE1_DEFAULTS,
    SMALL_VARIANT_SUMMARY_CASE1_DEFAULTS,
    CLINVAR_DEFAULTS,
    CLINVAR_FORM_DEFAULTS,
)
from ..models_support import (
    PrefetchClinvarReportQuery,
    ExportTableFileFilterQuery,
    CountOnlyFilterQuery,
    PrefetchFilterQuery,
    ExportVcfFileFilterQuery,
    LoadPrefetchedFilterQuery,
    ProjectCasesLoadPrefetchedFilterQuery,
)

# ---------------------------------------------------------------------------
# Test Helpers and Generic Test Data
# ---------------------------------------------------------------------------


class FilterTestBase(TestBase):
    """Base class for running the test for the ``SmallVariant`` filter queries.
    """

    def _get_fetch_and_query(self, query_class, cleaned_data_patch, query_type):
        engine = SQLALCHEMY_ENGINE
        patched_cleaned_data = {**self.base_cleaned_data, **cleaned_data_patch}

        def fetch_case_and_query():
            """Helper function that fetches the ``case`` by UUID and then generates the
            appropriate query.
            """
            if query_type == "case":
                obj = Case.objects.get(sodar_uuid=patched_cleaned_data["case_uuid"])
                previous_query = patched_cleaned_data.get("smallvariantquery_id", None)
            else:  # query_type == "project"
                obj = CaseAwareProject.objects.first()
                previous_query = patched_cleaned_data.get("projectcasessmallvariantquery_id", None)
            if previous_query:
                query = query_class(obj, engine, previous_query)
            else:
                query = query_class(obj, engine)
            return query.run(patched_cleaned_data)

        return fetch_case_and_query

    def run_filter_query(
        self, query_class, cleaned_data_patch, length, assert_raises=None, query_type="case"
    ):
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
        fetch_case_and_query = self._get_fetch_and_query(
            query_class, cleaned_data_patch, query_type
        )
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            results = list(fetch_case_and_query())
            self.assertEquals(length, len(results))
            return results

    def run_count_query(
        self, query_class, kwargs_patch, length, assert_raises=None, query_type="case"
    ):
        """Run query returning a result record count instead of result records."""
        fetch_case_and_query = self._get_fetch_and_query(query_class, kwargs_patch, query_type)
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            result = fetch_case_and_query()
            self.assertEquals(length, result)
            return result


# ---------------------------------------------------------------------------
# XFilterQuery: Tests for Case 1
# ---------------------------------------------------------------------------


def fixture_setup_case1_var_type():
    """Setup test case 1 -- a singleton with variants for var type filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
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


def fixture_setup_case1_dbsnp():
    """Setup test case 1 -- a singleton with variants for var type filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    coordinates = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
    }
    # Basic variant settings.
    basic_var = {
        "case_id": case.pk,
        **coordinates,
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
    SmallVariant.objects.create(**{**basic_var, "position": 100})
    # Variant that should be passing var_type MNV setting
    SmallVariant.objects.create(**{**basic_var, "position": 200})
    # Variant that should be passing var_type InDel setting
    SmallVariant.objects.create(**{**basic_var, "position": 300})

    Dbsnp.objects.create(**{**coordinates, "position": 100, "rsid": "rs001"})
    Dbsnp.objects.create(**{**coordinates, "position": 300, "rsid": "rs003"})


def fixture_setup_case1_frequency():
    """Setup test case 1 -- a singleton with variants for frequency filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    # Basic variant settings.
    basic_var = {**SMALL_VARIANT_CASE1_DEFAULTS, **{"case_id": case.pk}}

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
    SmallVariantSummary.objects.create(
        **{
            **SMALL_VARIANT_SUMMARY_CASE1_DEFAULTS,
            **{"position": 100, "count_het": 1, "count_hom_alt": 1},
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
    SmallVariantSummary.objects.create(
        **{
            **SMALL_VARIANT_SUMMARY_CASE1_DEFAULTS,
            **{"position": 200, "count_het": 2, "count_hom_alt": 2},
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
    SmallVariantSummary.objects.create(
        **{
            **SMALL_VARIANT_SUMMARY_CASE1_DEFAULTS,
            **{"position": 300, "count_het": 3, "count_hom_alt": 3},
        }
    )


def fixture_setup_case1_effects():
    """Setup test case 1 -- a singleton with variants for effects filter."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
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
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
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
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
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
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:1", symbol="AAA", name="AAA gene", entrez_id="123", ensembl_gene_id="ENSGAAA"
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:2", symbol="BBB", name="CCC gene", entrez_id="456", ensembl_gene_id="ENSGCCC"
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:3", symbol="CCC", name="BBB gene", entrez_id="789", ensembl_gene_id="ENSGBBB"
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

    SmallVariant.objects.create(
        **{**basic_var, **{"position": 100, "refseq_gene_id": "123", "ensembl_gene_id": "ENSGAAA"}}
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 200, "refseq_gene_id": "456", "ensembl_gene_id": "ENSGCCC"}}
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 201, "refseq_gene_id": "456", "ensembl_gene_id": "ENSGCCC"}}
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 300, "refseq_gene_id": "789", "ensembl_gene_id": "ENSGBBB"}}
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 301, "refseq_gene_id": "789", "ensembl_gene_id": "ENSGBBB"}}
    )
    SmallVariant.objects.create(
        **{**basic_var, **{"position": 302, "refseq_gene_id": "789", "ensembl_gene_id": "ENSGBBB"}}
    )


def fixture_setup_case1_load():
    """Setup test case 1 -- a singleton with variants for gene blacklist filter."""
    project = CaseAwareProject.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
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

    a = SmallVariant.objects.create(
        **{
            **basic_var,
            **{
                "position": 100,
                "refseq_gene_id": "123",
                "ensembl_gene_id": "ENSGAAA",
                "ensembl_effect": ["synonymous_variant"],
                "refseq_effect": ["stop_gained"],
            },
        }
    )
    b = SmallVariant.objects.create(
        **{**basic_var, **{"position": 200, "refseq_gene_id": "456", "ensembl_gene_id": "ENSGCCC"}}
    )
    c = SmallVariant.objects.create(
        **{**basic_var, **{"position": 201, "refseq_gene_id": "456", "ensembl_gene_id": "ENSGCCC"}}
    )

    smallvariantquery = SmallVariantQuery.objects.create(
        case=case, form_id="123", form_version=1, query_settings=[], name="test", public=False
    )
    smallvariantquery.query_results.add(a, c)

    projectcasessmallvariantquery = ProjectCasesSmallVariantQuery.objects.create(
        project=project, form_id="123", form_version=1, query_settings=[], name="test", public=False
    )
    projectcasessmallvariantquery.query_results.add(a, b)

    Acmg.objects.create(entrez_id="123", ensembl_gene_id="ENSGAAA", symbol="AAA")


#: A value for filtration form ``cleaned_data`` to be used for "Case 1" that lets
#: all variants through.
INCLUSIVE_CLEANED_DATA_CASE1 = {
    **CLINVAR_FORM_DEFAULTS,
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "effects": ["synonymous_variant"],
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
    "inhouse_enabled": False,
    "inhouse_carriers": 0,
    "inhouse_heterozygous": 0,
    "inhouse_homozygous": 0,
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
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "display_hgmd_public_membership": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
    # Gene lists
    "gene_blacklist": [],
    "genomic_region": [],
    "gene_whitelist": [],
}


class TestCaseOneLoadResults(FilterTestBase):

    setup_case_in_db = fixture_setup_case1_load
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_load_case_results(self):
        smallvariantquery = SmallVariantQuery.objects.first()
        results = self.run_filter_query(
            LoadPrefetchedFilterQuery, {"smallvariantquery_id": smallvariantquery.id}, 2
        )
        self.assertEqual(results[0].acmg_symbol, "AAA")
        self.assertIsNone(results[1].acmg_symbol)
        self.assertTrue(results[0].effect_ambiguity)
        self.assertFalse(results[1].effect_ambiguity)

    def test_load_project_cases_results(self):
        projectcasessmallvariantquery = ProjectCasesSmallVariantQuery.objects.first()
        results = self.run_filter_query(
            ProjectCasesLoadPrefetchedFilterQuery,
            {"projectcasessmallvariantquery_id": projectcasessmallvariantquery.id},
            2,
            query_type="project",
        )
        self.assertEqual(results[0].acmg_symbol, "AAA")
        self.assertIsNone(results[1].acmg_symbol)
        self.assertTrue(results[0].effect_ambiguity)
        self.assertFalse(results[1].effect_ambiguity)


class TestCaseOneQueryDatabaseSwitch(FilterTestBase):
    """Test whether both RefSeq and ENSEMBL databases work."""

    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_base_query_refseq_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_refseq_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_ensembl_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_ensembl_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"database_select": "refseq"}, 1)

    def test_base_query_ensembl_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_ensembl_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"database_select": "ensembl"}, 1)

    def test_base_query_refseq_check_gene_symbol(self):
        fetch_case_and_query = self._get_fetch_and_query(
            PrefetchFilterQuery, {"database_select": "refseq"}, "case"
        )
        results = list(fetch_case_and_query())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].symbol, "AAA")


class TestCaseOneQueryNotInDbsnp(FilterTestBase):
    """Test whether both RefSeq and ENSEMBL databases work."""

    setup_case_in_db = fixture_setup_case1_dbsnp
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_base_query_not_in_dbsnp_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"remove_if_in_dbsnp": True}, 1)

    def test_base_query_not_in_dbsnp_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"remove_if_in_dbsnp": True}, 1)

    # ExportVcfFileFilterQuery doesn't join dbsnp, so nothing is returned
    def test_base_query_not_in_dbsnp_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"remove_if_in_dbsnp": True}, 0)

    def test_base_query_not_in_dbsnp_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"remove_if_in_dbsnp": True}, 1)

    def test_base_query_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {}, 3)

    def test_base_query_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {}, 3)

    def test_base_query_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {}, 3)

    def test_base_query_count(self):
        self.run_count_query(CountOnlyFilterQuery, {}, 3)


class TestCaseOneQueryCase(FilterTestBase):
    """Test with correct and incorrect case UUID"""

    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_query_case_correct_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {}, 1)

    def test_query_case_correct_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {}, 1)

    def test_query_case_correct_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {}, 1)

    def test_query_case_correct_count(self):
        self.run_count_query(CountOnlyFilterQuery, {}, 1)

    def test_query_case_incorrect_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )

    def test_query_case_incorrect_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {"case_uuid": "88888888-8888-8888-8888-888888888888"},
            1,
            Case.DoesNotExist,
        )

    def test_query_case_incorrect_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_none_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {"var_type_snv": False, "var_type_mnv": False, "var_type_indel": False},
            0,
        )

    def test_var_type_none_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_mnv_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_mnv_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_mnv_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"var_type_snv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_snv_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"var_type_mnv": False, "var_type_indel": False}, 1
        )

    def test_var_type_indel_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1
        )

    def test_var_type_indel_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1
        )

    def test_var_type_indel_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1
        )

    def test_var_type_indel_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"var_type_snv": False, "var_type_mnv": False}, 1
        )

    def test_var_type_all_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {}, 3)

    def test_var_type_all_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {}, 3)

    def test_var_type_all_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {}, 3)

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
        self.run_filter_query(PrefetchFilterQuery, {}, 3)

    def test_frequency_filters_disabled_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {}, 3)

    def test_frequency_filters_disabled_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {}, 3)

    def test_frequency_filters_disabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {}, 3)

    def test_frequency_thousand_genomes_enabled_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_thousand_genomes_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"thousand_genomes_enabled": True}, 0)

    def test_frequency_exac_enabled_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_exac_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"exac_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_exomes_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gnomad_exomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_gnomad_genomes_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gnomad_genomes_enabled": True}, 0)

    def test_frequency_inhouse_enabled_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_inhouse_enabled_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_inhouse_enabled_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_inhouse_enabled_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"inhouse_enabled": True}, 0)

    def test_frequency_thousand_genomes_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_thousand_genomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": 0.01,
                "exac_homozygous": None,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_frequency_exac_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_exomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.01,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_frequency_gnomad_genomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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

    # NB: we use carriers instead of carriers for in-house DB

    def test_carriers_inhouse_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_carriers_inhouse_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_carriers_inhouse_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_carriers_inhouse_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": 4,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": 2,
                "thousand_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_thousand_genomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": 2,
                "exac_heterozygous": None,
            },
            2,
        )

    def test_homozygous_exac_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": 2,
                "gnomad_exomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_exomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": None,
                "gnomad_genomes_homozygous": 2,
                "gnomad_genomes_heterozygous": None,
            },
            2,
        )

    def test_homozygous_gnomad_genomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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

    def test_homozygous_inhouse_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_homozygous_inhouse_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": 2,
                "inhouse_heterozygous": None,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": None,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_thousand_genomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "exac_enabled": True,
                "exac_frequency": None,
                "exac_homozygous": None,
                "exac_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_exac_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
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
            ExportTableFileFilterQuery,
            {
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": None,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_gnomad_exomes_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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

    def test_heterozygous_inhouse_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )

    def test_heterozygous_inhouse_limits_count(self):
        self.run_count_query(
            CountOnlyFilterQuery,
            {
                "inhouse_enabled": True,
                "inhouse_carriers": None,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": 2,
            },
            2,
        )


class TestCaseOneQueryEffects(FilterTestBase):
    """Test effects settings (just an excerpt. everything else would be madness."""

    setup_case_in_db = fixture_setup_case1_effects
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE1

    def test_effects_none_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"effects": []}, 0)

    def test_effects_none_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"effects": []}, 0)

    def test_effects_none_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"effects": []}, 0)

    def test_effects_none_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"effects": []}, 0)

    def test_effects_one_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_one_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"effects": ["missense_variant"]}, 2)

    def test_effects_two_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_two_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_two_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_two_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"effects": ["stop_lost", "frameshift_variant"]}, 3
        )

    def test_effects_all_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )

    def test_effects_all_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )

    def test_effects_all_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
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
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_any_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_any_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_any_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "any"}, 8)

    def test_genotype_gt_ref_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_ref_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_ref_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_ref_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "ref"}, 1)

    def test_genotype_gt_het_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_het_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_het_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_het_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "het"}, 5)

    def test_genotype_gt_hom_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_hom_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_hom_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_hom_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "hom"}, 1)

    def test_genotype_gt_variant_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_variant_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_variant_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_variant_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "variant"}, 6)

    def test_genotype_gt_non_variant_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_variant_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_variant_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_variant_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "non-variant"}, 2)

    def test_genotype_gt_non_reference_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_gt_non_reference_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_gt_non_reference_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_gt_non_reference_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_gt": "non-reference"}, 7)

    def test_genotype_ad_limits_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ad_limits_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ad_limits_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ad_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_ad": 15}, 5)

    def test_genotype_ab_limits_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6)

    def test_genotype_ab_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6
        )

    def test_genotype_ab_limits_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6)

    def test_genotype_ab_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_ab": 0.3}, 6)

    def test_genotype_dp_het_limits_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7)
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8)

    def test_genotype_dp_het_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7
        )
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8
        )

    def test_genotype_dp_het_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7
        )
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8
        )

    def test_genotype_dp_het_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 21}, 7)
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_het": 20}, 8)

    def test_genotype_dp_hom_limits_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6)
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8)

    def test_genotype_dp_hom_limits_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6
        )
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8
        )

    def test_genotype_dp_hom_limits_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6
        )
        self.run_filter_query(
            ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8
        )

    def test_genotype_dp_hom_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 31}, 6)
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_dp_hom": 30}, 8)

    def test_genotype_gq_limits_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_gq_limits_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_gq_limits_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_gq_limits_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "drop-variant", "A_gq": 66}, 7)

    def test_genotype_fail_ignore_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_ignore_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_ignore_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_ignore_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"A_fail": "ignore"}, 8)

    def test_genotype_fail_drop_variant_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery,
            {"A_fail": "drop-variant", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15},
            4,
        )

    def test_genotype_fail_drop_variant_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {"A_fail": "drop-variant", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15},
            4,
        )

    def test_genotype_fail_drop_variant_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
            PrefetchFilterQuery,
            {"A_fail": "no-call", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15, "A_gt": "het"},
            6,
        )

    def test_genotype_fail_no_call_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery,
            {"A_fail": "no-call", "A_dp": 20, "A_ab": 0.3, "A_gq": 20, "A_ad": 15, "A_gt": "het"},
            6,
        )

    def test_genotype_fail_no_call_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery,
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
        self.run_filter_query(PrefetchFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_empty_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": []}, 6)

    def test_blacklist_one_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_one_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_one_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_one_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": ["AAA"]}, 5)

    def test_blacklist_two_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_two_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_two_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_two_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": ["AAA", "BBB"]}, 3)

    def test_blacklist_all_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0)

    def test_blacklist_all_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0
        )

    def test_blacklist_all_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0
        )

    def test_blacklist_all_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"gene_blacklist": ["AAA", "BBB", "CCC"]}, 0)

    def test_genomic_region_empty_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"genomic_region": []}, 6)

    def test_genomic_region_empty_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"genomic_region": []}, 6)

    def test_genomic_region_empty_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"genomic_region": []}, 6)

    def test_genomic_region_empty_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"genomic_region": []}, 6)

    def test_genomic_region_one_region_filter(self):
        self.run_filter_query(PrefetchFilterQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_one_region_export(self):
        self.run_filter_query(ExportTableFileFilterQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_one_region_vcf(self):
        self.run_filter_query(ExportVcfFileFilterQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_one_region_count(self):
        self.run_count_query(CountOnlyFilterQuery, {"genomic_region": [("1", 1, 199)]}, 1)

    def test_genomic_region_two_regions_filter(self):
        self.run_filter_query(
            PrefetchFilterQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4
        )

    def test_genomic_region_two_regions_export(self):
        self.run_filter_query(
            ExportTableFileFilterQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4
        )

    def test_genomic_region_two_regions_vcf(self):
        self.run_filter_query(
            ExportVcfFileFilterQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4
        )

    def test_genomic_region_two_regions_count(self):
        self.run_count_query(
            CountOnlyFilterQuery, {"genomic_region": [("1", 1, 199), ("1", 300, 399)]}, 4
        )


# ---------------------------------------------------------------------------
# XFilterQuery: Tests for Case 2
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
            {
                "sex": 1,
                "father": "F",
                "mother": "M",
                "patient": "C",
                "affected": 2,
                "has_gt_entries": True,
            },
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "F",
                "affected": 1,
                "has_gt_entries": True,
            },
            {
                "sex": 2,
                "father": "0",
                "mother": "0",
                "patient": "M",
                "affected": 1,
                "has_gt_entries": True,
            },
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
    **CLINVAR_FORM_DEFAULTS,
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "effects": ["synonymous_variant"],
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
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "display_hgmd_public_membership": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
    # Gene lists
    "gene_blacklist": [],
    "gene_whitelist": [],
    "genomic_region": [],
}


class TestCaseTwoDominantQuery(FilterTestBase):
    """Test the queries for dominant/de novo hypothesis"""

    setup_case_in_db = fixture_setup_case2
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE2

    cleaned_data_patch = {"C_gt": "het", "F_gt": "ref", "M_gt": "ref"}

    def test_query_de_novo_filter(self):
        res = self.run_filter_query(PrefetchFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 100)

    def test_query_de_novo_export(self):
        res = self.run_filter_query(ExportTableFileFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 100)

    def test_query_de_novo_count(self):
        self.run_count_query(CountOnlyFilterQuery, self.cleaned_data_patch, 1)


class TestCaseTwoRecessiveHomozygousQuery(FilterTestBase):
    """Test the queries for recessive homozygous hypothesis"""

    setup_case_in_db = fixture_setup_case2
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE2

    cleaned_data_patch = {"C_gt": "hom", "F_gt": "het", "M_gt": "het"}

    def test_query_recessive_hom_filter(self):
        res = self.run_filter_query(PrefetchFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 101)

    def test_query_recessive_hom_export(self):
        res = self.run_filter_query(ExportTableFileFilterQuery, self.cleaned_data_patch, 1)
        self.assertEqual(res[0].position, 101)

    def test_query_recessive_hom_count(self):
        self.run_count_query(CountOnlyFilterQuery, self.cleaned_data_patch, 1)


class TestCaseTwoCompoundRecessiveHeterozygousQuery(FilterTestBase):
    """Test the queries for compound recessive heterozygous hypothesis"""

    setup_case_in_db = fixture_setup_case2
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CASE2

    cleaned_data_patch = {"compound_recessive_enabled": True}

    def test_query_compound_het_prefetch_filter(self):
        res = self.run_filter_query(PrefetchFilterQuery, self.cleaned_data_patch, 2)
        self.assertEqual(res[0].position, 102)
        self.assertEqual(res[1].position, 103)

    def test_query_compound_het_export(self):
        res = self.run_filter_query(ExportTableFileFilterQuery, self.cleaned_data_patch, 2)
        self.assertEqual(res[0].position, 102)
        self.assertEqual(res[1].position, 103)

    def test_query_compound_het_count(self):
        self.run_count_query(CountOnlyFilterQuery, self.cleaned_data_patch, 2)

    def test_query_compound_het_load_prefetched_filter(self):
        case = Case.objects.first()
        query = SmallVariantQuery.objects.create(
            case=case, user=None, form_id="1", form_version=1, query_settings={}, public=False
        )
        res = self.run_filter_query(PrefetchFilterQuery, self.cleaned_data_patch, 2)
        query.query_results.add(res[0].id, res[1].id)
        res = self.run_filter_query(
            LoadPrefetchedFilterQuery,
            {**self.cleaned_data_patch, "smallvariantquery_id": query.id},
            2,
        )
        self.assertEqual(res[0].position, 102)
        self.assertEqual(res[1].position, 103)


# ---------------------------------------------------------------------------
# XFilterQuery: Tests for Case 3
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
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
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
        **CLINVAR_DEFAULTS,
        "clinical_significance": "pathogenic",
        "clinical_significance_ordered": ["pathogenic"],
        "review_status": "practice guideline",
        "review_status_ordered": ["practice guideline"],
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
    **CLINVAR_FORM_DEFAULTS,
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "effects": ["synonymous_variant"],
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
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": False,
    "clinvar_include_pathogenic": False,
    # Gene lists
    "gene_blacklist": [],
    "gene_whitelist": [],
    "genomic_region": [],
}


class CaseThreeClinvarMembershipFilterTestMixin:
    """Base class for testing query with ClinvarMembership filter."""

    # TODO: add similar tests for HgmdPublicLocus

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
    query_class = PrefetchFilterQuery

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_query_function = self.run_filter_query


class ExportFileFilterQueryTestCaseThreeClinvarMembershipFilter(
    CaseThreeClinvarMembershipFilterTestMixin, FilterTestBase
):
    """Test clinvar membership using ExportFileFilterQuery."""

    check_result_rows = True
    query_class = ExportTableFileFilterQuery

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
# ClinvarReportQuery: Case 4
# ---------------------------------------------------------------------------

# We use the singleton case 1 and construct different cases with clinvar annotation.

#: Defaults including all variants for case 4.
INCLUSIVE_CLEANED_DATA_CLINVAR_CASE4 = {
    **CLINVAR_FORM_DEFAULTS,
    "case_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
}


class ClinvarReportQueryTestCaseFour(TestBase):

    setup_case_in_db = fixture_setup_case1_simple
    base_cleaned_data = INCLUSIVE_CLEANED_DATA_CLINVAR_CASE4

    def _setup_clinvar_entry(self, cleaned_data_patch):
        """Setup patched Clinvar entry with values from ``clinvar_patch``.

        This function will take care of patching the correct position into the defaults.
        """
        clinvar_values = {
            **CLINVAR_DEFAULTS,
            "position": 100,
            "start": 100,
            "stop": 100,
            **cleaned_data_patch,
        }
        # Fill in significance and review status if missing (not included in patch)
        if not clinvar_values["clinical_significance_ordered"]:
            clinvar_values["clinical_significance_ordered"] = ["pathogenic"]
        if not clinvar_values["clinical_significance"]:
            clinvar_values["clinical_significance"] = "pathogenic"
        if not clinvar_values["review_status_ordered"]:
            clinvar_values["review_status_ordered"] = ["practice guideline"]
        if not clinvar_values["review_status"]:
            clinvar_values["review_status"] = clinvar_values["review_status_ordered"][0]
        Clinvar.objects.create(**clinvar_values)

    def _run_test(self, clinvar_patch, form_data_patch, expected_result_count):
        """Helper function for setting up the database, form data, and then running the test"""
        # Test-specific set-up
        self._setup_clinvar_entry(clinvar_patch)
        # Call function under test
        engine = SQLALCHEMY_ENGINE
        patched_cleaned_data = {**self.base_cleaned_data, **form_data_patch}
        case = Case.objects.get(sodar_uuid=patched_cleaned_data["case_uuid"])
        query = PrefetchClinvarReportQuery(case, engine)
        result = list(query.run(patched_cleaned_data))
        # Compare result.
        self.assertEquals(len(result), expected_result_count)

    # TODO: conver to use ``test_snake_case``

    def testPathogenicInclude(self):
        self._run_test({"pathogenic": 1}, {"clinvar_include_pathogenic": True}, 1)

    def testPathogenicNoInclude(self):
        self._run_test({"pathogenic": 0}, {"clinvar_include_pathogenic": True}, 0)

    def testLikelyPathogenicInclude(self):
        self._run_test({"likely_pathogenic": 1}, {"clinvar_include_likely_pathogenic": True}, 1)

    def testLikelyPathogenicNoInclude(self):
        self._run_test({"likely_pathogenic": 0}, {"clinvar_include_likely_pathogenic": True}, 0)

    def testUncertainSignificanceInclude(self):
        self._run_test(
            {"uncertain_significance": 1}, {"clinvar_include_uncertain_significance": True}, 1
        )

    def testUncertainSignificanceNoInclude(self):
        self._run_test(
            {"uncertain_significance": 0}, {"clinvar_include_uncertain_significance": True}, 0
        )

    def testLikelyBenignInclude(self):
        self._run_test({"likely_benign": 1}, {"clinvar_include_likely_benign": True}, 1)

    def testLikelyBenignNoInclude(self):
        self._run_test({"likely_benign": 0}, {"clinvar_include_likely_benign": True}, 0)

    def testBenignInclude(self):
        self._run_test({"benign": 1}, {"clinvar_include_benign": True}, 1)

    def testBenignNoInclude(self):
        self._run_test({"benign": 0}, {"clinvar_include_benign": True}, 0)

    def testGermlineInclude(self):
        self._run_test(
            {"origin": ["germline"]},
            {"clinvar_origin_germline": True, "clinvar_origin_somatic": False},
            1,
        )

    def testGermlineNoInclude(self):
        self._run_test(
            {"origin": ["germline"]},
            {"clinvar_origin_germline": False, "clinvar_origin_somatic": True},
            0,
        )

    def testSomaticInclude(self):
        self._run_test(
            {"origin": ["somatic"]},
            {"clinvar_origin_germline": False, "clinvar_origin_somatic": True},
            1,
        )

    def testSomaticNoInclude(self):
        self._run_test(
            {"origin": ["somatic"]},
            {"clinvar_origin_germline": True, "clinvar_origin_somatic": False},
            0,
        )

    def testPracticeGuidelineInclude(self):
        self._run_test(
            {"review_status_ordered": ["practice guideline"]},
            {"clinvar_status_practice_guideline": True},
            1,
        )

    def testPracticeGuidelineNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["practice guideline"]},
            {"clinvar_status_practice_guideline": False},
            0,
        )

    def testExpertPanelInclude(self):
        self._run_test(
            {"review_status_ordered": ["reviewed by expert panel"]},
            {"clinvar_status_expert_panel": True},
            1,
        )

    def testExpertPanelNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["reviewed by expert panel"]},
            {"clinvar_status_expert_panel": False},
            0,
        )

    def testMultipleNoConflictInclude(self):
        self._run_test(
            {"review_status_ordered": ["criteria provided, multiple submitters, no conflicts"]},
            {"clinvar_status_multiple_no_conflict": True},
            1,
        )

    def testMultipleNoConflictNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["criteria provided, multiple submitters, no conflicts"]},
            {"clinvar_status_multiple_no_conflict": False},
            0,
        )

    def testSingleInclude(self):
        self._run_test(
            {"review_status_ordered": ["criteria provided, single submitter"]},
            {"clinvar_status_single": True},
            1,
        )

    def testSingleNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["criteria provided, single submitter"]},
            {"clinvar_status_single": False},
            0,
        )

    def testConflictInclude(self):
        self._run_test(
            {"review_status_ordered": ["criteria provided, conflicting interpretations"]},
            {"clinvar_status_conflict": True},
            1,
        )

    def testConflictNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["criteria provided, conflicting interpretations"]},
            {"clinvar_status_conflict": False},
            0,
        )

    def testNoCriteriaInclude(self):
        self._run_test(
            {"review_status_ordered": ["no assertion criteria provided"]},
            {"clinvar_status_no_criteria": True},
            1,
        )

    def testNoCriteriaNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["no assertion criteria provided"]},
            {"clinvar_status_no_criteria": False},
            0,
        )

    def testNoAssertionInclude(self):
        self._run_test(
            {"review_status_ordered": ["no assertion provided"]},
            {"clinvar_status_no_assertion": True},
            1,
        )

    def testNoAssertionNoInclude(self):
        self._run_test(
            {"review_status_ordered": ["no assertion provided"]},
            {"clinvar_status_no_assertion": False},
            0,
        )
