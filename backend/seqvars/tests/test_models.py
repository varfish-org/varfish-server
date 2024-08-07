"""Test models and factories"""

from test_plus.test import TestCase

from seqvars.factory_defaults import create_seqvarspresetsset_short_read_genome
from seqvars.models import (
    SeqvarsGenotypeChoice,
    SeqvarsPredefinedQuery,
    SeqvarsQuery,
    SeqvarsQueryColumnsConfig,
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
    SeqvarsQueryColumnsConfigFactory,
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


class TestSeqvarsQuerySettings(TestCase):

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


class TestSeqvarsQuerySettingsGenotype(TestCase):

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


class TestSeqvarsQuerySettingsQuality(TestCase):

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


class TestSeqvarsQuerySettingsFrequency(TestCase):

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


class TestSeqvarsQuerySettingsConsequence(TestCase):

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


class TestSeqvarsQuerySettingsLocus(TestCase):

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


class TestSeqvarsQuerySettingsPhenotypePrio(TestCase):

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


class TestSeqvarsQuerySettingsVariantPrio(TestCase):

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


class TestSeqvarsQuerySettingsClinvar(TestCase):

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


class TestSeqvarsPredefinedQuery(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 0)
        SeqvarsPredefinedQueryFactory()
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 1)

    def test_str(self):
        clinvar = SeqvarsPredefinedQueryFactory()
        self.assertEqual(
            f"SeqvarsPredefinedQuery '{clinvar.sodar_uuid}'",
            clinvar.__str__(),
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


class TestSeqvarsQueryColumnsConfig(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarsQueryColumnsConfig.objects.count(), 0)
        SeqvarsQueryColumnsConfigFactory()
        self.assertEqual(SeqvarsQueryColumnsConfig.objects.count(), 1)

    def test_str(self):
        columnsconfig = SeqvarsQueryColumnsConfigFactory()
        self.assertEqual(
            f"SeqvarsQueryColumnsConfig '{columnsconfig.sodar_uuid}'",
            columnsconfig.__str__(),
        )


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
