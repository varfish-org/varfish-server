from django.conf.urls import url

from svs import views

app_name = "svs"

urlpatterns_ui = [
    # Views related to background SV jobs.
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/import/(?P<job>[0-9a-f-]+)/$",
        view=views.ImportStructuralVariantsJobDetailView.as_view(),
        name="import-job-detail",
    ),
    url(
        regex=r"^build-bg-sv/(?P<job>[0-9a-f-]+)/$",
        view=views.BuildBackgroundSvSetJobDetailView.as_view(),
        name="build-bg-sv-set-job-detail",
    ),
    url(
        regex=r"^cleanup-bg-sv/(?P<job>[0-9a-f-]+)/$",
        view=views.CleanupBackgroundSvSetJobDetailView.as_view(),
        name="cleanup-bg-sv-set-job-detail",
    ),
]

urlpatterns_ajax = [
    url(
        regex=r"^ajax/query-case/quick-presets/?$",
        view=views.SvQuickPresetsAjaxView.as_view(),
        name="ajax-quick-presets",
    ),
    url(
        regex=r"^ajax/query-case/category-presets/(?P<category>[a-zA-Z0-9\._-]+)/?$",
        view=views.SvCategoryPresetsApiView.as_view(),
        name="ajax-category-presets",
    ),
    url(
        regex=r"^ajax/query-case/inheritance-presets/(?P<case>[0-9a-f-]+)/?$",
        view=views.SvInheritancePresetsApiView.as_view(),
        name="ajax-inheritance-presets",
    ),
    # URLs for ``svs.queries.presets``
    url(
        regex=r"^ajax/query-case/query-settings-shortcut/(?P<case>[0-9a-f-]+)/$",
        view=views.SvQuerySettingsShortcutAjaxView.as_view(),
        name="ajax-svquerysettings-shortcut",
    ),
    # URLs for ``svs.queries.results``
    url(
        regex=r"^ajax/sv-query/list-create/(?P<case>[0-9a-f-]+)/$",
        view=views.SvQueryListCreateAjaxView.as_view(),
        name="ajax-svquery-listcreate",
    ),
    url(
        regex=r"^ajax/sv-query/retrieve-update-destroy/(?P<svquery>[0-9a-f-]+)/$",
        view=views.SvQueryRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-svquery-retrieveupdatedestroy",
    ),
    url(
        regex=r"^sv-query-result-set/list/(?P<svquery>[0-9a-f-]+)/$",
        view=views.SvQueryResultSetListAjaxView.as_view(),
        name="ajax-svqueryresultset-list",
    ),
    url(
        regex=r"^sv-query-result-set/retrieve/(?P<svqueryresultset>[0-9a-f-]+)/$",
        view=views.SvQueryResultSetRetrieveAjaxView.as_view(),
        name="ajax-svqueryresultset-retrieve",
    ),
    url(
        regex=r"^sv-query-result-row/list/(?P<svqueryresultset>[0-9a-f-]+)/$",
        view=views.SvQueryResultRowListAjaxView.as_view(),
        name="ajax-svqueryresultrow-list",
    ),
    url(
        regex=r"^sv-query-result-row/list/(?P<svqueryresultset>[0-9a-f-]+)/$",
        view=views.SvQueryResultRowListAjaxView.as_view(),
        name="ajax-svqueryresultrow-list",
    ),
    # URLs user annotations (flags, comments)
    url(
        regex=r"^ajax/structural-variant-flags/list-create/(?P<case>[0-9a-f-]+)/$",
        view=views.StructuralVariantFlagsListCreateAjaxView.as_view(),
        name="ajax-structuralvariantflags-listcreate",
    ),
    url(
        regex=r"^ajax/structural-variant-flags/retrieve-update-destroy/(?P<structuralvariantflags>[0-9a-f-]+)/$",
        view=views.StructuralVariantFlagsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-structuralvariantflags-retrieveupdatedestroy",
    ),
    url(
        regex=r"^ajax/structural-variant-comment/list-create/(?P<case>[0-9a-f-]+)/$",
        view=views.StructuralVariantCommentListCreateAjaxView.as_view(),
        name="ajax-structuralvariantcomment-listcreate",
    ),
    url(
        regex=r"^ajax/structural-variant-comment/retrieve-update-destroy/(?P<structuralvariantcomment>[0-9a-f-]+)/$",
        view=views.StructuralVariantCommentRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-structuralvariantcomment-retrieveupdatedestroy",
    ),
]

urlpatterns_api = []

urlpatterns = urlpatterns_ui + urlpatterns_ajax + urlpatterns_api
