from django.conf import settings
from django.urls import path, re_path
from djproxy.views import HttpProxy

from svs import views

app_name = "svs"

urlpatterns_ui = [
    # Views related to background SV jobs.
    path(
        "<uuid:project>/import/<uuid:job>/",
        view=views.ImportStructuralVariantsJobDetailView.as_view(),
        name="import-job-detail",
    ),
    path(
        "build-bg-sv/<uuid:job>/",
        view=views.BuildBackgroundSvSetJobDetailView.as_view(),
        name="build-bg-sv-set-job-detail",
    ),
    path(
        "cleanup-bg-sv/<uuid:job>/",
        view=views.CleanupBackgroundSvSetJobDetailView.as_view(),
        name="cleanup-bg-sv-set-job-detail",
    ),
]

urlpatterns_ajax = [
    path(
        "ajax/fetch-variants/<uuid:case>/",
        view=views.SvFetchVariantsAjaxView.as_view(),
        name="ajax-variants-fetch",
    ),
    path(
        "ajax/query-case/quick-presets/",
        view=views.SvQuickPresetsAjaxView.as_view(),
        name="ajax-quick-presets",
    ),
    path(
        "ajax/query-case/category-presets/<str:category>/",
        view=views.SvCategoryPresetsApiView.as_view(),
        name="ajax-category-presets",
    ),
    path(
        "ajax/query-case/inheritance-presets/<uuid:case>/",
        view=views.SvInheritancePresetsApiView.as_view(),
        name="ajax-inheritance-presets",
    ),
    # URLs for ``svs.queries.presets``
    path(
        "ajax/query-case/query-settings-shortcut/<uuid:case>/",
        view=views.SvQuerySettingsShortcutAjaxView.as_view(),
        name="ajax-svquerysettings-shortcut",
    ),
    # URLs for ``svs.queries.results``
    path(
        "ajax/sv-query/list-create/<uuid:case>/",
        view=views.SvQueryListCreateAjaxView.as_view(),
        name="ajax-svquery-listcreate",
    ),
    path(
        "ajax/sv-query/retrieve-update-destroy/<uuid:svquery>/",
        view=views.SvQueryRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-svquery-retrieveupdatedestroy",
    ),
    path(
        "sv-query-result-set/list/<uuid:svquery>/",
        view=views.SvQueryResultSetListAjaxView.as_view(),
        name="ajax-svqueryresultset-list",
    ),
    path(
        "sv-query-result-set/retrieve/<uuid:svqueryresultset>/",
        view=views.SvQueryResultSetRetrieveAjaxView.as_view(),
        name="ajax-svqueryresultset-retrieve",
    ),
    path(
        "sv-query-result-row/list/<uuid:svqueryresultset>/",
        view=views.SvQueryResultRowListAjaxView.as_view(),
        name="ajax-svqueryresultrow-list",
    ),
    path(
        "sv-query-result-row/retrieve/<uuid:svqueryresultrow>/",
        view=views.SvQueryResultRowRetrieveAjaxView.as_view(),
        name="ajax-svqueryresultrow-retrieve",
    ),
    # URLs user annotations (flags, comments)
    path(
        "ajax/structural-variant-flags/list-create/<uuid:case>/",
        view=views.StructuralVariantFlagsListCreateAjaxView.as_view(),
        name="ajax-structuralvariantflags-listcreate",
    ),
    path(
        "ajax/structural-variant-flags/list-project/<uuid:project>/",
        view=views.StructuralVariantFlagsListProjectAjaxView.as_view(),
        name="ajax-structuralvariantflags-listproject",
    ),
    path(
        "ajax/structural-variant-flags/retrieve-update-destroy/<uuid:structuralvariantflags>/",
        view=views.StructuralVariantFlagsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-structuralvariantflags-retrieveupdatedestroy",
    ),
    path(
        "ajax/structural-variant-comment/list-create/<uuid:case>/",
        view=views.StructuralVariantCommentListCreateAjaxView.as_view(),
        name="ajax-structuralvariantcomment-listcreate",
    ),
    path(
        "ajax/structural-variant-comment/list-project/<uuid:project>/",
        view=views.StructuralVariantCommentListProjectAjaxView.as_view(),
        name="ajax-structuralvariantcomment-listproject",
    ),
    path(
        "ajax/structural-variant-comment/retrieve-update-destroy/<uuid:structuralvariantcomment>/",
        view=views.StructuralVariantCommentRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-structuralvariantcomment-retrieveupdatedestroy",
    ),
    path(
        "ajax/structural-variant-acmg-rating/list-create/<uuid:case>/",
        view=views.StructuralVariantAcmgRatingListCreateAjaxView.as_view(),
        name="ajax-structuralvariantacmgrating-listcreate",
    ),
    path(
        "ajax/structural-variant-acmg-rating/list-project/<uuid:project>/",
        view=views.StructuralVariantAcmgRatingListProjectAjaxView.as_view(),
        name="ajax-structuralvariantacmgrating-listproject",
    ),
    path(
        "ajax/structural-variant-acmg-rating/retrieve-update-destroy/<uuid:structuralvariantacmgrating>/",
        view=views.StructuralVariantAcmgRatingRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-structuralvariantacmgrating-retrieveupdatedestroy",
    ),
    # Augment url patterns with proxy to worker.
    re_path(
        r"^worker/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=f"{settings.WORKER_REST_BASE_URL}/public/svs/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    re_path(
        r"^tracks/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=f"{settings.WORKER_REST_BASE_URL}/public/tracks/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
]

urlpatterns_api = []

urlpatterns = urlpatterns_ui + urlpatterns_ajax + urlpatterns_api
