from django.conf.urls import url

from cases import views, views_ajax, views_api

app_name = "cases"
ui_urlpatterns = [
    url(
        regex=r"^vueapp/(?P<project>[0-9a-f-]+)/?$",
        view=views.EntrypointView.as_view(),
        name="entrypoint",
    ),
]

ajax_urlpatterns = [
    url(
        regex=r"^ajax/case/list/(?P<project>[0-9a-f-]+)/?$",
        view=views_ajax.CaseListAjaxView.as_view(),
        name="ajax-case-list",
    ),
    url(
        regex=r"^ajax/case/update/(?P<case>[0-9a-f-]+)/?$",
        view=views_ajax.CaseUpdateAjaxView.as_view(),
        name="ajax-case-update",
    ),
    url(
        regex=r"^ajax/case-comment/list/(?P<case>[0-9a-f-]+)/?$",
        view=views_ajax.CaseCommentListAjaxView.as_view(),
        name="ajax-casecomment-list",
    ),
    url(
        regex=r"^ajax/case-gene-annotation/list/(?P<case>[0-9a-f-]+)/?$",
        view=views_ajax.CaseGeneAnnotationListAjaxView.as_view(),
        name="ajax-casegeneannotation-list",
    ),
    url(
        regex=r"ajax/user-permissions/(?P<project>[0-9a-f-]+)/?$",
        view=views_ajax.ProjectUserPermissionsAjaxView.as_view(),
        name="ajax-userpermissions",
    ),
]

api_urlpatterns = [
    url(
        regex=r"^api/case/list/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.CaseListApiView.as_view(),
        name="api-case-list",
    ),
    url(
        regex=r"^api/case/update/(?P<case>[0-9a-f-]+)/?$",
        view=views_api.CaseUpdateApiView.as_view(),
        name="api-case-update",
    ),
    url(
        regex=r"^api/case-comment/list/(?P<case>[0-9a-f-]+)/?$",
        view=views_api.CaseCommentListApiView.as_view(),
        name="api-casecomment-list",
    ),
    url(
        regex=r"^api/case-gene-annotation/list/(?P<case>[0-9a-f-]+)/?$",
        view=views_ajax.CaseGeneAnnotationListAjaxView.as_view(),
        name="api-casegeneannotation-list",
    ),
]


urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
