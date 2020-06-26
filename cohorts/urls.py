"""URL configuration for the ``importer`` app.
"""

from django.conf.urls import url
from . import views

app_name = "cohorts"

urlpatterns = [
    url(regex=r"^(?P<project>[0-9a-f-]+)/$", view=views.CohortView.as_view(), name="list",),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/create/$",
        view=views.CohortCreateView.as_view(),
        name="create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/update/(?P<cohort>[0-9a-f-]+)$",
        view=views.CohortUpdateView.as_view(),
        name="update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/delete/(?P<cohort>[0-9a-f-]+)$",
        view=views.CohortDeleteView.as_view(),
        name="delete",
    ),
]
