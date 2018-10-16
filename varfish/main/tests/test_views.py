from django.test import TestCase
from django.shortcuts import reverse

from ..models import SmallVariant, Case
from ..views import FilterView

import re


main_entry1 = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": 100,
    "reference": "A",
    "alternative": "G",
    "case_id": "A",
    "frequency": 0.001,
    "homozygous": 3,
    "effect": ["missense_variant"],
    "genotype": {
        "A": {"ad": [20, 0], "dp": 20, "gq": 99, "gt": "0/0"},
        "B": {"ad": [12, 8], "dp": 20, "gq": 99, "gt": "0/1"},
        "C": {"ad": [7, 13], "dp": 20, "gq": 99, "gt": "0/1"},
    },
    "ensembl_gene_id": "ENSG000001",
}

main_entry2 = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": 200,
    "reference": "C",
    "alternative": "T",
    "case_id": "A",
    "frequency": 0.05,
    "homozygous": 0,
    "effect": ["synonymous_variant"],
    "genotype": {
        "A": {"ad": [11, 9], "dp": 20, "gq": 99, "gt": "0/1"},
        "B": {"ad": [0, 20], "dp": 20, "gq": 99, "gt": "1/1"},
        "C": {"ad": [8, 12], "dp": 20, "gq": 99, "gt": "0/1"},
    },
    "ensembl_gene_id": "ENSG000001",
}

main_entry3 = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": 300,
    "reference": "C",
    "alternative": "T",
    "case_id": "A",
    "frequency": 0.01,
    "homozygous": 0,
    "effect": ["missense_variant", "stop_lost"],
    "genotype": {
        "A": {"ad": [9, 11], "dp": 20, "gq": 99, "gt": "0/1"},
        "B": {"ad": [0, 20], "dp": 20, "gq": 99, "gt": "1/1"},
        "C": {"ad": [8, 12], "dp": 20, "gq": 99, "gt": "0/1"},
    },
    "ensembl_gene_id": "ENSG000001",
}

pedigree_entry1 = {
    "case_id": "A",
    "pedigree": [
        {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
        {"sex": 1, "father": "0", "mother": "0", "patient": "D", "affected": 0},
        {"sex": 1, "father": "D", "mother": "C", "patient": "A", "affected": 0},
    ],
}

pedigree_entry2 = {
    "case_id": "B",
    "pedigree": [
        {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
        {"sex": 1, "father": "0", "mother": "0", "patient": "D", "affected": 0},
        {"sex": 2, "father": "D", "mother": "C", "patient": "B", "affected": 0},
    ],
}

REGEX = re.compile("Variants: (\d+)")

# class TestFilterView(TestCase):
#     def setUp(self):
#         Main.objects.get_or_create(**main_entry1)
#         Main.objects.get_or_create(**main_entry2)
#         Main.objects.get_or_create(**main_entry3)
#         Pedigree.objects.get_or_create(**pedigree_entry1)
#         Pedigree.objects.get_or_create(**pedigree_entry2)

#     def test_case(self):
#         response = self.client.post(
#             reverse("main:filter", kwargs={"case_id": "A"}),
#             {
#                 "frequency_filter": 0.01,
#                 "remove_homozygous": True,
#                 "effect_coding_transcript_intron_variant": False,
#                 "effect_complex_substitution": True,
#                 "effect_direct_tandem_duplication": True,
#                 "effect_disruptive_inframe_deletion": True,
#                 "effect_disruptive_inframe_insertion": True,
#                 "effect_downstream_gene_variant": False,
#                 "effect_feature_truncation": True,
#                 "effect_five_prime_UTR_exon_variant": False,
#                 "effect_five_prime_UTR_intron_variant": False,
#                 "effect_frameshift_elongation": True,
#                 "effect_frameshift_truncation": True,
#                 "effect_frameshift_variant": True,
#                 "effect_inframe_deletion": True,
#                 "effect_inframe_insertion": True,
#                 "effect_intergenic_variant": False,
#                 "effect_internal_feature_elongation": False,
#                 "effect_missense_variant": True,
#                 "effect_mnv": True,
#                 "effect_non_coding_transcript_exon_variant": False,
#                 "effect_non_coding_transcript_intron_variant": False,
#                 "effect_splice_acceptor_variant": True,
#                 "effect_splice_donor_variant": True,
#                 "effect_splice_region_variant": True,
#                 "effect_start_lost": True,
#                 "effect_stop_gained": True,
#                 "effect_stop_lost": True,
#                 "effect_stop_retained_variant": True,
#                 "effect_structural_variant": True,
#                 "effect_synonymous_variant": False,
#                 "effect_three_prime_UTR_exon_variant": False,
#                 "effect_three_prime_UTR_intron_variant": False,
#                 "effect_transcript_ablation": True,
#                 "effect_upstream_gene_variant": False,
#                 "gt_A": "0/0",
#                 "dp_A": 20,
#                 "ab_A": 0.2,
#                 "gq_A": 40,
#                 "ad_A": 10,
#                 "fail_A": "no-call",
#                 "gt_B": "0/0",
#                 "dp_B": 20,
#                 "ab_B": 0.2,
#                 "gq_B": 40,
#                 "ad_B": 10,
#                 "fail_C": "no-call",
#                 "gt_C": "0/0",
#                 "dp_C": 20,
#                 "ab_C": 0.2,
#                 "gq_C": 40,
#                 "ad_C": 10,
#                 "fail_C": "no-call",
#             },
#         )

#         match = re.search(REGEX, response.rendered_content)

#         self.assertEquals(response.status_code, 200)
#         self.assertEquals(int(match.group(1)), 1)
    