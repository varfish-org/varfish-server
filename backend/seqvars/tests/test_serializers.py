from django.forms import model_to_dict
from freezegun import freeze_time
from test_plus import TestCase

from seqvars.serializers import (
    SeqvarsPredefinedQuerySerializer,
    SeqvarsQueryColumnsConfigSerializer,
    SeqvarsQueryDetailsSerializer,
    SeqvarsQueryExecutionDetailsSerializer,
    SeqvarsQueryExecutionSerializer,
    SeqvarsQueryPresetsClinvarSerializer,
    SeqvarsQueryPresetsColumnsSerializer,
    SeqvarsQueryPresetsConsequenceSerializer,
    SeqvarsQueryPresetsFrequencySerializer,
    SeqvarsQueryPresetsLocusSerializer,
    SeqvarsQueryPresetsPhenotypePrioSerializer,
    SeqvarsQueryPresetsQualitySerializer,
    SeqvarsQueryPresetsSetDetailsSerializer,
    SeqvarsQueryPresetsSetSerializer,
    SeqvarsQueryPresetsSetVersionDetailsSerializer,
    SeqvarsQueryPresetsSetVersionSerializer,
    SeqvarsQueryPresetsVariantPrioSerializer,
    SeqvarsQuerySerializer,
    SeqvarsQuerySettingsClinvarSerializer,
    SeqvarsQuerySettingsConsequenceSerializer,
    SeqvarsQuerySettingsDetailsSerializer,
    SeqvarsQuerySettingsFrequencySerializer,
    SeqvarsQuerySettingsGenotypeSerializer,
    SeqvarsQuerySettingsLocusSerializer,
    SeqvarsQuerySettingsPhenotypePrioSerializer,
    SeqvarsQuerySettingsQualitySerializer,
    SeqvarsQuerySettingsSerializer,
    SeqvarsQuerySettingsVariantPrioSerializer,
    SeqvarsResultRowSerializer,
    SeqvarsResultSetSerializer,
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


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarsQueryPresetsQualitySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsquality = SeqvarsQueryPresetsQualityFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsQualitySerializer(self.querypresetsquality)
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
class TestSeqvarsQueryPresetsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsFrequencySerializer(self.querypresetsfrequency)
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
class TestSeqvarsQueryPresetsConsequenceSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsconsequence = SeqvarsQueryPresetsConsequenceFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsConsequenceSerializer(self.querypresetsconsequence)
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
class TestSeqvarsQueryPresetsLocusSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetslocus = SeqvarsQueryPresetsLocusFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsLocusSerializer(self.querypresetslocus)
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
class TestSeqvarsQueryPresetsPhenotypePrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsphenotypeprio = SeqvarsQueryPresetsPhenotypePrioFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsPhenotypePrioSerializer(self.querypresetsphenotypeprio)
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
class TestSeqvarsQueryPresetsVariantPrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsvariantprio = SeqvarsQueryPresetsVariantPrioFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsVariantPrioSerializer(self.querypresetsvariantprio)
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
class TestSeqvarsQueryPresetsClinvarSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsclinvar = SeqvarsQueryPresetsClinvarFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsClinvarSerializer(self.querypresetsclinvar)
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
class TestSeqvarsQueryPresetsColumnsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetscolumns = SeqvarsQueryPresetsColumnsFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsColumnsSerializer(self.querypresetscolumns)
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
class TestSeqvarsPredefinedQuerySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory()
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.predefinedquery = SeqvarsPredefinedQueryFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.quality = SeqvarsQueryPresetsQualityFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.frequency = SeqvarsQueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.consequence = SeqvarsQueryPresetsConsequenceFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.locus = SeqvarsQueryPresetsLocusFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.phenotypeprio = SeqvarsQueryPresetsPhenotypePrioFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.variantprio = SeqvarsQueryPresetsVariantPrioFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.clinvar = SeqvarsQueryPresetsClinvarFactory(
            presetssetversion=self.querypresetssetversion
        )
        self.predefinedquery.columns = SeqvarsQueryPresetsColumnsFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = SeqvarsPredefinedQuerySerializer(self.predefinedquery)
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
            "genotype",
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
        # Map the pydantic fields to their JSON value.
        expected["genotype"] = expected["genotype"].model_dump(mode="json")
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
class TestSeqvarsQueryPresetsSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsSetSerializer(self.querypresetsset)
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
class TestSeqvarsQueryPresetsSetDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory()
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsSetDetailsSerializer(self.querypresetsset)
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
                lambda elem: dict(SeqvarsQueryPresetsSetVersionDetailsSerializer(elem).data),
                self.querypresetsset.versions.all(),
            )
        )

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarsQueryPresetsSetVersionSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory()
        self.querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsSetVersionSerializer(self.querypresetssetversion)
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
class TestSeqvarsQueryPresetsSetVersionDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory()
        self.querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_serialize_existing(self):
        serializer = SeqvarsQueryPresetsSetVersionDetailsSerializer(self.querypresetssetversion)
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
            SeqvarsQueryPresetsSetSerializer(self.querypresetssetversion.presetsset).data
        )
        # We add the missing "querypresetsfrequency_set".
        expected["querypresetsfrequency_set"] = [
            SeqvarsQueryPresetsFrequencySerializer(self.querypresetsfrequency).data
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
class TestSeqvarsQuerySettingsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querysettings = SeqvarsQuerySettingsFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsSerializer(self.querysettings)
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
class TestSeqvarsQuerySettingsDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querysettings = SeqvarsQuerySettingsFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsDetailsSerializer(self.querysettings)
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
        expected["genotype"] = SeqvarsQuerySettingsGenotypeSerializer(
            self.querysettings.genotype
        ).data
        expected["quality"] = SeqvarsQuerySettingsQualitySerializer(self.querysettings.quality).data
        expected["consequence"] = SeqvarsQuerySettingsConsequenceSerializer(
            self.querysettings.consequence
        ).data
        expected["locus"] = SeqvarsQuerySettingsLocusSerializer(self.querysettings.locus).data
        expected["frequency"] = SeqvarsQuerySettingsFrequencySerializer(
            self.querysettings.frequency
        ).data
        expected["phenotypeprio"] = SeqvarsQuerySettingsPhenotypePrioSerializer(
            self.querysettings.phenotypeprio
        ).data
        expected["variantprio"] = SeqvarsQuerySettingsVariantPrioSerializer(
            self.querysettings.variantprio
        ).data
        expected["clinvar"] = SeqvarsQuerySettingsClinvarSerializer(self.querysettings.clinvar).data

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarsQuerySettingsGenotypeSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.genotype = SeqvarsQuerySettingsGenotypeFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsGenotypeSerializer(self.genotype)
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
class TestSeqvarsQuerySettingsQualitySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.quality = SeqvarsQuerySettingsQualityFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsQualitySerializer(self.quality)
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
class TestSeqvarsQuerySettingsConsequenceSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.consequence = SeqvarsQuerySettingsConsequenceFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsConsequenceSerializer(self.consequence)
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
class TestSeqvarsQuerySettingsLocusSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.locus = SeqvarsQuerySettingsLocusFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsLocusSerializer(self.locus)
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
class TestSeqvarsQuerySettingsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.frequency = SeqvarsQuerySettingsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsFrequencySerializer(self.frequency)
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
class TestSeqvarsQuerySettingsPhenotypePrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.phenotypeprio = SeqvarsQuerySettingsPhenotypePrioFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsPhenotypePrioSerializer(self.phenotypeprio)
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
class TestSeqvarsQuerySettingsVariantPrioSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.variantprio = SeqvarsQuerySettingsVariantPrioFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsVariantPrioSerializer(self.variantprio)
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
class TestSeqvarsQuerySettingsClinvarSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.clinvar = SeqvarsQuerySettingsClinvarFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySettingsClinvarSerializer(self.clinvar)
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
class TestSeqvarsQuerySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.query = SeqvarsQueryFactory()
        self.columnsconfig = SeqvarsQueryColumnsConfigFactory(query=self.query)
        self.query.refresh_from_db()

    def test_serialize_existing(self):
        serializer = SeqvarsQuerySerializer(self.query)
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
class TestSeqvarsQueryDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.query = SeqvarsQueryFactory()
        self.columnsconfig = SeqvarsQueryColumnsConfigFactory(query=self.query)
        self.query.refresh_from_db()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryDetailsSerializer(self.query)
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
        expected["settings"] = SeqvarsQuerySettingsDetailsSerializer(self.query.settings).data
        expected["columnsconfig"] = SeqvarsQueryColumnsConfigSerializer(
            self.query.columnsconfig
        ).data

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarsQueryExecutionSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.queryexecution = SeqvarsQueryExecutionFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryExecutionSerializer(self.queryexecution)
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
class TestSeqvarsQueryExecutionDetailsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.queryexecution = SeqvarsQueryExecutionFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsQueryExecutionDetailsSerializer(self.queryexecution)
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
            SeqvarsQuerySettingsDetailsSerializer(self.queryexecution.querysettings).data
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
class TestSeqvarsResultSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.resultset = SeqvarsResultSetFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsResultSetSerializer(self.resultset)
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
class TestSeqvarsResultRowSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarresultrow = SeqvarsResultRowFactory()

    def test_serialize_existing(self):
        serializer = SeqvarsResultRowSerializer(self.seqvarresultrow)
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
