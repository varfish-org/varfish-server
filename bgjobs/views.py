from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin
from projectroles.plugins import get_backend_api

from .models import BackgroundJob


class ProjectBackgroundJobView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display all ``BackgroundJob`` records for the project."""

    template_name = "bgjobs/project_backgroundjobs.html"
    permission_required = "bgjobs.view_jobs_own"
    model = BackgroundJob

    def get_queryset(self):
        # TODO: filter to user's job if can only see their own
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class BackgroundJobClearViewBase(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    TemplateView,
):
    """Base class for view clearing jobs."""

    #: The template is the same for both sub classes.
    template_name = "bgjobs/backgroundjob_confirm_clear.html"
    #: Set in sub class.
    which_jobs = None
    #: Set in sub class.
    permission_required = None

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["which_jobs"] = self.which_jobs
        return result

    def post(self, _request, **_kwargs):
        """Handle form POST."""
        context = self.get_context_data()
        project = context["project"]
        filter_kwargs = {"project": project}
        if self.which_jobs != "all":
            filter_kwargs["user"] = self.request.user

        try:
            bg_jobs = BackgroundJob.objects.filter(**filter_kwargs)
            bg_job_count = bg_jobs.count()
            bg_jobs.delete()

            timeline = get_backend_api("timeline_backend")
            if timeline:
                timeline.add_event(
                    project=self._get_project(self.request, self.kwargs),
                    app_name="bgjobs",
                    user=self.request.user,
                    event_name="clear_bg_jobs",
                    description="Clearing {} background jobs".format(
                        "user-owned" if self.which_jobs != "all" else "all"
                    ),
                    status_type="OK",
                )
            messages.success(self.request, "Removed {} background jobs".format(bg_job_count))
        except Exception as ex:
            messages.error(self.request, "Unable to remove background jobs: {}".format(ex))

        return HttpResponseRedirect(
            reverse("bgjobs:jobs-list", kwargs={"project": project.sodar_uuid})
        )


class BackgroundJobClearOwnView(BackgroundJobClearViewBase):
    """View for clearing a user's own background job."""

    which_jobs = "own"
    permission_required = "bgjobs.update_bgjob_own"


class BackgroundJobClearAllView(BackgroundJobClearViewBase):
    """View for clearing a background jobs in a project."""

    which_jobs = "all"
    permission_required = "bgjobs.update_bgjob_all"
