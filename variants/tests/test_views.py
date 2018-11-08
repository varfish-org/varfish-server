"""Tests for the filter view"""

from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from test_plus.test import TestCase

from projectroles.models import Project
from variants.models import SmallVariant
from frequencies.models import Exac, GnomadGenomes, GnomadExomes, ThousandGenomes

from .. import views
import json

PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}

DEFAULT_FILTER_FORM_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "compound_recessive_enabled": False,
    "effect_coding_transcript_intron_variant": True,
    "effect_complex_substitution": True,
    "effect_direct_tandem_duplication": True,
    "effect_disruptive_inframe_deletion": True,
    "effect_disruptive_inframe_insertion": True,
    "effect_downstream_gene_variant": True,
    "effect_feature_truncation": True,
    "effect_five_prime_UTR_exon_variant": True,
    "effect_five_prime_UTR_intron_variant": True,
    "effect_frameshift_elongation": True,
    "effect_frameshift_truncation": True,
    "effect_frameshift_variant": True,
    "effect_inframe_deletion": True,
    "effect_inframe_insertion": True,
    "effect_intergenic_variant": True,
    "effect_internal_feature_elongation": True,
    "effect_missense_variant": True,
    "effect_mnv": True,
    "effect_non_coding_transcript_exon_variant": True,
    "effect_non_coding_transcript_intron_variant": True,
    "effect_splice_acceptor_variant": True,
    "effect_splice_donor_variant": True,
    "effect_splice_region_variant": True,
    "effect_start_lost": True,
    "effect_stop_gained": True,
    "effect_stop_lost": True,
    "effect_stop_retained_variant": True,
    "effect_structural_variant": True,
    "effect_synonymous_variant": True,
    "effect_three_prime_UTR_exon_variant": True,
    "effect_three_prime_UTR_intron_variant": True,
    "effect_transcript_ablation": True,
    "effect_upstream_gene_variant": True,
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "gene_blacklist": "",
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "submit": "display",
}


def fixture_setup_case():
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
    )

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

    SmallVariant.objects.create(**{**basic_var, **{"position": 100}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 200}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 300}})

    return project.sodar_uuid, case.sodar_uuid


class TestViewBase(TestCase):

    setup_case_in_db = None

    def setUp(self):
        self.project_id, self.case_id = self.__class__.setup_case_in_db()

        self.request_factory = RequestFactory()

        # setup super user
        self.user = self.make_user("superuser")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()


class TestCaseListView(TestViewBase):

    setup_case_in_db = fixture_setup_case

    def test_render(self):
        with self.login(self.user):
            response = self.client.get(
                reverse("variants:case-list", kwargs={"project": self.project_id})
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["case_list"]), 1)


class TestCaseFilterView(TestViewBase):

    setup_case_in_db = fixture_setup_case

    def test_get(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.project_id, "case": self.case_id},
                )
            )

        self.assertEqual(response.status_code, 200)

    def test_post(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.project_id, "case": self.case_id},
                ),
                data=DEFAULT_FILTER_FORM_SETTING,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result_count"], 3)


def fixture_setup_expand():
    """Setup test case 1 -- a singleton with variants for gene blacklist filter."""
    project = Project.objects.create(**PROJECT_DICT)
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

    return project.sodar_uuid, None


class TestExpandView(TestViewBase):

    setup_case_in_db = fixture_setup_expand

    def setUp(self):
        super().setUp()

    def test_render(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:extend",
                    kwargs={
                        "project": self.project_id,
                        "release": "GRCh37",
                        "chromosome": "1",
                        "position": 100,
                        "reference": "A",
                        "alternative": "G",
                    },
                )
            )
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["position"], "100")
        self.assertEqual(content["gnomadexomes"]["an_sas"], 932)
        self.assertEqual(content["exac"]["an_sas"], 323)
        self.assertEqual(content["gnomadgenomes"]["an_asj"], 323)
        self.assertEqual(content["thousandgenomes"]["af_amr"], 0.0054)
