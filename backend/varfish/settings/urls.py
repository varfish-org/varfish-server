from django.conf.urls import url

from varfish.settings import views_api

urlpatterns = [
    url(
        regex=r"^api/site/?$",
        view=views_api.SiteSettingsRetrieveUpdateAPIView.as_view(),
        name="api-site-settings-retrieve-update",
    ),
    url(
        regex=r"^api/user/?$",
        view=views_api.UserSettingsRetrieveUpdateAPIView.as_view(),
        name="api-user-settings-retrieve-update",
    ),
    url(
        regex=r"^api/project/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.ProjectSettingsRetrieveUpdateAPIView.as_view(),
        name="api-project-settings-retrieve-update",
    ),
    url(
        regex=r"^api/project-user/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.ProjectUserSettingsRetrieveUpdateAPIView.as_view(),
        name="api-project-user-settings-retrieve-update",
    ),
]
