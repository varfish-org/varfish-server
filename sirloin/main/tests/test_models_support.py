from django.test import TestCase
from ..models import Main, Pedigree, Annotation
from ..private import query_to_list, obj_to_dict
from ..models_support import (
    build_frequency_term,
    build_homozygous_term,
    build_case_term,
    build_effects_term,
    build_genotype_term_list,
    build_genotype_term,
    build_genotype_quality_term,
    build_genotype_ad_term,
    build_genotype_dp_term,
    build_genotype_gq_term,
    build_genotype_ab_term,
    build_genotype_gt_term,
    build_top_level_query,
)

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
        "A": {"ad": [20, 0], "dp": 20, "gq": 33, "gt": "0/0"},
        "C": {"ad": [8, 12], "dp": 20, "gq": 99, "gt": "0/1"},
        "D": {"ad": [7, 13], "dp": 20, "gq": 99, "gt": "0/1"},
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
        "C": {"ad": [0, 20], "dp": 20, "gq": 33, "gt": "0/1"},
        "D": {"ad": [8, 12], "dp": 20, "gq": 99, "gt": "0/1"},
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
        "C": {"ad": [0, 20], "dp": 20, "gq": 99, "gt": "1/1"},
        "D": {"ad": [8, 12], "dp": 20, "gq": 99, "gt": "0/1"},
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

annotation_entry1 = {
    "chromosome": main_entry1["chromosome"],
    "position": main_entry1["position"],
    "reference": main_entry1["reference"],
    "alternative": main_entry1["alternative"],
    "effect": main_entry1["effect"],
    "impact": None,
    "gene_name": "KUNIBERT",
    "gene_id": None,
    "feature_type": None,
    "feature_id": None,
    "transcript_biotype": None,
    "rank": None,
    "hgvs_c": None,
    "hgvs_p": None,
    "cdna_pos_length": None,
    "cds_pos_length": None,
    "aa_pos_length": None,
    "distance": None,
    "errors": None,
}

annotation_entry2 = {
    "chromosome": main_entry2["chromosome"],
    "position": main_entry2["position"],
    "reference": main_entry2["reference"],
    "alternative": main_entry2["alternative"],
    "effect": main_entry2["effect"],
    "impact": None,
    "gene_name": "BRUNHILDE",
    "gene_id": None,
    "feature_type": None,
    "feature_id": None,
    "transcript_biotype": None,
    "rank": None,
    "hgvs_c": None,
    "hgvs_p": None,
    "cdna_pos_length": None,
    "cds_pos_length": None,
    "aa_pos_length": None,
    "distance": None,
    "errors": None,
}


annotation_entry3 = {
    "chromosome": main_entry3["chromosome"],
    "position": main_entry3["position"],
    "reference": main_entry3["reference"],
    "alternative": main_entry3["alternative"],
    "effect": main_entry3["effect"],
    "impact": None,
    "gene_name": "ARTUR",
    "gene_id": None,
    "feature_type": None,
    "feature_id": None,
    "transcript_biotype": None,
    "rank": None,
    "hgvs_c": None,
    "hgvs_p": None,
    "cdna_pos_length": None,
    "cds_pos_length": None,
    "aa_pos_length": None,
    "distance": None,
    "errors": None,
}

KEYS = (
    "chromosome",
    "position",
    "reference",
    "alternative",
    "frequency",
    "homozygous",
    "effect",
    "genotype",
    "case_id",
    "gene_name",
    "pedigree",
)

_entry1 = {**main_entry1, **pedigree_entry1, **annotation_entry1}
_entry2 = {**main_entry2, **pedigree_entry1, **annotation_entry2}
_entry3 = {**main_entry3, **pedigree_entry1, **annotation_entry3}

entry1 = {key: _entry1[key] for key in KEYS}
entry2 = {key: _entry2[key] for key in KEYS}
entry3 = {key: _entry3[key] for key in KEYS}


class Test(TestCase):
    def setUp(self):
        Main.objects.get_or_create(**main_entry1)
        Main.objects.get_or_create(**main_entry2)
        Main.objects.get_or_create(**main_entry3)
        Pedigree.objects.get_or_create(**pedigree_entry1)
        Pedigree.objects.get_or_create(**pedigree_entry2)
        Annotation.objects.get_or_create(**annotation_entry1)
        Annotation.objects.get_or_create(**annotation_entry2)
        Annotation.objects.get_or_create(**annotation_entry3)

    def test_max_frequency_001(self):
        conditions = [build_frequency_term({"max_frequency": 0.01})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1, entry3]
        self.assertEquals(results, expected)

    def test_remove_homozygous(self):
        conditions = [build_homozygous_term({"remove_homozygous": True})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry2, entry3]
        self.assertEquals(results, expected)

    def test_effects_missense_variant(self):
        conditions = [build_effects_term({"effects": ["missense_variant"]})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1, entry3]
        self.assertEquals(results, expected)

    def test_case_A(self):
        conditions = [build_case_term({"case_id": "A"})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1, entry2, entry3]
        self.assertEquals(results, expected)

    def test_gt_ref_A(self):
        conditions = [build_genotype_gt_term({"member": "A", "gt": "0/0"})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1]
        self.assertEquals(results, expected)

    def test_gq_40_A(self):
        conditions = [build_genotype_gq_term({"member": "A", "gq": 40})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry2, entry3]
        self.assertEquals(results, expected)

    def test_dp_20_A(self):
        conditions = [build_genotype_dp_term({"member": "A", "dp": 20})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1, entry2, entry3]
        self.assertEquals(results, expected)

    def test_ad_10_A(self):
        conditions = [build_genotype_ad_term({"member": "A", "ad": 10})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry3]
        self.assertEquals(results, expected)

    def test_ab_02_A(self):
        conditions = [build_genotype_ab_term({"member": "A", "ab": 0.2})]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry2, entry3]
        self.assertEquals(results, expected)

    def test_quality_complete_condition(self):
        conditions = [
            build_genotype_quality_term(
                {"member": "A", "dp": 20, "ad": 10, "ab": 0.2, "gq": 40}
            )
        ]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry3]
        self.assertEquals(results, expected)

    def test_genotype_and_quality_drop(self):
        conditions = [
            build_genotype_term(
                {
                    "member": "A",
                    "dp": 20,
                    "ad": 10,
                    "ab": 0.2,
                    "gq": 40,
                    "gt": "0/1",
                    "fail": "drop-variant",
                }
            )
        ]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry3]
        self.assertEquals(results, expected)

    def test_genotype_and_quality_nocall(self):
        conditions = [
            build_genotype_term(
                {
                    "member": "A",
                    "dp": 20,
                    "ad": 10,
                    "ab": 0.2,
                    "gq": 40,
                    "gt": "0/0",
                    "fail": "no-call",
                }
            )
        ]
        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1, entry2]
        self.assertEquals(results, expected)

    def test_genotype_quality_drop_and_nocall(self):
        conditions = [
            build_genotype_term_list(
                {
                    "genotype": [
                        {
                            "member": "A",
                            "dp": 20,
                            "ad": 10,
                            "ab": 0.2,
                            "gq": 40,
                            "gt": "0/0",
                            "fail": "no-call",
                        },
                        {
                            "member": "C",
                            "dp": 20,
                            "ad": 10,
                            "ab": 0.2,
                            "gq": 40,
                            "gt": "0/1",
                            "fail": "drop-variant",
                        },
                    ]
                }
            )
        ]

        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1]
        self.assertEquals(results, expected)

    def test_complete_query(self):
        kwargs = {
            "max_frequency": 0.01,
            "remove_homozygous": False,
            "effects": ["missense_variant"],
            "case_id": "A",
            "genotype": [
                {
                    "member": "A",
                    "dp": 20,
                    "ad": 10,
                    "ab": 0.2,
                    "gq": 20,
                    "gt": "0/0",
                    "fail": "no-call",
                },
                {
                    "member": "C",
                    "dp": 20,
                    "ad": 10,
                    "ab": 0.2,
                    "gq": 40,
                    "gt": "0/1",
                    "fail": "drop-variant",
                },
            ]
        }
        
        conditions = [
            build_frequency_term(kwargs),
            build_homozygous_term(kwargs),
            build_case_term(kwargs),
            build_effects_term(kwargs),
            build_genotype_term_list(kwargs),
        ]

        _results = Main.objects.raw(build_top_level_query(conditions))
        results = query_to_list(_results)
        expected = [entry1]
        self.assertEquals(results, expected)
