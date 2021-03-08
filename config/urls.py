from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import defaults as default_views

from httpproxy.views import HttpProxy
from projectroles.views import HomeView as ProjectRolesHomeView
from variants.views import KioskHomeView
from sentry_sdk import last_event_id


def handler500(request, *args, **argv):
    return render(request, "500.html", {"sentry_event_id": last_event_id()}, status=500)


# The functionality differs greatly depending on whether kiosk mode is enabled or not. However, the URL patterns
# do not need to.
if settings.KIOSK_MODE:
    urlpatterns = [
        url(r"^$", KioskHomeView.as_view(), name="kiosk-upload"),
        url(r"^real-home/$", ProjectRolesHomeView.as_view(), name="home"),
    ]
else:
    urlpatterns = [url(r"^$", ProjectRolesHomeView.as_view(), name="home")]
    HomeView = ProjectRolesHomeView

urlpatterns += [
    #    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r"^geneinfo/", include("geneinfo.urls")),
    url(r"^variants/", include("variants.urls")),
    url(r"^importer/", include("importer.urls")),
    url(r"^svs/", include("svs.urls")),
    url(r"^bgjobs/", include("bgjobs.urls")),
    url(r"^about/$", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    # User management
    # url(r'^users/', include('varfish.users.urls', namespace='users')),
    # Your stuff: custom urls includes go here
    url(r"api/auth/", include("knox.urls")),
    url(r"^login/$", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    url(r"^logout/$", auth_views.logout_then_login, name="logout"),
    # SODAR-core
    url(r"^project/", include("projectroles.urls")),
    url(r"^timeline/", include("timeline.urls")),
    url(r"^alerts/", include("adminalerts.urls")),
    url(r"^siteinfo/", include("siteinfo.urls")),
    url(r"^userprofile/", include("userprofile.urls")),
    url(r"^tokens/", include("tokens.urls")),  # will go to SODAR-core
    # The rendered Sphinx-based manual.
    url(r"^manual/", include("docs.urls")),
    url(r"^su/", include("django_su.urls")),
    url(r"^cohorts/", include("cohorts.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Augment with URLs for Beacon site.
if settings.VARFISH_ENABLE_BEACON_SITE:
    urlpatterns += [
        url(r"^beaconsite/", include("beaconsite.urls")),
    ]

# Augment url patterns with proxy for genomics england panelapp.
urlpatterns += [
    url(
        r"^proxy/panelapp/(?P<url>.*)$",
        HttpProxy.as_view(base_url="https://panelapp.genomicsengland.co.uk/api"),
    )
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r"^400/$", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        url(
            r"^403/$",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        url(
            r"^404/$",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        url(r"^500/$", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
