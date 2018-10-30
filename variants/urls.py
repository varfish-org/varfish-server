from django.conf.urls import url
from . import views


app_name = "variants"
urlpatterns = [
    url(regex=r"^(?P<project>[0-9a-f-]+)$", view=views.MainView.as_view(), name="case"),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/case/(?P<case>[0-9a-f-]+)/$",
        view=views.FilterView.as_view(),
        name="filter",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/api/extend/(?P<release>(GRCh37|GRCh38))-(?P<chromosome>(chr)?([0-9]{1,2}|[XY]|MT]))-(?P<position>[0-9]+)-(?P<reference>[ACGT]+)-(?P<alternative>[ACGT]+)/$",
        view=views.ExtendAPIView.as_view(),
        name="extend",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/export-job/resubmit/(?P<job>[0-9a-f-]+)/$",
        view=views.ExportFileJobResubmitView.as_view(),
        name="export-job-resubmit",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/export-job/view/(?P<job>[0-9a-f-]+)/$",
        view=views.ExportFileJobDetailView.as_view(),
        name="export-job-view",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/export-job/download/(?P<job>[0-9a-f-]+)/$",
        view=views.ExportFileJobDownloadView.as_view(),
        name="export-job-download",
    ),
]
