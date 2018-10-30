from django.conf.urls import url
from . import views

app_name = "bgjobs"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)$",
        view=views.ProjectBackgroundJobView.as_view(),
        name="job-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/clear/own$",
        view=views.BackgroundJobClearOwnView.as_view(),
        name="clear-own",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/clear/all$",
        view=views.BackgroundJobClearAllView.as_view(),
        name="clear-all",
    ),
]
