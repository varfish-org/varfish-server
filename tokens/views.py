import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
from django.urls import reverse
from knox.models import AuthToken

from projectroles.views import LoggedInPermissionMixin
from .forms import UserTokenCreateForm


class UserTokenListView(LoginRequiredMixin, LoggedInPermissionMixin, ListView):
    permission_required = "tokens.access"
    model = AuthToken
    template_name = "tokens/token_list.html"

    def get_queryset(self):
        """Only allow access to this user's query set."""
        return AuthToken.objects.filter(user=self.request.user)


class UserTokenCreateView(LoginRequiredMixin, LoggedInPermissionMixin, FormView):
    permission_required = "tokens.access"
    template_name = "tokens/token_create.html"
    form_class = UserTokenCreateForm

    def form_valid(self, form):
        ttl = datetime.timedelta(hours=form.clean().get("ttl")) or None
        context = self.get_context_data()
        _, context["token"] = AuthToken.objects.create(self.request.user, ttl)
        return render(self.request, "tokens/token_create_success.html", context)


class UserTokenDeleteView(LoginRequiredMixin, LoggedInPermissionMixin, DeleteView):
    permission_required = "tokens.access"
    model = AuthToken
    template_name = "tokens/token_confirm_delete.html"

    def get_success_url(self):
        return reverse("tokens:token-list")

    def get_queryset(self):
        """Only allow access to this user's query set."""
        return AuthToken.objects.filter(user=self.request.user)
