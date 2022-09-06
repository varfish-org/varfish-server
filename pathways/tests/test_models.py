"""Tests for Model queries to the ``pathways`` models."""

from variants.tests.helpers import QueryTestBase

from ..models import EnsemblToKegg, KeggInfo, RefseqToKegg
from .factories import EnsemblToKeggFactory, KeggInfoFactory, RefseqToKeggFactory


class TestPathwayQuery(QueryTestBase):
    """Test querying the pathways/KEGG models."""

    def test_ensembltokegg_query(self):
        created = EnsemblToKeggFactory.create()
        EnsemblToKeggFactory.create(gene_id=created.gene_id)
        self.run_filter_query(EnsemblToKegg, {"gene_id": created.gene_id}, 2)

    def test_ensembltokegg_empty(self):
        created = EnsemblToKeggFactory.create()
        self.run_filter_query(EnsemblToKegg, {"gene_id": created.gene_id + "MISSING"}, 0)

    def test_refseqtokegg_query(self):
        created = RefseqToKeggFactory.create()
        RefseqToKeggFactory.create(gene_id=created.gene_id)
        self.run_filter_query(RefseqToKegg, {"gene_id": created.gene_id}, 2)

    def test_refseqtokegg_empty(self):
        created = RefseqToKeggFactory.create()
        self.run_filter_query(RefseqToKegg, {"gene_id": created.gene_id + "MISSING"}, 0)

    def test_kegginfo_ensembl_query(self):
        created = EnsemblToKeggFactory.create()
        obj = self.run_get_query(KeggInfo, {"id": created.kegginfo_id})
        self.assertEquals(obj.name, created.kegginfo.name)

    def test_kegginfo_refseq_query(self):
        created = RefseqToKeggFactory.create()
        other = EnsemblToKeggFactory.create(gene_id=created.gene_id)
        obj = self.run_get_query(KeggInfo, {"id": created.kegginfo_id})
        self.assertEquals(obj.name, created.kegginfo.name)
        obj = self.run_get_query(KeggInfo, {"id": other.kegginfo_id})
        self.assertEquals(obj.name, other.kegginfo.name)

    def test_kegginfo_fail(self):
        created = KeggInfoFactory.create()
        self.run_get_query(KeggInfo, {"id": created.id + 1}, KeggInfo.DoesNotExist)
