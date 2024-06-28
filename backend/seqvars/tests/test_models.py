"""Test models and factories"""

from freezegun import freeze_time
from test_plus.test import TestCase

from seqvars.models import (
    GenotypeChoice,
    Query,
    QueryColumnsConfig,
    QueryExecution,
    QueryPresetsClinvar,
    QueryPresetsColumns,
    QueryPresetsConsequence,
    QueryPresetsFrequency,
    QueryPresetsLocus,
    QueryPresetsPhenotypePrio,
    QueryPresetsQuality,
    QueryPresetsSet,
    QueryPresetsVariantPrio,
    QuerySettings,
    QuerySettingsClinvar,
    QuerySettingsConsequence,
    QuerySettingsFrequency,
    QuerySettingsGenotype,
    QuerySettingsLocus,
    QuerySettingsPhenotypePrio,
    QuerySettingsQuality,
    QuerySettingsVariantPrio,
    ResultRow,
    ResultSet,
)
from seqvars.tests.factories import (
    QueryColumnsConfigFactory,
    QueryExecutionFactory,
    QueryFactory,
    QueryPresetsClinvarFactory,
    QueryPresetsColumnsFactory,
    QueryPresetsConsequenceFactory,
    QueryPresetsFrequencyFactory,
    QueryPresetsLocusFactory,
    QueryPresetsPhenotypePrioFactory,
    QueryPresetsQualityFactory,
    QueryPresetsSetFactory,
    QueryPresetsVariantPrioFactory,
    QuerySettingsClinvarFactory,
    QuerySettingsConsequenceFactory,
    QuerySettingsFactory,
    QuerySettingsFrequencyFactory,
    QuerySettingsGenotypeFactory,
    QuerySettingsLocusFactory,
    QuerySettingsPhenotypePrioFactory,
    QuerySettingsQualityFactory,
    QuerySettingsVariantPrioFactory,
    ResultRowFactory,
    ResultSetFactory,
    SampleGenotypeChoiceFactory,
)


class TestCaseGenotypeChoice(TestCase):

    def test_values(self):
        self.assertEqual(
            [
                "any",
                "ref",
                "het",
                "hom",
                "non-hom",
                "variant",
                "comphet_index",
                "recessive_index",
                "recessive_parent",
            ],
            GenotypeChoice.values(),
        )


class TestSampleGenotypeChoice(TestCase):

    def test_values(self):
        SampleGenotypeChoiceFactory()


class TestQueryPresetsSet(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsSet.objects.count(), 0)
        QueryPresetsSetFactory()
        self.assertEqual(QueryPresetsSet.objects.count(), 1)

    def test_str(self):
        querypresetsset = QueryPresetsSetFactory()
        self.assertEqual(
            f"QueryPresetsSet '{querypresetsset.sodar_uuid}'",
            querypresetsset.__str__(),
        )


class TestQueryPresetsQuality(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsQuality.objects.count(), 0)
        QueryPresetsQualityFactory()
        self.assertEqual(QueryPresetsQuality.objects.count(), 1)

    def test_str(self):
        querypresetsquality = QueryPresetsQualityFactory()
        self.assertEqual(
            f"QueryPresetsQuality '{querypresetsquality.sodar_uuid}'",
            querypresetsquality.__str__(),
        )


class TestQueryPresetsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsFrequency.objects.count(), 0)
        QueryPresetsFrequencyFactory()
        self.assertEqual(QueryPresetsFrequency.objects.count(), 1)

    def test_str(self):
        querypresetsfrequency = QueryPresetsFrequencyFactory()
        self.assertEqual(
            f"QueryPresetsFrequency '{querypresetsfrequency.sodar_uuid}'",
            querypresetsfrequency.__str__(),
        )


class TestQueryPresetsConsequence(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsConsequence.objects.count(), 0)
        QueryPresetsConsequenceFactory()
        self.assertEqual(QueryPresetsConsequence.objects.count(), 1)

    def test_str(self):
        querypresetsconsequence = QueryPresetsConsequenceFactory()
        self.assertEqual(
            f"QueryPresetsConsequence '{querypresetsconsequence.sodar_uuid}'",
            querypresetsconsequence.__str__(),
        )


class TestQueryPresetsLocus(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsLocus.objects.count(), 0)
        QueryPresetsLocusFactory()
        self.assertEqual(QueryPresetsLocus.objects.count(), 1)

    def test_str(self):
        querypresetslocus = QueryPresetsLocusFactory()
        self.assertEqual(
            f"QueryPresetsLocus '{querypresetslocus.sodar_uuid}'",
            querypresetslocus.__str__(),
        )


class TestQueryPresetsPhenotypePrio(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsPhenotypePrio.objects.count(), 0)
        QueryPresetsPhenotypePrioFactory()
        self.assertEqual(QueryPresetsPhenotypePrio.objects.count(), 1)

    def test_str(self):
        querypresetsphenotypeprio = QueryPresetsPhenotypePrioFactory()
        self.assertEqual(
            f"QueryPresetsPhenotypePrio '{querypresetsphenotypeprio.sodar_uuid}'",
            querypresetsphenotypeprio.__str__(),
        )


class TestQueryPresetsVariantPrio(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsVariantPrio.objects.count(), 0)
        QueryPresetsVariantPrioFactory()
        self.assertEqual(QueryPresetsVariantPrio.objects.count(), 1)

    def test_str(self):
        querypresetsvariantprio = QueryPresetsVariantPrioFactory()
        self.assertEqual(
            f"QueryPresetsVariantPrio '{querypresetsvariantprio.sodar_uuid}'",
            querypresetsvariantprio.__str__(),
        )


class TestQueryPresetsClinvar(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsClinvar.objects.count(), 0)
        QueryPresetsClinvarFactory()
        self.assertEqual(QueryPresetsClinvar.objects.count(), 1)

    def test_str(self):
        querypresetsclinvar = QueryPresetsClinvarFactory()
        self.assertEqual(
            f"QueryPresetsClinvar '{querypresetsclinvar.sodar_uuid}'",
            querypresetsclinvar.__str__(),
        )


class TestQueryPresetsColumns(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsColumns.objects.count(), 0)
        QueryPresetsColumnsFactory()
        self.assertEqual(QueryPresetsColumns.objects.count(), 1)

    def test_str(self):
        querypresetscolumns = QueryPresetsColumnsFactory()
        self.assertEqual(
            f"QueryPresetsColumns '{querypresetscolumns.sodar_uuid}'",
            querypresetscolumns.__str__(),
        )


class TestQuerySettings(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettings.objects.count(), 0)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 0)
        QuerySettingsFactory()
        self.assertEqual(QuerySettings.objects.count(), 1)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        querysettings = QuerySettingsFactory()
        self.assertEqual(
            f"QuerySettings '{querysettings.sodar_uuid}'",
            querysettings.__str__(),
        )


class TestQuerySettingsGenotype(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsGenotype.objects.count(), 0)
        QuerySettingsGenotypeFactory()
        self.assertEqual(QuerySettingsGenotype.objects.count(), 1)

    def test_str(self):
        genotype = QuerySettingsGenotypeFactory()
        self.assertEqual(
            f"QuerySettingsGenotype '{genotype.sodar_uuid}'",
            genotype.__str__(),
        )


class TestQuerySettingsQuality(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsQuality.objects.count(), 0)
        QuerySettingsQualityFactory()
        self.assertEqual(QuerySettingsQuality.objects.count(), 1)

    def test_str(self):
        quality = QuerySettingsQualityFactory()
        self.assertEqual(
            f"QuerySettingsQuality '{quality.sodar_uuid}'",
            quality.__str__(),
        )


class TestQuerySettingsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsFrequency.objects.count(), 0)
        QuerySettingsFrequencyFactory()
        self.assertEqual(QuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        frequency = QuerySettingsFrequencyFactory()
        self.assertEqual(
            f"QuerySettingsFrequency '{frequency.sodar_uuid}'",
            frequency.__str__(),
        )


class TestQuerySettingsConsequence(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsConsequence.objects.count(), 0)
        QuerySettingsConsequenceFactory()
        self.assertEqual(QuerySettingsConsequence.objects.count(), 1)

    def test_str(self):
        consequence = QuerySettingsConsequenceFactory()
        self.assertEqual(
            f"QuerySettingsConsequence '{consequence.sodar_uuid}'",
            consequence.__str__(),
        )


class TestQuerySettingsLocus(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsLocus.objects.count(), 0)
        QuerySettingsLocusFactory()
        self.assertEqual(QuerySettingsLocus.objects.count(), 1)

    def test_str(self):
        locus = QuerySettingsLocusFactory()
        self.assertEqual(
            f"QuerySettingsLocus '{locus.sodar_uuid}'",
            locus.__str__(),
        )


class TestQuerySettingsPhenotypePrio(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsPhenotypePrio.objects.count(), 0)
        QuerySettingsPhenotypePrioFactory()
        self.assertEqual(QuerySettingsPhenotypePrio.objects.count(), 1)

    def test_str(self):
        phenotypeprio = QuerySettingsPhenotypePrioFactory()
        self.assertEqual(
            f"QuerySettingsPhenotypePrio '{phenotypeprio.sodar_uuid}'",
            phenotypeprio.__str__(),
        )


class TestQuerySettingsVariantPrio(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsVariantPrio.objects.count(), 0)
        QuerySettingsVariantPrioFactory()
        self.assertEqual(QuerySettingsVariantPrio.objects.count(), 1)

    def test_str(self):
        variantprio = QuerySettingsVariantPrioFactory()
        self.assertEqual(
            f"QuerySettingsVariantPrio '{variantprio.sodar_uuid}'",
            variantprio.__str__(),
        )


class TestQuerySettingsClinvar(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsClinvar.objects.count(), 0)
        QuerySettingsClinvarFactory()
        self.assertEqual(QuerySettingsClinvar.objects.count(), 1)

    def test_str(self):
        clinvar = QuerySettingsClinvarFactory()
        self.assertEqual(
            f"QuerySettingsClinvar '{clinvar.sodar_uuid}'",
            clinvar.__str__(),
        )


class TestQuery(TestCase):

    def test_create(self):
        self.assertEqual(Query.objects.count(), 0)
        QueryFactory()
        self.assertEqual(Query.objects.count(), 1)

    def test_property_case(self):
        query = QueryFactory()
        self.assertEqual(
            query.session.caseanalysis.case.pk,
            query.case.pk,
        )

    def test_str(self):
        query = QueryFactory()
        self.assertEqual(
            f"Query '{query.sodar_uuid}'",
            query.__str__(),
        )


class TestQueryColumnsConfig(TestCase):

    def test_create(self):
        self.assertEqual(QueryColumnsConfig.objects.count(), 0)
        QueryColumnsConfigFactory()
        self.assertEqual(QueryColumnsConfig.objects.count(), 1)

    def test_str(self):
        columnsconfig = QueryColumnsConfigFactory()
        self.assertEqual(
            f"QueryColumnsConfig '{columnsconfig.sodar_uuid}'",
            columnsconfig.__str__(),
        )


class TestQueryExecution(TestCase):

    def test_create(self):
        self.assertEqual(QueryExecution.objects.count(), 0)
        QueryExecutionFactory()
        self.assertEqual(QueryExecution.objects.count(), 1)

    def test_property_case(self):
        queryexecution = QueryExecutionFactory()
        self.assertEqual(
            queryexecution.query.session.caseanalysis.case.pk,
            queryexecution.case.pk,
        )

    def test_str(self):
        queryexecution = QueryExecutionFactory()
        self.assertEqual(
            f"QueryExecution '{queryexecution.sodar_uuid}'",
            queryexecution.__str__(),
        )


class TestResultSet(TestCase):

    def test_create(self):
        self.assertEqual(ResultSet.objects.count(), 0)
        ResultSetFactory()
        self.assertEqual(ResultSet.objects.count(), 1)

    def test_property_case(self):
        resultset = ResultSetFactory()
        self.assertEqual(
            resultset.queryexecution.query.session.caseanalysis.case.pk,
            resultset.case.pk,
        )

    def test_get_absolute_url(self):
        resultset = ResultSetFactory()
        self.assertEqual(
            (f"/seqvars/api/resultset/{resultset.case.sodar_uuid}/" f"{resultset.sodar_uuid}/"),
            resultset.get_absolute_url(),
        )

    def test_str(self):
        resultset = ResultSetFactory()
        self.assertEqual(
            f"ResultSet '{resultset.sodar_uuid}'",
            resultset.__str__(),
        )


class TestResultRow(TestCase):

    def test_create(self):
        self.assertEqual(ResultRow.objects.count(), 0)
        ResultRowFactory()
        self.assertEqual(ResultRow.objects.count(), 1)

    def test_str(self):
        seqvarresultrow = ResultRowFactory()
        self.assertEqual(
            (
                f"ResultRow '{seqvarresultrow.sodar_uuid}' '{seqvarresultrow.release}-"
                f"{seqvarresultrow.chromosome}-{seqvarresultrow.start}-"
                f"{seqvarresultrow.reference}-{seqvarresultrow.alternative}'"
            ),
            seqvarresultrow.__str__(),
        )
