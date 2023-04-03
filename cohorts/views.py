import json

from django.middleware.csrf import get_token
from django.views.generic import ListView
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from cohorts.models import Cohort


class EntrypointView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of cohorts."""

    permission_required = "cohorts.view_data"
    template_name = "cohorts/entrypoint.html"
    model = Cohort

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["app_context"] = json.dumps(
            {
                "project": {
                    "sodar_uuid": str(context["project"].sodar_uuid),
                    "title": context["project"].title,
                },
                "base_url": "/cohorts/ajax/",
                "csrf_token": get_token(self.request),
                "user": {
                    "username": self.request.user.username,
                    "sodar_uuid": str(self.request.user.sodar_uuid),
                    "is_superuser": self.request.user.is_superuser,
                },
            }
        )
        return context
