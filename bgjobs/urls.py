from django.conf.urls import url
from . import views

app_name = "bgjobs"
urlpatterns = [
    url(regex=r"^(?P<project>[0-9a-f-]+)$", view=views.JobListView.as_view(), name="job-list")
]
