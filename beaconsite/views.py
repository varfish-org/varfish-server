from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, ModelFormMixin
from projectroles.views import (
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
    LoggedInPermissionMixin,
)

from .forms import ConsortiumForm, SiteForm
from .models import Consortium, Site


class IndexView(
    LoginRequiredMixin, LoggedInPermissionMixin, TemplateView,
):
    """Display entry point into site-wide app."""

    permission_required = "beaconsite.view_data"
    template_name = "beaconsite/index.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["site_list"] = Site.objects.all()[:5]
        result["consortium_list"] = Consortium.objects.all()[:5]
        return result


class ConsortiumListView(
    LoginRequiredMixin, LoggedInPermissionMixin, ListView,
):
    """Display list of ``Consortium`` records."""

    permission_required = "beaconsite.view_data"
    template_name = "beaconsite/consortium_list.html"
    model = Consortium


class ConsortiumDetailView(
    LoginRequiredMixin, LoggedInPermissionMixin, DetailView,
):
    """Detail view of ``Site`` record."""

    permission_required = "beaconsite.view_data"
    template_name = "beaconsite/consortium_detail.html"
    model = Consortium
    slug_url_kwarg = "consortium"
    slug_field = "sodar_uuid"


class ConsortiumModifyMixin(ModelFormMixin):
    def form_valid(self, form):
        form.save()
        form_action = "update" if self.object else "create"
        messages.success(self.request, "Consortium {}d.".format(form_action))
        return redirect(
            reverse("beaconsite:consortium-detail", kwargs={"consortium": form.instance.sodar_uuid})
        )


class ConsortiumCreateView(
    LoginRequiredMixin, ConsortiumModifyMixin, LoggedInPermissionMixin, CreateView
):

    permission_required = "beaconsite.add_data"
    template_name = "beaconsite/consortium_form.html"
    model = Consortium
    slug_url_kwarg = "consortium"
    slug_field = "sodar_uuid"
    form_class = ConsortiumForm


class ConsortiumUpdateView(
    LoginRequiredMixin, ConsortiumModifyMixin, LoggedInPermissionMixin, UpdateView
):
    permission_required = "beaconsite.update_data"
    template_name = "beaconsite/consortium_form.html"
    model = Consortium
    slug_url_kwarg = "consortium"
    slug_field = "sodar_uuid"
    form_class = ConsortiumForm


class ConsortiumDeleteView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DeleteView,
):
    permission_required = "beaconsite.delete_data"
    model = Consortium
    slug_url_kwarg = "consortium"
    slug_field = "sodar_uuid"

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Consortium deleted.")
        return reverse("beaconsite:consortium-list")


class SiteListView(
    LoginRequiredMixin, LoggedInPermissionMixin, ListView,
):
    """Display list of ``Site`` records."""

    permission_required = "beaconsite.view_data"
    template_name = "beaconsite/site_list.html"
    model = Site


class SiteDetailView(
    LoginRequiredMixin, LoggedInPermissionMixin, DetailView,
):
    """Detail view of ``Site`` record."""

    permission_required = "beaconsite.view_data"
    template_name = "beaconsite/site_detail.html"
    model = Site
    slug_url_kwarg = "site"
    slug_field = "sodar_uuid"


class SiteModifyMixin(ModelFormMixin):
    def form_valid(self, form):
        form.save()
        form_action = "update" if self.object else "create"
        messages.success(self.request, "Site {}d.".format(form_action))
        return redirect(
            reverse("beaconsite:site-detail", kwargs={"site": form.instance.sodar_uuid})
        )


class SiteCreateView(LoginRequiredMixin, SiteModifyMixin, LoggedInPermissionMixin, CreateView):
    permission_required = "beaconsite.add_data"
    template_name = "beaconsite/site_form.html"
    model = Consortium
    slug_url_kwarg = "site"
    slug_field = "sodar_uuid"
    form_class = SiteForm


class SiteUpdateView(LoginRequiredMixin, SiteModifyMixin, LoggedInPermissionMixin, UpdateView):
    permission_required = "beaconsite.update_data"
    template_name = "beaconsite/site_form.html"
    model = Site
    slug_url_kwarg = "site"
    slug_field = "sodar_uuid"
    form_class = SiteForm


class SiteDeleteView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DeleteView,
):
    permission_required = "beaconsite.delete_data"
    model = Site
    slug_url_kwarg = "site"
    slug_field = "sodar_uuid"

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Site deleted.")
        return reverse("beaconsite:site-list")
