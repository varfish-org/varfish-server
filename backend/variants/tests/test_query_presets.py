"""Tests for the ``variants.query_presets`` module."""

from test_plus.test import TestCase

from variants import query_presets


class TestEnumSex(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Sex.UNKNOWN.value, 0)
        self.assertEqual(query_presets.Sex.MALE.value, 1)
        self.assertEqual(query_presets.Sex.FEMALE.value, 2)


class TestEnumDiseaseState(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.DiseaseState.UNKNOWN.value, 0)
        self.assertEqual(query_presets.DiseaseState.UNAFFECTED.value, 1)
        self.assertEqual(query_presets.DiseaseState.AFFECTED.value, 2)


class TestConstantNobody(TestCase):
    def testValue(self):
        self.assertEqual(query_presets.NOBODY, "0")


class TestPedigreeMember(TestCase):
    def testConstructor(self):
        member = query_presets.PedigreeMember(
            family="FAM",
            name="index",
            father="father",
            mother="mother",
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        self.assertEqual(
            str(member),
            "PedigreeMember(family='FAM', name='index', father='father', mother='mother', "
            "sex=<Sex.MALE: 1>, disease_state=<DiseaseState.AFFECTED: 2>)",
        )

    def testFunctionsSingleton(self):
        member = query_presets.PedigreeMember(
            family="FAM",
            name="index",
            father="father",
            mother="mother",
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        self.assertTrue(member.has_both_parents())
        self.assertFalse(member.is_singleton())
        self.assertFalse(member.has_single_parent())

    def testFunctionsChildFather(self):
        child = query_presets.PedigreeMember(
            family="FAM",
            name="index",
            father="father",
            mother=query_presets.NOBODY,
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        self.assertFalse(child.has_both_parents())
        self.assertFalse(child.is_singleton())
        self.assertTrue(child.has_single_parent())

    def testFunctionsChildMother(self):
        child = query_presets.PedigreeMember(
            family="FAM",
            name="index",
            father=query_presets.NOBODY,
            mother="mother",
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        self.assertFalse(child.has_both_parents())
        self.assertFalse(child.is_singleton())
        self.assertTrue(child.has_single_parent())

    def testFunctionsTrio(self):
        child = query_presets.PedigreeMember(
            family="FAM",
            name="index",
            father="father",
            mother="mother",
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        _father = query_presets.PedigreeMember(  # noqa: F841
            family="FAM",
            name="index",
            father="father",
            mother="mother",
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        _mother = query_presets.PedigreeMember(  # noqa: F841
            family="FAM",
            name="index",
            father="father",
            mother="mother",
            sex=query_presets.Sex.MALE,
            disease_state=query_presets.DiseaseState.AFFECTED,
        )
        self.assertTrue(child.has_both_parents())
        self.assertFalse(child.is_singleton())
        self.assertFalse(child.has_single_parent())


class TestEnumGenotypeChoice(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.GenotypeChoice.ANY.value, "any")
        self.assertEqual(query_presets.GenotypeChoice.REF.value, "ref")
        self.assertEqual(query_presets.GenotypeChoice.HET.value, "het")
        self.assertEqual(query_presets.GenotypeChoice.HOM.value, "hom")
        self.assertEqual(query_presets.GenotypeChoice.NON_HOM.value, "non-hom")
        self.assertEqual(query_presets.GenotypeChoice.VARIANT.value, "variant")
        self.assertEqual(query_presets.GenotypeChoice.NON_VARIANT.value, "non-variant")
        self.assertEqual(query_presets.GenotypeChoice.NON_REFERENCE.value, "non-reference")


class PedigreesMixin:
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        # Setup some pedigrees for testing
        self.singleton = (
            query_presets.PedigreeMember(
                family="FAM",
                name="index",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.MALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
        )
        self.child_father = (
            query_presets.PedigreeMember(
                family="FAM",
                name="index",
                father="father",
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.MALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
            query_presets.PedigreeMember(
                family="FAM",
                name="father",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.MALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
        )
        self.child_mother = (
            query_presets.PedigreeMember(
                family="FAM",
                name="index",
                father=query_presets.NOBODY,
                mother="mother",
                sex=query_presets.Sex.MALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
            query_presets.PedigreeMember(
                family="FAM",
                name="mother",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.FEMALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
        )
        # Trio compatible with denovo mode of inheritance (also compatible with recessive)
        self.trio_denovo = (
            query_presets.PedigreeMember(
                family="FAM",
                name="index",
                father="father",
                mother="mother",
                sex=query_presets.Sex.MALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
            query_presets.PedigreeMember(
                family="FAM",
                name="father",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.FEMALE,
                disease_state=query_presets.DiseaseState.UNAFFECTED,
            ),
            query_presets.PedigreeMember(
                family="FAM",
                name="mother",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.FEMALE,
                disease_state=query_presets.DiseaseState.UNAFFECTED,
            ),
        )
        # Trio compatible with dominant mode of inheritance where father is also affected
        self.trio_dominant = (
            query_presets.PedigreeMember(
                family="FAM",
                name="index",
                father="father",
                mother="mother",
                sex=query_presets.Sex.MALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
            query_presets.PedigreeMember(
                family="FAM",
                name="father",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.FEMALE,
                disease_state=query_presets.DiseaseState.AFFECTED,
            ),
            query_presets.PedigreeMember(
                family="FAM",
                name="mother",
                father=query_presets.NOBODY,
                mother=query_presets.NOBODY,
                sex=query_presets.Sex.FEMALE,
                disease_state=query_presets.DiseaseState.UNAFFECTED,
            ),
        )


class TestEnumInheritance(PedigreesMixin, TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Inheritance.DE_NOVO.value, "de_novo")
        self.assertEqual(query_presets.Inheritance.DOMINANT.value, "dominant")
        self.assertEqual(
            query_presets.Inheritance.HOMOZYGOUS_RECESSIVE.value, "homozygous_recessive"
        )
        self.assertEqual(
            query_presets.Inheritance.COMPOUND_HETEROZYGOUS.value, "compound_heterozygous"
        )
        self.assertEqual(query_presets.Inheritance.RECESSIVE.value, "recessive")
        self.assertEqual(query_presets.Inheritance.X_RECESSIVE.value, "x_recessive")
        self.assertEqual(query_presets.Inheritance.AFFECTED_CARRIERS.value, "affected_carriers")
        self.assertEqual(query_presets.Inheritance.CUSTOM.value, "custom")
        self.assertEqual(query_presets.Inheritance.ANY.value, "any")

    def testToSettingsDeNovo(self):
        # singleton
        actual = query_presets.Inheritance.DE_NOVO.to_settings(self.singleton, self.singleton[0])
        self.assertEqual(
            actual,
            {
                "genotype": {"index": query_presets.GenotypeChoice.VARIANT.value},
                "recessive_index": None,
                "recessive_mode": None,
            },
        )
        # child with father
        actual = query_presets.Inheritance.DE_NOVO.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "father": query_presets.GenotypeChoice.REF.value,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.DE_NOVO.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.DE_NOVO.to_settings(self.trio_denovo, self.singleton[0])
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "father": query_presets.GenotypeChoice.REF.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.DE_NOVO.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "father": query_presets.GenotypeChoice.REF.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )

    def testToSettingsDominant(self):
        # singleton
        actual = query_presets.Inheritance.DOMINANT.to_settings(self.singleton, self.singleton[0])
        self.assertEqual(
            actual,
            {
                "genotype": {"index": query_presets.GenotypeChoice.HET.value},
                "recessive_index": None,
                "recessive_mode": None,
            },
        )
        # child with father
        actual = query_presets.Inheritance.DOMINANT.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HET.value,
                    "father": query_presets.GenotypeChoice.HET.value,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.DOMINANT.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HET.value,
                    "mother": query_presets.GenotypeChoice.HET.value,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.DOMINANT.to_settings(self.trio_denovo, self.singleton[0])
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HET.value,
                    "father": query_presets.GenotypeChoice.REF.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.DOMINANT.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HET.value,
                    "father": query_presets.GenotypeChoice.HET.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )

    def testToSettingsHomozygousRecessive(self):
        # singleton
        actual = query_presets.Inheritance.HOMOZYGOUS_RECESSIVE.to_settings(
            self.singleton, self.singleton[0].name
        )
        self.assertEqual(
            actual,
            {
                "genotype": {"index": query_presets.GenotypeChoice.HOM.value},
                "recessive_index": "index",
                "recessive_mode": None,
            },
        )
        # child with father
        actual = query_presets.Inheritance.HOMOZYGOUS_RECESSIVE.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "father": query_presets.GenotypeChoice.HOM.value,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.HOMOZYGOUS_RECESSIVE.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "mother": query_presets.GenotypeChoice.HOM.value,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.HOMOZYGOUS_RECESSIVE.to_settings(
            self.trio_denovo, self.trio_denovo[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "father": query_presets.GenotypeChoice.HET.value,
                    "mother": query_presets.GenotypeChoice.HET.value,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.HOMOZYGOUS_RECESSIVE.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "father": query_presets.GenotypeChoice.HOM.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )

    def testToSettingsCompoundHeterozygous(self):
        # singleton
        actual = query_presets.Inheritance.COMPOUND_HETEROZYGOUS.to_settings(
            self.singleton, self.singleton[0].name
        )
        self.assertEqual(
            actual,
            {
                "genotype": {"index": None},
                "recessive_index": "index",
                "recessive_mode": "compound-recessive",
            },
        )
        # child with father
        actual = query_presets.Inheritance.COMPOUND_HETEROZYGOUS.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "compound-recessive",
                "genotype": {
                    "index": None,
                    "father": None,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.COMPOUND_HETEROZYGOUS.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "compound-recessive",
                "genotype": {
                    "index": None,
                    "mother": None,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.COMPOUND_HETEROZYGOUS.to_settings(
            self.trio_denovo, self.trio_denovo[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "compound-recessive",
                "genotype": {
                    "index": None,
                    "father": None,
                    "mother": None,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.COMPOUND_HETEROZYGOUS.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "compound-recessive",
                "genotype": {
                    "index": None,
                    "father": None,
                    "mother": None,
                },
            },
        )

    def testToSettingsRecessive(self):
        # singleton
        actual = query_presets.Inheritance.RECESSIVE.to_settings(
            self.singleton, self.singleton[0].name
        )
        self.assertEqual(
            actual,
            {
                "genotype": {"index": None},
                "recessive_index": "index",
                "recessive_mode": "recessive",
            },
        )
        # child with father
        actual = query_presets.Inheritance.RECESSIVE.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "recessive",
                "genotype": {
                    "index": None,
                    "father": None,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.RECESSIVE.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "recessive",
                "genotype": {
                    "index": None,
                    "mother": None,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.RECESSIVE.to_settings(
            self.trio_denovo, self.trio_denovo[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "recessive",
                "genotype": {
                    "index": None,
                    "father": None,
                    "mother": None,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.RECESSIVE.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": "index",
                "recessive_mode": "recessive",
                "genotype": {
                    "index": None,
                    "father": None,
                    "mother": None,
                },
            },
        )

    def testToSettingsXRecessive(self):
        # singleton
        actual = query_presets.Inheritance.X_RECESSIVE.to_settings(
            self.singleton, self.singleton[0].name
        )
        self.assertEqual(
            actual,
            {
                "genotype": {"index": query_presets.GenotypeChoice.HOM.value},
                "recessive_index": self.singleton[0].name,
                "recessive_mode": None,
            },
        )
        # child with father
        actual = query_presets.Inheritance.X_RECESSIVE.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": self.child_father[0].name,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "father": query_presets.GenotypeChoice.HOM.value,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.X_RECESSIVE.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": self.child_father[0].name,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "mother": query_presets.GenotypeChoice.ANY.value,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.X_RECESSIVE.to_settings(
            self.trio_denovo, self.trio_denovo[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": self.trio_denovo[0].name,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "father": query_presets.GenotypeChoice.REF.value,
                    "mother": query_presets.GenotypeChoice.HET.value,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.X_RECESSIVE.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": self.trio_dominant[0].name,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.HOM.value,
                    "father": query_presets.GenotypeChoice.HOM.value,
                    "mother": query_presets.GenotypeChoice.REF.value,
                },
            },
        )

    def testToSettingsAffectedCarriers(self):
        # singleton
        actual = query_presets.Inheritance.AFFECTED_CARRIERS.to_settings(
            self.singleton, self.singleton[0].name
        )
        self.assertEqual(
            actual,
            {
                "genotype": {"index": query_presets.GenotypeChoice.VARIANT.value},
                "recessive_index": None,
                "recessive_mode": None,
            },
        )
        # child with father
        actual = query_presets.Inheritance.AFFECTED_CARRIERS.to_settings(
            self.child_father, self.child_father[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "father": query_presets.GenotypeChoice.VARIANT.value,
                },
            },
        )
        # child with mother
        actual = query_presets.Inheritance.AFFECTED_CARRIERS.to_settings(
            self.child_mother, self.child_mother[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "mother": query_presets.GenotypeChoice.VARIANT.value,
                },
            },
        )
        # trio denovo
        actual = query_presets.Inheritance.AFFECTED_CARRIERS.to_settings(
            self.trio_denovo, self.trio_denovo[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "father": query_presets.GenotypeChoice.ANY.value,
                    "mother": query_presets.GenotypeChoice.ANY.value,
                },
            },
        )
        # trio dominant inherited
        actual = query_presets.Inheritance.AFFECTED_CARRIERS.to_settings(
            self.trio_dominant, self.trio_dominant[0].name
        )
        self.assertEqual(
            actual,
            {
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {
                    "index": query_presets.GenotypeChoice.VARIANT.value,
                    "father": query_presets.GenotypeChoice.VARIANT.value,
                    "mother": query_presets.GenotypeChoice.ANY.value,
                },
            },
        )


class TestEnumFrequency(TestCase):
    def testValues(self):
        self.assertEqual(
            query_presets.Frequency.DOMINANT_SUPER_STRICT.value, "dominant_super_strict"
        )
        self.assertEqual(query_presets.Frequency.DOMINANT_STRICT.value, "dominant_strict")
        self.assertEqual(query_presets.Frequency.DOMINANT_RELAXED.value, "dominant_relaxed")
        self.assertEqual(query_presets.Frequency.RECESSIVE_STRICT.value, "recessive_strict")
        self.assertEqual(query_presets.Frequency.RECESSIVE_RELAXED.value, "recessive_relaxed")
        self.assertEqual(query_presets.Frequency.ANY.value, "any")

    def testToSettingsDominantSuperStrict(self):
        self.assertEqual(
            query_presets.Frequency.DOMINANT_SUPER_STRICT.to_settings(),
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_homozygous": 0,
                "thousand_genomes_heterozygous": 1,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": 0.002,
                "exac_enabled": True,
                "exac_homozygous": 0,
                "exac_heterozygous": 1,
                "exac_hemizygous": None,
                "exac_frequency": 0.002,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_homozygous": 0,
                "gnomad_exomes_heterozygous": 1,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": 0.002,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_homozygous": 0,
                "gnomad_genomes_heterozygous": 1,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": 0.002,
                "inhouse_enabled": True,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_hemizygous": None,
                "inhouse_carriers": 20,
                "mtdb_enabled": False,
                "mtdb_count": None,
                "mtdb_frequency": None,
                "helixmtdb_enabled": False,
                "helixmtdb_het_count": None,
                "helixmtdb_hom_count": None,
                "helixmtdb_frequency": None,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
            },
        )

    def testToSettingsDominantStrict(self):
        self.assertEqual(
            query_presets.Frequency.DOMINANT_STRICT.to_settings(),
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_homozygous": 0,
                "thousand_genomes_heterozygous": 4,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": 0.002,
                "exac_enabled": True,
                "exac_homozygous": 0,
                "exac_heterozygous": 10,
                "exac_hemizygous": None,
                "exac_frequency": 0.002,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_homozygous": 0,
                "gnomad_exomes_heterozygous": 20,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": 0.002,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_homozygous": 0,
                "gnomad_genomes_heterozygous": 4,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": 0.002,
                "inhouse_enabled": True,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_hemizygous": None,
                "inhouse_carriers": 20,
                "mtdb_enabled": True,
                "mtdb_count": 10,
                "mtdb_frequency": 0.01,
                "helixmtdb_enabled": True,
                "helixmtdb_hom_count": 200,
                "helixmtdb_het_count": None,
                "helixmtdb_frequency": 0.01,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
            },
        )

    def testToSettingsDominantRelaxed(self):
        self.assertEqual(
            query_presets.Frequency.DOMINANT_RELAXED.to_settings(),
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_homozygous": 0,
                "thousand_genomes_heterozygous": 10,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": 0.01,
                "exac_enabled": True,
                "exac_homozygous": 0,
                "exac_heterozygous": 25,
                "exac_hemizygous": None,
                "exac_frequency": 0.01,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_homozygous": 0,
                "gnomad_exomes_heterozygous": 50,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_homozygous": 0,
                "gnomad_genomes_heterozygous": 20,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": 0.01,
                "inhouse_enabled": True,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_hemizygous": None,
                "inhouse_carriers": 20,
                "mtdb_enabled": True,
                "mtdb_count": 50,
                "mtdb_frequency": 0.15,
                "helixmtdb_enabled": True,
                "helixmtdb_het_count": None,
                "helixmtdb_hom_count": 400,
                "helixmtdb_frequency": 0.15,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
            },
        )

    def testToSettingsRecessiveStrict(self):
        self.assertEqual(
            query_presets.Frequency.RECESSIVE_STRICT.to_settings(),
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_homozygous": 0,
                "thousand_genomes_heterozygous": 24,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": 0.001,
                "exac_enabled": True,
                "exac_homozygous": 0,
                "exac_heterozygous": 60,
                "exac_hemizygous": None,
                "exac_frequency": 0.001,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_homozygous": 0,
                "gnomad_exomes_heterozygous": 120,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": 0.001,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_homozygous": 0,
                "gnomad_genomes_heterozygous": 15,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": 0.001,
                "inhouse_enabled": True,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_hemizygous": None,
                "inhouse_carriers": 20,
                "mtdb_enabled": False,
                "mtdb_count": None,
                "mtdb_frequency": None,
                "helixmtdb_enabled": False,
                "helixmtdb_het_count": None,
                "helixmtdb_hom_count": None,
                "helixmtdb_frequency": None,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
            },
        )

    def testToSettingsRecessiveRelaxed(self):
        self.assertEqual(
            query_presets.Frequency.RECESSIVE_RELAXED.to_settings(),
            {
                "thousand_genomes_enabled": True,
                "thousand_genomes_homozygous": 4,
                "thousand_genomes_heterozygous": 240,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": 0.01,
                "exac_enabled": True,
                "exac_homozygous": 10,
                "exac_heterozygous": 600,
                "exac_hemizygous": None,
                "exac_frequency": 0.01,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_homozygous": 20,
                "gnomad_exomes_heterozygous": 1200,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": 0.01,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_homozygous": 4,
                "gnomad_genomes_heterozygous": 150,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": 0.01,
                "inhouse_enabled": True,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_hemizygous": None,
                "inhouse_carriers": 20,
                "mtdb_enabled": False,
                "mtdb_count": None,
                "mtdb_frequency": None,
                "helixmtdb_enabled": False,
                "helixmtdb_het_count": None,
                "helixmtdb_hom_count": None,
                "helixmtdb_frequency": None,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
            },
        )

    def testToSettingsAny(self):
        self.assertEqual(
            query_presets.Frequency.ANY.to_settings(),
            {
                "thousand_genomes_enabled": False,
                "thousand_genomes_homozygous": None,
                "thousand_genomes_heterozygous": None,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": None,
                "exac_enabled": False,
                "exac_homozygous": None,
                "exac_heterozygous": None,
                "exac_hemizygous": None,
                "exac_frequency": None,
                "gnomad_exomes_enabled": False,
                "gnomad_exomes_homozygous": None,
                "gnomad_exomes_heterozygous": None,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": None,
                "gnomad_genomes_enabled": False,
                "gnomad_genomes_homozygous": None,
                "gnomad_genomes_heterozygous": None,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": None,
                "inhouse_enabled": False,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_carriers": None,
                "mtdb_enabled": False,
                "mtdb_count": None,
                "mtdb_frequency": None,
                "helixmtdb_enabled": False,
                "helixmtdb_het_count": None,
                "helixmtdb_hom_count": None,
                "helixmtdb_frequency": None,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
            },
        )


class TestEnumImpact(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Impact.NULL_VARIANT.value, "null_variant")
        self.assertEqual(query_presets.Impact.AA_CHANGE_SPLICING.value, "aa_change_splicing")
        self.assertEqual(
            query_presets.Impact.ALL_CODING_DEEP_INTRONIC.value, "all_coding_deep_intronic"
        )
        self.assertEqual(query_presets.Impact.WHOLE_TRANSCRIPT.value, "whole_transcript")
        self.assertEqual(query_presets.Impact.ANY.value, "any")

    def testToSettingsNullVariant(self):
        self.assertEqual(
            query_presets.Impact.NULL_VARIANT.to_settings(),
            {
                "var_type_snv": True,
                "var_type_mnv": True,
                "var_type_indel": True,
                "transcripts_coding": True,
                "transcripts_noncoding": False,
                "max_exon_dist": None,
                "effects": [
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "internal_feature_elongation",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "structural_variant",
                    "transcript_ablation",
                ],
            },
        )

    def testToSettingsAaChangeSplicing(self):
        self.assertEqual(
            query_presets.Impact.AA_CHANGE_SPLICING.to_settings(),
            {
                "var_type_snv": True,
                "var_type_mnv": True,
                "var_type_indel": True,
                "transcripts_coding": True,
                "transcripts_noncoding": False,
                "max_exon_dist": None,
                "effects": [
                    "complex_substitution",
                    "direct_tandem_duplication",
                    "disruptive_inframe_deletion",
                    "disruptive_inframe_insertion",
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "inframe_deletion",
                    "inframe_insertion",
                    "internal_feature_elongation",
                    "missense_variant",
                    "mnv",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "splice_region_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "structural_variant",
                    "transcript_ablation",
                ],
            },
        )

    def testToSettingsAllCodingDeepIntronic(self):
        self.assertEqual(
            query_presets.Impact.ALL_CODING_DEEP_INTRONIC.to_settings(),
            {
                "var_type_snv": True,
                "var_type_mnv": True,
                "var_type_indel": True,
                "transcripts_coding": True,
                "transcripts_noncoding": False,
                "max_exon_dist": None,
                "effects": [
                    "coding_transcript_intron_variant",
                    "complex_substitution",
                    "direct_tandem_duplication",
                    "disruptive_inframe_deletion",
                    "disruptive_inframe_insertion",
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "inframe_deletion",
                    "inframe_insertion",
                    "internal_feature_elongation",
                    "missense_variant",
                    "mnv",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "splice_region_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "structural_variant",
                    "synonymous_variant",
                    "transcript_ablation",
                ],
            },
        )

    def testToSettingsWholeTranscript(self):
        self.assertEqual(
            query_presets.Impact.WHOLE_TRANSCRIPT.to_settings(),
            {
                "var_type_snv": True,
                "var_type_mnv": True,
                "var_type_indel": True,
                "transcripts_coding": True,
                "transcripts_noncoding": True,
                "max_exon_dist": None,
                "effects": [
                    "3_prime_UTR_exon_variant",
                    "3_prime_UTR_intron_variant",
                    "5_prime_UTR_exon_variant",
                    "5_prime_UTR_intron_variant",
                    "coding_transcript_intron_variant",
                    "complex_substitution",
                    "direct_tandem_duplication",
                    "disruptive_inframe_deletion",
                    "disruptive_inframe_insertion",
                    "downstream_gene_variant",
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "inframe_deletion",
                    "inframe_insertion",
                    "internal_feature_elongation",
                    "missense_variant",
                    "mnv",
                    "non_coding_transcript_exon_variant",
                    "non_coding_transcript_intron_variant",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "splice_region_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "stop_retained_variant",
                    "structural_variant",
                    "synonymous_variant",
                    "transcript_ablation",
                    "upstream_gene_variant",
                ],
            },
        )

    def testToSettingsAny(self):
        self.assertEqual(
            query_presets.Impact.ANY.to_settings(),
            {
                "var_type_snv": True,
                "var_type_mnv": True,
                "var_type_indel": True,
                "transcripts_coding": True,
                "transcripts_noncoding": True,
                "max_exon_dist": None,
                "effects": [
                    "3_prime_UTR_exon_variant",
                    "3_prime_UTR_intron_variant",
                    "5_prime_UTR_exon_variant",
                    "5_prime_UTR_intron_variant",
                    "coding_transcript_intron_variant",
                    "complex_substitution",
                    "direct_tandem_duplication",
                    "disruptive_inframe_deletion",
                    "disruptive_inframe_insertion",
                    "downstream_gene_variant",
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "inframe_deletion",
                    "inframe_insertion",
                    "intergenic_variant",
                    "internal_feature_elongation",
                    "missense_variant",
                    "mnv",
                    "non_coding_transcript_exon_variant",
                    "non_coding_transcript_intron_variant",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "splice_region_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "stop_retained_variant",
                    "structural_variant",
                    "synonymous_variant",
                    "transcript_ablation",
                    "upstream_gene_variant",
                ],
            },
        )


class TestEnumQualityFail(TestCase):
    def testValues(self):
        self.assertEqual(query_presets._QualityFail.DROP_VARIANT.value, "drop-variant")
        self.assertEqual(query_presets._QualityFail.IGNORE.value, "ignore")
        self.assertEqual(query_presets._QualityFail.NO_CALL.value, "no-call")


class TestEnumQuality(PedigreesMixin, TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Quality.SUPER_STRICT.value, "super_strict")
        self.assertEqual(query_presets.Quality.STRICT.value, "strict")
        self.assertEqual(query_presets.Quality.RELAXED.value, "relaxed")
        self.assertEqual(query_presets.Quality.ANY.value, "any")

    def testToSettingsSuperStrict(self):
        self.assertEqual(
            query_presets.Quality.SUPER_STRICT.to_settings(self.trio_denovo),
            {
                "quality": {
                    "father": {
                        "ab": 0.3,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 30,
                    },
                    "index": {
                        "ab": 0.3,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 30,
                    },
                    "mother": {
                        "ab": 0.3,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 30,
                    },
                },
            },
        )

    def testToSettingsStrict(self):
        self.assertEqual(
            query_presets.Quality.STRICT.to_settings(self.trio_denovo),
            {
                "quality": {
                    "father": {
                        "ab": 0.2,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                    "index": {
                        "ab": 0.2,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                    "mother": {
                        "ab": 0.2,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                },
            },
        )

    def testToSettingsRelaxed(self):
        self.assertEqual(
            query_presets.Quality.RELAXED.to_settings(self.trio_denovo),
            {
                "quality": {
                    "father": {
                        "ab": 0.1,
                        "ad": 2,
                        "ad_max": None,
                        "dp_het": 8,
                        "dp_hom": 4,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                    "index": {
                        "ab": 0.1,
                        "ad": 2,
                        "ad_max": None,
                        "dp_het": 8,
                        "dp_hom": 4,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                    "mother": {
                        "ab": 0.1,
                        "ad": 2,
                        "ad_max": None,
                        "dp_het": 8,
                        "dp_hom": 4,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                },
            },
        )

    def testToSettingsAny(self):
        self.assertEqual(
            query_presets.Quality.ANY.to_settings(self.trio_denovo),
            {
                "quality": {
                    "father": {
                        "ab": 0.0,
                        "ad": 0,
                        "ad_max": None,
                        "dp_het": 0,
                        "dp_hom": 0,
                        "fail": "ignore",
                        "gq": 0,
                    },
                    "index": {
                        "ab": 0.0,
                        "ad": 0,
                        "ad_max": None,
                        "dp_het": 0,
                        "dp_hom": 0,
                        "fail": "ignore",
                        "gq": 0,
                    },
                    "mother": {
                        "ab": 0.0,
                        "ad": 0,
                        "ad_max": None,
                        "dp_het": 0,
                        "dp_hom": 0,
                        "fail": "ignore",
                        "gq": 0,
                    },
                },
            },
        )


class TestEnumChromosomes(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Chromosomes.WHOLE_GENOME.value, "whole_genome")
        self.assertEqual(query_presets.Chromosomes.AUTOSOMES.value, "autosomes")
        self.assertEqual(query_presets.Chromosomes.X_CHROMOSOME.value, "x_chromosome")
        self.assertEqual(query_presets.Chromosomes.Y_CHROMOSOME.value, "y_chromosome")
        self.assertEqual(query_presets.Chromosomes.MT_CHROMOSOME.value, "mt_chromosome")

    def testToSettingsWholeGenome(self):
        self.assertEqual(
            query_presets.Chromosomes.WHOLE_GENOME.to_settings(),
            {
                "genomic_region": [],
                "gene_allowlist": [],
                "gene_blocklist": [],
            },
        )

    def testToSettingsAutosomes(self):
        self.assertEqual(
            query_presets.Chromosomes.AUTOSOMES.to_settings(),
            {
                "genomic_region": [f"{num}" for num in range(1, 23)],
                "gene_allowlist": [],
                "gene_blocklist": [],
            },
        )

    def testToSettingsXChromosome(self):
        self.assertEqual(
            query_presets.Chromosomes.X_CHROMOSOME.to_settings(),
            {
                "genomic_region": [
                    "X",
                ],
                "gene_allowlist": [],
                "gene_blocklist": [],
            },
        )

    def testToSettingsYChromosome(self):
        self.assertEqual(
            query_presets.Chromosomes.Y_CHROMOSOME.to_settings(),
            {
                "genomic_region": [
                    "Y",
                ],
                "gene_allowlist": [],
                "gene_blocklist": [],
            },
        )

    def testToSettingsMTChromosome(self):
        self.assertEqual(
            query_presets.Chromosomes.MT_CHROMOSOME.to_settings(),
            {
                "genomic_region": [
                    "MT",
                ],
                "gene_allowlist": [],
                "gene_blocklist": [],
            },
        )


class TestEnumFlagsEtc(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.FlagsEtc.DEFAULTS.value, "defaults")
        self.assertEqual(query_presets.FlagsEtc.CLINVAR_ONLY.value, "clinvar_only")
        self.assertEqual(query_presets.FlagsEtc.USER_FLAGGED.value, "user_flagged")

    def testToSettingsDefaults(self):
        self.assertEqual(
            query_presets.FlagsEtc.DEFAULTS.to_settings(),
            {
                "clinvar_include_benign": False,
                "clinvar_include_likely_benign": False,
                "clinvar_include_likely_pathogenic": True,
                "clinvar_include_pathogenic": True,
                "clinvar_include_uncertain_significance": False,
                "clinvar_paranoid_mode": False,
                "flag_bookmarked": True,
                "flag_incidental": True,
                "flag_candidate": True,
                "flag_doesnt_segregate": True,
                "flag_final_causative": True,
                "flag_for_validation": True,
                "flag_no_disease_association": True,
                "flag_molecular_empty": True,
                "flag_molecular_negative": True,
                "flag_molecular_positive": True,
                "flag_molecular_uncertain": True,
                "flag_phenotype_match_empty": True,
                "flag_phenotype_match_negative": True,
                "flag_phenotype_match_positive": True,
                "flag_phenotype_match_uncertain": True,
                "flag_segregates": True,
                "flag_simple_empty": True,
                "flag_summary_empty": True,
                "flag_summary_negative": True,
                "flag_summary_positive": True,
                "flag_summary_uncertain": True,
                "flag_validation_empty": True,
                "flag_validation_negative": True,
                "flag_validation_positive": True,
                "flag_validation_uncertain": True,
                "flag_visual_empty": True,
                "flag_visual_negative": True,
                "flag_visual_positive": True,
                "flag_visual_uncertain": True,
                "require_in_clinvar": False,
            },
        )

    def testToSettingsClinvarOnly(self):
        self.assertEqual(
            query_presets.FlagsEtc.CLINVAR_ONLY.to_settings(),
            {
                "flag_bookmarked": True,
                "flag_incidental": True,
                "flag_candidate": True,
                "flag_doesnt_segregate": True,
                "flag_final_causative": True,
                "flag_for_validation": True,
                "flag_no_disease_association": True,
                "flag_molecular_empty": True,
                "flag_molecular_negative": True,
                "flag_molecular_positive": True,
                "flag_molecular_uncertain": True,
                "flag_phenotype_match_empty": True,
                "flag_phenotype_match_negative": True,
                "flag_phenotype_match_positive": True,
                "flag_phenotype_match_uncertain": True,
                "flag_segregates": True,
                "flag_simple_empty": True,
                "flag_summary_empty": True,
                "flag_summary_negative": True,
                "flag_summary_positive": True,
                "flag_summary_uncertain": True,
                "flag_validation_empty": True,
                "flag_validation_negative": True,
                "flag_validation_positive": True,
                "flag_validation_uncertain": True,
                "flag_visual_empty": True,
                "flag_visual_negative": True,
                "flag_visual_positive": True,
                "flag_visual_uncertain": True,
                "require_in_clinvar": True,
                "clinvar_paranoid_mode": False,
            },
        )

    def testToSettingsUserFlagged(self):
        self.assertEqual(
            query_presets.FlagsEtc.USER_FLAGGED.to_settings(),
            {
                "clinvar_include_benign": False,
                "clinvar_include_likely_benign": False,
                "clinvar_include_likely_pathogenic": True,
                "clinvar_include_pathogenic": True,
                "clinvar_include_uncertain_significance": False,
                "flag_bookmarked": True,
                "flag_incidental": True,
                "flag_candidate": True,
                "flag_doesnt_segregate": True,
                "flag_final_causative": True,
                "flag_for_validation": True,
                "flag_no_disease_association": True,
                "flag_molecular_empty": False,
                "flag_molecular_negative": True,
                "flag_molecular_positive": True,
                "flag_molecular_uncertain": True,
                "flag_phenotype_match_empty": False,
                "flag_phenotype_match_negative": True,
                "flag_phenotype_match_positive": True,
                "flag_phenotype_match_uncertain": True,
                "flag_segregates": True,
                "flag_simple_empty": False,
                "flag_summary_empty": False,
                "flag_summary_negative": True,
                "flag_summary_positive": True,
                "flag_summary_uncertain": True,
                "flag_validation_empty": False,
                "flag_validation_negative": True,
                "flag_validation_positive": True,
                "flag_validation_uncertain": True,
                "flag_visual_empty": False,
                "flag_visual_negative": True,
                "flag_visual_positive": True,
                "flag_visual_uncertain": True,
                "require_in_clinvar": False,
                "clinvar_paranoid_mode": False,
            },
        )


class TestQuickPresets(PedigreesMixin, TestCase):
    def testValueDefaults(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.defaults),
            "QuickPresets(label='defaults', inheritance=<Inheritance.ANY: 'any'>, "
            "frequency=<Frequency.DOMINANT_STRICT: 'dominant_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueDeNovo(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.de_novo),
            "QuickPresets(label='de novo', inheritance=<Inheritance.DE_NOVO: 'de_novo'>, "
            "frequency=<Frequency.DOMINANT_STRICT: 'dominant_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.SUPER_STRICT: 'super_strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueDominant(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.dominant),
            "QuickPresets(label='dominant', inheritance=<Inheritance.DOMINANT: 'dominant'>, "
            "frequency=<Frequency.DOMINANT_STRICT: 'dominant_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueHomozygousRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.homozygous_recessive),
            "QuickPresets(label='homozygous recessive', "
            "inheritance=<Inheritance.HOMOZYGOUS_RECESSIVE: 'homozygous_recessive'>, "
            "frequency=<Frequency.RECESSIVE_STRICT: 'recessive_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueCompoundRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.compound_recessive),
            "QuickPresets(label='compound recessive', "
            "inheritance=<Inheritance.COMPOUND_HETEROZYGOUS: 'compound_heterozygous'>, "
            "frequency=<Frequency.RECESSIVE_STRICT: 'recessive_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.recessive),
            "QuickPresets(label='recessive', inheritance=<Inheritance.RECESSIVE: 'recessive'>, "
            "frequency=<Frequency.RECESSIVE_STRICT: 'recessive_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueXRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.x_recessive),
            "QuickPresets(label='X-recessive', inheritance=<Inheritance.X_RECESSIVE: 'x_recessive'>, "
            "frequency=<Frequency.RECESSIVE_STRICT: 'recessive_strict'>, "
            "impact=<Impact.AA_CHANGE_SPLICING: 'aa_change_splicing'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.X_CHROMOSOME: 'x_chromosome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueClinvarPathogenic(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.clinvar_pathogenic),
            "QuickPresets(label='ClinVar pathogenic', "
            "inheritance=<Inheritance.AFFECTED_CARRIERS: 'affected_carriers'>, "
            "frequency=<Frequency.ANY: 'any'>, impact=<Impact.ANY: 'any'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.CLINVAR_ONLY: 'clinvar_only'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueMitochondrial(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.mitochondrial),
            "QuickPresets(label='mitochondrial', inheritance=<Inheritance.AFFECTED_CARRIERS: 'affected_carriers'>, "
            "frequency=<Frequency.DOMINANT_STRICT: 'dominant_strict'>, impact=<Impact.ANY: 'any'>, "
            "quality=<Quality.STRICT: 'strict'>, chromosomes=<Chromosomes.MT_CHROMOSOME: 'mt_chromosome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueWholeExome(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.whole_exome),
            "QuickPresets(label='whole exome', inheritance=<Inheritance.ANY: 'any'>, "
            "frequency=<Frequency.ANY: 'any'>, "
            "impact=<Impact.ANY: 'any'>, "
            "quality=<Quality.ANY: 'any'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, "
            "flagsetc=<FlagsEtc.DEFAULTS: 'defaults'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testToSettingsDefaults(self):
        # NB: we only test the full output for the defaults and otherwise just smoke test to_settings.
        self.assertEqual(
            query_presets.QUICK_PRESETS.defaults.to_settings(self.trio_denovo),
            {
                "clinvar_include_benign": False,
                "clinvar_include_likely_benign": False,
                "clinvar_include_likely_pathogenic": True,
                "clinvar_include_pathogenic": True,
                "clinvar_include_uncertain_significance": False,
                "clinvar_paranoid_mode": False,
                "database": query_presets.Database.REFSEQ.value,
                "max_exon_dist": None,
                "effects": [
                    "complex_substitution",
                    "direct_tandem_duplication",
                    "disruptive_inframe_deletion",
                    "disruptive_inframe_insertion",
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "inframe_deletion",
                    "inframe_insertion",
                    "internal_feature_elongation",
                    "missense_variant",
                    "mnv",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "splice_region_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "structural_variant",
                    "transcript_ablation",
                ],
                "exac_enabled": True,
                "exac_frequency": 0.002,
                "exac_hemizygous": None,
                "exac_heterozygous": 10,
                "exac_homozygous": 0,
                "flag_bookmarked": True,
                "flag_incidental": True,
                "flag_candidate": True,
                "flag_doesnt_segregate": True,
                "flag_final_causative": True,
                "flag_for_validation": True,
                "flag_molecular_empty": True,
                "flag_molecular_negative": True,
                "flag_molecular_positive": True,
                "flag_molecular_uncertain": True,
                "flag_no_disease_association": True,
                "flag_phenotype_match_empty": True,
                "flag_phenotype_match_negative": True,
                "flag_phenotype_match_positive": True,
                "flag_phenotype_match_uncertain": True,
                "flag_segregates": True,
                "flag_simple_empty": True,
                "flag_summary_empty": True,
                "flag_summary_negative": True,
                "flag_summary_positive": True,
                "flag_summary_uncertain": True,
                "flag_validation_empty": True,
                "flag_validation_negative": True,
                "flag_validation_positive": True,
                "flag_validation_uncertain": True,
                "flag_visual_empty": True,
                "flag_visual_negative": True,
                "flag_visual_positive": True,
                "flag_visual_uncertain": True,
                "gene_allowlist": [],
                "gene_blocklist": [],
                "genomic_region": [],
                "genotype": {
                    "father": query_presets.GenotypeChoice.ANY.value,
                    "index": query_presets.GenotypeChoice.ANY.value,
                    "mother": query_presets.GenotypeChoice.ANY.value,
                },
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.002,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_heterozygous": 20,
                "gnomad_exomes_homozygous": 0,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_frequency": 0.002,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_heterozygous": 4,
                "gnomad_genomes_homozygous": 0,
                "helixmtdb_enabled": True,
                "helixmtdb_frequency": 0.01,
                "helixmtdb_het_count": None,
                "helixmtdb_hom_count": 200,
                "inhouse_carriers": 20,
                "inhouse_enabled": True,
                "inhouse_hemizygous": None,
                "inhouse_heterozygous": None,
                "inhouse_homozygous": None,
                "mitomap_count": None,
                "mitomap_enabled": False,
                "mitomap_frequency": None,
                "quality": {
                    "index": {
                        "ab": 0.2,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                    "mother": {
                        "ab": 0.2,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                    "father": {
                        "ab": 0.2,
                        "ad": 3,
                        "ad_max": None,
                        "dp_het": 10,
                        "dp_hom": 5,
                        "fail": "drop-variant",
                        "gq": 10,
                    },
                },
                "mtdb_count": 10,
                "mtdb_enabled": True,
                "mtdb_frequency": 0.01,
                "recessive_index": None,
                "recessive_mode": None,
                "require_in_clinvar": False,
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.002,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_heterozygous": 4,
                "thousand_genomes_homozygous": 0,
                "transcripts_coding": True,
                "transcripts_noncoding": False,
                "var_type_indel": True,
                "var_type_mnv": True,
                "var_type_snv": True,
            },
        )

    def testToSettingsOther(self):
        self.assertTrue(query_presets.QUICK_PRESETS.defaults.to_settings(self.trio_denovo))
        self.assertTrue(query_presets.QUICK_PRESETS.de_novo.to_settings(self.trio_denovo))
        self.assertTrue(query_presets.QUICK_PRESETS.dominant.to_settings(self.trio_denovo))
        self.assertTrue(
            query_presets.QUICK_PRESETS.homozygous_recessive.to_settings(self.trio_denovo)
        )
        self.assertTrue(
            query_presets.QUICK_PRESETS.compound_recessive.to_settings(self.trio_denovo)
        )
        self.assertTrue(query_presets.QUICK_PRESETS.recessive.to_settings(self.trio_denovo))
        self.assertTrue(query_presets.QUICK_PRESETS.x_recessive.to_settings(self.trio_denovo))
        self.assertTrue(
            query_presets.QUICK_PRESETS.clinvar_pathogenic.to_settings(self.trio_denovo)
        )
        self.assertTrue(query_presets.QUICK_PRESETS.mitochondrial.to_settings(self.trio_denovo))
