from django.test import TestCase
from ..models import Main
from ..private import query_to_list, obj_to_dict


entry1 = {
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

entry2 = {
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

entry3 = {
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


class Test(TestCase):
    def setUp(self):
        Main.objects.get_or_create(**entry1)
        Main.objects.get_or_create(**entry2)
        Main.objects.get_or_create(**entry3)

    def test_max_frequency_001(self):
        _results = Main.objects.raw(
            "SELECT id, frequency FROM main_main WHERE frequency <= {max_frequency}".format(
                max_frequency=0.01
            )
        )

        results = query_to_list(_results)
        expected = [
            {"frequency": entry1["frequency"]},
            {"frequency": entry3["frequency"]},
        ]

        self.assertEquals(results, expected)

    def test_remove_homozygous(self):
        _results = Main.objects.raw(
            "SELECT id, homozygous FROM main_main WHERE homozygous = 0"
        )

        self.assertEquals(len(list(_results)), 2)

    def test_effects_missense_variant(self):
        _results = Main.objects.raw(
            "SELECT id, effect FROM main_main WHERE effect && ARRAY[{effects}]::VARCHAR[]".format(
                effects="'missense_variant'"
            )
        )

        results = query_to_list(_results)
        expected = [
            {"effect": ["missense_variant"]},
            {"effect": ["missense_variant", "stop_lost"]},
        ]

        self.assertEquals(results, expected)

    def test_case_A(self):
        _results = Main.objects.raw(
            "SELECT id, case_id FROM main_main WHERE case_id = '{case_id}'".format(
                case_id="A"
            )
        )

        self.assertEquals(len(list(_results)), 3)

    def test_gt_ref_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main WHERE genotype->'A'->>'gt' = '{gt}'".format(
                gt="0/0"
            )
        )

        results = query_to_list(_results)
        expected = [{"genotype": entry1["genotype"]}]

        self.assertEquals(results, expected)

    def test_gq_40_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_Main WHERE (genotype->'A'->>'gq')::int >= {gq}".format(
                gq=40
            )
        )
        results = query_to_list(_results)
        expected = [
            {"genotype": entry1["genotype"]},
            {"genotype": entry2["genotype"]},
            {"genotype": entry3["genotype"]},
        ]

        self.assertEquals(results, expected)

    def test_dp_20_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main WHERE (genotype->'A'->>'dp')::int >= {dp}".format(
                dp=20
            )
        )

        results = query_to_list(_results)
        expected = [
            {"genotype": entry1["genotype"]},
            {"genotype": entry2["genotype"]},
            {"genotype": entry3["genotype"]},
        ]

        self.assertEquals(results, expected)

    def test_ad_10_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main WHERE (genotype->'A'->'ad'->>1)::int >= {ad}".format(
                ad=10
            )
        )

        results = query_to_list(_results)
        expected = [{"genotype": entry3["genotype"]}]

        self.assertEquals(results, expected)

    def test_ab_gt_02_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main WHERE ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) >= {ab}".format(
                ab=0.2
            )
        )

        results = query_to_list(_results)
        expected = [
            {"genotype": entry2["genotype"]},
            {"genotype": entry3["genotype"]},
        ]

        self.assertEquals(results, expected)

    def test_ab_lt_08_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main WHERE ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) <= 1-{ab}".format(
                ab=0.2
            )
        )

        results = query_to_list(_results)
        expected = [
            {"genotype": entry1["genotype"]},
            {"genotype": entry2["genotype"]},
            {"genotype": entry3["genotype"]},
        ]

        self.assertEquals(results, expected)

    def test_ab_btwn_02_08_A(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main "
            "WHERE {ab} <= ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) "
            "AND ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) <= 1-{ab}".format(
                ab=0.2
            )
        )

        results = query_to_list(_results)
        expected = [
            {"genotype": entry2["genotype"]},
            {"genotype": entry3["genotype"]},
        ]

        self.assertEquals(results, expected)

    def test_quality_complete_condition(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main "
            "WHERE {ab} <= ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) "
            "AND ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) <= 1-{ab} "
            "AND (genotype->'A'->'ad'->>1)::int >= {ad} "
            "AND (genotype->'A'->>'dp')::int >= {dp} "
            "AND (genotype->'A'->>'gq')::int >= {gq}".format(
                ab=0.2, ad=10, dp=20, gq=40
            )
        )

        results = query_to_list(_results)
        expected = [{"genotype": entry3["genotype"]}]

        self.assertEquals(results, expected)

    def test_genotype_and_quality_drop(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main "
            "WHERE {ab} <= ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) "
            "AND ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) <= 1-{ab} "
            "AND (genotype->'A'->'ad'->>1)::int >= {ad} "
            "AND (genotype->'A'->>'dp')::int >= {dp} "
            "AND (genotype->'A'->>'gq')::int >= {gq} "
            "AND genotype->'A'->>'gt' = '{gt}'".format(
                ab=0.2, ad=10, dp=20, gq=40, gt="0/1"
            )
        )

        results = query_to_list(_results)
        expected = [{"genotype": entry3["genotype"]}]

        self.assertEquals(results, expected)

    def test_genotype_and_quality_nocall(self):
        _results = Main.objects.raw(
            "SELECT id, genotype FROM main_main "
            "WHERE NOT ({ab} <= ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) "
            "AND ((genotype->'A'->'ad'->>1)::float / (genotype->'A'->>'dp')::float) <= 1-{ab} "
            "AND (genotype->'A'->'ad'->>1)::int >= {ad} "
            "AND (genotype->'A'->>'dp')::int >= {dp} "
            "AND (genotype->'A'->>'gq')::int >= {gq}) "
            "OR genotype->'A'->>'gt' = '{gt}'".format(
                ab=0.2, ad=10, dp=20, gq=40, gt="0/0"
            )
        )

        results = query_to_list(_results)
        expected = [
            {"genotype": entry1["genotype"]},
            {"genotype": entry2["genotype"]},
        ]

        self.assertEquals(results, expected)
