from django_pydantic_field.rest_framework import AutoSchema
from rest_framework import viewsets

from seqvars.models import SeqvarResultSet
from seqvars.serializers import SeqvarResultSetSerializer


class SeqvarResultSetView(viewsets.ModelViewSet):
    queryset = SeqvarResultSet.objects.all()
    serializer_class = SeqvarResultSetSerializer

    # optional support of OpenAPI schema generation for Pydantic fields
    schema = AutoSchema()
