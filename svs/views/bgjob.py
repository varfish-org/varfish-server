"""Views for background jobs from the ``svs`` app"""

import re

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.urls import resolve
from django.views.generic import DetailView
from projectroles.models import Project
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from svs.models import (
    BuildBackgroundSvSetJob,
    CleanupBackgroundSvSetJob,
    ImportStructuralVariantBgJob,
)


class ImportStructuralVariantsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of import case background jobs."""

    permission_required = "variants.view_data"
    template_name = "svs/import_job_detail.html"
    model = ImportStructuralVariantBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class _ProjectAccessMixin:
    """Mixin for providing access to a Project object from request kwargs"""

    #: The model class to use for projects.  You can override this to replace it
    #: with a proxy model, for example.
    project_class = Project

    def get_project(self, request=None, kwargs=None):
        """
        Return SODAR Project object based or None if not found, based on
        the current request and view kwargs. If arguments are not provided,
        uses self.request and/or self.kwargs.
        :param request: Request object (optional)
        :param kwargs: View kwargs (optional)
        :return: Object of project_class or None if not found
        """
        request = request or getattr(self, "request")
        kwargs = kwargs or getattr(self, "kwargs")
        # Ensure kwargs can be accessed
        if kwargs is None:
            raise ImproperlyConfigured("View kwargs are not accessible")

        # Project class object
        if "project" in kwargs:
            return self.project_class.objects.filter(sodar_uuid=kwargs["project"]).first()

        # Other object types
        if not request:
            raise ImproperlyConfigured("Current HTTP request is not accessible")

        if getattr(self, "model", None):
            model = getattr(self, "model")
            uuid_kwarg = getattr(self, "slug_url_kwarg")
        else:
            model = None
            uuid_kwarg = None

        for k, v in kwargs.items():
            if re.match(r"[0-9a-f-]+", v):
                try:
                    app_name = resolve(request.path).app_name
                    if app_name.find(".") != -1:
                        app_name = app_name.split(".")[0]
                    model = apps.get_model(app_name, k)
                    uuid_kwarg = k
                    break
                except LookupError:
                    pass

        if not model:
            return None

        try:
            obj = model.objects.get(sodar_uuid=kwargs[uuid_kwarg])
            if hasattr(obj, "project"):
                return obj.project
            # Some objects may have a get_project() func instead of foreignkey
            elif hasattr(obj, "get_project") and callable(getattr(obj, "get_project", None)):
                return obj.get_project()
        except model.DoesNotExist:
            return None


class BuildBackgroundSvSetJobDetailView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DetailView
):
    """Display status and further details of build sv set background jobs."""

    permission_required = "variants.view_data"
    template_name = "svs/build_bg_job_detail.html"
    model = BuildBackgroundSvSetJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


class CleanupBackgroundSvSetJobDetailView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DetailView
):
    """Display status and further details of cleanup sv set background jobs."""

    permission_required = "variants.view_data"
    template_name = "svs/cleanup_bg_job_detail.html"
    model = CleanupBackgroundSvSetJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
