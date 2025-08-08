import typing

from django.db import transaction
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from cases_import import tasks
from cases_import.models.base import CaseImportAction, CaseImportBackgroundJob
from cases_import.serializers import CaseImportActionSerializer
from seqvars.views_api import ProjectContextBaseViewSet
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class CaseImportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CaseImportActionViewSet(ProjectContextBaseViewSet, viewsets.ModelViewSet):
    pagination_class = CaseImportPagination
    permission_classes = [SODARAPIProjectPermission]
    queryset = CaseImportAction.objects.all()
    renderer_classes = [VarfishApiRenderer]
    serializer_class = CaseImportActionSerializer
    versioning_class = VarfishApiVersioning
    lookup_url_kwarg = "caseimportaction"

    def get_queryset(self):
        return CaseImportAction.objects.filter(project__sodar_uuid=self.kwargs["project"])

    def get_permission_required(self):
        if self.action == "create":
            return "cases_import.create_data"
        elif self.action == "update" or self.action == "partial_update":
            return "cases_import.update_data"
        elif self.action == "destroy":
            return "cases_import.delete_data"
        return "cases_import.view_data"

    def create(self, request, *args, **kwargs):
        """Override to ensure creation happens in a transaction.

        This is important so we can rely on the serializer validation to be consistent
        with the creation (e.g., on collision checks).
        """
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            caseimportbackgroundjob = self.perform_create(serializer)
        if caseimportbackgroundjob:
            tasks.run_caseimportactionbackgroundjob.delay(
                caseimportactionbackgroundjob_pk=caseimportbackgroundjob.pk
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer) -> typing.Optional[CaseImportBackgroundJob]:
        """Override the ``perform_create()`` method as to create the appropriate background
        import job.

        Note that this relies on ``create()`` using ``transaction.atomic()``.
        """
        super().perform_create(serializer)
        # at this point ``serializer.instance`` has been set and can be used
        if serializer.instance.state == CaseImportAction.STATE_SUBMITTED:
            return CaseImportBackgroundJob.objects.create_full(
                caseimportaction=serializer.instance,
                user=self.request.user,
            )
        else:
            return None

    def update(self, request, *args, **kwargs):
        """Override to ensure creation happens in a transaction.

        This is important so we can rely on the serializer validation to be consistent
        with the creation (e.g., on collision checks).
        """
        partial = kwargs.pop("partial", False)
        with transaction.atomic():
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            caseimportbackgroundjob = self.perform_update(serializer)
        if caseimportbackgroundjob:
            tasks.run_caseimportactionbackgroundjob.delay(
                caseimportactionbackgroundjob_pk=caseimportbackgroundjob.pk
            )
        return Response(serializer.data)

    def perform_update(self, serializer) -> typing.Optional[CaseImportBackgroundJob]:
        """Override the ``perform_create()`` method as to create the appropriate background
        import job

        Note that this relies on ``update()`` using ``transaction.atomic()``.
        """
        super().perform_update(serializer)
        # at this point ``serializer.instance`` has been set and can be used
        if serializer.instance.state == CaseImportAction.STATE_SUBMITTED:
            return CaseImportBackgroundJob.objects.create_full(
                caseimportaction=serializer.instance,
                user=self.request.user,
            )
        else:
            return None

    def destroy(self, request, *args, **kwargs):
        """Override to prevent destruction unless state is draft."""
        with transaction.atomic():
            instance = self.get_object()
            if instance.state != CaseImportAction.STATE_DRAFT:
                return Response(
                    {"detail": "Only case import actions in state draft can be deleted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
