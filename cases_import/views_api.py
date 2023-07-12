# from projectroles.views_api import SODARAPIBaseMixin
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

# from cases_import.models import CaseImportAction
# from cases_import.serializers import CaseImportActionSerializer
# from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


# class CaseImportActionListCreateApiView(SODARAPIBaseMixin, ListCreateAPIView):
#     """DRF list-create API view the ``CaseImportAction`` model."""

#     serializer_class = CaseImportActionSerializer
#     renderer_classes = [VarfishApiRenderer]
#     versioning_class = VarfishApiVersioning
#     queryset = CaseImportAction.objects.all()

#     def get_permission_required(self):
#         if self.request.method == "POST":
#             return "cases_import.create_data"
#         else:
#             return "cases_import.view_data"


# class CaseImportActionRetrieveUpdateDestroyApiView(SODARAPIBaseMixin, RetrieveUpdateDestroyAPIView):
#     """DRF retrieve-update-destroy API view for the ``CaseImportAction`` model."""

#     lookup_field = "sodar_uuid"
#     lookup_url_kwarg = "enrichmentkit"

#     serializer_class = CaseImportActionSerializer
#     renderer_classes = [VarfishApiRenderer]
#     versioning_class = VarfishApiVersioning
#     queryset = CaseImportAction.objects.all()

#     def get_permission_required(self):
#         if self.request.method == "GET":
#             return "cases_import.view_data"
#         elif self.request.method == "DELETE":
#             return "cases_import.delete_data"
#         else:
#             return "cases_import.update_data"
