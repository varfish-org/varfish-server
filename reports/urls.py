from django.conf.urls import url
from . import views

app_name = "reports"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/template/$",
        view=views.ReportTemplateListView.as_view(),
        name="template-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/template/create/$",
        view=views.ReportTemplateCreateView.as_view(),
        name="template-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/template/view/(?P<template>[0-9a-f-]+)/?$",
        view=views.ReportTemplateDetailView.as_view(),
        name="template-view",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/template/download/(?P<template>[0-9a-f-]+)/?$",
        view=views.ReportTemplateDownloadView.as_view(),
        name="template-download",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/template/update/(?P<template>[0-9a-f-]+)/?$",
        view=views.ReportTemplateUpdateView.as_view(),
        name="template-update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/template/delete/(?P<template>[0-9a-f-]+)/?$",
        view=views.ReportTemplateDeleteView.as_view(),
        name="template-delete",
    ),
]
