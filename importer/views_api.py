"""API views for the importer models."""

import logging

from bgjobs.models import BackgroundJob
from django.contrib.auth import get_user_model
from django.db import transaction
from projectroles.constants import get_sodar_constants
from projectroles.views_api import SODARAPIBaseProjectMixin, SODARAPIGenericProjectMixin
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveDestroyAPIView,
)

from . import tasks
from .models import CaseImportInfo, VariantSetImportInfo, CaseImportState, ImportCaseBgJob
from .serializers import (
    CaseImportInfoSerializer,
    VariantSetImportInfoSerializer,
    BamQcFileSerializer,
    DatabaseInfoFileSerializer,
    EffectFileSerializer,
    GenotypeFileSerializer,
)

#: Logger to use in this module.
LOGGER = logging.getLogger(__name__)

#: The User model to use.
User = get_user_model()

#: Get SODAR contants.
SODAR_CONSTANTS = get_sodar_constants()


class CaseImportInfoListCreateView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    """DRF list-create API view the ``CaseImportInfo`` model."""

    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
    serializer_class = CaseImportInfoSerializer

    def get_queryset(self):
        qs = CaseImportInfo.objects.filter(project=self.get_project())

        # All users with project access can see the cases, or limit case list to a given owner
        if "owner" in self.request.query_params:
            try:
                qs = qs.filter(owner=User.objects.get(username=self.request.query_params["owner"]))
            except User.DoesNotExist:
                qs = qs.none()

        return qs

    def get_permission_required(self):
        if self.request.method == "POST":
            return "importer.add_import"
        else:
            return "importer.view_import"


class CaseImportInfoRetrieveUpdateDestroyView(
    SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    """DRF retrieve-update-destroy API view for the ``CaseImportInfo`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "caseimportinfo"
    serializer_class = CaseImportInfoSerializer
    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]

    def perform_update(self, serializer):
        old_state = self.get_object().state
        new_state = serializer.validated_data.get("state", old_state)
        # React on change to submitted.
        job = None
        with transaction.atomic():
            new_obj = serializer.save()
            if (
                old_state != CaseImportState.SUBMITTED.value
                and new_state == CaseImportState.SUBMITTED.value
            ):
                LOGGER.info("Submitting background job for case %s", new_obj.name)
                base_job = BackgroundJob.objects.create(
                    name="Import of case %s" % new_obj.name,
                    project=new_obj.project,
                    job_type=ImportCaseBgJob.spec_name,
                    user=self.request.user,
                )
                job = ImportCaseBgJob.objects.create(
                    project=new_obj.project, import_info=new_obj, bg_job=base_job
                )
        if job:
            tasks.run_import_case_bg_job.delay(pk=job.id)

    def get_queryset(self):
        return CaseImportInfo.objects.filter(project=self.get_project())

    def get_permission_required(self):
        if self.request.method == "GET":
            return "importer.view_import"
        elif self.request.method == "DELETE":
            return "importer.delete_import"
        else:
            return "importer.update_import"


class RelatedMixin:
    """Helper mixin for setting up serializer context and queryset."""

    related_class = None
    related_lookup_field = None
    related_lookup_url_kwarg = None

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result[self.related_lookup_field] = self.related_class.objects.get(
            sodar_uuid=self.kwargs[self.related_lookup_url_kwarg]
        )
        return result

    def get_queryset(self):
        obj = self.related_class.objects.get(sodar_uuid=self.kwargs[self.related_lookup_url_kwarg])
        return self.serializer_class.Meta.model.objects.filter(**{self.related_lookup_field: obj})


class VariantSetImportBaseMixin(SODARAPIBaseProjectMixin, RelatedMixin):

    serializer_class = VariantSetImportInfoSerializer

    related_class = CaseImportInfo
    related_lookup_field = "case_import_info"
    related_lookup_url_kwarg = "caseimportinfo"

    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]


class VariantSetImportInfoListCreateView(VariantSetImportBaseMixin, ListCreateAPIView):
    """DRF list-create API view the ``VariantSetImportInfo`` model."""

    def get_permission_required(self):
        if self.request.method == "POST":
            return "importer.add_import"
        else:
            return "importer.view_import"


class VariantSetImportInfoRetrieveUpdateDestroyView(
    VariantSetImportBaseMixin, RetrieveUpdateDestroyAPIView
):
    """DRF retrieve-update-destroy API view for the ``VariantSetImportInfo`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "variantsetimportinfo"

    def get_permission_required(self):
        if self.request.method == "GET":
            return "importer.view_import"
        elif self.request.method == "DELETE":
            return "importer.delete_import"
        else:
            return "importer.update_import"


class BamQcFileBaseMixin(SODARAPIBaseProjectMixin, RelatedMixin):

    serializer_class = BamQcFileSerializer

    related_class = CaseImportInfo
    related_lookup_field = "case_import_info"
    related_lookup_url_kwarg = "caseimportinfo"

    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]


class BamQcFileListCreateView(BamQcFileBaseMixin, ListCreateAPIView):
    """DRF list-create API view the ``BamQcFile`` model."""

    def get_permission_required(self):
        if self.request.method == "POST":
            return "importer.add_import"
        else:
            return "importer.view_import"


class BamQcFileRetrieveDestroyView(BamQcFileBaseMixin, RetrieveDestroyAPIView):
    """DRF retrieve-update-destroy API view for the ``BamQcFile`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "bamqcfile"

    def get_permission_required(self):
        if self.request.method == "GET":
            return "importer.view_import"
        elif self.request.method == "DELETE":
            return "importer.delete_import"
        else:
            return "importer.update_import"


class GenotypeFileBaseMixin(SODARAPIBaseProjectMixin, RelatedMixin):

    serializer_class = GenotypeFileSerializer

    related_class = VariantSetImportInfo
    related_lookup_field = "variant_set_import_info"
    related_lookup_url_kwarg = "variantsetimportinfo"

    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]


class GenotypeFileListCreateView(GenotypeFileBaseMixin, ListCreateAPIView):
    """DRF list-create API view the ``GenotypeFile`` model."""

    def get_permission_required(self):
        if self.request.method == "POST":
            return "importer.add_import"
        else:
            return "importer.view_import"


class GenotypeFileRetrieveDestroyView(GenotypeFileBaseMixin, RetrieveDestroyAPIView):
    """DRF retrieve-update-destroy API view for the ``GenotypeFile`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "genotypefile"

    def get_permission_required(self):
        if self.request.method == "GET":
            return "importer.view_import"
        elif self.request.method == "DELETE":
            return "importer.delete_import"
        else:
            return "importer.update_import"


class EffectsFileBaseMixin(SODARAPIBaseProjectMixin, RelatedMixin):

    serializer_class = EffectFileSerializer

    related_class = VariantSetImportInfo
    related_lookup_field = "variant_set_import_info"
    related_lookup_url_kwarg = "variantsetimportinfo"

    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]


class EffectsFileListCreateView(EffectsFileBaseMixin, ListCreateAPIView):
    """DRF list-create API view the ``EffectsFile`` model."""

    def get_permission_required(self):
        if self.request.method == "POST":
            return "importer.add_import"
        else:
            return "importer.view_import"


class EffectsFileRetrieveDestroyView(EffectsFileBaseMixin, RetrieveDestroyAPIView):
    """DRF retrieve-update-destroy API view for the ``EffectsFile`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "effectsfile"

    def get_permission_required(self):
        if self.request.method == "GET":
            return "importer.view_import"
        elif self.request.method == "DELETE":
            return "importer.delete_import"
        else:
            return "importer.update_import"


class DatabaseInfoFileBaseMixin(SODARAPIBaseProjectMixin, RelatedMixin):

    serializer_class = DatabaseInfoFileSerializer

    related_class = VariantSetImportInfo
    related_lookup_field = "variant_set_import_info"
    related_lookup_url_kwarg = "variantsetimportinfo"

    project_type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]


class DatabaseInfoFileListCreateView(DatabaseInfoFileBaseMixin, ListCreateAPIView):
    """DRF list-create API view the ``DatabaseInfoFile`` model."""

    def get_permission_required(self):
        if self.request.method == "POST":
            return "importer.add_import"
        else:
            return "importer.view_import"


class DatabaseInfoFileRetrieveDestroyView(DatabaseInfoFileBaseMixin, RetrieveDestroyAPIView):
    """DRF retrieve-update-destroy API view for the ``DatabaseInfoFile`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "databaseinfofile"

    def get_permission_required(self):
        if self.request.method == "GET":
            return "importer.view_import"
        elif self.request.method == "DELETE":
            return "importer.delete_import"
        else:
            return "importer.update_import"
