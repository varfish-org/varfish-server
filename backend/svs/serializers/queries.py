"""DRF Serializers for queries, results, and related background jobs."""

from bgjobs.models import BackgroundJob
from projectroles.serializers import SODARModelSerializer
from rest_framework import serializers

from svs.models import FilterSvBgJob, SvQuery, SvQueryResultRow, SvQueryResultSet
from variants.serializers import create_only_validator


class BackgroundJobSerializer(SODARModelSerializer):
    """Serializer for the ``bgjobs.BackgroundJob`` model.

    This serializer is only used in a read-only context.
    """

    class Meta:
        model = BackgroundJob

        fields = ("sodar_uuid", "date_created", "date_modified", "status")
        read_only_fields = fields


class FilterSvBgJobSerializer(SODARModelSerializer):
    """Serializer for the ``FilterSvBgJob`` model.

    This serializer is only used in a read-only context.

    Note that the using views should ``preselect_related()`` aggressively to keep down the required database
    queries.
    """

    #: Nested serialization of base background job
    bg_job = BackgroundJobSerializer(many=False, read_only=True)
    #: UUID of the related case
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: UUID of the related project
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    #: UUID of the related query
    svquery = serializers.ReadOnlyField(source="svquery.sodar_uuid")
    #: UUID of the creating user
    user = serializers.ReadOnlyField(source="user.sodar_uuid")

    class Meta:
        model = FilterSvBgJob
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "bg_job",
            "case",
            "project",
            "svquery",
            "user",
        )
        read_only_fields = fields


class SvQuerySerializer(SODARModelSerializer):
    """Serializer for the ``SvQuery`` model.

    This serializer is only used in a read-only context.

    Note that the using views should ``preselect_related()`` aggressively to keep down the required database
    queries.
    """

    #: UUID of the related case
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: UUID of the creating user
    user = serializers.ReadOnlyField(source="user.sodar_uuid")

    query_settings = serializers.JSONField(
        validators=[
            create_only_validator,
            # query_settings_validator,  # TODO: properly validate with JSON schema!
        ]
    )

    def create(self, validated_data):
        """Make case and user writeable on creation."""
        validated_data["user"] = self.context["request"].user
        validated_data["case"] = self.context["case"]
        return super().create(validated_data)

    class Meta:
        model = SvQuery
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "user",
            "case",
            "query_state",
            "query_state_msg",
            "query_settings",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "user",
            "case",
            "query_state",
            "query_state_msg",
        )


class SvQueryWithLogsSerializer(SvQuerySerializer):
    #: Log messages
    logs = serializers.SerializerMethodField()

    def get_logs(self, obj):
        jobs = obj.filtersvbgjob_set.all()
        if not jobs:
            return []
        else:
            the_bg_job = jobs[0].bg_job
            return [
                f"{log_entry.date_created} | {log_entry.level} | {log_entry.message}"
                for log_entry in the_bg_job.log_entries.all()
            ]

    class Meta:
        model = SvQuery
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "user",
            "case",
            "query_state",
            "query_state_msg",
            "query_settings",
            "logs",
        )
        read_only_fields = fields


class SvQueryResultSetSerializer(SODARModelSerializer):
    """Serializer for the ``SvQueryResult`` model.

    This serializer is only used in a read-only context.

    Note that the using views should ``preselect_related()`` aggressively to keep down the required database
    queries.
    """

    #: UUID of the related query
    svquery = serializers.ReadOnlyField(source="svquery.sodar_uuid")
    #: UUID of the related case
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    class Meta:
        model = SvQueryResultSet
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "svquery",
            "case",
            "start_time",
            "end_time",
            "elapsed_seconds",
            "result_row_count",
        )
        read_only_fields = fields


class SvQueryResultRowSerializer(SODARModelSerializer):
    """Serializer for the ``SvQueryResult`` model **with** the paylaod.

    This serializer is only used in a read-only context.

    Note that the using views should ``preselect_related()`` aggressively to keep down the required database
    queries.
    """

    #: UUID of the related query result set
    svqueryresultset = serializers.ReadOnlyField(source="svqueryresultset.sodar_uuid")

    class Meta:
        model = SvQueryResultRow
        fields = (
            "sodar_uuid",
            "svqueryresultset",
            "release",
            "chromosome",
            "chromosome_no",
            "bin",
            "chromosome2",
            "chromosome_no2",
            "bin2",
            "start",
            "end",
            "pe_orientation",
            "sv_type",
            "sv_sub_type",
            "payload",
        )
        read_only_fields = fields
