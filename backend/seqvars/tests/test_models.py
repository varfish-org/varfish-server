"""Test models and factories"""

from freezegun import freeze_time
from parameterized import parameterized
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus.test import TestCase

from cases_analysis.tests.factories import CaseAnalysisSessionFactory
from seqvars.factory_defaults import create_seqvarspresetsset_short_read_genome
from seqvars.models.base import (
    SeqvarsGenotypeChoice,
    SeqvarsGenotypePresetChoice,
    SeqvarsGenotypePresetsPydantic,
    SeqvarsPredefinedQuery,
    SeqvarsQuery,
    SeqvarsQueryExecution,
    SeqvarsQueryPresetsClinvar,
    SeqvarsQueryPresetsColumns,
    SeqvarsQueryPresetsConsequence,
    SeqvarsQueryPresetsFrequency,
    SeqvarsQueryPresetsLocus,
    SeqvarsQueryPresetsPhenotypePrio,
    SeqvarsQueryPresetsQuality,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
    SeqvarsQueryPresetsVariantPrio,
    SeqvarsQuerySettings,
    SeqvarsQuerySettingsClinvar,
    SeqvarsQuerySettingsColumns,
    SeqvarsQuerySettingsConsequence,
    SeqvarsQuerySettingsFrequency,
    SeqvarsQuerySettingsGenotype,
    SeqvarsQuerySettingsLocus,
    SeqvarsQuerySettingsPhenotypePrio,
    SeqvarsQuerySettingsQuality,
    SeqvarsQuerySettingsVariantPrio,
    SeqvarsRecessiveModeChoice,
    SeqvarsResultRow,
    SeqvarsResultSet,
)
from seqvars.tests.factories import (
    SeqvarsPredefinedQueryFactory,
    SeqvarsQueryExecutionFactory,
    SeqvarsQueryFactory,
    SeqvarsQueryPresetsClinvarFactory,
    SeqvarsQueryPresetsColumnsFactory,
    SeqvarsQueryPresetsConsequenceFactory,
    SeqvarsQueryPresetsFrequencyFactory,
    SeqvarsQueryPresetsLocusFactory,
    SeqvarsQueryPresetsPhenotypePrioFactory,
    SeqvarsQueryPresetsQualityFactory,
    SeqvarsQueryPresetsSetFactory,
    SeqvarsQueryPresetsSetVersionFactory,
    SeqvarsQueryPresetsVariantPrioFactory,
    SeqvarsQuerySettingsClinvarFactory,
    SeqvarsQuerySettingsColumnsFactory,
    SeqvarsQuerySettingsConsequenceFactory,
    SeqvarsQuerySettingsFactory,
    SeqvarsQuerySettingsFrequencyFactory,
    SeqvarsQuerySettingsGenotypeFactory,
    SeqvarsQuerySettingsLocusFactory,
    SeqvarsQuerySettingsPhenotypePrioFactory,
    SeqvarsQuerySettingsQualityFactory,
    SeqvarsQuerySettingsVariantPrioFactory,
    SeqvarsResultRowFactory,
    SeqvarsResultSetFactory,
)
from variants.tests.factories import ProjectFactory


class TestSeqvarsCaseGenotypeChoice(TestCase):

    def test_values(self):
        self.assertEqual(
            [
                "any",
                "ref",
                "het",
                "hom",
                "non_het",
                "non_hom",
                "variant",
                "recessive_index",
                "recessive_father",
                "recessive_mother",
            ],
            SeqvarsGenotypeChoice.values(),
        )


class TestSeqvarsRecessiveModeChoice(TestCase):

    def test_values(self):
        self.assertEqual(
            [
                "disabled",
                "comphet_recessive",
                "homozygous_recessive",
                "recessive",
            ],
            SeqvarsRecessiveModeChoice.values(),
        )


class TestSeqvarsQueryPresetsSet(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsSet.objects.count(), 0)
        SeqvarsQueryPresetsSetFactory()
        self.assertEqual(SeqvarsQueryPresetsSet.objects.count(), 1)

    def test_str(self):
        querypresetsset = SeqvarsQueryPresetsSetFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsSet '{querypresetsset.sodar_uuid}'",
            querypresetsset.__str__(),
        )

    def test_clone_from_db(self):
        # Note: only smoke test implemented so far.
        project = ProjectFactory()
        querypresetsset = SeqvarsQueryPresetsSetFactory()
        querypresetsset.clone_with_latest_version(project=project)

    def test_clone_factory_default(self):
        # Note: only smoke test implemented so far.
        project = ProjectFactory()
        querypresetset = create_seqvarspresetsset_short_read_genome()
        querypresetset.clone_with_latest_version(project=project)


class TestSeqvarsQueryPresetsSetVersion(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsSetVersion.objects.count(), 0)
        SeqvarsQueryPresetsSetVersionFactory()
        self.assertEqual(SeqvarsQueryPresetsSetVersion.objects.count(), 1)

    def test_str(self):
        querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsSetVersion '{querypresetssetversion.sodar_uuid}'",
            querypresetssetversion.__str__(),
        )


class TestSeqvarsQueryPresetsQuality(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsQuality.objects.count(), 0)
        SeqvarsQueryPresetsQualityFactory()
        self.assertEqual(SeqvarsQueryPresetsQuality.objects.count(), 1)

    def test_str(self):
        querypresetsquality = SeqvarsQueryPresetsQualityFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsQuality '{querypresetsquality.sodar_uuid}'",
            querypresetsquality.__str__(),
        )


class TestSeqvarsQueryPresetsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsFrequency.objects.count(), 0)
        SeqvarsQueryPresetsFrequencyFactory()
        self.assertEqual(SeqvarsQueryPresetsFrequency.objects.count(), 1)

    def test_str(self):
        querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsFrequency '{querypresetsfrequency.sodar_uuid}'",
            querypresetsfrequency.__str__(),
        )


class TestSeqvarsQueryPresetsConsequence(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsConsequence.objects.count(), 0)
        SeqvarsQueryPresetsConsequenceFactory()
        self.assertEqual(SeqvarsQueryPresetsConsequence.objects.count(), 1)

    def test_str(self):
        querypresetsconsequence = SeqvarsQueryPresetsConsequenceFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsConsequence '{querypresetsconsequence.sodar_uuid}'",
            querypresetsconsequence.__str__(),
        )


class TestSeqvarsQueryPresetsLocus(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsLocus.objects.count(), 0)
        SeqvarsQueryPresetsLocusFactory()
        self.assertEqual(SeqvarsQueryPresetsLocus.objects.count(), 1)

    def test_str(self):
        querypresetslocus = SeqvarsQueryPresetsLocusFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsLocus '{querypresetslocus.sodar_uuid}'",
            querypresetslocus.__str__(),
        )


class TestSeqvarsQueryPresetsPhenotypePrio(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsPhenotypePrio.objects.count(), 0)
        SeqvarsQueryPresetsPhenotypePrioFactory()
        self.assertEqual(SeqvarsQueryPresetsPhenotypePrio.objects.count(), 1)

    def test_str(self):
        querypresetsphenotypeprio = SeqvarsQueryPresetsPhenotypePrioFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsPhenotypePrio '{querypresetsphenotypeprio.sodar_uuid}'",
            querypresetsphenotypeprio.__str__(),
        )


class TestSeqvarsQueryPresetsVariantPrio(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsVariantPrio.objects.count(), 0)
        SeqvarsQueryPresetsVariantPrioFactory()
        self.assertEqual(SeqvarsQueryPresetsVariantPrio.objects.count(), 1)

    def test_str(self):
        querypresetsvariantprio = SeqvarsQueryPresetsVariantPrioFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsVariantPrio '{querypresetsvariantprio.sodar_uuid}'",
            querypresetsvariantprio.__str__(),
        )


class TestSeqvarsQueryPresetsClinvar(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsClinvar.objects.count(), 0)
        SeqvarsQueryPresetsClinvarFactory()
        self.assertEqual(SeqvarsQueryPresetsClinvar.objects.count(), 1)

    def test_str(self):
        querypresetsclinvar = SeqvarsQueryPresetsClinvarFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsClinvar '{querypresetsclinvar.sodar_uuid}'",
            querypresetsclinvar.__str__(),
        )


class TestSeqvarsQueryPresetsColumns(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsColumns.objects.count(), 0)
        SeqvarsQueryPresetsColumnsFactory()
        self.assertEqual(SeqvarsQueryPresetsColumns.objects.count(), 1)

    def test_str(self):
        querypresetscolumns = SeqvarsQueryPresetsColumnsFactory()
        self.assertEqual(
            f"SeqvarsQueryPresetsColumns '{querypresetscolumns.sodar_uuid}'",
            querypresetscolumns.__str__(),
        )


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarsQuerySettings(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 0)
        SeqvarsQuerySettingsFactory()
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        querysettings = SeqvarsQuerySettingsFactory()
        self.assertEqual(
            f"SeqvarsQuerySettings '{querysettings.sodar_uuid}'",
            querysettings.__str__(),
        )

    def test_from_predefinedquery(self):
        predefinedquery = SeqvarsPredefinedQueryFactory()
        session = CaseAnalysisSessionFactory()
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 0)
        querysettings = SeqvarsQuerySettings.objects.from_predefinedquery(
            session=session,
            predefinedquery=predefinedquery,
        )
        _ = querysettings
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 1)

    def test_make_clone(self):
        predefinedquery = SeqvarsPredefinedQueryFactory()
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.from_predefinedquery(
            session=session,
            predefinedquery=predefinedquery,
        )
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 1)

        cloned_querysettings = querysettings.make_clone()
        _ = cloned_querysettings
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 2)


class TestSeqvarsQuerySettingsGenotype(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 0)
        SeqvarsQuerySettingsGenotypeFactory()
        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 1)

    def test_str(self):
        genotype = SeqvarsQuerySettingsGenotypeFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsGenotype '{genotype.sodar_uuid}'",
            genotype.__str__(),
        )

    @parameterized.expand([[value] for value in SeqvarsGenotypePresetChoice.values()])
    def test_from_presets(self, genotypepresets_choice: SeqvarsGenotypePresetChoice):
        session = CaseAnalysisSessionFactory()
        # Make individual names predictable.
        for idx, individual in enumerate(session.case.pedigree_obj.individual_set.all()):
            individual.name = f"IND_{idx}"
            individual.save()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        genotypepresets = SeqvarsGenotypePresetsPydantic(choice=genotypepresets_choice)

        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 0)
        genotypesettings = SeqvarsQuerySettingsGenotype.objects.from_presets(
            pedigree=session.case.pedigree_obj,
            querysettings=querysettings,
            genotypepresets=genotypepresets,
        )

        self.assertEqual(SeqvarsQuerySettingsGenotype.objects.count(), 1)
        self.assertMatchSnapshot(
            [v.model_dump(mode="json") for v in genotypesettings.sample_genotype_choices],
            "sample_genotype_choices",
        )


class TestSeqvarsQuerySettingsQuality(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 0)
        SeqvarsQuerySettingsQualityFactory()
        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 1)

    def test_str(self):
        quality = SeqvarsQuerySettingsQualityFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsQuality '{quality.sodar_uuid}'",
            quality.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        # Make individual names predictable.
        for idx, individual in enumerate(session.case.pedigree_obj.individual_set.all()):
            individual.name = f"IND_{idx}"
            individual.save()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        qualitypresets = SeqvarsQueryPresetsQualityFactory()

        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 0)
        qualitysettings = SeqvarsQuerySettingsQuality.objects.from_presets(
            pedigree=session.case.pedigree_obj,
            querysettings=querysettings,
            qualitypresets=qualitypresets,
        )

        self.assertEqual(SeqvarsQuerySettingsQuality.objects.count(), 1)
        self.assertMatchSnapshot(
            [v.model_dump(mode="json") for v in qualitysettings.sample_quality_filters],
            "sample_quality_filters",
        )


class TestSeqvarsQuerySettingsFrequency(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 0)
        SeqvarsQuerySettingsFrequencyFactory()
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        frequency = SeqvarsQuerySettingsFrequencyFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsFrequency '{frequency.sodar_uuid}'",
            frequency.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        frequencypresets = SeqvarsQueryPresetsFrequencyFactory()

        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 0)
        frequencysettings = SeqvarsQuerySettingsFrequency.objects.from_presets(
            querysettings=querysettings, frequencypresets=frequencypresets
        )

        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)
        for key in (
            "gnomad_exomes",
            "gnomad_genomes",
            "gnomad_mitochondrial",
            "helixmtdb",
            "inhouse",
        ):
            self.assertMatchSnapshot(getattr(frequencysettings, key).model_dump(mode="json"), key)


class TestSeqvarsQuerySettingsConsequence(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 0)
        SeqvarsQuerySettingsConsequenceFactory()
        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 1)

    def test_str(self):
        consequence = SeqvarsQuerySettingsConsequenceFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsConsequence '{consequence.sodar_uuid}'",
            consequence.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        consequencepresets = SeqvarsQueryPresetsConsequenceFactory()

        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 0)
        consequencesettings = SeqvarsQuerySettingsConsequence.objects.from_presets(
            querysettings=querysettings, consequencepresets=consequencepresets
        )

        self.assertEqual(SeqvarsQuerySettingsConsequence.objects.count(), 1)
        for key in (
            "variant_types",
            "transcript_types",
            "variant_consequences",
            "max_distance_to_exon",
        ):
            if key == "max_distance_to_exon":
                self.assertMatchSnapshot(getattr(consequencesettings, key), key)
            else:
                self.assertMatchSnapshot([str(v) for v in getattr(consequencesettings, key)], key)


class TestSeqvarsQuerySettingsLocus(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 0)
        SeqvarsQuerySettingsLocusFactory()
        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 1)

    def test_str(self):
        locus = SeqvarsQuerySettingsLocusFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsLocus '{locus.sodar_uuid}'",
            locus.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        locuspresets = SeqvarsQueryPresetsLocusFactory()

        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 0)
        locussettings = SeqvarsQuerySettingsLocus.objects.from_presets(
            querysettings=querysettings, locuspresets=locuspresets
        )

        self.assertEqual(SeqvarsQuerySettingsLocus.objects.count(), 1)
        for key in (
            "genes",
            "gene_panels",
            "genome_regions",
        ):
            self.assertMatchSnapshot(
                [x.model_dump(mode="json") for x in getattr(locussettings, key)], key
            )


class TestSeqvarsQuerySettingsPhenotypePrio(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 0)
        SeqvarsQuerySettingsPhenotypePrioFactory()
        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 1)

    def test_str(self):
        phenotypeprio = SeqvarsQuerySettingsPhenotypePrioFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsPhenotypePrio '{phenotypeprio.sodar_uuid}'",
            phenotypeprio.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        phenotypepriopresets = SeqvarsQueryPresetsPhenotypePrioFactory()

        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 0)
        phenotypepriosettings = SeqvarsQuerySettingsPhenotypePrio.objects.from_presets(
            querysettings=querysettings, phenotypepriopresets=phenotypepriopresets
        )

        self.assertEqual(SeqvarsQuerySettingsPhenotypePrio.objects.count(), 1)
        for key in (
            "phenotype_prio_enabled",
            "phenotype_prio_algorithm",
        ):
            self.assertMatchSnapshot(getattr(phenotypepriosettings, key), key)
        self.assertMatchSnapshot(
            [x.model_dump(mode="json") for x in phenotypepriosettings.terms], "terms"
        )


class TestSeqvarsQuerySettingsVariantPrio(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 0)
        SeqvarsQuerySettingsVariantPrioFactory()
        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 1)

    def test_str(self):
        variantprio = SeqvarsQuerySettingsVariantPrioFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsVariantPrio '{variantprio.sodar_uuid}'",
            variantprio.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        variantpriopresets = SeqvarsQueryPresetsVariantPrioFactory()

        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 0)
        variantpriosettings = SeqvarsQuerySettingsVariantPrio.objects.from_presets(
            querysettings=querysettings, variantpriopresets=variantpriopresets
        )

        self.assertEqual(SeqvarsQuerySettingsVariantPrio.objects.count(), 1)
        self.assertMatchSnapshot(variantpriosettings.variant_prio_enabled, "variant_prio_enabled")
        self.assertMatchSnapshot(
            [v.model_dump(mode="json") for v in variantpriosettings.services], "services"
        )


class TestSeqvarsQuerySettingsClinvar(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 0)
        SeqvarsQuerySettingsClinvarFactory()
        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 1)

    def test_str(self):
        clinvar = SeqvarsQuerySettingsClinvarFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsClinvar '{clinvar.sodar_uuid}'",
            clinvar.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        clinvarpresets = SeqvarsQueryPresetsClinvarFactory()

        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 0)
        clinvarsettings = SeqvarsQuerySettingsClinvar.objects.from_presets(
            querysettings=querysettings, clinvarpresets=clinvarpresets
        )

        self.assertEqual(SeqvarsQuerySettingsClinvar.objects.count(), 1)
        for key in (
            "clinvar_presence_required",
            "clinvar_germline_aggregate_description",
            "allow_conflicting_interpretations",
        ):
            if key == "clinvar_germline_aggregate_description":
                self.assertMatchSnapshot([str(v) for v in getattr(clinvarsettings, key)], key)
            else:
                self.assertMatchSnapshot(getattr(clinvarsettings, key), key)


class TestSeqvarsQuerySettingsColumns(TestCaseSnapshot, TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 0)
        SeqvarsQuerySettingsColumnsFactory()
        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 1)

    def test_str(self):
        columnsconfig = SeqvarsQuerySettingsColumnsFactory()
        self.assertEqual(
            f"SeqvarsQuerySettingsColumns '{columnsconfig.sodar_uuid}'",
            columnsconfig.__str__(),
        )

    def test_from_presets(self):
        session = CaseAnalysisSessionFactory()
        querysettings = SeqvarsQuerySettings.objects.create(session=session)
        columnspresets = SeqvarsQueryPresetsColumnsFactory()

        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 0)
        columnssettings = SeqvarsQuerySettingsColumns.objects.from_presets(
            querysettings=querysettings, columnspresets=columnspresets
        )

        self.assertEqual(SeqvarsQuerySettingsColumns.objects.count(), 1)
        for key in ("column_settings",):
            self.assertMatchSnapshot(getattr(columnssettings, key), key)


class TestSeqvarsPredefinedQuery(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 0)
        SeqvarsPredefinedQueryFactory()
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 1)

    def test_str(self):
        predefinedquery = SeqvarsPredefinedQueryFactory()
        self.assertEqual(
            f"SeqvarsPredefinedQuery '{predefinedquery.sodar_uuid}'",
            predefinedquery.__str__(),
        )


class TestSeqvarsQuery(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQuery.objects.count(), 0)
        SeqvarsQueryFactory()
        self.assertEqual(SeqvarsQuery.objects.count(), 1)

    def test_property_case(self):
        query = SeqvarsQueryFactory()
        self.assertEqual(
            query.session.caseanalysis.case.pk,
            query.case.pk,
        )

    def test_str(self):
        query = SeqvarsQueryFactory()
        self.assertEqual(
            f"SeqvarsQuery '{query.sodar_uuid}'",
            query.__str__(),
        )

    def test_from_predefinedquery(self):
        session = CaseAnalysisSessionFactory()
        predefinedquery = SeqvarsPredefinedQueryFactory()
        self.assertEqual(SeqvarsQuery.objects.count(), 0)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 0)
        query = SeqvarsQuery.objects.from_predefinedquery(
            session=session,
            predefinedquery=predefinedquery,
        )
        _ = query
        self.assertEqual(SeqvarsQuery.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)


class TestSeqvarsQueryExecution(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryExecution.objects.count(), 0)
        SeqvarsQueryExecutionFactory()
        self.assertEqual(SeqvarsQueryExecution.objects.count(), 1)

    def test_property_case(self):
        queryexecution = SeqvarsQueryExecutionFactory()
        self.assertEqual(
            queryexecution.query.session.caseanalysis.case.pk,
            queryexecution.case.pk,
        )

    def test_str(self):
        queryexecution = SeqvarsQueryExecutionFactory()
        self.assertEqual(
            f"SeqvarsQueryExecution '{queryexecution.sodar_uuid}'",
            queryexecution.__str__(),
        )


class TestSeqvarsResultSet(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsResultSet.objects.count(), 0)
        SeqvarsResultSetFactory()
        self.assertEqual(SeqvarsResultSet.objects.count(), 1)

    def test_property_case(self):
        resultset = SeqvarsResultSetFactory()
        self.assertEqual(
            resultset.queryexecution.query.session.caseanalysis.case.pk,
            resultset.case.pk,
        )

    def test_get_absolute_url(self):
        resultset = SeqvarsResultSetFactory()
        self.assertEqual(
            (f"/seqvars/api/resultset/{resultset.case.sodar_uuid}/" f"{resultset.sodar_uuid}/"),
            resultset.get_absolute_url(),
        )

    def test_str(self):
        resultset = SeqvarsResultSetFactory()
        self.assertEqual(
            f"SeqvarsResultSet '{resultset.sodar_uuid}'",
            resultset.__str__(),
        )


class TestSeqvarsResultRow(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsResultRow.objects.count(), 0)
        SeqvarsResultRowFactory()
        self.assertEqual(SeqvarsResultRow.objects.count(), 1)

    def test_str(self):
        seqvarresultrow = SeqvarsResultRowFactory()
        self.assertEqual(
            (
                f"SeqvarsResultRow '{seqvarresultrow.sodar_uuid}' '{seqvarresultrow.genome_release}-"
                f"{seqvarresultrow.chrom}-{seqvarresultrow.pos}-"
                f"{seqvarresultrow.ref_allele}-{seqvarresultrow.alt_allele}'"
            ),
            seqvarresultrow.__str__(),
        )
