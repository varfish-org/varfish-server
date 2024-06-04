from rest_framework import serializers

from genepanels.models import GenePanel, GenePanelCategory


class GenePanelSerializer(serializers.ModelSerializer):
    """Serializer that serializes ``GenePanel``."""

    class Meta:
        model = GenePanel
        fields = (
            "identifier",
            "state",
            "version_major",
            "version_minor",
            "title",
            "description",
        )
        read_only_fields = (
            "identifier",
            "state",
            "version_major",
            "version_minor",
            "title",
            "description",
        )


class GenePanelCategorySerializer(serializers.ModelSerializer):
    """Serializer that serializes ``GenePanelCategory``."""

    genepanel_set = serializers.SerializerMethodField()

    class Meta:
        model = GenePanelCategory
        fields = (
            "title",
            "description",
            "genepanel_set",
        )
        read_only_fields = (
            "title",
            "description",
            "genepanel_set",
        )

    def get_genepanel_set(self, obj):
        """Corresponds to the ``genepanel_set`` field defined above."""
        return GenePanelSerializer(obj.genepanel_set.filter(state="active"), many=True).data
