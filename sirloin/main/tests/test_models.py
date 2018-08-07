# from django.test import TestCase
# from ..models import Main, Pedigree
# from ..private import query_to_list, obj_to_dict


# main_entry1 = {
#     "release": "GRCh37",
#     "chromosome": "1",
#     "position": 100,
#     "reference": "A",
#     "alternative": "G",
#     "case_id": "A",
#     "frequency": 0.001,
#     "homozygous": 3,
#     "effect": ["missense_variant"],
#     "genotype": {
#         "A": {"ad": [20, 0], "dp": 20, "gq": 99, "gt": "0/0"},
#         "B": {"ad": [12, 8], "dp": 20, "gq": 99, "gt": "0/1"},
#         "C": {"ad": [7, 13], "dp": 20, "gq": 99, "gt": "0/1"},
#     },
#     "ensembl_gene_id": "ENSG000001",
# }

# main_entry2 = {
#     "release": "GRCh37",
#     "chromosome": "1",
#     "position": 200,
#     "reference": "C",
#     "alternative": "T",
#     "case_id": "A",
#     "frequency": 0.05,
#     "homozygous": 0,
#     "effect": ["synonymous_variant"],
#     "genotype": {
#         "A": {"ad": [11, 9], "dp": 20, "gq": 99, "gt": "0/1"},
#         "B": {"ad": [0, 20], "dp": 20, "gq": 99, "gt": "1/1"},
#         "C": {"ad": [8, 12], "dp": 20, "gq": 99, "gt": "0/1"},
#     },
#     "ensembl_gene_id": "ENSG000001",
# }

# pedigree_entry1 = {
#     "case": "A",
#     "pedigree": [
#         {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
#         {"sex": 1, "father": "0", "mother": "0", "patient": "D", "affected": 0},
#         {"sex": 1, "father": "D", "mother": "C", "patient": "A", "affected": 0},
#     ],
# }

# pedigree_entry2 = {
#     "case": "B",
#     "pedigree": [
#         {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
#         {"sex": 1, "father": "0", "mother": "0", "patient": "D", "affected": 0},
#         {"sex": 2, "father": "D", "mother": "C", "patient": "B", "affected": 0},
#     ],
# }


# class MainTest(TestCase):
#     def setUp(self):
#         Main.objects.get_or_create(**main_entry1)
#         Main.objects.get_or_create(**main_entry2)

#     def test_main(self):
#         result = query_to_list(Main.objects.raw("SELECT * FROM main_main"))
#         expected = [main_entry1, main_entry2]
#         self.assertEquals(result, expected)


# class PedigreeTest(TestCase):
#     def setUp(self):
#         Pedigree.objects.get_or_create(**pedigree_entry1)
#         Pedigree.objects.get_or_create(**pedigree_entry2)

#     def test_pedigree(self):
#         result = query_to_list(Main.objects.raw("SELECT * FROM main_pedigree"))
#         expected = [pedigree_entry1, pedigree_entry2]
#         self.assertEquals(result, expected)
