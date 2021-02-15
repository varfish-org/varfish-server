"""The views for the ``clinvar_export`` app.

The UI for this app is completely Vue-based so we only render the entry point.
"""

import json

from django.middleware.csrf import get_token
from django.urls import reverse
from django.views.generic import ListView
from projectroles.views import (
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
    LoggedInPermissionMixin,
)

from .models import SubmissionSet


class SubmissionSetView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of cohorts.
    """

    permission_required = "variants.view_data"
    template_name = "submission_set/entrypoint.html"
    model = SubmissionSet

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["app_context"] = json.dumps(
            {
                "project_uuid": str(context["project"].sodar_uuid),
                "base_url": reverse(
                    "clinvar_export:ajax-organisation-list",
                    kwargs={"project": self.get_project().sodar_uuid},
                ).replace("/organisation/", ""),
                "csrf_token": get_token(self.request),
            }
        )
        return context
