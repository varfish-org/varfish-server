from django.test import TestCase
from ..models import Main, Pedigree, Annotation
from django.forms import model_to_dict
from ..models_support import QueryBuilder


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


class Test(TestCase):
    def setUp(self):
        # set extended diff report
        self.maxDiff = None

        # insert objects into test database
        p1, _ = Pedigree.objects.get_or_create(**pedigree_entry1)
        p2, _ = Pedigree.objects.get_or_create(**pedigree_entry2)
        # replace case string by pedigree object
        _main_entry1 = dict(main_entry1)
        _main_entry2 = dict(main_entry2)
        _main_entry3 = dict(main_entry3)
        _main_entry1["case_id"] = p1
        _main_entry2["case_id"] = p1
        _main_entry3["case_id"] = p1
        Main.objects.get_or_create(**_main_entry1)
        Main.objects.get_or_create(**_main_entry2)
        Main.objects.get_or_create(**_main_entry3)
        Annotation.objects.get_or_create(**annotation_entry1)
        Annotation.objects.get_or_create(**annotation_entry2)
        Annotation.objects.get_or_create(**annotation_entry3)

    def test_max_frequency_001(self):
        qb = QueryBuilder()
        frequency_condition = qb.build_frequency_term({"max_frequency": 0.01})
        term, args = qb.build_top_level_query([frequency_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry3]
        self.assertEquals(results, expected)

    def test_remove_homozygous(self):
        qb = QueryBuilder()
        homozygous_condition = qb.build_homozygous_term(
            {"remove_homozygous": True}
        )
        term, args = qb.build_top_level_query([homozygous_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_effects_missense_variant(self):
        qb = QueryBuilder()
        effect_condition = qb.build_effects_term(
            {"effects": ["missense_variant"]}
        )
        term, args = qb.build_top_level_query([effect_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry3]
        self.assertEquals(results, expected)

    def test_case_A(self):
        qb = QueryBuilder()
        case_condition = qb.build_case_term({"case_id": "A"})
        term, args = qb.build_top_level_query([case_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_gt_ref_A(self):
        qb = QueryBuilder()
        gt_condition = qb.build_genotype_gt_term({"member": "A", "gt": ["0/0"]})
        term, args = qb.build_top_level_query([gt_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1]
        self.assertEquals(results, expected)

    def test_gt_None_ref_A(self):
        qb = QueryBuilder()
        gt_condition = qb.build_genotype_gt_term({"member": "A", "gt": None})
        term, args = qb.build_top_level_query([gt_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_gt_variant_ref_A(self):
        qb = QueryBuilder()
        gt_condition = qb.build_genotype_gt_term(
            {"member": "A", "gt": ["0/0", "0/1"]}
        )
        term, args = qb.build_top_level_query([gt_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_gq_40_A(self):
        qb = QueryBuilder()
        gq_condition = qb.build_genotype_gq_term({"member": "A", "gq": 40})
        term, args = qb.build_top_level_query([gq_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_dp_20_A(self):
        qb = QueryBuilder()
        dp_condition = qb.build_genotype_dp_term({"member": "A", "dp": 20})
        term, args = qb.build_top_level_query([dp_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_ad_10_A(self):
        qb = QueryBuilder()
        ad_condition = qb.build_genotype_ad_term({"member": "A", "ad": 10})
        term, args = qb.build_top_level_query([ad_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry3]
        self.assertEquals(results, expected)

    def test_ab_02_A(self):
        qb = QueryBuilder()
        ab_condition = qb.build_genotype_ab_term({"member": "A", "ab": 0.2})
        term, args = qb.build_top_level_query([ab_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry2, main_entry3]
        self.assertEquals(results, expected)

    def test_quality_complete_condition(self):
        qb = QueryBuilder()
        genotype_condition = qb.build_genotype_quality_term(
            {"member": "A", "dp": 20, "ad": 10, "ab": 0.2, "gq": 40}
        )
        term, args = qb.build_top_level_query([genotype_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry3]
        self.assertEquals(results, expected)

    def test_genotype_and_quality_drop(self):
        qb = QueryBuilder()
        genotype_condition = qb.build_genotype_term(
            {
                "member": "A",
                "dp": 20,
                "ad": 10,
                "ab": 0.2,
                "gq": 40,
                "gt": ["0/1"],
                "fail": "drop-variant",
            }
        )
        term, args = qb.build_top_level_query([genotype_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry3]
        self.assertEquals(results, expected)

    def test_genotype_and_quality_nocall(self):
        qb = QueryBuilder()
        genotype_condition = qb.build_genotype_term(
            {
                "member": "A",
                "dp": 20,
                "ad": 10,
                "ab": 0.2,
                "gq": 40,
                "gt": ["0/0"],
                "fail": "no-call",
            }
        )
        term, args = qb.build_top_level_query([genotype_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1, main_entry2]
        self.assertEquals(results, expected)

    def test_genotype_quality_drop_and_nocall(self):
        qb = QueryBuilder()
        genotype_condition = qb.build_genotype_term_list(
            {
                "genotype": [
                    {
                        "member": "A",
                        "dp": 20,
                        "ad": 10,
                        "ab": 0.2,
                        "gq": 40,
                        "gt": ["0/0"],
                        "fail": "no-call",
                    },
                    {
                        "member": "C",
                        "dp": 20,
                        "ad": 10,
                        "ab": 0.2,
                        "gq": 40,
                        "gt": ["0/1"],
                        "fail": "drop-variant",
                    },
                ]
            }
        )
        term, args = qb.build_top_level_query([genotype_condition])
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1]
        self.assertEquals(results, expected)

    def test_complete_query(self):
        qb = QueryBuilder()
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
                    "gt": ["0/0"],
                    "fail": "no-call",
                },
                {
                    "member": "C",
                    "dp": 20,
                    "ad": 10,
                    "ab": 0.2,
                    "gq": 40,
                    "gt": ["0/1"],
                    "fail": "drop-variant",
                },
            ],
        }

        conditions = [
            qb.build_frequency_term(kwargs),
            qb.build_homozygous_term(kwargs),
            qb.build_case_term(kwargs),
            qb.build_effects_term(kwargs),
            qb.build_genotype_term_list(kwargs),
        ]

        term, args = qb.build_top_level_query(conditions)
        _results = Main.objects.raw(term, args)
        results = [
            model_to_dict(_result, exclude=["id"]) for _result in _results
        ]
        expected = [main_entry1]
        self.assertEquals(results, expected)
