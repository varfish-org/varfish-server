"""User annotation--related urls."""
from django.conf.urls import url

from variants.views.ajax.annos import CaseUserAnnotatedVariantsAjaxView

ui_urlpatterns = []

ajax_urlpatterns = [
    url(
        regex=r"^ajax/smallvariant/user-annotated-case/(?P<case>[0-9a-f-]+)/?$",
        view=CaseUserAnnotatedVariantsAjaxView.as_view(),
        name="ajax-smallvariant-userannotatedcase",
    ),
]

api_urlpatterns = []

annos_ajax_urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
