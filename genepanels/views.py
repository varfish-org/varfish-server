import uuid

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from django.views.generic.edit import CreateView, DeleteView, ModelFormMixin, UpdateView
from projectroles.views import LoggedInPermissionMixin, LoginRequiredMixin, ProjectContextMixin

from genepanels.forms import GenePanelCategoryForm, GenePanelForm
from genepanels.models import GenePanel, GenePanelCategory, GenePanelState


class IndexView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    TemplateView,
):
    """Display entry point into site-wide app."""

    permission_required = "genepanels.view_data"
    template_name = "genepanels/index.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["object_list"] = GenePanelCategory.objects.all()[:5]
        result["show_retired"] = False
        return result


class GenePanelCategoryListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ListView,
):
    """Display entry point into site-wide app."""

    permission_required = "genepanels.view_data"
    model = GenePanelCategory
    template_name = "genepanels/category_list.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["object_list"] = GenePanelCategory.objects.all()[:5]
        result["show_retired"] = "show_retired" in self.request.GET
        return result

    def get_queryset(self):
        return super().get_queryset().prefetch_related("genepanel_set")


class GenePanelCategoryModifyMixin(ModelFormMixin):
    def form_valid(self, form):
        form.save()
        form_action = "update" if self.object else "create"
        messages.success(self.request, f"Gene panel category {form_action}d.")
        return redirect(
            reverse("genepanels:category-detail", kwargs={"category": form.instance.sodar_uuid})
        )


class GenePanelCategoryDetailView(LoginRequiredMixin, LoggedInPermissionMixin, DetailView):
    permission_required = "genepanels.view_data"
    template_name = "genepanels/category_detail.html"
    model = GenePanelCategory
    slug_url_kwarg = "category"
    slug_field = "sodar_uuid"


class GenePanelCategoryCreateView(
    LoginRequiredMixin, GenePanelCategoryModifyMixin, LoggedInPermissionMixin, CreateView
):
    permission_required = "beaconsite.add_data"
    template_name = "genepanels/category_form.html"
    model = GenePanelCategory
    slug_url_kwarg = "category"
    slug_field = "sodar_uuid"
    form_class = GenePanelCategoryForm


class GenePanelCategoryUpdateView(
    LoginRequiredMixin, GenePanelCategoryModifyMixin, LoggedInPermissionMixin, UpdateView
):
    permission_required = "genepanels.update_data"
    template_name = "genepanels/category_form.html"
    model = GenePanelCategory
    slug_url_kwarg = "category"
    slug_field = "sodar_uuid"
    form_class = GenePanelCategoryForm


class GenePanelCategoryDeleteView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DeleteView
):
    template_name = "genepanels/category_confirm_delete.html"
    permission_required = "genepanels.delete_data"
    model = GenePanelCategory
    slug_url_kwarg = "category"
    slug_field = "sodar_uuid"

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Gene panel category deleted.")
        return reverse("genepanels:category-list")


class GenePanelModifyMixin(ModelFormMixin):
    def form_valid(self, form):
        form.save()
        form_action = "update" if self.object else "create"
        messages.success(self.request, f"Gene panel category {form_action}d.")
        return redirect(
            reverse("genepanels:genepanel-detail", kwargs={"panel": form.instance.sodar_uuid})
        )


class GenePanelDetailView(LoginRequiredMixin, LoggedInPermissionMixin, DetailView):
    permission_required = "genepanels.view_data"
    template_name = "genepanels/genepanel_detail.html"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"


class GenePanelCreateView(
    LoginRequiredMixin, GenePanelModifyMixin, LoggedInPermissionMixin, CreateView
):
    permission_required = "beaconsite.add_data"
    template_name = "genepanels/genepanel_form.html"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"
    form_class = GenePanelForm

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        if "category" in self.request.GET:
            result["initial"]["category"] = self.request.GET["category"]
        return result


class GenePanelUpdateView(
    LoginRequiredMixin, GenePanelModifyMixin, LoggedInPermissionMixin, UpdateView
):
    permission_required = "genepanels.update_data"
    template_name = "genepanels/genepanel_form.html"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"
    form_class = GenePanelForm

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["initial"]["category"] = self.object.category.sodar_uuid
        return result


class GenePanelDeleteView(
    LoginRequiredMixin, LoggedInPermissionMixin, ProjectContextMixin, DeleteView
):
    template_name = "genepanels/genepanel_confirm.html"
    permission_required = "genepanels.delete_data"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["action"] = "delete"
        return result

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.state != GenePanelState.DRAFT.value:
            messages.error(self.request, "You can only delete gene panels in draft state.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.state != GenePanelState.DRAFT.value:
            messages.error(self.request, "You can only delete gene panels in draft state.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Gene panel draft deleted.")
        return reverse("genepanels:category-list")


class GenePanelReleaseView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    SingleObjectTemplateResponseMixin,
    BaseDetailView,
):
    template_name = "genepanels/genepanel_confirm.html"
    permission_required = "genepanels.update_data"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["action"] = "release"
        current_active = GenePanel.objects.filter(
            identifier=self.object.identifier, state=GenePanelState.ACTIVE.value
        )
        result["old_object"] = current_active[0] if current_active else None
        return result

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.state != GenePanelState.DRAFT.value:
            messages.error(self.request, "You can only release gene panels in draft state.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.state != GenePanelState.DRAFT.value:
            messages.error(self.request, "You can only release gene panels in draft state.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            for panel in GenePanel.objects.filter(
                identifier=self.object.identifier, state=GenePanelState.ACTIVE.value
            ):
                panel.state = GenePanelState.RETIRED.value
                panel.save()
            self.object.state = GenePanelState.ACTIVE.value
            self.object.signed_off_by = request.user
            self.object.save()
            return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Gene panel has been released.")
        return reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})


class GenePanelRetireView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    SingleObjectTemplateResponseMixin,
    BaseDetailView,
):
    template_name = "genepanels/genepanel_confirm.html"
    permission_required = "genepanels.update_data"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["action"] = "retire"
        return result

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.state != GenePanelState.ACTIVE.value:
            messages.error(self.request, "You can only retire active gene panels.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.state != GenePanelState.ACTIVE.value:
            messages.error(self.request, "You can only retire active gene panels.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            self.object.state = GenePanelState.RETIRED.value
            self.object.save()
            return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Gene panel has been retired.")
        return reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})


class GenePanelCopyAsDraftView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    SingleObjectTemplateResponseMixin,
    BaseDetailView,
):
    template_name = "genepanels/genepanel_confirm.html"
    permission_required = "genepanels.update_data"
    model = GenePanel
    slug_url_kwarg = "panel"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["action"] = "copy-as-draft"
        return result

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        old_objects = GenePanel.objects.filter(
            identifier=self.object.identifier, state=GenePanelState.DRAFT.value
        )
        if old_objects:
            messages.error(self.request, "There already is a draft for this gene panel.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": old_objects[0].sodar_uuid})
            )
        else:
            return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        current_draft = GenePanel.objects.filter(
            identifier=self.object.identifier, state=GenePanelState.DRAFT.value
        )
        if current_draft:
            messages.error(self.request, "There already is a draft for this gene panel.")
            return redirect(
                reverse("genepanels:genepanel-detail", kwargs={"panel": self.object.sodar_uuid})
            )
        else:
            self.object_copy = self._copy_as_draft(self.object)
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Override for redirecting alert list view with message"""
        messages.success(self.request, "Gene panel copied as draft.")
        return reverse("genepanels:genepanel-detail", kwargs={"panel": self.object_copy.sodar_uuid})

    def _copy_as_draft(self, object):
        """Copy the given GenePanel in 'object' and return the copy."""
        # See https://docs.djangoproject.com/en/4.1/topics/db/queries/#copying-model-instances on copying objects.
        panel_copy = GenePanel.objects.get(sodar_uuid=object.sodar_uuid)
        panel_copy.pk = None
        panel_copy.sodar_uuid = uuid.uuid4()
        panel_copy._state.adding = True
        panel_copy.version_minor += 1
        panel_copy.state = GenePanelState.DRAFT.value
        panel_copy.signed_off_by = None
        panel_copy.save()
        # Copy over all panel entries
        for entry in object.genepanelentry_set.all():
            entry_copy = entry
            entry_copy.sodar_uuid = uuid.uuid4()
            entry_copy.pk = None
            entry_copy._state.adding = True
            entry_copy.panel = panel_copy
            entry_copy.save()
        return panel_copy
