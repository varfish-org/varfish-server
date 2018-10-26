from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, View, ListView

from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

from .models import BackgroundJob


class JobListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    template_name = "bgjobs/job_list.html"
    permission_required = "bgjobs.view_data"
    model = BackgroundJob

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])
