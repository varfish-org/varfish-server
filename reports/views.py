from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import ModelFormMixin, CreateView, UpdateView, DeleteView
from projectroles.views import (
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
)

from .forms import ReportTemplateForm
from .models import ReportTemplate


class ReportTemplateListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    template_name = "reports/reporttemplate_list.html"
    permission_required = "reports.view_data"
    model = ReportTemplate

    def get_queryset(self):
        return super().get_queryset().filter(project__sodar_uuid=self.kwargs["project"])


class ReportTemplateDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    permission_required = "reports.view_data"
    template_name = "reports/reporttemplate_detail.html"
    model = ReportTemplate
    slug_url_kwarg = "template"
    slug_field = "sodar_uuid"


class ReportTemplateDownloadView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    permission_required = "reports.view_data"
    template_name = "reports/reporttemplate_detail.html"
    model = ReportTemplate
    slug_url_kwarg = "template"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        template = self.get_object()
        response = HttpResponse(
            b"",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % template.filename
        return response


class ReportTemplateModifyMixin(ModelFormMixin):
    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["project"] = self.get_project()
        return result

    def form_valid(self, form):
        import pdb

        pdb.set_trace()
        form.save()
        form_action = "update" if self.object else "create"
        messages.success(self.request, "Report template {}d.".format(form_action))
        return redirect(
            reverse(
                "reports:template-view",
                kwargs={
                    "project": self.get_project().sodar_uuid,
                    "template": form.instance.sodar_uuid,
                },
            )
        )


class ReportTemplateCreateView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    ReportTemplateModifyMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    CreateView,
):

    permission_required = "reports.add_data"
    template_name = "reports/reporttemplate_form.html"
    model = ReportTemplate
    slug_url_kwarg = "template"
    slug_field = "sodar_uuid"
    form_class = ReportTemplateForm


class ReportTemplateUpdateView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    ReportTemplateModifyMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    UpdateView,
):
    permission_required = "reports.update_data"
    template_name = "reports/reporttemplate_form.html"
    model = ReportTemplate
    slug_url_kwarg = "template"
    slug_field = "sodar_uuid"
    form_class = ReportTemplateForm


class ReportTemplateDeleteView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    DeleteView,
):
    permission_required = "reports.delete_data"
    model = ReportTemplate
    slug_url_kwarg = "template"
    slug_field = "sodar_uuid"

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Report template deleted.")
        return reverse("reports:template-list", kwargs={"project": self.get_project().sodar_uuid})
