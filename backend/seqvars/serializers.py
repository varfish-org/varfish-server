from rest_framework import generics, serializers
from django_pydantic_field.rest_framework import SchemaField

from seqvars.models import DataSourceInfos, SeqvarResultRow, SeqvarResultRowPayload, SeqvarResultSet


class SeqvarResultRowSerializer(serializers.ModelSerializer):
    payload = SchemaField(schema=SeqvarResultRowPayload)

    class Meta:
        model = SeqvarResultRow
        fields = '__all__'


class SeqvarResultSetSerializer(serializers.ModelSerializer):
    datasoruce_infos = SchemaField(schema=DataSourceInfos)

    class Meta:
        model = SeqvarResultSet
        fields = '__all__'