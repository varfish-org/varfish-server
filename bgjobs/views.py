from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from projectroles.views import LoggedInPermissionMixin, ProjectContextMixin, ProjectPermissionMixin

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
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class BackgroundJobClearViewBase(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    TemplateView,
):
    """Base class for view clearing jobs."""

    template_name = "bgjobs/backgroundjob_confirm_clear.html"
    which_jobs = None
    permission_required = None

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["which_jobs"] = self.which_jobs
        return result

    def post(self, request, **kwargs):
        context = self.get_context_data()
        project = context["project"]
        filter_kwargs = {"project": project}
        if self.which_jobs != "all":
            filter_kwargs["user"] = self.request.user

        try:
            bg_jobs = BackgroundJob.objects.filter(**filter_kwargs)
            bg_job_count = bg_jobs.count()
            bg_jobs.delete()

            messages.success(self.request, "Removed {} background jobs".format(bg_job_count))
        except Exception as ex:
            messages.error(self.request, "Unable to remove background jobs: {}".format(ex))

        return HttpResponseRedirect(
            reverse("bgjobs:job-list", kwargs={"project": project.sodar_uuid})
        )


class BackgroundJobClearOwnView(BackgroundJobClearViewBase):
    """View for clearing a user's own background job."""

    which_jobs = "own"
    permission_required = "bgjobs.update_bgjob_own"


class BackgroundJobClearAllView(BackgroundJobClearViewBase):
    """View for clearing a background jobs in a project."""

    which_jobs = "all"
    permission_required = "bgjobs.update_bgjob_all"
