from dataclasses import asdict

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from projectroles.models import Project
from projectroles.views_api import SODARAPIBaseProjectMixin, SODARAPIProjectPermission
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import BasePermission

from vf_settings.serializers import (
    AllSettingsSerializer,
    ProjectSettingsSerializer,
    ProjectUserSettingsSerializer,
    SiteSettingsSerializer,
    UserSettingsSerializer,
)
from vf_settings.settings_api import SettingsAPI

User = get_user_model()


class NoProjectSettingsPermission(BasePermission):
    """Base permission for settings."""

    def has_permission(self, request, view):
        if not hasattr(view, "permission_required") and (
            not hasattr(view, "get_permission_required")
            or not callable(getattr(view, "get_permission_required", None))
        ):
            raise ImproperlyConfigured(
                "{0} is missing the permission_required attribute. "
                "Define {0}.permission_required, or override "
                "{0}.get_permission_required().".format(view.__class__.__name__)
            )
        elif hasattr(view, "permission_required"):
            perm = view.permission_required
        else:
            perm = view.get_permission_required()

        return request.user.has_perm(perm)


class AllSettingsPermission(SODARAPIProjectPermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if "project" in view.kwargs:
            return super().has_permission(request, view)

        return True


class SettingsRetrieveUpdateBaseAPIView(RetrieveUpdateAPIView):
    """Retrieve and update settings base API view."""

    @property
    def _user(self):
        if self.scope.endswith("user"):
            return self.request.user
        return None

    @property
    def _project(self):
        if self.scope.startswith("project"):
            return Project.objects.get(sodar_uuid=self.kwargs["project"])
        return None

    def get(self, request, *args, **kwargs):
        if self.request.GET.get("a") == "reset":
            settings_api = SettingsAPI(project=self._project, user=self._user)
            settings_api.reset_scope_settings()

        return super().get(request, *args, **kwargs)

    def get_object(self):
        settings_api = SettingsAPI(project=self._project, user=self._user)
        return asdict(settings_api.get_scope_settings())

    def perform_update(self, serializer):
        settings_api = SettingsAPI(project=self._project, user=self._user)
        settings_api.set_scope_settings(serializer.validated_data)
        serializer.save()

    def get_permission_required(self):
        action = "view"
        if self.request.method in ("PUT", "PATCH") or (
            self.request.method == "GET" and self.request.GET.get("a") == "reset"
        ):
            action = "update"
        return f"vf_settings.{action}_{self.scope}"


class SiteSettingsRetrieveUpdateAPIView(SettingsRetrieveUpdateBaseAPIView):
    """Retrieve and update site settings API view."""

    serializer_class = SiteSettingsSerializer
    permission_classes = [NoProjectSettingsPermission]
    scope = "site"


class ProjectSettingsRetrieveUpdateAPIView(
    SODARAPIBaseProjectMixin, SettingsRetrieveUpdateBaseAPIView
):
    """Retrieve and update project settings API view."""

    serializer_class = ProjectSettingsSerializer
    scope = "project"


class ProjectUserSettingsRetrieveUpdateAPIView(
    SODARAPIBaseProjectMixin, SettingsRetrieveUpdateBaseAPIView
):
    """Retrieve and update project user settings API view."""

    serializer_class = ProjectUserSettingsSerializer
    scope = "project_user"


class UserSettingsRetrieveUpdateAPIView(SettingsRetrieveUpdateBaseAPIView):
    """Retrieve and update user settings API view."""

    serializer_class = UserSettingsSerializer
    permission_classes = [NoProjectSettingsPermission]
    scope = "user"


class AllSettingsRetrieveAPIView(SODARAPIBaseProjectMixin, RetrieveAPIView):
    """Retrieve all settings API view."""

    serializer_class = AllSettingsSerializer
    permission_classes = [AllSettingsPermission]
    permission_required = "vf_settings.view_project"

    def get_object(self):
        project = None

        if "project" in self.kwargs:
            project = Project.objects.get(sodar_uuid=self.kwargs["project"])

        settings_api = SettingsAPI(project=project, user=self.request.user)
        return asdict(settings_api.get_all_settings())
