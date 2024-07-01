from django.forms import model_to_dict
from freezegun import freeze_time
from test_plus import TestCase

from seqvars.serializers import (
    PredefinedQuerySerializer,
    QueryColumnsConfigSerializer,
    QueryDetailsSerializer,
    QueryExecutionDetailsSerializer,
    QueryExecutionSerializer,
    QueryPresetsClinvarSerializer,
    QueryPresetsColumnsSerializer,
    QueryPresetsConsequenceSerializer,
    QueryPresetsFrequencySerializer,
    QueryPresetsLocusSerializer,
    QueryPresetsPhenotypePrioSerializer,
    QueryPresetsQualitySerializer,
    QueryPresetsSetDetailsSerializer,
    QueryPresetsSetSerializer,
    QueryPresetsSetVersionDetailsSerializer,
    QueryPresetsSetVersionSerializer,
    QueryPresetsVariantPrioSerializer,
    QuerySerializer,
    QuerySettingsClinvarSerializer,
    QuerySettingsConsequenceSerializer,
    QuerySettingsDetailsSerializer,
    QuerySettingsFrequencySerializer,
    QuerySettingsGenotypeSerializer,
    QuerySettingsLocusSerializer,
    QuerySettingsPhenotypePrioSerializer,
    QuerySettingsQualitySerializer,
    QuerySettingsSerializer,
    QuerySettingsVariantPrioSerializer,
    ResultRowSerializer,
    ResultSetSerializer,
)
from seqvars.tests.factories import (
    PredefinedQueryFactory,
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
    QueryPresetsSetVersionFactory,
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
)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsQualitySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsquality = QueryPresetsQualityFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsQualitySerializer(self.querypresetsquality)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # QueryPresetsQuality
            "filter_active",
            "min_dp_het",
            "min_dp_hom",
            "min_ab_het",
            "min_gq",
            "min_ad",
            "max_ad",
        ]
        expected = model_to_dict(
            self.querypresetsquality,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetsquality.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsfrequency = QueryPresetsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsFrequencySerializer(self.querypresetsfrequency)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # FrequencySettingsBase
            "gnomad_exomes_enabled",
            "gnomad_exomes_frequency",
            "gnomad_exomes_homozygous",
            "gnomad_exomes_heterozygous",
            "gnomad_exomes_hemizygous",
            "gnomad_genomes_enabled",
            "gnomad_genomes_frequency",
            "gnomad_genomes_homozygous",
            "gnomad_genomes_heterozygous",
            "gnomad_genomes_hemizygous",
            "helixmtdb_enabled",
            "helixmtdb_heteroplasmic",
            "helixmtdb_homoplasmic",
            "helixmtdb_frequency",
            "inhouse_enabled",
            "inhouse_carriers",
            "inhouse_homozygous",
            "inhouse_heterozygous",
            "inhouse_hemizygous",
        ]
        expected = model_to_dict(
            self.querypresetsfrequency,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetsfrequency.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsConsequenceSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsconsequence = QueryPresetsConsequenceFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsConsequenceSerializer(self.querypresetsconsequence)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # ConsequenceSettingsBase
            "variant_types",
            "transcript_types",
            "variant_consequences",
            "max_distance_to_exon",
        ]
        expected = model_to_dict(
            self.querypresetsconsequence,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetsconsequence.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the enums from pydantic fields to their string value.
        expected["transcript_types"] = [x.value for x in expected["transcript_types"]]
        expected["variant_consequences"] = [x.value for x in expected["variant_consequences"]]
        expected["variant_types"] = [x.value for x in expected["variant_types"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsLocusSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetslocus = QueryPresetsLocusFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsLocusSerializer(self.querypresetslocus)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # LocusSettingsBase
            "genes",
            "gene_panels",
            "genome_regions",
        ]
        expected = model_to_dict(
            self.querypresetslocus,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetslocus.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["gene_panels"] = [x.model_dump(mode="json") for x in expected["gene_panels"]]
        expected["genes"] = [x.model_dump(mode="json") for x in expected["genes"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsPhenotypePrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsphenotypeprio = QueryPresetsPhenotypePrioFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsPhenotypePrioSerializer(self.querypresetsphenotypeprio)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # PhenotypePrioSettingsBase
            "phenotype_prio_enabled",
            "phenotype_prio_algorithm",
            "terms",
        ]
        expected = model_to_dict(
            self.querypresetsphenotypeprio,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetsphenotypeprio.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["terms"] = [x.model_dump(mode="json") for x in expected["terms"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsVariantPrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsvariantprio = QueryPresetsVariantPrioFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsVariantPrioSerializer(self.querypresetsvariantprio)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # VariantPrioSettingsBase
            "variant_prio_enabled",
            "services",
        ]
        expected = model_to_dict(
            self.querypresetsvariantprio,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetsvariantprio.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["services"] = [x.model_dump(mode="json") for x in expected["services"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsClinvarSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsclinvar = QueryPresetsClinvarFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsClinvarSerializer(self.querypresetsclinvar)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # ClinvarSettingsBase
            "clinvar_presence_required",
            "clinvar_germline_aggregate_description",
            "allow_conflicting_interpretations",
        ]
        expected = model_to_dict(
            self.querypresetsclinvar,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetsclinvar.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["clinvar_germline_aggregate_description"] = [
            x.value for x in expected["clinvar_germline_aggregate_description"]
        ]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsColumnsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetscolumns = QueryPresetsColumnsFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsColumnsSerializer(self.querypresetscolumns)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # ColumnsSettingsBase
            "column_settings",
        ]
        expected = model_to_dict(
            self.querypresetscolumns,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.querypresetscolumns.presetssetversion.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["column_settings"] = [
            x.model_dump(mode="json") for x in expected["column_settings"]
        ]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestPredefinedQuerySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = QueryPresetsSetFactory()
        self.querypresetssetversion = QueryPresetsSetVersionFactory(presetsset=self.querypresetsset)
        self.predefinedquery = PredefinedQueryFactory(presetssetversion=self.querypresetssetversion)
        self.predefinedquery.quality = QueryPresetsQualityFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.frequency = QueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.consequence = QueryPresetsConsequenceFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.locus = QueryPresetsLocusFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.phenotypeprio = QueryPresetsPhenotypePrioFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.variantprio = QueryPresetsVariantPrioFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.clinvar = QueryPresetsClinvarFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.columns = QueryPresetsColumnsFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = PredefinedQuerySerializer(self.predefinedquery)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsBase
            "presetssetversion",
            # ColumnsSettingsBase
            "included_in_sop",
            "quality",
            "frequency",
            "consequence",
            "locus",
            "phenotypeprio",
            "variantprio",
            "clinvar",
            "columns",
        ]
        expected = model_to_dict(
            self.predefinedquery,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetssetversion"] = self.predefinedquery.presetssetversion.sodar_uuid
        expected["quality"] = self.predefinedquery.quality.sodar_uuid
        expected["frequency"] = self.predefinedquery.frequency.sodar_uuid
        expected["consequence"] = self.predefinedquery.consequence.sodar_uuid
        expected["locus"] = self.predefinedquery.locus.sodar_uuid
        expected["phenotypeprio"] = self.predefinedquery.phenotypeprio.sodar_uuid
        expected["variantprio"] = self.predefinedquery.variantprio.sodar_uuid
        expected["clinvar"] = self.predefinedquery.clinvar.sodar_uuid
        expected["columns"] = self.predefinedquery.columns.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = QueryPresetsSetFactory()

    def test_serialize_existing(self):
        serializer = QueryPresetsSetSerializer(self.querypresetsset)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsSet
            "project",
        ]
        expected = model_to_dict(
            self.querypresetsset,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["project"] = self.querypresetsset.project.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = QueryPresetsSetFactory()
        self.querypresetssetversion = QueryPresetsSetVersionFactory(presetsset=self.querypresetsset)
        self.querypresetsfrequency = QueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = QueryPresetsSetDetailsSerializer(self.querypresetsset)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # QueryPresetsSet
            "project",
            "versions",
        ]
        expected = model_to_dict(
            self.querypresetsset,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["project"] = self.querypresetsset.project.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Update the deeply nested related objects.
        expected["versions"] = list(
            map(
                lambda elem: dict(QueryPresetsSetVersionDetailsSerializer(elem).data),
                self.querypresetsset.versions.all(),
            )
        )

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetVersionSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querypresetssetversion = QueryPresetsSetVersionFactory()
        self.querypresetsfrequency = QueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = QueryPresetsSetVersionSerializer(self.querypresetssetversion)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QueryPresetsSetVersion
            "presetsset",
            "version_major",
            "version_minor",
            "status",
            "signed_off_by",
        ]
        expected = model_to_dict(
            self.querypresetssetversion,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetsset"] = self.querypresetssetversion.presetsset.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetVersionDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querypresetssetversion = QueryPresetsSetVersionFactory()
        self.querypresetsfrequency = QueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = QueryPresetsSetVersionDetailsSerializer(self.querypresetssetversion)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QueryPresetsSetVersion
            "presetsset",
            "version_major",
            "version_minor",
            "status",
            "signed_off_by",
            # (only in details serializer)
            "querypresetsfrequency_set",
            "querypresetsvariantprio_set",
            "querypresetsclinvar_set",
            "querypresetscolumns_set",
            "querypresetslocus_set",
            "querypresetsconsequence_set",
            "querypresetsquality_set",
            "querypresetsphenotypeprio_set",
            "predefinedquery_set",
        ]
        expected = model_to_dict(
            self.querypresetssetversion,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["presetsset"] = dict(
            QueryPresetsSetSerializer(self.querypresetssetversion.presetsset).data
        )
        # We add the missing "querypresetsfrequency_set".
        expected["querypresetsfrequency_set"] = [
            QueryPresetsFrequencySerializer(self.querypresetsfrequency).data
        ]
        expected["querypresetsvariantprio_set"] = []
        expected["querypresetsclinvar_set"] = []
        expected["querypresetscolumns_set"] = []
        expected["querypresetslocus_set"] = []
        expected["querypresetsconsequence_set"] = []
        expected["querypresetsquality_set"] = []
        expected["querypresetsphenotypeprio_set"] = []
        expected["predefinedquery_set"] = []
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querysettings = QuerySettingsFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsSerializer(self.querysettings)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettings
            "session",
            # "presetssetversion",
            "genotype",
            "quality",
            "consequence",
            "locus",
            "frequency",
            "phenotypeprio",
            "variantprio",
            "clinvar",
        ]
        expected = model_to_dict(
            self.querysettings,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["session"] = self.querysettings.session.sodar_uuid
        # expected["presetssetversion"] = self.querysettings.presetssetversion.sodar_uuid  # is None
        expected["genotype"] = self.querysettings.genotype.sodar_uuid
        expected["quality"] = self.querysettings.quality.sodar_uuid
        expected["consequence"] = self.querysettings.consequence.sodar_uuid
        expected["locus"] = self.querysettings.locus.sodar_uuid
        expected["frequency"] = self.querysettings.frequency.sodar_uuid
        expected["phenotypeprio"] = self.querysettings.phenotypeprio.sodar_uuid
        expected["variantprio"] = self.querysettings.variantprio.sodar_uuid
        expected["clinvar"] = self.querysettings.clinvar.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querysettings = QuerySettingsFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsDetailsSerializer(self.querysettings)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettings
            "session",
            # "presetssetversion",
            "genotype",
            "quality",
            "consequence",
            "locus",
            "frequency",
            "phenotypeprio",
            "variantprio",
            "clinvar",
        ]
        expected = model_to_dict(
            self.querysettings,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["session"] = self.querysettings.session.sodar_uuid
        # expected["presetssetversion"] = self.querysettings.presetssetversion.sodar_uuid  # is None
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # The same is true for the related one-to-one fields.
        expected["genotype"] = QuerySettingsGenotypeSerializer(self.querysettings.genotype).data
        expected["quality"] = QuerySettingsQualitySerializer(self.querysettings.quality).data
        expected["consequence"] = QuerySettingsConsequenceSerializer(
            self.querysettings.consequence
        ).data
        expected["locus"] = QuerySettingsLocusSerializer(self.querysettings.locus).data
        expected["frequency"] = QuerySettingsFrequencySerializer(self.querysettings.frequency).data
        expected["phenotypeprio"] = QuerySettingsPhenotypePrioSerializer(
            self.querysettings.phenotypeprio
        ).data
        expected["variantprio"] = QuerySettingsVariantPrioSerializer(
            self.querysettings.variantprio
        ).data
        expected["clinvar"] = QuerySettingsClinvarSerializer(self.querysettings.clinvar).data

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsGenotypeSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.genotype = QuerySettingsGenotypeFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsGenotypeSerializer(self.genotype)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # GenotypeSettingsBase
            "sample_genotype_choices",
        ]
        expected = model_to_dict(
            self.genotype,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.genotype.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["sample_genotype_choices"] = [
            x.model_dump(mode="json") for x in expected["sample_genotype_choices"]
        ]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsQualitySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.quality = QuerySettingsQualityFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsQualitySerializer(self.quality)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # QualitySettingsBase
            "sample_quality_filters",
        ]
        expected = model_to_dict(
            self.quality,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.quality.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["sample_quality_filters"] = [
            x.model_dump(mode="json") for x in expected["sample_quality_filters"]
        ]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsConsequenceSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.consequence = QuerySettingsConsequenceFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsConsequenceSerializer(self.consequence)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # ConsequenceSettingsBase
            "variant_types",
            "transcript_types",
            "variant_consequences",
            "max_distance_to_exon",
        ]
        expected = model_to_dict(
            self.consequence,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.consequence.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsLocusSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.locus = QuerySettingsLocusFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsLocusSerializer(self.locus)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # LocusSettingsBase
            "genes",
            "gene_panels",
            "genome_regions",
        ]
        expected = model_to_dict(
            self.locus,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.locus.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["genes"] = [x.model_dump(mode="json") for x in expected["genes"]]
        expected["gene_panels"] = [x.model_dump(mode="json") for x in expected["gene_panels"]]
        expected["genome_regions"] = [x.model_dump(mode="json") for x in expected["genome_regions"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.frequency = QuerySettingsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsFrequencySerializer(self.frequency)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # FrequencySettingsBase
            "gnomad_exomes_enabled",
            "gnomad_exomes_frequency",
            "gnomad_exomes_homozygous",
            "gnomad_exomes_heterozygous",
            "gnomad_exomes_hemizygous",
            "gnomad_genomes_enabled",
            "gnomad_genomes_frequency",
            "gnomad_genomes_homozygous",
            "gnomad_genomes_heterozygous",
            "gnomad_genomes_hemizygous",
            "helixmtdb_enabled",
            "helixmtdb_heteroplasmic",
            "helixmtdb_homoplasmic",
            "helixmtdb_frequency",
            "inhouse_enabled",
            "inhouse_carriers",
            "inhouse_homozygous",
            "inhouse_heterozygous",
            "inhouse_hemizygous",
        ]
        expected = model_to_dict(
            self.frequency,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.frequency.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsPhenotypePrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.phenotypeprio = QuerySettingsPhenotypePrioFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsPhenotypePrioSerializer(self.phenotypeprio)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # PhenotypePrioSettingsBase
            "phenotype_prio_enabled",
            "phenotype_prio_algorithm",
            "terms",
        ]
        expected = model_to_dict(
            self.phenotypeprio,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.phenotypeprio.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["terms"] = [x.model_dump(mode="json") for x in expected["terms"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsVariantPrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.variantprio = QuerySettingsVariantPrioFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsVariantPrioSerializer(self.variantprio)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # VariantPrioSettingsBase
            "variant_prio_enabled",
            "services",
        ]
        expected = model_to_dict(
            self.variantprio,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.variantprio.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Map the pydantic fields to their JSON value.
        expected["services"] = [x.model_dump(mode="json") for x in expected["services"]]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsClinvarSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.clinvar = QuerySettingsClinvarFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsClinvarSerializer(self.clinvar)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QuerySettingsBase
            "querysettings",
            # ClinvarSettingsBase
            "clinvar_presence_required",
            "clinvar_germline_aggregate_description",
            "allow_conflicting_interpretations",
        ]
        expected = model_to_dict(
            self.clinvar,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.clinvar.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.query = QueryFactory()
        self.columnsconfig = QueryColumnsConfigFactory(query=self.query)
        self.query.refresh_from_db()

    def test_serialize_existing(self):
        serializer = QuerySerializer(self.query)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # Query
            "rank",
            "label",
            "session",
            "settings",
            "columnsconfig",
        ]
        expected = model_to_dict(
            self.query,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["session"] = self.query.session.sodar_uuid
        expected["settings"] = self.query.settings.sodar_uuid
        expected["columnsconfig"] = self.query.columnsconfig.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.query = QueryFactory()
        self.columnsconfig = QueryColumnsConfigFactory(query=self.query)
        self.query.refresh_from_db()

    def test_serialize_existing(self):
        serializer = QueryDetailsSerializer(self.query)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # Query
            "rank",
            "label",
            "session",
            "settings",
            "columnsconfig",
        ]
        expected = model_to_dict(
            self.query,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["sodar_uuid"] = str(self.query.sodar_uuid)
        expected["session"] = self.query.session.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # The same is true for settings.
        expected["settings"] = QuerySettingsDetailsSerializer(self.query.settings).data
        expected["columnsconfig"] = QueryColumnsConfigSerializer(self.query.columnsconfig).data

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryExecutionSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.queryexecution = QueryExecutionFactory()

    def test_serialize_existing(self):
        serializer = QueryExecutionSerializer(self.queryexecution)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QueryExecution
            "state",
            "complete_percent",
            "start_time",
            "end_time",
            "elapsed_seconds",
            "query",
            "querysettings",
        ]
        expected = model_to_dict(
            self.queryexecution,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["query"] = self.queryexecution.query.sodar_uuid
        expected["querysettings"] = self.queryexecution.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # We convert the ``FakeDateTime`` objects into strings
        expected["start_time"] = expected["start_time"].isoformat().replace("+00:00", "Z")
        expected["end_time"] = expected["end_time"].isoformat().replace("+00:00", "Z")
        # ... and also fix the "elapsed_seconds" value.
        expected["elapsed_seconds"] = expected["elapsed_seconds"]

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQueryExecutionDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.queryexecution = QueryExecutionFactory()

    def test_serialize_existing(self):
        serializer = QueryExecutionDetailsSerializer(self.queryexecution)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # QueryExecution
            "state",
            "complete_percent",
            "start_time",
            "end_time",
            "elapsed_seconds",
            "query",
            "querysettings",
        ]
        expected = model_to_dict(
            self.queryexecution,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["query"] = self.queryexecution.query.sodar_uuid
        # We render the query settings as a dictionary.
        expected["querysettings"] = dict(
            QuerySettingsDetailsSerializer(self.queryexecution.querysettings).data
        )
        expected["querysettings"]["frequency"] = dict(expected["querysettings"]["frequency"])
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # We convert the ``FakeDateTime`` objects into strings
        expected["start_time"] = expected["start_time"].isoformat().replace("+00:00", "Z")
        expected["end_time"] = expected["end_time"].isoformat().replace("+00:00", "Z")
        # ... and also fix the "elapsed_seconds" value.
        expected["elapsed_seconds"] = float(expected["elapsed_seconds"])

        self.assertEqual(set(serializer.data.keys()), set(fields))
        # Convert OrderedDict in result to dict.
        result = dict(serializer.data)
        result["querysettings"] = dict(result["querysettings"])
        self.assertDictEqual(result, expected)


@freeze_time("2012-01-14 12:00:01")
class TestResultSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.resultset = ResultSetFactory()

    def test_serialize_existing(self):
        serializer = ResultSetSerializer(self.resultset)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # ResultSet
            "queryexecution",
            "datasource_infos",
        ]
        expected = model_to_dict(
            self.resultset,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["queryexecution"] = self.resultset.queryexecution.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Create JSON dump of datasource_infos.
        expected["datasource_infos"] = self.resultset.datasource_infos.model_dump(mode="json")

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestResultRowSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarresultrow = ResultRowFactory()

    def test_serialize_existing(self):
        serializer = ResultRowSerializer(self.seqvarresultrow)
        fields = [
            "sodar_uuid",
            "resultset",
            "release",
            "chromosome",
            "chromosome_no",
            "start",
            "stop",
            "reference",
            "alternative",
            "payload",
        ]
        expected = model_to_dict(
            self.seqvarresultrow,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["resultset"] = self.seqvarresultrow.resultset.sodar_uuid
        # Create JSON dump of payload.
        expected["payload"] = self.seqvarresultrow.payload.model_dump(mode="json")

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)
