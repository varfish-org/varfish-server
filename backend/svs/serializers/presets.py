"""DRF Serializers for presets."""

import typing

import attrs
from rest_framework import serializers


@attrs.define
class SettingsShortcuts:
    """Helper class that contains the results of the settings shortcuts"""

    presets: typing.Dict[str, str]
    query_settings: typing.Dict[str, typing.Any]


class SvQuerySettingsShortcutsSerializer(serializers.Serializer):
    presets = serializers.JSONField()
    query_settings = serializers.JSONField()
