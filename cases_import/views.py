from django.views.generic import TemplateView
from projectroles.views import LoggedInPermissionMixin, LoginRequiredMixin


class IndexView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    TemplateView,
):
    permission_required = "cases_import.view_data"
    template_name = "cases_import/index.html"
