"""Tests for performing direct queries via the Django models classes.
"""

from clinvar.models import Clinvar
from frequencies.models import Exac, ThousandGenomes, GnomadExomes, GnomadGenomes
from geneinfo.models import Hgnc, Mim2geneMedgen, Hpo
from pathways.models import KeggInfo, EnsemblToKegg, RefseqToKegg

from ._helpers import TestBase

# ---------------------------------------------------------------------------
# Test Helper Code
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests for querying Clinvar table
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests for querying HGNC Gene Info table
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests for querying Pathway table
# ---------------------------------------------------------------------------


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
