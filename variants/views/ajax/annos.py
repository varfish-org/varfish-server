import contextlib

from django.utils import timezone
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.helpers import get_engine
from variants.models import Case
from variants.queries import CaseLoadUserAnnotatedQuery
from variants.serializers import SmallVariantForResultSerializer


class CaseUserAnnotatedVariantsAjaxView(ListAPIView):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [SODARAPIProjectPermission]
    queryset = Case.objects.all()

    serializer_class = SmallVariantForResultSerializer

    def get_permission_required(self):
        return "variants.view_data"

    def get(self, request, *args, **kwargs):
        # Build and run the query.
        query = CaseLoadUserAnnotatedQuery(case_or_cases=self.get_object(), engine=get_engine())
        started = timezone.now()
        # Fetch all results and compute elapsed time
        with contextlib.closing(query.run(kwargs={})) as results:
            rows = list(map(lambda row: dict(row.items()), results.fetchall()))
        time_elapsed = timezone.now() - started
        return Response({"time_elapsed": time_elapsed, "rows": rows}, status=status.HTTP_200_OK)
