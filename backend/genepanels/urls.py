"""URL configuration for the ``genepanels`` app.
"""

from django.conf.urls import url

from genepanels import views

app_name = "genepanels"

ui_urlpatterns = [
    url(
        regex=r"^$",
        view=views.IndexView.as_view(),
        name="index",
    ),
    url(
        regex=r"^category/$",
        view=views.GenePanelCategoryListView.as_view(),
        name="category-list",
    ),
    url(
        regex=r"^category/create/$",
        view=views.GenePanelCategoryCreateView.as_view(),
        name="category-create",
    ),
    url(
        regex=r"^category/update/(?P<category>[0-9a-f-]+)$",
        view=views.GenePanelCategoryUpdateView.as_view(),
        name="category-update",
    ),
    url(
        regex=r"^category/(?P<category>[0-9a-f-]+)$",
        view=views.GenePanelCategoryDetailView.as_view(),
        name="category-detail",
    ),
    url(
        regex=r"^category/delete/(?P<category>[0-9a-f-]+)$",
        view=views.GenePanelCategoryDeleteView.as_view(),
        name="category-delete",
    ),
    url(
        regex=r"^panel/create/$",
        view=views.GenePanelCreateView.as_view(),
        name="genepanel-create",
    ),
    url(
        regex=r"^panel/update/(?P<panel>[0-9a-f-]+)$",
        view=views.GenePanelUpdateView.as_view(),
        name="genepanel-update",
    ),
    url(
        regex=r"^panel/(?P<panel>[0-9a-f-]+)$",
        view=views.GenePanelDetailView.as_view(),
        name="genepanel-detail",
    ),
    url(
        regex=r"^panel/delete/(?P<panel>[0-9a-f-]+)$",
        view=views.GenePanelDeleteView.as_view(),
        name="genepanel-delete",
    ),
    url(
        regex=r"^panel/copy-as-draft/(?P<panel>[0-9a-f-]+)$",
        view=views.GenePanelCopyAsDraftView.as_view(),
        name="genepanel-copy-as-draft",
    ),
    url(
        regex=r"^panel/release/(?P<panel>[0-9a-f-]+)$",
        view=views.GenePanelReleaseView.as_view(),
        name="genepanel-release",
    ),
    url(
        regex=r"^panel/retire/(?P<panel>[0-9a-f-]+)$",
        view=views.GenePanelRetireView.as_view(),
        name="genepanel-retire",
    ),
]

urlpatterns = ui_urlpatterns
