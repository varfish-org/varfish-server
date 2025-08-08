"""User annotation--related urls."""

from django.urls import path

from variants.views.ajax.annos import CaseUserAnnotatedVariantsAjaxView

ui_urlpatterns = []

ajax_urlpatterns = [
    path(
        "ajax/smallvariant/user-annotated-case/<uuid:case>/",
        view=CaseUserAnnotatedVariantsAjaxView.as_view(),
        name="ajax-smallvariant-userannotatedcase",
    ),
]

api_urlpatterns = []

annos_ajax_urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
