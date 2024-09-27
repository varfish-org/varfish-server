"""The views for the ``cases`` app.

The UI for this app is completely Vue-based so we only render the entry point.
"""

import json

from django.conf import settings
from django.forms.models import model_to_dict
from django.middleware.csrf import get_token
from django.views.generic import ListView
from projectroles.app_settings import AppSettingAPI
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from extra_annos.models import ExtraAnnoField
from variants.models import Case


class EntrypointView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of cohorts."""

    permission_required = "cases.view_data"
    template_name = "cases/entrypoint.html"
    model = Case

    def get_context_data(self, *args, **kwargs):
        setting_api = AppSettingAPI()
        context = super().get_context_data(*args, **kwargs)
        extra_anno_fields = self._get_extra_anno_fields()
        context["app_context"] = json.dumps(
            {
                "project": {
                    "sodar_uuid": str(context["project"].sodar_uuid),
                    "title": context["project"].title,
                },
                "base_url": "/cases/ajax/",
                "csrf_token": get_token(self.request),
                "user": {
                    "username": self.request.user.username,
                    "sodar_uuid": str(self.request.user.sodar_uuid),
                    "is_superuser": self.request.user.is_superuser,
                },
                "umd_predictor_api_token": setting_api.get(
                    "variants", "umd_predictor_api_token", user=self.request.user
                ),
                "ga4gh_beacon_network_widget_enabled": setting_api.get(
                    "variants", "ga4gh_beacon_network_widget_enabled", user=self.request.user
                ),
                "exomiser_enabled": settings.VARFISH_ENABLE_EXOMISER_PRIORITISER,
                "cadd_enabled": settings.VARFISH_ENABLE_CADD,
                "cada_enabled": settings.VARFISH_ENABLE_CADA,
                "extra_anno_fields": extra_anno_fields,
                "url_prefixes": {
                    "annonars": settings.VARFISH_BACKEND_URL_PREFIX_ANNONARS,
                    "mehari": settings.VARFISH_BACKEND_URL_PREFIX_MEHARI,
                    "viguno": settings.VARFISH_BACKEND_URL_PREFIX_VIGUNO,
                    "nginx": settings.VARFISH_BACKEND_URL_PREFIX_NGINX,
                },
            }
        )
        return context

    def _get_extra_anno_fields(self):
        def my_model_to_dict(field_obj):
            return model_to_dict(field_obj, fields=("field", "label"))

        return list(map(my_model_to_dict, ExtraAnnoField.objects.all()))
