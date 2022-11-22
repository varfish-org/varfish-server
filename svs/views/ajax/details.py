"""AJAX views for retrieving SV variant details."""

from rest_framework.views import APIView


class SvDetailView(APIView):
    """AJAX endpoint for retrieving details about a structural variant.

    **URL:** ``/svs/ajax/structuralvariant/details/{case.sodar_uuid}/{sv.sv_type}-{sv.chrom}-{sv.start}-{sv.end}/``

    **Methods:** ``GET``
    """
