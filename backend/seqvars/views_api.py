from rest_framework import generics
from django_pydantic_field.rest_framework import AutoSchema

from seqvars.serializers import SeqvarResultRowSerializer


class SeqvarResultSetView(generics.RetrieveAPIView):
    serializer_class = SeqvarResultRowSerializer

    # optional support of OpenAPI schema generation for Pydantic fields
    schema = AutoSchema()
