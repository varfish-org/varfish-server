from rest_framework import serializers


class SettingsBaseSerializer(serializers.Serializer):
    """Base class for settings serializers."""

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            if k in instance:
                instance[k] = v
        return instance


class SiteSettingsSerializer(SettingsBaseSerializer):
    """Serializer for site settings."""

    test_param = serializers.CharField(allow_blank=True)


class ProjectSettingsSerializer(SettingsBaseSerializer):
    """Serializer for project settings."""

    user_defined_tags = serializers.CharField(allow_blank=True)
    disable_pedigree_sex_check = serializers.BooleanField()
    exclude_from_inhouse_db = serializers.BooleanField()
    ts_tv_valid_range = serializers.CharField(allow_blank=True)
    test_param = serializers.CharField(allow_blank=True)


class ProjectUserSettingsSerializer(SettingsBaseSerializer):
    """Serializer for project user settings."""

    test_param = serializers.CharField(allow_blank=True)


class UserSettingsSerializer(SettingsBaseSerializer):
    """Serializer for user settings."""

    umd_predictor_api_token = serializers.CharField(allow_blank=True)
    ga4gh_beacon_network_widget_enabled = serializers.BooleanField()
    latest_version_seen_changelog = serializers.CharField(allow_blank=True)
    test_param = serializers.CharField(allow_blank=True)


class AllSettingsSerializer(
    SiteSettingsSerializer,
    ProjectSettingsSerializer,
    ProjectUserSettingsSerializer,
    UserSettingsSerializer,
):
    """Serializer for all settings."""
