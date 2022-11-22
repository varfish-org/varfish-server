"""Vue app entry point for ``svs`` app"""

from ipaddress import ip_address, ip_network
import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.middleware.csrf import get_token
from django.urls import resolve
from django.views.generic import DetailView
from projectroles.models import Project
from projectroles.plugins import get_app_plugin
from projectroles.views import (
    APP_NAME,
    PROJECT_TYPE_CATEGORY,
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    app_settings,
)

from variants.models import Case


class ProjectAccessMixin:
    """We need to override the project access mixin here"""

    #: Model class to use for projects. Can be overridden by e.g. a proxy model
    project_class = Project

    def get_project(self, request=None, kwargs=None):
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

        model = Case
        uuid_kwarg = "case"

        try:
            obj = model.objects.get(sodar_uuid=kwargs[uuid_kwarg])
            if hasattr(obj, "project"):
                return obj.project
            # Some objects may have a get_project() func instead of foreignkey
            elif hasattr(obj, "get_project") and callable(getattr(obj, "get_project", None)):
                return obj.get_project()
        except model.DoesNotExist:
            return None


class ProjectPermissionMixin(PermissionRequiredMixin, ProjectAccessMixin):
    """
    We must override this because of limitations in projectroles.
    """

    def get_permission_object(self):
        return self.get_project()

    def has_permission(self):
        """Overrides for project permission access"""
        project = self.get_project()
        if not project:
            raise Http404

        # Override permissions for superuser, owner or delegate
        perm_override = self.request.user.is_superuser or project.is_owner_or_delegate(
            self.request.user
        )
        if not perm_override and app_settings.get_app_setting(
            "projectroles", "ip_restrict", project
        ):
            for k in ("HTTP_X_FORWARDED_FOR", "X_FORWARDED_FOR", "FORWARDED", "REMOTE_ADDR"):
                v = self.request.META.get(k)
                if v:
                    client_address = ip_address(v.split(",")[0])
                    break
            else:  # Can't fetch client ip address
                return False

            for record in app_settings.get_app_setting("projectroles", "ip_allowlist", project):
                if "/" in record:
                    if client_address in ip_network(record):
                        break
                elif client_address == ip_address(record):
                    break
            else:
                return False

        # Disable project app access for categories unless specifically enabled
        if project.type == PROJECT_TYPE_CATEGORY:
            request_url = resolve(self.request.get_full_path())
            if request_url.app_name != APP_NAME:
                app_plugin = get_app_plugin(request_url.app_name)
                if app_plugin and app_plugin.category_enable:
                    return True
                return False

        # Disable access for non-owner/delegate if remote project is revoked
        if project.is_revoked() and not perm_override:
            return False

        return super().has_permission()

    def get_queryset(self, *args, **kwargs):
        """
        Override get_queryset() to filter down to the currently selected object.
        """
        qs = super().get_queryset(*args, **kwargs)
        if qs.model == ProjectAccessMixin.project_class:
            return qs
        elif hasattr(qs.model, "get_project_filter_key"):
            return qs.filter(**{qs.model.get_project_filter_key(): self.get_project()})
        elif hasattr(qs.model, "project") or hasattr(qs.model, "get_project"):
            return qs.filter(project=self.get_project())
        else:
            raise AttributeError(
                'Model does not have "project" member, get_project() function '
                'or "get_project_filter_key()" function'
            )


class SvFilterEntrypoint(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Entrypoint for SV filtration."""

    permission_required = "svs.view_data"
    template_name = "svs/entrypoint.html"
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"
    model = Case

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["app_context"] = json.dumps(
            {
                "case_uuid": str(self.object.sodar_uuid),
                "project": {
                    "sodar_uuid": str(context["project"].sodar_uuid),
                    "title": context["project"].title,
                },
                "csrf_token": get_token(self.request),
            }
        )
        return context
