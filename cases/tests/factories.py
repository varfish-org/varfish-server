import datetime

import factory

from cases.models import Individual, Pedigree
from seqmeta.tests.factories import EnrichmentKitFactory
from variants.models import CaseAlignmentStats, PedigreeRelatedness
from variants.tests.factories import CaseFactory, CaseVariantStatsFactory, SmallVariantSetFactory

BAM_STATS_SAMPLE = {
    "bamstats": {
        "is sorted": 1,
        "reads MQ0": 2614891,
        "sequences": 45348682,
        "error rate": 0.003512454,
        "mismatches": 15819585,
        "bases mapped": 4522209600,
        "reads mapped": 45222096,
        "reads paired": 45348682,
        "total length": 4534868200,
        "1st fragments": 22674341,
        "bases trimmed": 0,
        "average length": 100,
        "last fragments": 22674341,
        "maximum length": 100,
        "reads unmapped": 126586,
        "average quality": 37.6,
        "reads QC failed": 0,
        "bases duplicated": 290597000,
        "reads duplicated": 2905970,
        "filtered sequences": 0,
        "insert size average": 318.2,
        "raw total sequences": 45348682,
        "bases mapped (cigar)": 4503855383,
        "inward oriented pairs": 22381314,
        "reads properly paired": 44699564,
        "non-primary alignments": 25448,
        "outward oriented pairs": 15648,
        "reads mapped and paired": 45130240,
        "total last fragment length": 2267434100,
        "total first fragment length": 2267434100,
        "average last fragment length": 100,
        "maximum last fragment length": 100,
        "pairs with other orientation": 16092,
        "average first fragment length": 100,
        "maximum first fragment length": 100,
        "insert size standard deviation": 106.3,
        "pairs on different chromosomes": 152066,
        "percentage of properly paired reads (%)": 98.6,
    },
    "idxstats": {
        "*": {"mapped": 0, "unmapped": 34730},
        "1": {"mapped": 5027864, "unmapped": 10074},
        "2": {"mapped": 3521340, "unmapped": 7478},
        "3": {"mapped": 2568394, "unmapped": 5003},
        "4": {"mapped": 2006423, "unmapped": 3961},
        "5": {"mapped": 2163724, "unmapped": 4100},
        "6": {"mapped": 2406382, "unmapped": 4653},
        "7": {"mapped": 2158425, "unmapped": 4320},
        "8": {"mapped": 1544814, "unmapped": 3095},
        "9": {"mapped": 1842284, "unmapped": 3614},
        "X": {"mapped": 2216138, "unmapped": 4394},
        "Y": {"mapped": 3474, "unmapped": 35},
        "10": {"mapped": 1943543, "unmapped": 3833},
        "11": {"mapped": 2283314, "unmapped": 4736},
        "12": {"mapped": 2290240, "unmapped": 4455},
        "13": {"mapped": 914975, "unmapped": 1728},
        "14": {"mapped": 1447964, "unmapped": 2879},
        "15": {"mapped": 1675941, "unmapped": 3424},
        "16": {"mapped": 1611981, "unmapped": 3489},
        "17": {"mapped": 2230669, "unmapped": 4822},
        "18": {"mapped": 747245, "unmapped": 1388},
        "19": {"mapped": 1978025, "unmapped": 4410},
        "20": {"mapped": 896705, "unmapped": 1855},
        "21": {"mapped": 452682, "unmapped": 967},
        "22": {"mapped": 711651, "unmapped": 1697},
        "MT": {"mapped": 19542, "unmapped": 42},
    },
}


class CaseAlignmentStatsFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Case`` objects."""

    case = factory.SubFactory(CaseFactory)
    variant_set = factory.SubFactory(SmallVariantSetFactory, case=factory.SelfAttribute("..case"))

    @factory.lazy_attribute
    def bam_stats(self):
        return {line["patient"]: BAM_STATS_SAMPLE for line in self.case.pedigree}

    class Meta:
        model = CaseAlignmentStats


class PedigreeRelatednessFactory(factory.django.DjangoModelFactory):

    het_1_2 = 1
    het_1 = 1
    het_2 = 1
    n_ibs0 = 1
    n_ibs1 = 1
    n_ibs2 = 1

    stats = factory.SubFactory(CaseVariantStatsFactory)

    @factory.lazy_attribute
    def sample1(self):
        return self.stats.variant_set.case.pedigree[0]["patient"]

    @factory.lazy_attribute
    def sample2(self):
        if len(self.stats.variant_set.case.pedigree) > 1:
            return self.stats.variant_set.case.pedigree[1]["patient"]
        else:
            return self.stats.variant_set.case.pedigree[0]["patient"]

    class Meta:
        model = PedigreeRelatedness


class PedigreeFactory(factory.django.DjangoModelFactory):
    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    case = factory.SubFactory(CaseFactory)

    class Meta:
        model = Pedigree


class IndividualFactory(factory.django.DjangoModelFactory):
    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    pedigree = factory.SubFactory(PedigreeFactory)
    name = factory.Sequence(lambda n: f"individual-{n}")
    sex = Individual.SEX_MALE
    karyotypic_sex = Individual.KARYOTYPE_XY
    assay = Individual.ASSAY_WES
    enrichmentkit = factory.SubFactory(EnrichmentKitFactory)

    class Meta:
        model = Individual
