from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from cohorts.forms import CohortForm
from cohorts.models import Cohort
from variants.models import CaseAwareProject


class CohortView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of cohorts."""

    permission_required = "variants.view_data"
    template_name = "cohorts/cohort_list.html"
    model = Cohort


class CohortCreateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    CreateView,
):
    """Create cohort."""

    permission_required = "variants.view_data"
    template_name = "cohorts/cohort_create.html"
    model = Cohort
    form_class = CohortForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass user to form.
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Set user in form before submitting.
        form.instance.user = self.request.user
        # Exchange Project object with CaseAwareProject in form before submitting.
        form.instance.project = CaseAwareProject.objects.get(id=self.get_project().id)
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        # Add all user accessible projects to help organize the case checkboxes by project.
        projects = []
        if self.request.user.is_superuser:
            query = CaseAwareProject.objects.filter(type="PROJECT")
        else:
            query = CaseAwareProject.objects.filter(roles__user=self.request.user, type="PROJECT")
        for project in query:
            if len(project.get_active_smallvariant_cases()):
                projects.append(project)
        context["projects"] = projects
        return context


class CohortUpdateView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    """Update cohort."""

    permission_required = "variants.view_data"
    template_name = "cohorts/cohort_update.html"
    model = Cohort
    form_class = CohortForm
    slug_url_kwarg = "cohort"
    slug_field = "sodar_uuid"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass user to form.
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Exchange Project object with CaseAwareProject in form before submitting.
        form.instance.project = CaseAwareProject.objects.get(id=self.get_project().id)
        if self.object.user == self.request.user or self.request.user.is_superuser:
            messages.success(
                self.request, mark_safe("Cohort <strong>%s</strong> updated." % self.object.name)
            )
            return super().form_valid(form)
        messages.error(self.request, mark_safe("Can't update other user's cohort."))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        # Add all user accessible projects to help organize the case checkboxes by project.
        projects = []
        if self.request.user.is_superuser:
            query = CaseAwareProject.objects.filter(type="PROJECT")
        else:
            query = CaseAwareProject.objects.filter(roles__user=self.request.user, type="PROJECT")
        for project in query:
            if len(project.get_active_smallvariant_cases()):
                projects.append(project)
        context["projects"] = projects
        return context


class CohortDeleteView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    """Delete cohort."""

    permission_required = "variants.view_data"
    template_name = "cohorts/cohort_confirm_delete.html"
    model = Cohort
    slug_url_kwarg = "cohort"
    slug_field = "sodar_uuid"

    def get_success_url(self):
        return reverse("cohorts:list", kwargs={"project": self.object.project.sodar_uuid})

    def delete(self, request, *args, **kwargs):
        """Fall-back check if a user tries to delete a cohort that doesn't belong to him (unless it's a superuser).
        UI is designed in a way that users shouldn't reach this point, but you never know.
        """
        self.object = self.get_object()
        if self.object.user == request.user or request.user.is_superuser:
            messages.success(
                request, mark_safe("Cohort <strong>%s</strong> deleted." % self.object.name)
            )
            return super().delete(request, *args, **kwargs)
        messages.error(request, "Can't delete other user's cohort.")
        return HttpResponseRedirect(self.get_success_url())
