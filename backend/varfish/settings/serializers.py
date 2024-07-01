from rest_framework import serializers


class SettingsBaseSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            if k in instance:
                instance[k] = v
        return instance


class SiteSettingsSerializer(SettingsBaseSerializer):
    pass


class ProjectSettingsSerializer(SettingsBaseSerializer):
    user_defined_tags = serializers.CharField(allow_blank=True)
    disable_pedigree_sex_check = serializers.BooleanField()
    exclude_from_inhouse_db = serializers.BooleanField()
    ts_tv_valid_range = serializers.CharField(allow_blank=True)


class ProjectUserSettingsSerializer(SettingsBaseSerializer):
    pass


class UserSettingsSerializer(SettingsBaseSerializer):
    umd_predictor_api_token = serializers.CharField()
    ga4gh_beacon_network_widget_enabled = serializers.BooleanField()
    latest_version_seen_changelog = serializers.CharField()
