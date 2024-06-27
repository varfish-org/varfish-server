from django.forms import model_to_dict
from freezegun import freeze_time
from test_plus import TestCase

from seqvars.serializers import (
    QueryDetailsSerializer,
    QueryExecutionDetailsSerializer,
    QueryExecutionSerializer,
    QueryPresetsFrequencySerializer,
    QueryPresetsSetDetailsSerializer,
    QueryPresetsSetSerializer,
    QuerySerializer,
    QuerySettingsDetailsSerializer,
    QuerySettingsFrequencySerializer,
    QuerySettingsSerializer,
    ResultRowSerializer,
    ResultSetSerializer,
)
from seqvars.tests.factories import (
    QueryExecutionFactory,
    QueryFactory,
    QueryPresetsFrequencyFactory,
    QueryPresetsSetFactory,
    QuerySettingsFactory,
    QuerySettingsFrequencyFactory,
    ResultRowFactory,
    ResultSetFactory,
)


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
            "presetsset",
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
        expected["presetsset"] = self.querypresetsfrequency.presetsset.sodar_uuid
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
class TestQueryPresetsSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.querypresetsset = QueryPresetsSetFactory()
        self.querypresetsfrequency = QueryPresetsFrequencyFactory(presetsset=self.querypresetsset)

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
        self.maxDiff = None
        self.querypresetsset = QueryPresetsSetFactory()
        self.querypresetsfrequency = QueryPresetsFrequencyFactory(presetsset=self.querypresetsset)

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
            # (only in details serializer)
            "querypresetsfrequency_set",
        ]
        expected = model_to_dict(
            self.querypresetsset,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["project"] = self.querypresetsset.project.sodar_uuid
        # We add the missing "querypresetsfrequency_set".
        expected["querypresetsfrequency_set"] = [
            QueryPresetsFrequencySerializer(self.querypresetsfrequency).data
        ]
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
            "querysettingsfrequency",
        ]
        expected = model_to_dict(
            self.querysettings,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["session"] = self.querysettings.session.sodar_uuid
        expected["querysettingsfrequency"] = self.querysettings.querysettingsfrequency.sodar_uuid
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
            "querysettingsfrequency",
        ]
        expected = model_to_dict(
            self.querysettings,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["session"] = self.querysettings.session.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # The same is true for the related one-to-one fields.
        expected["querysettingsfrequency"] = QuerySettingsFrequencySerializer(
            self.querysettings.querysettingsfrequency
        ).data

        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.querysettingsfrequency = QuerySettingsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = QuerySettingsFrequencySerializer(self.querysettingsfrequency)
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
            self.querysettingsfrequency,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["querysettings"] = self.querysettingsfrequency.querysettings.sodar_uuid
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
            "settings_buffer",
        ]
        expected = model_to_dict(
            self.query,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["session"] = self.query.session.sodar_uuid
        expected["settings_buffer"] = self.query.settings_buffer.sodar_uuid
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
            "settings_buffer",
        ]
        expected = model_to_dict(
            self.query,
            fields=fields,
        )
        # We replace the related objects with their UUIDs.
        expected["session"] = self.query.session.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # The same is true for settings_buffer.
        expected["settings_buffer"] = QuerySettingsDetailsSerializer(
            self.query.settings_buffer
        ).data

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
        expected["querysettings"]["querysettingsfrequency"] = dict(
            expected["querysettings"]["querysettingsfrequency"]
        )
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
