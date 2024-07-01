from dataclasses import asdict

from django.contrib.auth import get_user_model
from projectroles.models import Project
from projectroles.views_api import SODARAPIBaseProjectMixin
from rest_framework.generics import RetrieveUpdateAPIView

from varfish.settings.serializers import (
    ProjectSettingsSerializer,
    ProjectUserSettingsSerializer,
    SiteSettingsSerializer,
    UserSettingsSerializer,
)
from varfish.settings.settings_api import SettingsAPI

User = get_user_model()


class SettingsRetrieveUpdateBaseAPIView(RetrieveUpdateAPIView):
    """Retrieve and update settings base API view."""

    @property
    def _user(self):
        if self.scope.endswith("USER"):
            return self.request.user
        return None

    @property
    def _project(self):
        if self.scope.startswith("PROJECT"):
            return Project.objects.get(sodar_uuid=self.kwargs["project"])
        return None

    def get(self, request, *args, **kwargs):
        if self.request.GET.get("a") == "reset":
            settings_api = SettingsAPI(scope=self.scope, project=self._project, user=self._user)
            settings_api.reset_settings()

        return super().get(request, *args, **kwargs)

    def get_object(self):
        settings_api = SettingsAPI(scope=self.scope, project=self._project, user=self._user)
        return asdict(settings_api.get_settings())

    def perform_update(self, serializer):
        settings_api = SettingsAPI(scope=self.scope, project=self._project, user=self._user)
        settings_api.set_settings(serializer.validated_data)
        serializer.save()

    def get_permission_required(self):
        scope = self.scope.lower()

        if self.request.method == "PUT" or (
            self.request.method == "GET" and self.request.GET.get("a") == "reset"
        ):
            return f"settings.{scope}.update_data"

        return f"settings.{scope}.view_data"


class SiteSettingsRetrieveUpdateAPIView(SettingsRetrieveUpdateBaseAPIView):
    serializer_class = SiteSettingsSerializer
    scope = "SITE"


class ProjectSettingsRetrieveUpdateAPIView(
    SODARAPIBaseProjectMixin, SettingsRetrieveUpdateBaseAPIView
):
    serializer_class = ProjectSettingsSerializer
    scope = "PROJECT"


class ProjectUserSettingsRetrieveUpdateAPIView(
    SODARAPIBaseProjectMixin, SettingsRetrieveUpdateBaseAPIView
):
    serializer_class = ProjectUserSettingsSerializer
    scope = "PROJECT_USER"


class UserSettingsRetrieveUpdateAPIView(SettingsRetrieveUpdateBaseAPIView):
    serializer_class = UserSettingsSerializer
    scope = "USER"
