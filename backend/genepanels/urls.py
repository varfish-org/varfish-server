"""URL configuration for the ``genepanels`` app.
"""

from django.urls import path

from genepanels import views, views_api

app_name = "genepanels"

ui_urlpatterns = [
    path(
        "",
        view=views.IndexView.as_view(),
        name="index",
    ),
    path(
        "category/",
        view=views.GenePanelCategoryListView.as_view(),
        name="category-list",
    ),
    path(
        "category/create/",
        view=views.GenePanelCategoryCreateView.as_view(),
        name="category-create",
    ),
    path(
        "category/update/<uuid:category>/",
        view=views.GenePanelCategoryUpdateView.as_view(),
        name="category-update",
    ),
    path(
        "category/<uuid:category>/",
        view=views.GenePanelCategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "category/delete/<uuid:category>/",
        view=views.GenePanelCategoryDeleteView.as_view(),
        name="category-delete",
    ),
    path(
        "panel/create/",
        view=views.GenePanelCreateView.as_view(),
        name="genepanel-create",
    ),
    path(
        "panel/update/<uuid:panel>/",
        view=views.GenePanelUpdateView.as_view(),
        name="genepanel-update",
    ),
    path(
        "panel/<uuid:panel>/",
        view=views.GenePanelDetailView.as_view(),
        name="genepanel-detail",
    ),
    path(
        "panel/delete/<uuid:panel>/",
        view=views.GenePanelDeleteView.as_view(),
        name="genepanel-delete",
    ),
    path(
        "panel/copy-as-draft/<uuid:panel>/",
        view=views.GenePanelCopyAsDraftView.as_view(),
        name="genepanel-copy-as-draft",
    ),
    path(
        "panel/release/<uuid:panel>/",
        view=views.GenePanelReleaseView.as_view(),
        name="genepanel-release",
    ),
    path(
        "panel/retire/<uuid:panel>/",
        view=views.GenePanelRetireView.as_view(),
        name="genepanel-retire",
    ),
]

api_patterns = [
    path(
        "api/genepanel-category/list/",
        view=views_api.GenePanelCategoryListApiView.as_view(),
        name="genepanel-category-list",
    ),
    path(
        "api/lookup-genepanel/",
        view=views_api.LookupGenePanelApiView.as_view(),
        name="lookup-genepanel",
    ),
]

urlpatterns = ui_urlpatterns + api_patterns
