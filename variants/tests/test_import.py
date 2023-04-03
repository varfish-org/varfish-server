"""Tests for the importing."""

import os.path
import shutil
import tempfile

from bgjobs.models import BackgroundJob
from test_plus.test import TestCase

from variants.models import Case, ImportVariantsBgJob, SmallVariant, SmallVariantSet
from variants.tasks import run_import_variants_bg_job
from variants.tests.factories import CaseFactory, SmallVariantFactory


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
                    "reference",
                    "alternative",
                    "var_type",
                    "case_id",
                    "set_id",
                    "info",
                    "genotype",
                    "num_hom_alt",
                    "num_hom_ref",
                    "num_het",
                    "num_hemi_alt",
                    "num_hemi_ref",
                    "in_clinvar",
                    "exac_frequency",
                    "exac_homozygous",
                    "exac_heterozygous",
                    "exac_hemizygous",
                    "thousand_genomes_frequency",
                    "thousand_genomes_homozygous",
                    "thousand_genomes_heterozygous",
                    "thousand_genomes_hemizygous",
                    "gnomad_exomes_frequency",
                    "gnomad_exomes_homozygous",
                    "gnomad_exomes_heterozygous",
                    "gnomad_exomes_hemizygous",
                    "gnomad_genomes_frequency",
                    "gnomad_genomes_homozygous",
                    "gnomad_genomes_heterozygous",
                    "gnomad_genomes_hemizygous",
                    "refseq_gene_id",
                    "refseq_transcript_id",
                    "refseq_transcript_coding",
                    "refseq_hgvs_c",
                    "refseq_hgvs_p",
                    "refseq_effect",
                    "refseq_exon_dist",
                    "ensembl_gene_id",
                    "ensembl_transcript_id",
                    "ensembl_transcript_coding",
                    "ensembl_hgvs_c",
                    "ensembl_hgvs_p",
                    "ensembl_effect",
                    "ensembl_exon_dist",
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
                    "14907",
                    "14907",
                    "585",
                    "A",
                    "G",
                    "snv",
                    ".",
                    ".",
                    "{}",
                    "{"
                    + ",".join(('"""%s""":{"""gt""":"""0/1"""}' % member for member in members))
                    + "}",
                    "0",
                    "1",
                    "3",
                    "0",
                    "0",
                    "FALSE",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0.495934",
                    "221",
                    "14194",
                    "0",
                    "653635",
                    "NR_024540.1",
                    "FALSE",
                    "n.1301+63T>C",
                    ".",
                    '{"non_coding_transcript_intron_variant"}',
                    "63",
                    "ENSG00000227232",
                    "ENST00000423562.1",
                    "FALSE",
                    "n.1202+63T>C",
                    ".",
                    '{"non_coding_transcript_intron_variant"}',
                    "63",
                )
            ),
            file=tsvf,
        )
    with open(os.path.join(directory, "%s.db-infos.tsv" % name), "wt") as tsvf:
        print("\t".join(("genomebuild", "db_name", "release")), file=tsvf)
        print("\t".join(("GRCh37", "ExAC", "r1.0")), file=tsvf)

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
            job_type=ImportVariantsBgJob.spec_name,
            user=self.admin,
        )
        import_job = ImportVariantsBgJob.objects.create(
            bg_job=bg_job,
            project=self.case.project,
            case_name=self.case.name,
            index_name=self.case.index,
            path_ped=os.path.join(self.data_dir, "%s.ped" % self.case.name),
            path_genotypes=[os.path.join(self.data_dir, "%s.gts.tsv" % self.case.name)],
            path_db_info=[os.path.join(self.data_dir, "%s.db-infos.tsv" % self.case.name)],
        )

        run_import_variants_bg_job(import_job.pk)

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SmallVariantSet.objects.count(), 1)
        self.assertEqual(SmallVariant.objects.count(), 1)


class TestImportTwice(TestCase):
    """Test the import process with an already existing case"""

    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.small_var = SmallVariantFactory()
        self.case = Case.objects.first()
        write_test_files(self.data_dir, self.case.name, [m["patient"] for m in self.case.pedigree])
        self.admin = self.make_user("admin")

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def testRunImportCreate(self):
        """Test submission with defaults."""

        self.assertEqual(Case.objects.count(), 1)
        old_variant_set = SmallVariantSet.objects.first()
        old_variant = SmallVariant.objects.first()

        bg_job = BackgroundJob.objects.create(
            name="Import of case %s" % self.case.name,
            project=self.case.project,
            job_type=ImportVariantsBgJob.spec_name,
            user=self.admin,
        )
        import_job = ImportVariantsBgJob.objects.create(
            bg_job=bg_job,
            project=self.case.project,
            case_name=self.case.name,
            index_name=self.case.index,
            path_ped=os.path.join(self.data_dir, "%s.ped" % self.case.name),
            path_genotypes=[os.path.join(self.data_dir, "%s.gts.tsv" % self.case.name)],
            path_db_info=[os.path.join(self.data_dir, "%s.db-infos.tsv" % self.case.name)],
        )

        run_import_variants_bg_job(import_job.pk)

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SmallVariantSet.objects.count(), 1)
        self.assertEqual(SmallVariant.objects.count(), 1)

        variant_set = SmallVariantSet.objects.first()
        variant = SmallVariant.objects.first()
        self.assertNotEqual(old_variant_set.id, variant_set.id)
        self.assertNotEqual(old_variant.id, variant.id)
