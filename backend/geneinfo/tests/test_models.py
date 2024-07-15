"""Tests for Model queries to the ``geneinfo`` models."""

from variants.tests.helpers import QueryTestBase

from ..models import Hgnc, Hpo, Mim2geneMedgen
from .factories import HgncFactory, HpoFactory, Mim2geneMedgenFactory


class TestGeneinfoQuery(QueryTestBase):
    """Test querying Hgnc"""

    def test_hgnc_query_refseq(self):
        created = HgncFactory.create()
        obj = self.run_get_query(Hgnc, {"entrez_id": created.entrez_id})
        self.assertEquals(obj.symbol, created.symbol)

    def test_hgnc_query_refseq_fail(self):
        created = HgncFactory.create()
        self.run_get_query(Hgnc, {"entrez_id": created.entrez_id + "MISSING"}, Hgnc.DoesNotExist)

    def test_hgnc_query_ensembl(self):
        created = HgncFactory.create()
        obj = self.run_get_query(Hgnc, {"ensembl_gene_id": created.ensembl_gene_id})
        self.assertEquals(obj.symbol, created.symbol)

    def test_hgnc_query_ensembl_fail(self):
        created = HgncFactory.create()
        self.run_get_query(
            Hgnc, {"ensembl_gene_id": created.ensembl_gene_id + "MISSING"}, Hgnc.DoesNotExist
        )

    def test_mim2genemedgen(self):
        """Test mim2gene medgen query. only works with refseq id"""
        entrez_id = "1235"
        Mim2geneMedgenFactory.create(entrez_id=entrez_id)
        Mim2geneMedgenFactory.create(entrez_id=entrez_id)
        self.run_filter_query(Mim2geneMedgen, {"entrez_id": entrez_id}, 2)

    def test_mim2genemedgen_empty_list(self):
        """Test mem2gene medgen query with no results"""
        created = Mim2geneMedgenFactory.create()
        self.run_filter_query(Mim2geneMedgen, {"entrez_id": created.entrez_id + "MISSING"}, 0)

    def test_hpo(self):
        """Test hpo query"""
        database_id = "OMIM:1235"
        HpoFactory.create(database_id=database_id)
        HpoFactory.create(database_id=database_id)
        self.run_filter_query(Hpo, {"database_id": database_id}, 2)

    def test_hpo_empty(self):
        """Test hpo query with empty results"""
        created = HpoFactory.create()
        self.run_filter_query(Hpo, {"database_id": created.database_id + "MISSING"}, 0)
