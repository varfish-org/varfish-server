"""Tests for the filter view"""

from django.urls import reverse
from projectroles.models import Project

from pathways.models import EnsemblToKegg, KeggInfo, RefseqToKegg
from variants.tests.test_views import TestViewBase

from ..models import Hgnc, Hpo, Mim2geneMedgen

PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}


def fixture_setup_geneinfo_incomplete(user):
    """Setup test entries for geneinfo view (including pathway tables)"""

    Project.objects.create(**PROJECT_DICT)

    # Setup tables from geneinfo app
    Hgnc.objects.create(
        hgnc_id="HGNC:1",
        symbol="AAA",
        name="AAA gene",
        entrez_id="123",
        ensembl_gene_id="ENSG1",
        omim_id="1",
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:2",
        symbol="BBB",
        name="CCC gene",
        entrez_id="456",
        ensembl_gene_id="ENSG2",
        omim_id="2",
    )
    Hgnc.objects.create(
        hgnc_id="HGNC:3",
        symbol="CCC",
        name="BBB gene",
        entrez_id="789",
        ensembl_gene_id="ENSG3",
        omim_id="3",
    )

    # Setup tables from pathway app
    kegginfo1 = KeggInfo.objects.create(kegg_id="hsa1", name="Pathway1")
    kegginfo2 = KeggInfo.objects.create(kegg_id="hsa2", name="Pathway2")
    EnsemblToKegg.objects.create(gene_id="ENSG1", kegginfo_id=kegginfo1.pk)
    EnsemblToKegg.objects.create(gene_id="ENSG1", kegginfo_id=kegginfo2.pk)
    EnsemblToKegg.objects.create(gene_id="ENSG2", kegginfo_id=kegginfo2.pk)
    RefseqToKegg.objects.create(gene_id="123", kegginfo_id=kegginfo1.pk)
    RefseqToKegg.objects.create(gene_id="456", kegginfo_id=kegginfo1.pk)
    RefseqToKegg.objects.create(gene_id="456", kegginfo_id=kegginfo2.pk)


def fixture_setup_geneinfo(user):
    fixture_setup_geneinfo_incomplete(user)
    """Setup test entries for geneinfo view (including pathway tables)"""

    Mim2geneMedgen.objects.create(omim_id=1, entrez_id="123")
    Mim2geneMedgen.objects.create(omim_id=2, entrez_id="456")
    Mim2geneMedgen.objects.create(omim_id=3, entrez_id="789")
    Hpo.objects.create(database_id="OMIM:1", hpo_id="HP:001")
    Hpo.objects.create(database_id="OMIM:2", hpo_id="HP:002")
    Hpo.objects.create(database_id="OMIM:3", hpo_id="HP:003")


class TestGeneView(TestViewBase):
    """Test gene view"""

    setup_case_in_db = fixture_setup_geneinfo

    def test_geneinfo_ensembl(self):
        with self.login(self.superuser):
            project = Project.objects.first()
            response = self.client.get(
                reverse("geneinfo:gene", kwargs={"project": project.sodar_uuid, "gene_id": "ENSG1"})
            )
            self.assertEquals(response.status_code, 200)

    def test_geneinfo_refseq(self):
        with self.login(self.superuser):
            project = Project.objects.first()
            response = self.client.get(
                reverse("geneinfo:gene", kwargs={"project": project.sodar_uuid, "gene_id": "123"})
            )
            self.assertEquals(response.status_code, 200)

    def test_geneinfo_render_complete(self):
        with self.login(self.superuser):
            project = Project.objects.first()
            response = self.client.get(
                reverse("geneinfo:gene", kwargs={"project": project.sodar_uuid, "gene_id": "456"})
            )
            self.assertEquals(response.context["hgnc"]["symbol"], "BBB")
            self.assertEquals(len(response.context["kegg"]), 2)
            self.assertEquals(response.context["kegg"][0]["name"], "Pathway1")
            self.assertEquals(response.context["kegg"][1]["name"], "Pathway2")
            self.assertEquals(len(response.context["mim2genemedgen"]), 1)
            self.assertEquals(len(response.context["mim2genemedgen"]["2"]), 1)
            self.assertEquals(response.context["mim2genemedgen"]["2"][0]["hpo_id"], "HP:002")
            self.assertEquals(len(response.context["hgncomim"]), 1)
            self.assertEquals(len(response.context["hgncomim"]["2"]), 1)
            self.assertEquals(response.context["hgncomim"]["2"][0]["hpo_id"], "HP:002")

    def test_geneinfo_render_empty(self):
        with self.login(self.superuser):
            project = Project.objects.first()
            response = self.client.get(
                reverse("geneinfo:gene", kwargs={"project": project.sodar_uuid, "gene_id": "000"})
            )
            self.assertIsNone(response.context["hgnc"])
            self.assertEquals(response.context["kegg"], [])
            self.assertIsNone(response.context["mim2genemedgen"])
            self.assertIsNone(response.context["hgncomim"])


class TestGeneViewIncomplete(TestViewBase):
    """Test gene view"""

    setup_case_in_db = fixture_setup_geneinfo_incomplete

    def test_geneinfo_render_missing_omim(self):
        with self.login(self.superuser):
            project = Project.objects.first()
            response = self.client.get(
                reverse("geneinfo:gene", kwargs={"project": project.sodar_uuid, "gene_id": "456"})
            )
            self.assertEquals(response.context["hgnc"]["symbol"], "BBB")
            self.assertEquals(response.context["mim2genemedgen"], {})
            self.assertEquals(response.context["hgncomim"], {})
