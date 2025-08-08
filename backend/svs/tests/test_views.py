# from django.urls import reverse

# from geneinfo.tests.factories import HgncFactory
# from svs.models import StructuralVariant
# from svs.tests.factories import StructuralVariantGeneAnnotationFactory
# from variants.tests.factories import CaseWithVariantSetFactory
# from variants.tests.helpers import ViewTestBase

# class TestSecondHitView(ViewTestBase):
#     """Test view that displays small variant second hits."""
#
#     def setUp(self):
#         super().setUp()
#         self.case, _, self.variant_set = CaseWithVariantSetFactory.get(project=self.project)
#         self.sv_gene_annotation = StructuralVariantGeneAnnotationFactory(
#             sv__variant_set__case=self.case,
#             sv__variant_set=self.variant_set,
#         )
#         self.sv = StructuralVariant.objects.get(sv_uuid=self.sv_gene_annotation.sv_uuid)
#         self.sv_gene_annotation2 = StructuralVariantGeneAnnotationFactory(
#             variant_set__case=self.case,
#             sv__variant_set=self.variant_set,
#             ensembl_gene_id=self.sv_gene_annotation.ensembl_gene_id,
#             refseq_gene_id=self.sv_gene_annotation.refseq_gene_id,
#         )
#         self.sv2 = StructuralVariant.objects.get(sv_uuid=self.sv_gene_annotation2.sv_uuid)
#         self.hgnc = HgncFactory(
#             ensembl_gene_id=self.sv_gene_annotation.ensembl_gene_id,
#             entrez_id=self.sv_gene_annotation.refseq_gene_id,
#         )
#
#     def test_with_role(self):
#         with self.login(self.user_contributor):
#             response = self.client.get(
#                 reverse(
#                     "svs:second-hit",
#                     kwargs={
#                         "case": self.case.sodar_uuid,
#                         "database": "refseq",
#                         "gene_id": self.sv_gene_annotation.refseq_gene_id,
#                     },
#                 )
#                 + "?sv_uuid=%s" % self.sv_gene_annotation.sv_uuid
#             )
#             self.assert_http_200_ok(response)
#             self.assertNotIn(
#                 f"{self.sv.chromosome}:{self.sv.start:,}", response.content.decode("utf-8")
#             )
#             self.assertIn(
#                 f"{self.sv2.chromosome}:{self.sv2.start:,}", response.content.decode("utf-8")
#             )
#
#     def test_as_superuser(self):
#         with self.login(self.superuser):
#             response = self.client.get(
#                 reverse(
#                     "svs:second-hit",
#                     kwargs={
#                         "case": self.case.sodar_uuid,
#                         "database": "refseq",
#                         "gene_id": self.sv_gene_annotation.refseq_gene_id,
#                     },
#                 )
#                 + "?sv_uuid=%s" % self.sv_gene_annotation.sv_uuid
#             )
#             self.assert_http_200_ok(response)
#             self.assertNotIn(
#                 f"{self.sv.chromosome}:{self.sv.start:,}", response.content.decode("utf-8")
#             )
#             self.assertIn(
#                 f"{self.sv2.chromosome}:{self.sv2.start:,}", response.content.decode("utf-8")
#             )
#
#     def test_without_role(self):
#         with self.login(self.user_no_roles):
#             response = self.client.get(
#                 reverse(
#                     "svs:second-hit",
#                     kwargs={
#                         "case": self.case.sodar_uuid,
#                         "database": "refseq",
#                         "gene_id": self.sv_gene_annotation.refseq_gene_id,
#                     },
#                 )
#                 + "?sv_uuid=%s" % self.sv_gene_annotation.sv_uuid
#             )
#             self.assert_http_302_found(response, url="/")
#
#     def test_with_role_and_no_sv_uuid(self):
#         with self.login(self.user_contributor):
#             response = self.client.get(
#                 reverse(
#                     "svs:second-hit",
#                     kwargs={
#                         "case": self.case.sodar_uuid,
#                         "database": "refseq",
#                         "gene_id": self.sv_gene_annotation.refseq_gene_id,
#                     },
#                 )
#             )
#             self.assert_http_200_ok(response)
#             self.assertIn(
#                 f"{self.sv.chromosome}:{self.sv.start:,}", response.content.decode("utf-8")
#             )
#             self.assertIn(
#                 f"{self.sv2.chromosome}:{self.sv2.start:,}", response.content.decode("utf-8")
#             )
