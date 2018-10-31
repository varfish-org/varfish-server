from django.test import TestCase
from variants.models import SmallVariant, Case
from geneinfo.models import Hgnc
from dbsnp.models import Dbsnp
from projectroles.models import Project
from frequencies.models import Exac, GnomadExomes, GnomadGenomes, ThousandGenomes
from django.forms import model_to_dict
from ..models_support import QueryBuilder
from collections import namedtuple

EntrySmallvariant = namedtuple(
    "EntrySmallvariant",
    " ".join(
        [
            "release chromosome position reference alternative var_type case_id genotype in_clinvar",
            # frequencies
            "exac_frequency exac_homozygous exac_heterozygous exac_hemizygous",
            "thousand_genomes_frequency thousand_genomes_homozygous thousand_genomes_heterozygous thousand_genomes_hemizygous",
            "gnomad_exomes_frequency gnomad_exomes_homozygous gnomad_exomes_heterozygous gnomad_exomes_hemizygous",
            "gnomad_genomes_frequency gnomad_genomes_homozygous gnomad_genomes_heterozygous gnomad_genomes_hemizygous",
            # transcript information
            "refseq_gene_id refseq_transcript_id refseq_transcript_coding refseq_hgvs_c refseq_hgvs_p refseq_effect",
            "ensembl_gene_id ensembl_transcript_id ensembl_transcript_coding ensembl_hgvs_c ensembl_hgvs_p ensembl_effect",
        ]
    ),
)
EntryCase = namedtuple("EntryCase", "sodar_uuid name index pedigree project")
EntryDbsnp = namedtuple("EntryDbsnp", "release chromosome position reference alternative rsid")
EntryHgnc = namedtuple("EntryHgnc", "hgnc_id symbol name entrez_id")
EntryGnomadgenomes = namedtuple(
    "EntryGnomadgenomes",
    (
        "release chromosome position reference alternative "
        "ac ac_afr ac_amr ac_asj ac_eas ac_fin ac_nfe ac_oth "
        "an an_afr an_amr an_asj an_eas an_fin an_nfe an_oth "
        "hemi hemi_afr hemi_amr hemi_asj hemi_eas hemi_fin hemi_nfe hemi_oth "
        "hom hom_afr hom_amr hom_asj hom_eas hom_fin hom_nfe hom_oth "
        "popmax ac_popmax an_popmax af_popmax hemi_popmax hom_popmax "
        "af af_afr af_amr af_asj af_eas af_fin af_nfe af_oth"
    ),
)
EntryGnomadexomes = namedtuple(
    "EntryGnomadexomes",
    (
        "release chromosome position reference alternative "
        "ac ac_afr ac_amr ac_asj ac_eas ac_fin ac_nfe ac_oth ac_sas "
        "an an_afr an_amr an_asj an_eas an_fin an_nfe an_oth an_sas "
        "hemi hemi_afr hemi_amr hemi_asj hemi_eas hemi_fin hemi_nfe hemi_oth hemi_sas "
        "hom hom_afr hom_amr hom_asj hom_eas hom_fin hom_nfe hom_oth hom_sas "
        "popmax ac_popmax an_popmax af_popmax hemi_popmax hom_popmax "
        "af af_afr af_amr af_asj af_eas af_fin af_nfe af_oth af_sas"
    ),
)
EntryExac = namedtuple(
    "EntryExac",
    (
        "release chromosome position reference alternative "
        "ac ac_afr ac_amr ac_eas ac_fin ac_nfe ac_oth ac_sas "
        "an an_afr an_amr an_eas an_fin an_nfe an_oth an_sas "
        "hemi hemi_afr hemi_amr hemi_eas hemi_fin hemi_nfe hemi_oth hemi_sas "
        "hom hom_afr hom_amr hom_eas hom_fin hom_nfe hom_oth hom_sas "
        "popmax ac_popmax an_popmax af_popmax hemi_popmax hom_popmax "
        "af af_afr af_amr af_eas af_fin af_nfe af_oth af_sas"
    ),
)
EntryThousandgenomes = namedtuple(
    "EntryThousandgenomes",
    "release chromosome position reference alternative ac an het hom af af_afr af_amr af_eas af_eur af_sas",
)

project = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}


########################
# Smallvariant entries #
########################
class DefaultGenerator:
    def __init__(self):
        self.position = 0

    def _next_position(self):
        pos = self.position
        self.position += 100
        return pos

    def _smallvariant_case(self):
        return EntrySmallvariant(
            "GRCh37",
            "1",
            self._next_position(),
            "A",
            "G",
            "snv",
            1,
            {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
            False,
            0.01,
            0,
            0,
            0,  # Exac
            0.01,
            0,
            0,
            0,  # Thousand genomes
            0.01,
            0,
            0,
            0,  # Gnomad exomes
            0.01,
            0,
            0,
            0,  # Gnomad genomes
            "12345",
            "NR_00001.1",
            False,
            "n.111+2T>C",
            "p.=",
            ["synonymous_variant"],  # refseq
            "ENSG000001",
            "ENST000001",
            False,
            "n.111+2T>C",
            "p.=",
            ["synonymous_variant"],  # ensembl
        )._asdict()

    def smallvariant_case1(self):
        return self._smallvariant_case()

    def smallvariant_case2(self):
        case = self._smallvariant_case()
        case["case_id"] = 2
        case["genotype"] = {
            "A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
        }
        return case

    def smallvariant_case3(self):
        case = self._smallvariant_case()
        case["case_id"] = 3
        case["genotype"] = {
            "A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "D": {"ad": 15, "db": 30, "gq": 99, "gt": "0/1"},
        }
        return case

    def smallvariant_case4(self):
        case = self._smallvariant_case()
        case["case_id"] = 4
        case["genotype"] = {
            "A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "B": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "D": {"ad": 15, "db": 30, "gq": 99, "gt": "0/1"},
        }
        return case

    def smallvariant_case5(self):
        case = self._smallvariant_case()
        case["case_id"] = 5
        case["genotype"] = {
            "A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            "B": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
        }


dg = DefaultGenerator()

# Smallvariant: Case 1
smallvariant_case1_entry1 = dg.smallvariant_case1()
smallvariant_case1_entry1["var_type"] = "snv"
smallvariant_case1_entry2 = dg.smallvariant_case1()
smallvariant_case1_entry2["var_type"] = "mnv"
smallvariant_case1_entry3 = dg.smallvariant_case1()
smallvariant_case1_entry3["var_type"] = "indel"
smallvariant_case1_entry4 = dg.smallvariant_case1()
smallvariant_case1_entry4["gnomad_genomes_frequency"] = 0.001
smallvariant_case1_entry4["gnomad_genomes_heterozygous"] = 1
smallvariant_case1_entry4["gnomad_genomes_homozygous"] = 1
smallvariant_case1_entry4["gnomad_exomes_frequency"] = 0.001
smallvariant_case1_entry4["gnomad_exomes_heterozygous"] = 1
smallvariant_case1_entry4["gnomad_exomes_homozygous"] = 1
smallvariant_case1_entry4["exac_frequency"] = 0.001
smallvariant_case1_entry4["exac_heterozygous"] = 1
smallvariant_case1_entry4["exac_homozygous"] = 1
smallvariant_case1_entry4["thousand_genomes_frequency"] = 0.001
smallvariant_case1_entry4["thousand_genomes_heterozygous"] = 1
smallvariant_case1_entry4["thousand_genomes_homozygous"] = 1
smallvariant_case1_entry5 = dg.smallvariant_case1()
smallvariant_case1_entry5["gnomad_genomes_frequency"] = 0.01
smallvariant_case1_entry5["gnomad_genomes_heterozygous"] = 2
smallvariant_case1_entry5["gnomad_genomes_homozygous"] = 2
smallvariant_case1_entry5["gnomad_exomes_frequency"] = 0.01
smallvariant_case1_entry5["gnomad_exomes_heterozygous"] = 2
smallvariant_case1_entry5["gnomad_exomes_homozygous"] = 2
smallvariant_case1_entry5["exac_frequency"] = 0.01
smallvariant_case1_entry5["exac_heterozygous"] = 2
smallvariant_case1_entry5["exac_homozygous"] = 2
smallvariant_case1_entry5["thousand_genomes_frequency"] = 0.01
smallvariant_case1_entry5["thousand_genomes_heterozygous"] = 2
smallvariant_case1_entry5["thousand_genomes_homozygous"] = 2
smallvariant_case1_entry6 = dg.smallvariant_case1()
smallvariant_case1_entry6["gnomad_genomes_frequency"] = 0.1
smallvariant_case1_entry6["gnomad_genomes_heterozygous"] = 3
smallvariant_case1_entry6["gnomad_genomes_homozygous"] = 3
smallvariant_case1_entry6["gnomad_exomes_frequency"] = 0.1
smallvariant_case1_entry6["gnomad_exomes_heterozygous"] = 3
smallvariant_case1_entry6["gnomad_exomes_homozygous"] = 3
smallvariant_case1_entry6["exac_frequency"] = 0.1
smallvariant_case1_entry6["exac_heterozygous"] = 3
smallvariant_case1_entry6["exac_homozygous"] = 3
smallvariant_case1_entry6["thousand_genomes_frequency"] = 0.1
smallvariant_case1_entry6["thousand_genomes_heterozygous"] = 3
smallvariant_case1_entry6["thousand_genomes_homozygous"] = 3
smallvariant_case1_entry7 = dg.smallvariant_case1()
smallvariant_case1_entry7["refseq_effect"] = ["missense_variant", "stop_lost"]
smallvariant_case1_entry8 = dg.smallvariant_case1()
smallvariant_case1_entry8["refseq_effect"] = ["missense_variant", "frameshift_variant"]
smallvariant_case1_entry9 = dg.smallvariant_case1()
smallvariant_case1_entry9["refseq_effect"] = ["frameshift_variant"]
smallvariant_case1_entry10 = dg.smallvariant_case1()
smallvariant_case1_entry10["genotype"]["A"] = {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}
smallvariant_case1_entry11 = dg.smallvariant_case1()
smallvariant_case1_entry11["genotype"]["A"] = {"ad": 0, "dp": 30, "gq": 99, "gt": "0/0"}
smallvariant_case1_entry12 = dg.smallvariant_case1()
smallvariant_case1_entry12["genotype"]["A"] = {"ad": 30, "dp": 30, "gq": 99, "gt": "1/1"}
smallvariant_case1_entry13 = dg.smallvariant_case1()
smallvariant_case1_entry13["genotype"]["A"] = {"ad": 0, "dp": 10, "gq": 66, "gt": "./."}
smallvariant_case1_entry14 = dg.smallvariant_case1()
smallvariant_case1_entry14["genotype"]["A"] = {"ad": 15, "dp": 20, "gq": 33, "gt": "1/0"}
smallvariant_case1_entry15 = dg.smallvariant_case1()
smallvariant_case1_entry15["genotype"]["A"] = {"ad": 21, "dp": 30, "gq": 99, "gt": "0/1"}
smallvariant_case1_entry16 = dg.smallvariant_case1()
smallvariant_case1_entry16["genotype"]["A"] = {"ad": 9, "dp": 30, "gq": 99, "gt": "0/1"}
smallvariant_case1_entry17 = dg.smallvariant_case1()
smallvariant_case1_entry17["genotype"]["A"] = {"ad": 6, "dp": 30, "gq": 99, "gt": "0/1"}

# recessive, not disease causing
smallvariant_case3_entry1 = dg.smallvariant_case3()
smallvariant_case3_entry1["genotype"]["A"]["gt"] = "0/1"
smallvariant_case3_entry1["genotype"]["C"]["gt"] = "0/1"
smallvariant_case3_entry1["genotype"]["D"]["gt"] = "0/1"
# dominant
smallvariant_case3_entry2 = dg.smallvariant_case3()
smallvariant_case3_entry2["genotype"]["A"]["gt"] = "1/1"
smallvariant_case3_entry2["genotype"]["A"]["ad"] = 30
smallvariant_case3_entry2["genotype"]["C"]["gt"] = "1/1"
smallvariant_case3_entry2["genotype"]["C"]["ad"] = 30
smallvariant_case3_entry2["genotype"]["D"]["gt"] = "0/0"
smallvariant_case3_entry2["genotype"]["D"]["ad"] = 0
# recessive, disease causing
smallvariant_case3_entry3 = dg.smallvariant_case3()
smallvariant_case3_entry3["genotype"]["A"]["gt"] = "1/1"
smallvariant_case3_entry3["genotype"]["A"]["ad"] = 30
smallvariant_case3_entry3["genotype"]["C"]["gt"] = "0/1"
smallvariant_case3_entry3["genotype"]["D"]["gt"] = "0/1"
# de novo
smallvariant_case3_entry4 = dg.smallvariant_case3()
smallvariant_case3_entry4["genotype"]["A"]["gt"] = "0/1"
smallvariant_case3_entry4["genotype"]["C"]["gt"] = "0/0"
smallvariant_case3_entry4["genotype"]["C"]["ad"] = 0
smallvariant_case3_entry4["genotype"]["D"]["gt"] = "0/0"
smallvariant_case3_entry4["genotype"]["D"]["ad"] = 0
# compound heterozygous
smallvariant_case3_entry5 = dg.smallvariant_case3()
smallvariant_case3_entry5["genotype"]["A"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["C"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["D"]["gt"] = "0/0"
smallvariant_case3_entry5["genotype"]["D"]["ad"] = 0
smallvariant_case3_entry5["refseq_gene_id"] = "123"
smallvariant_case3_entry6 = dg.smallvariant_case3()
smallvariant_case3_entry5["genotype"]["A"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["C"]["gt"] = "0/0"
smallvariant_case3_entry5["genotype"]["C"]["ad"] = 0
smallvariant_case3_entry5["genotype"]["D"]["gt"] = "0/1"
smallvariant_case3_entry6["refseq_gene_id"] = "123"
smallvariant_case3_entry7 = dg.smallvariant_case3()
smallvariant_case3_entry5["genotype"]["A"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["C"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["D"]["gt"] = "0/1"
smallvariant_case3_entry7["refseq_gene_id"] = "123"
smallvariant_case3_entry8 = dg.smallvariant_case3()
smallvariant_case3_entry5["genotype"]["A"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["C"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["D"]["gt"] = "0/0"
smallvariant_case3_entry8["refseq_gene_id"] = "456"
smallvariant_case3_entry9 = dg.smallvariant_case3()
smallvariant_case3_entry5["genotype"]["A"]["gt"] = "1/1"
smallvariant_case3_entry5["genotype"]["A"]["ad"] = 30
smallvariant_case3_entry5["genotype"]["C"]["gt"] = "0/0"
smallvariant_case3_entry5["genotype"]["C"]["ad"] = 0
smallvariant_case3_entry5["genotype"]["D"]["gt"] = "0/1"
smallvariant_case3_entry9["refseq_gene_id"] = "456"
smallvariant_case3_entry10 = dg.smallvariant_case3()
smallvariant_case3_entry5["genotype"]["A"]["gt"] = "0/0"
smallvariant_case3_entry5["genotype"]["A"]["ad"] = 0
smallvariant_case3_entry5["genotype"]["C"]["gt"] = "0/1"
smallvariant_case3_entry5["genotype"]["D"]["gt"] = "0/0"
smallvariant_case3_entry5["genotype"]["D"]["ad"] = 0
smallvariant_case3_entry10["refseq_gene_id"] = "456"
# smallvariant_case3_entry11 = dg.smallvariant_case3()
# smallvariant_case3_entry11["refseq_gene_id"] = "789"
# smallvariant_case3_entry12 = dg.smallvariant_case3()
# smallvariant_case3_entry12["refseq_gene_id"] = "789"
# smallvariant_case3_entry13 = dg.smallvariant_case3()
# smallvariant_case3_entry13["refseq_gene_id"] = "789"

################
# Case entries #
################

# Case: singleton
case_entry1 = EntryCase(
    "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "A",
    "A",
    [{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
    1,
)
# Case: one parent
case_entry2 = EntryCase(
    "a705b1c8-3eda-48e5-8989-86a259a56b08",
    "A",
    "A",
    [
        {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
        {"sex": 1, "father": "D", "mother": "C", "patient": "A", "affected": 1},
    ],
    1,
)
# Case: trio
case_entry3 = EntryCase(
    "3b0f155d-b02a-49f0-be74-15e1732c7fe3",
    "A",
    "A",
    [
        {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
        {"sex": 1, "father": "0", "mother": "0", "patient": "D", "affected": 0},
        {"sex": 1, "father": "D", "mother": "C", "patient": "A", "affected": 1},
    ],
    1,
)
# Case: siblings
case_entry4 = EntryCase(
    "e3d156a6-ab2d-4d17-999a-ed85aabe2d23",
    "A",
    "A",
    [
        {"sex": 2, "father": "0", "mother": "0", "patient": "C", "affected": 0},
        {"sex": 1, "father": "0", "mother": "0", "patient": "D", "affected": 0},
        {"sex": 1, "father": "D", "mother": "C", "patient": "A", "affected": 1},
        {"sex": 1, "father": "D", "mother": "C", "patient": "B", "affected": 1},
    ],
    1,
)
# Case: siblings with artificial parents
case_entry5 = EntryCase(
    "0d097e38-abdb-49c1-88eb-0d110f708367",
    "A",
    "A",
    [
        {"sex": 2, "father": "0", "mother": "0", "patient": "FAM_A_Ib", "affected": 0},
        {"sex": 1, "father": "0", "mother": "0", "patient": "FAM_A_Ia", "affected": 0},
        {"sex": 1, "father": "FAM_A_Ia", "mother": "FAM_A_Ib", "patient": "A", "affected": 1},
        {"sex": 1, "father": "FAM_A_Ia", "mother": "FAM_A_Ib", "patient": "B", "affected": 1},
    ],
    1,
)

#################
# Dbsnp entries #
#################
# dbsnp_entry1 = EntryDbsnp(
#     smallvariant_entry1["release"], smallvariant_entry1["chromosome"], smallvariant_entry1["position"],
#     smallvariant_entry1["reference"], smallvariant_entry1["alternative"], "rs0001"
# )

################
# Hgnc entries #
################
hgnc_entry1 = EntryHgnc("HGNC:1", "AAA", "AAA gene", "123")._asdict()
hgnc_entry2 = EntryHgnc("HGNC:2", "BBB", "BBB gene", "456")._asdict()
hgnc_entry3 = EntryHgnc("HGNC:3", "CCC", "CCC gene", "789")._asdict()

#####################
# Frequency entries #
#####################
gnomadgenomes_entry1 = EntryGnomadgenomes(
    "GRCh37",
    "1",
    100,
    "A",
    "G",
    None,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    None,
    8726,
    838,
    302,
    1620,
    3464,
    14996,
    982,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    "AFR",
    1,
    8726,
    0.0001146,
    None,
    0,
    None,
    0.0001146,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
)
gnomadexomes_entry1 = EntryGnomadexomes(
    "GRCh37",
    "1",
    100,
    "A",
    "G",
    None,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    None,
    8726,
    838,
    302,
    1620,
    3464,
    14996,
    982,
    892,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    "AFR",
    1,
    8726,
    0.0001146,
    None,
    0,
    None,
    0.0001146,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
)
exac_entry1 = EntryExac(
    "GRCh37",
    "1",
    100,
    "A",
    "G",
    None,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    None,
    8726,
    838,
    302,
    1620,
    3464,
    14996,
    982,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    "AFR",
    1,
    8726,
    0.0001146,
    None,
    0,
    None,
    0.0001146,
    0,
    0,
    0,
    0,
    0,
    0,
)
thousandgenomes_entry1 = EntryThousandgenomes(
    "GRCh37", "1", 100, "A", "G", 3, 5008, 3, 0, 0.000058, 0, 0.0054, 0, 0, 0
)


class TestHelperMixin:
    def _helper(self, function_name, kwargs_patch, length):
        # get a copy of kwargs
        kwargs = dict(self.kwargs)
        # patch copy, order is important!
        kwargs = {**kwargs, **kwargs_patch}
        qb = QueryBuilder()
        base = qb.build_base_query(kwargs)
        query, args = base, kwargs
        if function_name:
            fun = getattr(qb, function_name)
            conditions = [fun(kwargs)]
            query, args = qb.build_top_level_query(base, conditions)
        results = self.database.objects.raw(query, args)
        # check only length of results
        self.assertEquals(length, len(list(results)))


class TestBase(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {"database_select": "refseq"}
        # create smallvariant entries for case 1
        SmallVariant.objects.create(**smallvariant_case1_entry1)

    def test_base_query_refseq(self):
        self._helper(None, {}, 1)

    def test_base_query_ensembl(self):
        self._helper(None, {"database_select": "ensembl"}, 1)


class TestCaseDB(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {"database_select": "refseq"}

        # create project in projectroles app
        project_object = Project.objects.create(**project)
        # create case entries, connected to project
        case_entry1_copy = case_entry1._asdict()
        case_entry1_copy["project"] = project_object
        Case.objects.create(**case_entry1_copy)
        SmallVariant.objects.create(**smallvariant_case1_entry1)

    def test_case_uuid_wrong(self):
        self._helper("build_case_term", {"case": "88888888-8888-8888-8888-888888888888"}, 0)

    def test_case_uuid_correct(self):
        self._helper("build_case_term", {"case": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3"}, 1)


class TestVarType(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {
            "database_select": "refseq",
            "var_type_snv": False,
            "var_type_mnv": False,
            "var_type_indel": False,
        }
        SmallVariant.objects.create(**smallvariant_case1_entry1)
        SmallVariant.objects.create(**smallvariant_case1_entry2)
        SmallVariant.objects.create(**smallvariant_case1_entry3)

    def test_var_type_none(self):
        self._helper("build_vartype_term", {}, 0)

    def test_var_type_snv(self):
        self._helper("build_vartype_term", {"var_type_snv": True}, 1)

    def test_var_type_mnv(self):
        self._helper("build_vartype_term", {"var_type_mnv": True}, 1)

    def test_var_type_indel(self):
        self._helper("build_vartype_term", {"var_type_indel": True}, 1)

    def test_var_type_all(self):
        self._helper(
            "build_vartype_term",
            {"var_type_snv": True, "var_type_mnv": True, "var_type_indel": True},
            3,
        )


class TestFrequency(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {
            "database_select": "refseq",
            "gnomad_exomes_enabled": False,
            "gnomad_exomes_frequency": 0.0,
            "gnomad_exomes_heterozygous": 0,
            "gnomad_exomes_homozygous": 0,
            "gnomad_genomes_enabled": False,
            "gnomad_genomes_frequency": 0.0,
            "gnomad_genomes_heterozygous": 0,
            "gnomad_genomes_homozygous": 0,
            "exac_enabled": False,
            "exac_frequency": 0.0,
            "exac_heterozygous": 0,
            "exac_homozygous": 0,
            "thousand_genomes_enabled": False,
            "thousand_genomes_frequency": 0.0,
            "thousand_genomes_heterozygous": 0,
            "thousand_genomes_homozygous": 0,
        }
        SmallVariant.objects.create(**smallvariant_case1_entry4)
        SmallVariant.objects.create(**smallvariant_case1_entry5)
        SmallVariant.objects.create(**smallvariant_case1_entry6)

    def test_gnomad_exomes_frequency_disabled(self):
        self._helper("build_frequency_term", {}, 3)

    def test_gnomad_exomes_frequency_enabled(self):
        self._helper("build_frequency_term", {"gnomad_exomes_enabled": True}, 0)

    def test_gnomad_exomes_frequency_limits(self):
        self._helper(
            "build_frequency_term",
            {"gnomad_exomes_enabled": True, "gnomad_exomes_frequency": 0.01},
            2,
        )

    def test_gnomad_exomes_frequency_none(self):
        self._helper(
            "build_frequency_term",
            {"gnomad_exomes_enabled": True, "gnomad_exomes_frequency": None},
            3,
        )

    def test_gnomad_exomes_heterozygous_disabled(self):
        self._helper("build_heterozygous_term", {}, 3)

    def test_gnomad_exomes_heterozygous_enabled(self):
        self._helper("build_heterozygous_term", {"gnomad_exomes_enabled": True}, 0)

    def test_gnomad_exomes_heterozygous_limits(self):
        self._helper(
            "build_heterozygous_term",
            {"gnomad_exomes_enabled": True, "gnomad_exomes_heterozygous": 2},
            2,
        )

    def test_gnomad_exomes_heterozygous_none(self):
        self._helper(
            "build_heterozygous_term",
            {"gnomad_exomes_enabled": True, "gnomad_exomes_heterozygous": None},
            3,
        )

    def test_gnomad_exomes_homozygous_disabled(self):
        self._helper("build_homozygous_term", {}, 3)

    def test_gnomad_exomes_homozygous_enabled(self):
        self._helper("build_homozygous_term", {"gnomad_exomes_enabled": True}, 0)

    def test_gnomad_exomes_homozygous_limits(self):
        self._helper(
            "build_homozygous_term",
            {"gnomad_exomes_enabled": True, "gnomad_exomes_homozygous": 2},
            2,
        )

    def test_gnomad_exomes_homozygous_none(self):
        self._helper(
            "build_homozygous_term",
            {"gnomad_exomes_enabled": True, "gnomad_exomes_homozygous": None},
            3,
        )

    def test_gnomad_genomes_disabled(self):
        self._helper("build_frequency_term", {}, 3)

    def test_gnomad_genomes_enabled(self):
        self._helper("build_frequency_term", {"gnomad_genomes_enabled": True}, 0)

    def test_gnomad_genomes_frequency_limits(self):
        self._helper(
            "build_frequency_term",
            {"gnomad_genomes_enabled": True, "gnomad_genomes_frequency": 0.01},
            2,
        )

    def test_gnomad_genomes_frequency_none(self):
        self._helper(
            "build_frequency_term",
            {"gnomad_genomes_enabled": True, "gnomad_genomes_frequency": None},
            3,
        )

    def test_gnomad_genomes_heterozygous_disabled(self):
        self._helper("build_heterozygous_term", {}, 3)

    def test_gnomad_genomes_heterozygous_enabled(self):
        self._helper("build_heterozygous_term", {"gnomad_genomes_enabled": True}, 0)

    def test_gnomad_genomes_heterozygous_limits(self):
        self._helper(
            "build_heterozygous_term",
            {"gnomad_genomes_enabled": True, "gnomad_genomes_heterozygous": 2},
            2,
        )

    def test_gnomad_genomes_heterozygous_none(self):
        self._helper(
            "build_heterozygous_term",
            {"gnomad_genomes_enabled": True, "gnomad_genomes_heterozygous": None},
            3,
        )

    def test_gnomad_genomes_homozygous_disabled(self):
        self._helper("build_homozygous_term", {}, 3)

    def test_gnomad_genomes_homozygous_enabled(self):
        self._helper("build_homozygous_term", {"gnomad_genomes_enabled": True}, 0)

    def test_gnomad_genomes_homozygous_limits(self):
        self._helper(
            "build_homozygous_term",
            {"gnomad_genomes_enabled": True, "gnomad_genomes_homozygous": 2},
            2,
        )

    def test_gnomad_genomes_homozygous_none(self):
        self._helper(
            "build_homozygous_term",
            {"gnomad_genomes_enabled": True, "gnomad_genomes_homozygous": None},
            3,
        )

    def test_exac_disabled(self):
        self._helper("build_frequency_term", {}, 3)

    def test_exac_enabled(self):
        self._helper("build_frequency_term", {"exac_enabled": True}, 0)

    def test_exac_frequency_limits(self):
        self._helper("build_frequency_term", {"exac_enabled": True, "exac_frequency": 0.01}, 2)

    def test_exac_frequency_none(self):
        self._helper("build_frequency_term", {"exac_enabled": True, "exac_frequency": None}, 3)

    def test_exac_heterozygous_disabled(self):
        self._helper("build_heterozygous_term", {}, 3)

    def test_exac_heterozygous_enabled(self):
        self._helper("build_heterozygous_term", {"exac_enabled": True}, 0)

    def test_exac_heterozygous_limits(self):
        self._helper("build_heterozygous_term", {"exac_enabled": True, "exac_heterozygous": 2}, 2)

    def test_exac_heterozygous_none(self):
        self._helper(
            "build_heterozygous_term", {"exac_enabled": True, "exac_heterozygous": None}, 3
        )

    def test_exac_homozygous_disabled(self):
        self._helper("build_homozygous_term", {}, 3)

    def test_exac_homozygous_enabled(self):
        self._helper("build_homozygous_term", {"exac_enabled": True}, 0)

    def test_exac_homozygous_limits(self):
        self._helper("build_homozygous_term", {"exac_enabled": True, "exac_homozygous": 2}, 2)

    def test_exac_homozygous_none(self):
        self._helper("build_homozygous_term", {"exac_enabled": True, "exac_homozygous": None}, 3)

    def test_thousand_genomes_disabled(self):
        self._helper("build_frequency_term", {}, 3)

    def test_thousand_genomes_enabled(self):
        self._helper("build_frequency_term", {"thousand_genomes_enabled": True}, 0)

    def test_thousand_genomes_frequency_limits(self):
        self._helper(
            "build_frequency_term",
            {"thousand_genomes_enabled": True, "thousand_genomes_frequency": 0.01},
            2,
        )

    def test_thousand_genomes_frequency_none(self):
        self._helper(
            "build_frequency_term",
            {"thousand_genomes_enabled": True, "thousand_genomes_frequency": None},
            3,
        )

    def test_thousand_genomes_heterozygous_disabled(self):
        self._helper("build_heterozygous_term", {}, 3)

    def test_thousand_genomes_heterozygous_enabled(self):
        self._helper("build_heterozygous_term", {"thousand_genomes_enabled": True}, 0)

    def test_thousand_genomes_heterozygous_limits(self):
        self._helper(
            "build_heterozygous_term",
            {"thousand_genomes_enabled": True, "thousand_genomes_heterozygous": 2},
            2,
        )

    def test_thousand_genomes_heterozygous_none(self):
        self._helper(
            "build_heterozygous_term",
            {"thousand_genomes_enabled": True, "thousand_genomes_heterozygous": None},
            3,
        )

    def test_thousand_genomes_homozygous_disabled(self):
        self._helper("build_homozygous_term", {}, 3)

    def test_thousand_genomes_homozygous_enabled(self):
        self._helper("build_homozygous_term", {"thousand_genomes_enabled": True}, 0)

    def test_thousand_genomes_homozygous_limits(self):
        self._helper(
            "build_homozygous_term",
            {"thousand_genomes_enabled": True, "thousand_genomes_homozygous": 2},
            2,
        )

    def test_thousand_genomes_homozygous_none(self):
        self._helper(
            "build_homozygous_term",
            {"thousand_genomes_enabled": True, "thousand_genomes_homozygous": None},
            3,
        )


class TestEffects(TestHelperMixin, TestCase):
    def setUp(self):
        # set extended diff report
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {
            "database_select": "refseq",
            # "missense_variant", "stop_lost", "frameshift_variant"
            "effects": [],
        }
        SmallVariant.objects.create(**smallvariant_case1_entry7)
        SmallVariant.objects.create(**smallvariant_case1_entry8)
        SmallVariant.objects.create(**smallvariant_case1_entry9)

    def test_effects_none(self):
        self._helper("build_effects_term", {}, 0)

    def test_effects_one(self):
        self._helper("build_effects_term", {"effects": ["missense_variant"]}, 2)

    def test_effects_two(self):
        self._helper("build_effects_term", {"effects": ["stop_lost", "frameshift_variant"]}, 3)

    def test_effects_all(self):
        self._helper(
            "build_effects_term",
            {"effects": ["missense_variant", "stop_lost", "frameshift_variant"]},
            3,
        )


class TestGenotypeSingleton(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {
            "database_select": "refseq",
            "member": "A",
            "gt": None,
            "ad": 15,
            "ab": 0.3,
            "gq": 20,
            "dp": 10,
            "fail": "drop-variant",
        }
        project_object = Project.objects.create(**project)
        case_entry1_copy = case_entry1._asdict()
        case_entry1_copy["project"] = project_object
        Case.objects.create(**case_entry1_copy)
        SmallVariant.objects.create(**smallvariant_case1_entry10)
        SmallVariant.objects.create(**smallvariant_case1_entry11)
        SmallVariant.objects.create(**smallvariant_case1_entry12)
        SmallVariant.objects.create(**smallvariant_case1_entry13)
        SmallVariant.objects.create(**smallvariant_case1_entry14)
        SmallVariant.objects.create(**smallvariant_case1_entry15)
        SmallVariant.objects.create(**smallvariant_case1_entry16)
        SmallVariant.objects.create(**smallvariant_case1_entry17)

    def test_genotype_gt_any(self):
        self._helper("build_genotype_gt_term", {"gt": None}, 8)

    def test_genotype_gt_ref(self):
        self._helper("build_genotype_gt_term", {"gt": ("0/0",)}, 1)

    def test_genotype_gt_het(self):
        self._helper("build_genotype_gt_term", {"gt": ("0/1", "1/0")}, 5)

    def test_genotype_gt_hom(self):
        self._helper("build_genotype_gt_term", {"gt": ("1/1",)}, 1)

    def test_genotype_gt_variant(self):
        self._helper("build_genotype_gt_term", {"gt": ("1/0", "0/1", "1/1")}, 6)

    def test_genotype_gt_non_variant(self):
        self._helper("build_genotype_gt_term", {"gt": ("0/0", "./.")}, 2)

    def test_genotype_gt_non_reference(self):
        self._helper("build_genotype_gt_term", {"gt": ("1/0", "0/1", "1/1", "./.")}, 7)

    def test_genotype_ad_limits(self):
        self._helper("build_genotype_ad_term", {"ad": 15}, 5)

    def test_genotype_ab_limits(self):
        self._helper("build_genotype_ab_term", {"ab": 0.3}, 6)

    def test_genotype_dp_limits(self):
        self._helper("build_genotype_dp_term", {"dp": 20}, 7)

    def test_genotype_gq_limits(self):
        self._helper("build_genotype_gq_term", {"gq": 66}, 7)

    def test_genotype_fail_ignore(self):
        self._helper("build_genotype_term", {"fail": "ignore"}, 8)

    def test_genotype_fail_drop_variant(self):
        self._helper("build_genotype_term", {"fail": "drop-variant"}, 4)

    def test_genotype_fail_no_call(self):
        self._helper("build_genotype_term", {"fail": "no-call", "gt": ("0/1",)}, 6)


class TestGenotypeTrio(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {
            "database_select": "refseq",
            "genotype": [
                {
                    "member": "A",
                    "gt": ("0/1",),
                    "ad": 15,
                    "ab": 0.3,
                    "dp": 30,
                    "gq": 99,
                    "fail": "ignore",
                },
                {
                    "member": "C",
                    "gt": ("0/1",),
                    "ad": 15,
                    "ab": 0.3,
                    "dp": 30,
                    "gq": 99,
                    "fail": "ignore",
                },
                {
                    "member": "D",
                    "gt": ("0/1",),
                    "ad": 15,
                    "ab": 0.3,
                    "dp": 30,
                    "gq": 99,
                    "fail": "ignore",
                },
            ],
        }
        project_object = Project.objects.create(**project)
        case_entry3_copy = case_entry3._asdict()
        case_entry3_copy["project"] = project_object
        Case.objects.create(**case_entry3_copy)
        SmallVariant.objects.create(**smallvariant_case3_entry1)
        SmallVariant.objects.create(**smallvariant_case3_entry2)
        SmallVariant.objects.create(**smallvariant_case3_entry3)
        SmallVariant.objects.create(**smallvariant_case3_entry4)

    def test_genotype_trio_recessive_unaffected(self):
        self._helper("build_genotype_term_list", {}, 1)

    def test_genotype_trio_recessive_affected(self):
        self._helper(
            "build_genotype_term_list",
            {
                "genotype": [
                    {
                        "member": "A",
                        "gt": ("1/1",),
                        "ad": 30,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                    {
                        "member": "C",
                        "gt": ("0/1", "1/0"),
                        "ad": 15,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                    {
                        "member": "D",
                        "gt": ("0/1", "1/0"),
                        "ad": 15,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                ]
            },
            1,
        )

    def test_genotype_trio_denovo(self):
        self._helper(
            "build_genotype_term_list",
            {
                "genotype": [
                    {
                        "member": "A",
                        "gt": ("0/1", "1/0"),
                        "ad": 15,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                    {
                        "member": "C",
                        "gt": ("0/0",),
                        "ad": 0,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                    {
                        "member": "D",
                        "gt": ("0/0",),
                        "ad": 0,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                ]
            },
            1,
        )

    def test_genotype_trio_dominant(self):
        self._helper(
            "build_genotype_term_list",
            {
                "genotype": [
                    {
                        "member": "A",
                        "gt": ("1/1",),
                        "ad": 30,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                    {
                        "member": "C",
                        "gt": ("1/1",),
                        "ad": 30,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                    {
                        "member": "D",
                        "gt": ("0/0",),
                        "ad": 0,
                        "ab": 0.3,
                        "dp": 30,
                        "gq": 99,
                        "fail": "ignore",
                    },
                ]
            },
            1,
        )


class TestComphet(TestHelperMixin, TestCase):
    def setUp(self):
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {
            "case": "3b0f155d-b02a-49f0-be74-15e1732c7fe3",
            "effects": ["synonymous_variant"],
            "gene_blacklist": [],
            "database_select": "refseq",
            "var_type_snv": True,
            "var_type_mnv": True,
            "var_type_indel": True,
            "gnomad_exomes_enabled": False,
            "gnomad_exomes_frequency": 0.0,
            "gnomad_exomes_heterozygous": 0,
            "gnomad_exomes_homozygous": 0,
            "gnomad_genomes_enabled": False,
            "gnomad_genomes_frequency": 0.0,
            "gnomad_genomes_heterozygous": 0,
            "gnomad_genomes_homozygous": 0,
            "exac_enabled": False,
            "exac_frequency": 0.0,
            "exac_heterozygous": 0,
            "exac_homozygous": 0,
            "thousand_genomes_enabled": False,
            "thousand_genomes_frequency": 0.0,
            "thousand_genomes_heterozygous": 0,
            "thousand_genomes_homozygous": 0,
        }
        project_object = Project.objects.create(**project)
        case_entry3_copy = case_entry3._asdict()
        case_entry3_copy["project"] = project_object
        self.case = Case.objects.create(**case_entry3_copy)
        SmallVariant.objects.create(**smallvariant_case3_entry5)
        SmallVariant.objects.create(**smallvariant_case3_entry6)
        SmallVariant.objects.create(**smallvariant_case3_entry7)
        SmallVariant.objects.create(**smallvariant_case3_entry8)
        SmallVariant.objects.create(**smallvariant_case3_entry9)
        SmallVariant.objects.create(**smallvariant_case3_entry10)
        Hgnc.objects.create(**hgnc_entry1)
        Hgnc.objects.create(**hgnc_entry2)

    def test_comphet(self):
        qb = QueryBuilder()
        kwargs = dict(self.kwargs)
        kwargs["pedigree"] = [
            {"patient": "A", "role": "index"},
            {"patient": "D", "role": "father"},
            {"patient": "C", "role": "mother"},
        ]
        kwargs["genotype"] = [
            {"member": "A", "gt": None, "ad": 15, "ab": 0.3, "dp": 30, "gq": 99, "fail": "ignore"},
            {"member": "C", "gt": None, "ad": 15, "ab": 0.3, "dp": 30, "gq": 99, "fail": "ignore"},
            {"member": "D", "gt": None, "ad": 15, "ab": 0.3, "dp": 30, "gq": 99, "fail": "ignore"},
        ]
        query, args = qb.build_comphet_query(kwargs)
        results = SmallVariant.objects.raw(query, args)
        self.assertEquals(2, len(list(results)))


# class TestGenotypeTrio(TestHelperMixin, TestCase):
#     def setUp(self):
#         self.maxDiff = None
#         self.database = SmallVariant
#         self.kwargs = {
#             "database_select": "refseq",
#             "genotype": [
#                 {"gt": ("0/1",), "member": "A", "ad": 15},
#                 {"gt": ("0/1",), "member": "C", },
#                 {"gt": ("0/1",), "member": "D", },
#             ],
#         }
#         project_object = Project.objects.create(**project)
#         case_entry2_copy = case_entry2._asdict()
#         # case_entry3_copy = case_entry3._asdict()
#         # case_entry4_copy = case_entry4._asdict()
#         # case_entry5_copy = case_entry5._asdict()
#         case_entry2_copy["project"] = project_object
#         # case_entry3_copy["project"] = project_object
#         # case_entry4_copy["project"] = project_object
#         # case_entry5_copy["project"] = project_object
#         Case.objects.create(**case_entry2_copy)
#         # Case.objects.create(**case_entry3_copy)
#         # Case.objects.create(**case_entry4_copy)
#         # Case.objects.create(**case_entry5_copy)
#         SmallVariant.objects.create(**smallvariant_case3_entry1)
#         SmallVariant.objects.create(**smallvariant_case3_entry2)
#         SmallVariant.objects.create(**smallvariant_case3_entry3)
#         SmallVariant.objects.create(**smallvariant_case3_entry4)
#
#     def test_genotype_trio_recessive(self):
#         self._helper("build_genotype_term_list", {
#             "genotype": [
#                 {"gt": ("0/1", "1/0"), "member": "A"},
#                 {"gt": ("0/1", "1/0"), "member": "C"},
#                 {"gt": ("0/0",), "member": "D"}
#             ]}, 1)
#
#     def test_genotype_trio_denovo(self):
#         self._helper("build_genotype_term_list", {
#             "genotype": [
#                 {"gt": ("0/1", "1/0", "1/1"), "member": "A"},
#                 {"gt": ("0/0",), "member": "C"},
#                 {"gt": ("0/0",), "member": "D"}
#             ]}, 1)


class Test(TestHelperMixin, TestCase):
    def setUp(self):
        # set extended diff report
        self.maxDiff = None
        self.database = SmallVariant
        self.kwargs = {"database_select": "refseq"}

        # create project in projectroles app
        project_object = Project.objects.create(**project)

        # create case entries, connected to project
        case_entry1_copy = case_entry1._asdict()
        # case_entry2_copy = case_entry2._asdict()
        # case_entry3_copy = case_entry3._asdict()
        # case_entry4_copy = case_entry4._asdict()
        # case_entry5_copy = case_entry5._asdict()
        case_entry1_copy["project"] = project_object
        # case_entry2_copy["project"] = project_object
        # case_entry3_copy["project"] = project_object
        # case_entry4_copy["project"] = project_object
        # case_entry5_copy["project"] = project_object
        Case.objects.create(**case_entry1_copy)
        # Case.objects.create(**case_entry2_copy)
        # Case.objects.create(**case_entry3_copy)
        # Case.objects.create(**case_entry4_copy)
        # Case.objects.create(**case_entry5_copy)

        # create frequency tables
        # GnomadGenomes.objects.create(**gnomadgenomes_entry1._asdict())
        # GnomadExomes.objects.create(**gnomadexomes_entry1._asdict())
        # Exac.objects.create(**exac_entry1._asdict())
        # ThousandGenomes.objects.create(**thousandgenomes_entry1._asdict())

        # create smallvariant entries for case 1
        # SmallVariant.objects.create(**smallvariant_case1_entry1)
        # SmallVariant.objects.create(**smallvariant_case1_entry2)
        # SmallVariant.objects.create(**smallvariant_case1_entry3)

    #     Dbsnp.objects.get_or_create(**dbsnp_entry1)
    #     Dbsnp.objects.get_or_create(**dbsnp_entry2)
    #     Dbsnp.objects.get_or_create(**dbsnp_entry3)
    #     Hgnc.objects.get_or_create(**hgnc_entry1)
    #     Hgnc.objects.get_or_create(**hgnc_entry2)
    #     Hgnc.objects.get_or_create(**hgnc_entry3)

    # def test_base_query_refseq(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     _results = SmallVariant.objects.raw(base)
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     results_sorted = sorted(results, key=lambda key: key["position"])
    #     expected = [smallvariant_case1_entry1, smallvariant_case1_entry2, smallvariant_case1_entry3]
    #     self.assertEquals(results_sorted, expected)
    #
    # def test_base_query_ensembl(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'ensembl'})
    #     _results = SmallVariant.objects.raw(base)
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     results_sorted = sorted(results, key=lambda key: key["position"])
    #     expected = [smallvariant_case1_entry1, smallvariant_case1_entry2, smallvariant_case1_entry3]
    #     self.assertEquals(results_sorted, expected)
    #
    # def test_var_type_none(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": False,
    #         "var_type_mnv": False,
    #         "var_type_indel": False,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = []
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_snv(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": True,
    #         "var_type_mnv": False,
    #         "var_type_indel": False,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry1]
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_mnv(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": False,
    #         "var_type_mnv": True,
    #         "var_type_indel": False,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry2]
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_indel(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": False,
    #         "var_type_mnv": False,
    #         "var_type_indel": True,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_snv_mnv(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": True,
    #         "var_type_mnv": True,
    #         "var_type_indel": False,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry1, smallvariant_case1_entry2]
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_snv_indel(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": True,
    #         "var_type_mnv": False,
    #         "var_type_indel": True,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry1, smallvariant_case1_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_mnv_indel(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": False,
    #         "var_type_mnv": True,
    #         "var_type_indel": True,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry2, smallvariant_case1_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_var_type_snv_mnv_indel(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_vartype_term({
    #         "var_type_snv": True,
    #         "var_type_mnv": True,
    #         "var_type_indel": True,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     expected = [smallvariant_case1_entry1, smallvariant_case1_entry2, smallvariant_case1_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_frequency_gnomad_exomes(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_frequency_term({
    #         "gnomad_exomes_enabled": True,
    #         "gnomad_exomes_frequency": 0.01,
    #         "gnomad_genomes_enabled": False,
    #         "gnomad_genomes_frequency": None,
    #         "exac_enabled": False,
    #         "exac_frequency": None,
    #         "thousand_genomes_enabled": False,
    #         "thousand_genomes_frequency": None,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     results_sorted = sorted(results, key=lambda key: key["position"])
    #     expected = [smallvariant_case1_entry4, smallvariant_case1_entry6]
    #     self.assertEquals(results_sorted, expected)
    #
    # def test_frequency_gnomad_genomes(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_frequency_term({
    #         "gnomad_exomes_enabled": False,
    #         "gnomad_exomes_frequency": None,
    #         "gnomad_genomes_enabled": True,
    #         "gnomad_genomes_frequency": 0.01,
    #         "exac_enabled": False,
    #         "exac_frequency": None,
    #         "thousand_genomes_enabled": False,
    #         "thousand_genomes_frequency": None,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     results_sorted = sorted(results, key=lambda key: key["position"])
    #     expected = [smallvariant_case1_entry4, smallvariant_case1_entry5]
    #     self.assertEquals(results_sorted, expected)
    #
    # def test_frequency_exac(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_frequency_term({
    #         "gnomad_exomes_enabled": False,
    #         "gnomad_exomes_frequency": None,
    #         "gnomad_genomes_enabled": False,
    #         "gnomad_genomes_frequency": None,
    #         "exac_enabled": True,
    #         "exac_frequency": 0.01,
    #         "thousand_genomes_enabled": False,
    #         "thousand_genomes_frequency": None,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     results_sorted = sorted(results, key=lambda key: key["position"])
    #     expected = [smallvariant_case1_entry5, smallvariant_case1_entry6]
    #     self.assertEquals(results_sorted, expected)
    #
    # def test_frequency_thousand_genomes(self):
    #     qb = QueryBuilder()
    #     base = qb.build_base_query({'database_select': 'refseq'})
    #     condition = qb.build_frequency_term({
    #         "gnomad_exomes_enabled": False,
    #         "gnomad_exomes_frequency": None,
    #         "gnomad_genomes_enabled": False,
    #         "gnomad_genomes_frequency": None,
    #         "exac_enabled": False,
    #         "exac_frequency": None,
    #         "thousand_genomes_enabled": True,
    #         "thousand_genomes_frequency": 0.01,
    #     })
    #     _results = SmallVariant.objects.raw(*qb.build_top_level_query(base, [condition]))
    #     results = [model_to_dict(_result, exclude=["id"]) for _result in _results]
    #     results_sorted = sorted(results, key=lambda key: key["position"])
    #     expected = [smallvariant_case1_entry5, smallvariant_case1_entry6]
    #     self.assertEquals(results_sorted, expected)

    # def test_max_frequency_001(self):
    #     qb = QueryBuilder()
    #     frequency_condition = qb.build_frequency_term({"max_frequency": 0.01})
    #     term, args = qb.build_top_level_query([frequency_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_remove_homozygous(self):
    #     qb = QueryBuilder()
    #     homozygous_condition = qb.build_homozygous_term(
    #         {"remove_homozygous": True}
    #     )
    #     term, args = qb.build_top_level_query([homozygous_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_effects_missense_variant(self):
    #     qb = QueryBuilder()
    #     effect_condition = qb.build_effects_term(
    #         {"effects": ["missense_variant"]}
    #     )
    #     term, args = qb.build_top_level_query([effect_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_case_A(self):
    #     qb = QueryBuilder()
    #     case_condition = qb.build_case_term({"case_name": "A"})
    #     term, args = qb.build_top_level_query([case_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_gt_ref_A(self):
    #     qb = QueryBuilder()
    #     gt_condition = qb.build_genotype_gt_term({"member": "A", "gt": ["0/0"]})
    #     term, args = qb.build_top_level_query([gt_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1]
    #     self.assertEquals(results, expected)
    #
    # def test_gt_None_ref_A(self):
    #     qb = QueryBuilder()
    #     gt_condition = qb.build_genotype_gt_term({"member": "A", "gt": None})
    #     term, args = qb.build_top_level_query([gt_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_gt_variant_ref_A(self):
    #     qb = QueryBuilder()
    #     gt_condition = qb.build_genotype_gt_term(
    #         {"member": "A", "gt": ["0/0", "0/1"]}
    #     )
    #     term, args = qb.build_top_level_query([gt_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_gq_40_A(self):
    #     qb = QueryBuilder()
    #     gq_condition = qb.build_genotype_gq_term({"member": "A", "gq": 40})
    #     term, args = qb.build_top_level_query([gq_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_dp_20_A(self):
    #     qb = QueryBuilder()
    #     dp_condition = qb.build_genotype_dp_term({"member": "A", "dp": 20})
    #     term, args = qb.build_top_level_query([dp_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_ad_10_A(self):
    #     qb = QueryBuilder()
    #     ad_condition = qb.build_genotype_ad_term({"member": "A", "ad": 10})
    #     term, args = qb.build_top_level_query([ad_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_ab_02_A(self):
    #     qb = QueryBuilder()
    #     ab_condition = qb.build_genotype_ab_term({"member": "A", "ab": 0.2})
    #     term, args = qb.build_top_level_query([ab_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry2, smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_quality_complete_condition(self):
    #     qb = QueryBuilder()
    #     genotype_condition = qb.build_genotype_quality_term(
    #         {"member": "A", "dp": 20, "ad": 10, "ab": 0.2, "gq": 40}
    #     )
    #     term, args = qb.build_top_level_query([genotype_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_genotype_and_quality_drop(self):
    #     qb = QueryBuilder()
    #     genotype_condition = qb.build_genotype_term(
    #         {
    #             "member": "A",
    #             "dp": 20,
    #             "ad": 10,
    #             "ab": 0.2,
    #             "gq": 40,
    #             "gt": ["0/1"],
    #             "fail": "drop-variant",
    #         }
    #     )
    #     term, args = qb.build_top_level_query([genotype_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry3]
    #     self.assertEquals(results, expected)
    #
    # def test_genotype_and_quality_nocall(self):
    #     qb = QueryBuilder()
    #     genotype_condition = qb.build_genotype_term(
    #         {
    #             "member": "A",
    #             "dp": 20,
    #             "ad": 10,
    #             "ab": 0.2,
    #             "gq": 40,
    #             "gt": ["0/0"],
    #             "fail": "no-call",
    #         }
    #     )
    #     term, args = qb.build_top_level_query([genotype_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1, smallvariant_entry2]
    #     self.assertEquals(results, expected)
    #
    # def test_genotype_quality_drop_and_nocall(self):
    #     qb = QueryBuilder()
    #     genotype_condition = qb.build_genotype_term_list(
    #         {
    #             "genotype": [
    #                 {
    #                     "member": "A",
    #                     "dp": 20,
    #                     "ad": 10,
    #                     "ab": 0.2,
    #                     "gq": 40,
    #                     "gt": ["0/0"],
    #                     "fail": "no-call",
    #                 },
    #                 {
    #                     "member": "C",
    #                     "dp": 20,
    #                     "ad": 10,
    #                     "ab": 0.2,
    #                     "gq": 40,
    #                     "gt": ["0/1"],
    #                     "fail": "drop-variant",
    #                 },
    #             ]
    #         }
    #     )
    #     term, args = qb.build_top_level_query([genotype_condition])
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1]
    #     self.assertEquals(results, expected)
    #
    # def test_complete_query(self):
    #     qb = QueryBuilder()
    #     kwargs = {
    #         "max_frequency": 0.01,
    #         "remove_homozygous": False,
    #         "effects": ["missense_variant"],
    #         "case_name": "A",
    #         "genotype": [
    #             {
    #                 "member": "A",
    #                 "dp": 20,
    #                 "ad": 10,
    #                 "ab": 0.2,
    #                 "gq": 20,
    #                 "gt": ["0/0"],
    #                 "fail": "no-call",
    #             },
    #             {
    #                 "member": "C",
    #                 "dp": 20,
    #                 "ad": 10,
    #                 "ab": 0.2,
    #                 "gq": 40,
    #                 "gt": ["0/1"],
    #                 "fail": "drop-variant",
    #             },
    #         ],
    #     }
    #
    #     conditions = [
    #         qb.build_frequency_term(kwargs),
    #         qb.build_homozygous_term(kwargs),
    #         qb.build_case_term(kwargs),
    #         qb.build_effects_term(kwargs),
    #         qb.build_genotype_term_list(kwargs),
    #     ]
    #
    #     term, args = qb.build_top_level_query(conditions)
    #     _results = SmallVariant.objects.raw(term, args)
    #     results = [
    #         model_to_dict(_result, exclude=["id"]) for _result in _results
    #     ]
    #     expected = [smallvariant_entry1]
    #     self.assertEquals(results, expected)
    #
    # def test_gnomadgenomes_query(self):
    #     qb = QueryBuilder()
    #     kwargs = {
    #         "release": "GRCh37",
    #         "chromosome": "1",
    #         "position": 100,
    #         "reference": "A",
    #         "alternative": "G",
    #     }
    #     _results = list(GnomadGenomes.objects.raw(*qb.build_gnomadgenomes_query(kwargs)))[0]
    #     results = {
    #         "release": _results.release,
    #         "chromosome": _results.chromosome,
    #         "position": _results.position,
    #         "reference": _results.reference,
    #         "alternative": _results.alternative,
    #         "ac": _results.ac,
    #         "ac_afr": _results.ac_afr,
    #         "ac_amr": _results.ac_amr,
    #         "ac_asj": _results.ac_asj,
    #         "ac_eas": _results.ac_eas,
    #         "ac_fin": _results.ac_fin,
    #         "ac_nfe": _results.ac_nfe,
    #         "ac_oth": _results.ac_oth,
    #         "an": _results.an,
    #         "an_afr": _results.an_afr,
    #         "an_amr": _results.an_amr,
    #         "an_asj": _results.an_asj,
    #         "an_eas": _results.an_eas,
    #         "an_fin": _results.an_fin,
    #         "an_nfe": _results.an_nfe,
    #         "an_oth": _results.an_oth,
    #         "hemi": _results.hemi,
    #         "hemi_afr": _results.hemi_afr,
    #         "hemi_amr": _results.hemi_amr,
    #         "hemi_asj": _results.hemi_asj,
    #         "hemi_eas": _results.hemi_eas,
    #         "hemi_fin": _results.hemi_fin,
    #         "hemi_nfe": _results.hemi_nfe,
    #         "hemi_oth": _results.hemi_oth,
    #         "hom": _results.hom,
    #         "hom_afr": _results.hom_afr,
    #         "hom_amr": _results.hom_amr,
    #         "hom_asj": _results.hom_asj,
    #         "hom_eas": _results.hom_eas,
    #         "hom_fin": _results.hom_fin,
    #         "hom_nfe": _results.hom_nfe,
    #         "hom_oth": _results.hom_oth,
    #         "popmax": _results.popmax,
    #         "ac_popmax": _results.ac_popmax,
    #         "an_popmax": _results.an_popmax,
    #         "af_popmax": _results.af_popmax,
    #         "hemi_popmax": _results.hemi_popmax,
    #         "hom_popmax": _results.hom_popmax,
    #         "af": _results.af,
    #         "af_afr": _results.af_afr,
    #         "af_amr": _results.af_amr,
    #         "af_asj": _results.af_asj,
    #         "af_eas": _results.af_eas,
    #         "af_fin": _results.af_fin,
    #         "af_nfe": _results.af_nfe,
    #         "af_oth": _results.af_oth,
    #         "het": _results.het,
    #         'het_afr': _results.het_afr,
    #         'het_amr': _results.het_amr,
    #         'het_asj': _results.het_asj,
    #         'het_eas': _results.het_eas,
    #         'het_fin': _results.het_fin,
    #         'het_nfe': _results.het_nfe,
    #         'het_oth': _results.het_oth,
    #     }
    #     expected = {
    #         **gnomadgenomes_entry1._asdict(),
    #         "het": None,
    #         'het_afr': 1,
    #         'het_amr': 0,
    #         'het_asj': 0,
    #         'het_eas': 0,
    #         'het_fin': 0,
    #         'het_nfe': 0,
    #         'het_oth': 0,
    #     }
    #
    #     self.assertDictEqual(results, expected)
    #
    # def test_gnomadexomes_query(self):
    #     qb = QueryBuilder()
    #     kwargs = {
    #         "release": "GRCh37",
    #         "chromosome": "1",
    #         "position": 100,
    #         "reference": "A",
    #         "alternative": "G",
    #     }
    #     _results = list(GnomadExomes.objects.raw(*qb.build_gnomadexomes_query(kwargs)))[0]
    #     results = {
    #         "release": _results.release,
    #         "chromosome": _results.chromosome,
    #         "position": _results.position,
    #         "reference": _results.reference,
    #         "alternative": _results.alternative,
    #         "ac": _results.ac,
    #         "ac_afr": _results.ac_afr,
    #         "ac_amr": _results.ac_amr,
    #         "ac_asj": _results.ac_asj,
    #         "ac_eas": _results.ac_eas,
    #         "ac_fin": _results.ac_fin,
    #         "ac_nfe": _results.ac_nfe,
    #         "ac_oth": _results.ac_oth,
    #         "ac_sas": _results.ac_sas,
    #         "an": _results.an,
    #         "an_afr": _results.an_afr,
    #         "an_amr": _results.an_amr,
    #         "an_asj": _results.an_asj,
    #         "an_eas": _results.an_eas,
    #         "an_fin": _results.an_fin,
    #         "an_nfe": _results.an_nfe,
    #         "an_oth": _results.an_oth,
    #         "an_sas": _results.an_sas,
    #         "hemi": _results.hemi,
    #         "hemi_afr": _results.hemi_afr,
    #         "hemi_amr": _results.hemi_amr,
    #         "hemi_asj": _results.hemi_asj,
    #         "hemi_eas": _results.hemi_eas,
    #         "hemi_fin": _results.hemi_fin,
    #         "hemi_nfe": _results.hemi_nfe,
    #         "hemi_oth": _results.hemi_oth,
    #         "hemi_sas": _results.hemi_sas,
    #         "hom": _results.hom,
    #         "hom_afr": _results.hom_afr,
    #         "hom_amr": _results.hom_amr,
    #         "hom_asj": _results.hom_asj,
    #         "hom_eas": _results.hom_eas,
    #         "hom_fin": _results.hom_fin,
    #         "hom_nfe": _results.hom_nfe,
    #         "hom_oth": _results.hom_oth,
    #         "hom_sas": _results.hom_sas,
    #         "popmax": _results.popmax,
    #         "ac_popmax": _results.ac_popmax,
    #         "an_popmax": _results.an_popmax,
    #         "af_popmax": _results.af_popmax,
    #         "hemi_popmax": _results.hemi_popmax,
    #         "hom_popmax": _results.hom_popmax,
    #         "af": _results.af,
    #         "af_afr": _results.af_afr,
    #         "af_amr": _results.af_amr,
    #         "af_asj": _results.af_asj,
    #         "af_eas": _results.af_eas,
    #         "af_fin": _results.af_fin,
    #         "af_nfe": _results.af_nfe,
    #         "af_oth": _results.af_oth,
    #         "af_sas": _results.af_sas,
    #         "het": _results.het,
    #         'het_afr': _results.het_afr,
    #         'het_amr': _results.het_amr,
    #         'het_asj': _results.het_asj,
    #         'het_eas': _results.het_eas,
    #         'het_fin': _results.het_fin,
    #         'het_nfe': _results.het_nfe,
    #         'het_oth': _results.het_oth,
    #         "het_sas": _results.het_sas,
    #     }
    #     expected = {
    #         **gnomadexomes_entry1._asdict(),
    #         "het": None,
    #         'het_afr': 1,
    #         'het_amr': 0,
    #         'het_asj': 0,
    #         'het_eas': 0,
    #         'het_fin': 0,
    #         'het_nfe': 0,
    #         'het_oth': 0,
    #         "het_sas": 0,
    #     }
    #
    #     self.assertDictEqual(results, expected)
    #
    # def test_exac_query(self):
    #     qb = QueryBuilder()
    #     kwargs = {
    #         "release": "GRCh37",
    #         "chromosome": "1",
    #         "position": 100,
    #         "reference": "A",
    #         "alternative": "G",
    #     }
    #     _results = list(Exac.objects.raw(*qb.build_exac_query(kwargs)))[0]
    #     results = {
    #         "release": _results.release,
    #         "chromosome": _results.chromosome,
    #         "position": _results.position,
    #         "reference": _results.reference,
    #         "alternative": _results.alternative,
    #         "ac": _results.ac,
    #         "ac_afr": _results.ac_afr,
    #         "ac_amr": _results.ac_amr,
    #         "ac_eas": _results.ac_eas,
    #         "ac_fin": _results.ac_fin,
    #         "ac_nfe": _results.ac_nfe,
    #         "ac_oth": _results.ac_oth,
    #         "ac_sas": _results.ac_sas,
    #         "an": _results.an,
    #         "an_afr": _results.an_afr,
    #         "an_amr": _results.an_amr,
    #         "an_eas": _results.an_eas,
    #         "an_fin": _results.an_fin,
    #         "an_nfe": _results.an_nfe,
    #         "an_oth": _results.an_oth,
    #         "an_sas": _results.an_sas,
    #         "hemi": _results.hemi,
    #         "hemi_afr": _results.hemi_afr,
    #         "hemi_amr": _results.hemi_amr,
    #         "hemi_eas": _results.hemi_eas,
    #         "hemi_fin": _results.hemi_fin,
    #         "hemi_nfe": _results.hemi_nfe,
    #         "hemi_oth": _results.hemi_oth,
    #         "hemi_sas": _results.hemi_sas,
    #         "hom": _results.hom,
    #         "hom_afr": _results.hom_afr,
    #         "hom_amr": _results.hom_amr,
    #         "hom_eas": _results.hom_eas,
    #         "hom_fin": _results.hom_fin,
    #         "hom_nfe": _results.hom_nfe,
    #         "hom_oth": _results.hom_oth,
    #         "hom_sas": _results.hom_sas,
    #         "popmax": _results.popmax,
    #         "ac_popmax": _results.ac_popmax,
    #         "an_popmax": _results.an_popmax,
    #         "af_popmax": _results.af_popmax,
    #         "hemi_popmax": _results.hemi_popmax,
    #         "hom_popmax": _results.hom_popmax,
    #         "af": _results.af,
    #         "af_afr": _results.af_afr,
    #         "af_amr": _results.af_amr,
    #         "af_eas": _results.af_eas,
    #         "af_fin": _results.af_fin,
    #         "af_nfe": _results.af_nfe,
    #         "af_oth": _results.af_oth,
    #         "af_sas": _results.af_sas,
    #         "het": _results.het,
    #         'het_afr': _results.het_afr,
    #         'het_amr': _results.het_amr,
    #         'het_eas': _results.het_eas,
    #         'het_fin': _results.het_fin,
    #         'het_nfe': _results.het_nfe,
    #         'het_oth': _results.het_oth,
    #         "het_sas": _results.het_sas,
    #     }
    #     expected = {
    #         **exac_entry1._asdict(),
    #         "het": None,
    #         'het_afr': 1,
    #         'het_amr': 0,
    #         'het_eas': 0,
    #         'het_fin': 0,
    #         'het_nfe': 0,
    #         'het_oth': 0,
    #         'het_sas': 0,
    #     }
    #
    #     self.assertDictEqual(results, expected)
    #
    # def test_thousandgenomes_query(self):
    #     qb = QueryBuilder()
    #     kwargs = {
    #         "release": "GRCh37",
    #         "chromosome": "1",
    #         "position": 100,
    #         "reference": "A",
    #         "alternative": "G",
    #     }
    #     _results = list(ThousandGenomes.objects.raw(*qb.build_thousandgenomes_query(kwargs)))[0]
    #     results = {
    #         "release": _results.release,
    #         "chromosome": _results.chromosome,
    #         "position": _results.position,
    #         "reference": _results.reference,
    #         "alternative": _results.alternative,
    #         "ac": _results.ac,
    #         "an": _results.an,
    #         "het": _results.het,
    #         "hom": _results.hom,
    #         "af": _results.af,
    #         "af_afr": _results.af_afr,
    #         "af_amr": _results.af_amr,
    #         "af_eas": _results.af_eas,
    #         "af_eur": _results.af_eur,
    #         "af_sas": _results.af_sas,
    #     }
    #     expected = {
    #         **thousandgenomes_entry1._asdict(),
    #     }
    #
    #     self.assertDictEqual(results, expected)

    # def test_knowngeneaa_query(self):
    #     self.assertEquals(results, expected)
    #
    # def test_base_query(self):
    #     self.assertEquals(results, expected)
