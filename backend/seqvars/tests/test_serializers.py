from django.forms import model_to_dict
from freezegun import freeze_time
from test_plus import TestCase

from seqvars.serializers import (
    SeqvarPresetsFrequencySerializer,
    SeqvarQueryExecutionSerializer,
    SeqvarQueryPresetsSetRetrieveSerializer,
    SeqvarQueryPresetsSetSerializer,
    SeqvarQuerySerializer,
    SeqvarQuerySettingsFrequencySerializer,
    SeqvarQuerySettingsSerializer,
    SeqvarResultRowSerializer,
    SeqvarResultSetSerializer,
)
from seqvars.tests.factories import (
    SeqvarPresetsFrequencyFactory,
    SeqvarQueryExecutionFactory,
    SeqvarQueryFactory,
    SeqvarQueryPresetsSetFactory,
    SeqvarQuerySettingsFactory,
    SeqvarQuerySettingsFrequencyFactory,
    SeqvarResultRowFactory,
    SeqvarResultSetFactory,
)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarPresetsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.seqvarquerypresetsfrequency = SeqvarPresetsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = SeqvarPresetsFrequencySerializer(self.seqvarquerypresetsfrequency)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # SeqvarPresetsBase
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
            self.seqvarquerypresetsfrequency,
            fields=fields,
        )
        # We replace the presets set object with its UUID.
        expected["presetsset"] = self.seqvarquerypresetsfrequency.presetsset.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQueryPresetsSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.seqvarquerypresetsset = SeqvarQueryPresetsSetFactory()

    def test_serialize_existing(self):
        serializer = SeqvarQueryPresetsSetSerializer(self.seqvarquerypresetsset)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # SeqvarQueryPresetsSet
            "project",
        ]
        expected = model_to_dict(
            self.seqvarquerypresetsset,
            fields=fields,
        )
        # We replace the project object with its UUID.
        expected["project"] = self.seqvarquerypresetsset.project.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQueryPresetsSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarquerypresetsset = SeqvarQueryPresetsSetFactory()
        self.seqvarpresetsfrequency = SeqvarPresetsFrequencyFactory(
            presetsset=self.seqvarquerypresetsset
        )

    def test_serialize_existing(self):
        serializer = SeqvarQueryPresetsSetRetrieveSerializer(self.seqvarquerypresetsset)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # LabeledSortableBase
            "label",
            "description",
            "rank",
            # SeqvarQueryPresetsSet
            "project",
            # (only in RetrieveSerializer)
            "seqvarpresetsfrequency_set",
        ]
        expected = model_to_dict(
            self.seqvarquerypresetsset,
            fields=fields,
        )
        # We replace the project object with its UUID.
        expected["project"] = self.seqvarquerypresetsset.project.sodar_uuid
        # We add the missing "seqvarpresetsfrequency_set".
        expected["seqvarpresetsfrequency_set"] = [
            SeqvarPresetsFrequencySerializer(self.seqvarpresetsfrequency).data
        ]
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQuerySettingsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarquerysettings = SeqvarQuerySettingsFactory()

    def test_serialize_existing(self):
        serializer = SeqvarQuerySettingsSerializer(self.seqvarquerysettings)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # SeqvarQuerySettings
            "case",
            "seqvarquerysettingsfrequency",
        ]
        expected = model_to_dict(
            self.seqvarquerysettings,
            fields=fields,
        )
        # We replace the case object with its UUID.
        expected["case"] = self.seqvarquerysettings.case.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # The same is true for the related one-to-one fields.
        expected["seqvarquerysettingsfrequency"] = SeqvarQuerySettingsFrequencySerializer(
            self.seqvarquerysettings.seqvarquerysettingsfrequency
        ).data
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQuerySettingsFrequencySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.seqvarquerysettingsfrequency = SeqvarQuerySettingsFrequencyFactory()

    def test_serialize_existing(self):
        serializer = SeqvarQuerySettingsFrequencySerializer(self.seqvarquerysettingsfrequency)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # SeqvarQuerySettingsBase
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
            self.seqvarquerysettingsfrequency,
            fields=fields,
        )
        # We replace the query settings object with its UUID.
        expected["querysettings"] = self.seqvarquerysettingsfrequency.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQuerySerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.seqvarquery = SeqvarQueryFactory()

    def test_serialize_existing(self):
        serializer = SeqvarQuerySerializer(self.seqvarquery)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # SeqvarQuery
            "rank",
            "label",
            "session",
            "settings_buffer",
        ]
        expected = model_to_dict(
            self.seqvarquery,
            fields=fields,
        )
        # We replace the session and settings buffer object with its UUID.
        expected["session"] = self.seqvarquery.session.sodar_uuid
        expected["settings_buffer"] = self.seqvarquery.settings_buffer.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQueryExecutionSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory()

    def test_serialize_existing(self):
        serializer = SeqvarQueryExecutionSerializer(self.seqvarqueryexecution)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # SeqvarQueryExecution
            "state",
            "complete_percent",
            "start_time",
            "end_time",
            "elapsed_seconds",
            "query",
            "querysettings",
        ]
        expected = model_to_dict(
            self.seqvarqueryexecution,
            fields=fields,
        )
        # We replace the query and query settings object with its UUID.
        expected["query"] = self.seqvarqueryexecution.query.sodar_uuid
        expected["querysettings"] = self.seqvarqueryexecution.querysettings.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # We convert the ``FakeDateTime`` objects into strings
        expected["start_time"] = expected["start_time"].isoformat().replace("+00:00", "Z")
        expected["end_time"] = expected["end_time"].isoformat().replace("+00:00", "Z")
        # ... and also fix the "elapsed_seconds" value.
        expected["elapsed_seconds"] = int(expected["elapsed_seconds"])
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarResultSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarresultset = SeqvarResultSetFactory()

    def test_serialize_existing(self):
        serializer = SeqvarResultSetSerializer(self.seqvarresultset)
        fields = [
            # BaseModel
            "sodar_uuid",
            "date_created",
            "date_modified",
            # SeqvarResultSet
            "queryexecution",
            "datasource_infos",
        ]
        expected = model_to_dict(
            self.seqvarresultset,
            fields=fields,
        )
        # We replace the query execution object with its UUID.
        expected["queryexecution"] = self.seqvarresultset.queryexecution.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        # Create JSON dump of datasource_infos.
        expected["datasource_infos"] = self.seqvarresultset.datasource_infos.model_dump(mode="json")
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarResultRowSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.seqvarresultrow = SeqvarResultRowFactory()

    def test_serialize_existing(self):
        serializer = SeqvarResultRowSerializer(self.seqvarresultrow)
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
        # We replace the result set object with its UUID.
        expected["resultset"] = self.seqvarresultrow.resultset.sodar_uuid
        # Create JSON dump of payload.
        expected["payload"] = self.seqvarresultrow.payload.model_dump(mode="json")
        self.assertEqual(set(serializer.data.keys()), set(fields))
        self.assertDictEqual(dict(serializer.data), expected)
