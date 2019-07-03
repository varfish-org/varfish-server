"""Tests for the importing of SVs."""

import os.path
import shutil
import tempfile

from bgjobs.models import BackgroundJob
from test_plus.test import TestCase

from svs.models import (
    ImportStructuralVariantBgJob,
    StructuralVariantSet,
    StructuralVariant,
    StructuralVariantGeneAnnotation,
)
from svs.tasks import run_import_structural_variants_bg_job
from svs.tests.factories import StructuralVariantGeneAnnotationFactory
from variants.models import Case
from variants.tests.factories import CaseFactory


def write_test_files(directory, name, members):
    """Writes some test files to the given ``directory``"""
    with open(os.path.join(directory, "%s.gts.tsv" % name), "wt") as tsvf:
        print(
            "\t".join(
                (
                    "release",
                    "chromosome",
                    "chromosome_no",
                    "start",
                    "end",
                    "bin",
                    "start_ci_left",
                    "start_ci_right",
                    "end_ci_left",
                    "end_ci_right",
                    "case_id",
                    "set_id",
                    "sv_uuid",
                    "caller",
                    "sv_type",
                    "sv_sub_type",
                    "info",
                    "genotype",
                )
            ),
            file=tsvf,
        )
        print(
            "\t".join(
                (
                    "GRCh37",
                    "1",
                    "1",
                    "10321",
                    "10376",
                    "585",
                    "-17",
                    "17",
                    "-17",
                    "17",
                    ".",
                    ".",
                    "4176ccb0-2370-4c0f-8772-f53323c800e2",
                    "EMBL.DELLYv0.7.8",
                    "DEL",
                    "DEL",
                    '{"""backgroundCarriers""":0,"""affectedCarriers""":0,"""unaffectedCarriers""":0}',
                    "{"
                    + ",".join(('"""%s""":{"""gt""":"""0/1"""}' % member for member in members))
                    + "}",
                )
            ),
            file=tsvf,
        )
    with open(os.path.join(directory, "%s.feature-effects.tsv" % name), "wt") as tsvf:
        print(
            "\t".join(
                (
                    "case_id",
                    "set_id",
                    "sv_uuid",
                    "refseq_gene_id",
                    "refseq_transcript_id",
                    "refseq_transcript_coding",
                    "refseq_effect",
                    "ensembl_gene_id",
                    "ensembl_transcript_id",
                    "ensembl_transcript_coding",
                    "ensembl_effect",
                )
            ),
            file=tsvf,
        )
        print(
            "\t".join(
                (
                    ".",
                    ".",
                    "4176ccb0-2370-4c0f-8772-f53323c800e2",
                    "100287102",
                    "NR_046018.2",
                    "FALSE",
                    '{"upstream_gene_variant","non_coding_transcript_variant"}',
                    "ENSG00000223972",
                    "ENST00000450305.2",
                    "FALSE",
                    '{"upstream_gene_variant","non_coding_transcript_variant"}',
                )
            ),
            file=tsvf,
        )
    with open(os.path.join(directory, "%s.db-infos.tsv" % name), "wt") as tsvf:
        print("\t".join(("genomebuild", "db_name", "release")), file=tsvf)
        print("\t".join(("GRCh37", "gnomAD-SV", "r1.0")), file=tsvf)

    with open(os.path.join(directory, "%s.ped" % name), "wt") as pedf:
        for member in members:
            print("\t".join(("FAM", member, "0", "0", "1", "2")), file=pedf)


class TestImportOnce(TestCase):
    """Test the import process with a non-existing case"""

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.case = CaseFactory()
        self.admin = self.make_user("admin")
        write_test_files(self.data_dir, self.case.name, [m["patient"] for m in self.case.pedigree])

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def testRunImportCreate(self):
        """Test submission with defaults."""
        self.assertEqual(Case.objects.count(), 1)

        bg_job = BackgroundJob.objects.create(
            name="Import of case %s" % self.case.name,
            project=self.case.project,
            job_type=ImportStructuralVariantBgJob.spec_name,
            user=self.admin,
        )
        import_job = ImportStructuralVariantBgJob.objects.create(
            bg_job=bg_job,
            project=self.case.project,
            case_name=self.case.name,
            index_name=self.case.index,
            path_ped=os.path.join(self.data_dir, "%s.ped" % self.case.name),
            path_genotypes=[os.path.join(self.data_dir, "%s.gts.tsv" % self.case.name)],
            path_feature_effects=[
                os.path.join(self.data_dir, "%s.feature-effects.tsv" % self.case.name)
            ],
            path_db_info=[os.path.join(self.data_dir, "%s.db-infos.tsv" % self.case.name)],
        )

        run_import_structural_variants_bg_job(import_job.pk)

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(StructuralVariantSet.objects.count(), 1)
        self.assertEqual(StructuralVariant.objects.count(), 1)


class TestImportTwice(TestCase):
    """Test the import process with an already existing case"""

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.sv_effect = StructuralVariantGeneAnnotationFactory()
        self.case = Case.objects.first()
        write_test_files(self.data_dir, self.case.name, [m["patient"] for m in self.case.pedigree])
        self.admin = self.make_user("admin")

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def testRunImportCreate(self):
        """Test submission with defaults."""

        self.assertEqual(Case.objects.count(), 1)
        old_variant_set = StructuralVariantSet.objects.first()
        old_variant = StructuralVariant.objects.first()

        bg_job = BackgroundJob.objects.create(
            name="Import of case %s" % self.case.name,
            project=self.case.project,
            job_type=ImportStructuralVariantBgJob.spec_name,
            user=self.admin,
        )
        import_job = ImportStructuralVariantBgJob.objects.create(
            bg_job=bg_job,
            project=self.case.project,
            case_name=self.case.name,
            index_name=self.case.index,
            path_ped=os.path.join(self.data_dir, "%s.ped" % self.case.name),
            path_genotypes=[os.path.join(self.data_dir, "%s.gts.tsv" % self.case.name)],
            path_feature_effects=[
                os.path.join(self.data_dir, "%s.feature-effects.tsv" % self.case.name)
            ],
            path_db_info=[os.path.join(self.data_dir, "%s.db-infos.tsv" % self.case.name)],
        )

        run_import_structural_variants_bg_job(import_job.pk)

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(StructuralVariantSet.objects.count(), 1)
        self.assertEqual(StructuralVariant.objects.count(), 1)

        variant_set = StructuralVariantSet.objects.first()
        variant = StructuralVariant.objects.first()
        self.assertNotEqual(old_variant_set.id, variant_set.id)
        self.assertNotEqual(old_variant.id, variant.id)
