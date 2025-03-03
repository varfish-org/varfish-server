from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, re_path
from django.views import View
from django.views import defaults as default_views
from django.views.generic import TemplateView
from djproxy.views import HttpProxy
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from projectroles.views import HomeView as ProjectRolesHomeView
from sentry_sdk import last_event_id


def handler500(request, *args, **argv):
    if request.user and "User" in str(type(request.user)):
        return render(request, "500.html", {"sentry_event_id": last_event_id()}, status=500)
    else:
        return HttpResponse(status=500)


# URL Patterns for SODAR Core
# ------------------------------------------------------------------------------

urlpatterns = [path("", ProjectRolesHomeView.as_view(), name="home")]
HomeView = ProjectRolesHomeView

# URL Patterns for VarFish
# ------------------------------------------------------------------------------

urlpatterns += [
    path("icons/", include("dj_iconify.urls")),
    path("variants/", include("variants.urls")),
    path("importer/", include("importer.urls")),
    path("svs/", include("svs.urls")),
    path("bgjobs/", include("bgjobs.urls")),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    # Your stuff: custom urls includes go here
    path("api/auth/", include("knox.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", auth_views.logout_then_login, name="logout"),
    # SODAR-core
    path("project/", include("projectroles.urls")),
    path("timeline/", include("timeline.urls")),
    path("admin_alerts/", include("adminalerts.urls")),
    path("app_alerts/", include("appalerts.urls")),
    path("siteinfo/", include("siteinfo.urls")),
    path("userprofile/", include("userprofile.urls")),
    path("tokens/", include("tokens.urls")),  # will go to SODAR-core
    # The rendered Sphinx-based manual.
    path("manual/", include("docs.urls")),
    path("su/", include("django_su.urls")),
    path("cohorts/", include("cohorts.urls")),
    path("beaconsite/", include("beaconsite.urls")),
    path("genepanels/", include("genepanels.urls")),
    path("vueapp/", include("varfish.vueapp.urls")),
    path("cases/", include("cases.urls")),
    path("varannos/", include("varannos.urls")),
    path("seqmeta/", include("seqmeta.urls")),
    path("cases-import/", include("cases_import.urls")),
    path("cases-qc/", include("cases_qc.urls")),
    path("cases-analysis/", include("cases_analysis.urls")),
    path("seqvars/", include("seqvars.urls")),
]

# URL Patterns for DRF Spectacular
# ------------------------------------------------------------------------------

urlpatterns += [
    # Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # UI
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


# URL Patterns for Proxies
# ------------------------------------------------------------------------------

urlpatterns += [
    # Augment url patterns with proxy for genomics england panelapp.
    re_path(
        r"proxy/panelapp/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url="https://panelapp.genomicsengland.co.uk/api/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    # Augment url patterns with proxy for variantvalidator.org.
    re_path(
        r"proxy/variantvalidator/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url="https://rest.variantvalidator.org/VariantValidator/variantvalidator/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    # Augment URL patterns with proxy for local services.
    re_path(
        r"proxy/varfish/annonars/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_ANNONARS,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    re_path(
        r"proxy/varfish/mehari/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_MEHARI,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    re_path(
        r"proxy/varfish/nginx/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_NGINX,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    # Augment url patterns with proxy for PubTator3
    re_path(
        r"proxy/remote/pubtator3-api/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url="https://www.ncbi.nlm.nih.gov/research/pubtator3-api/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    re_path(
        r"proxy/varfish/viguno/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_VIGUNO,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
]

# URL Patterns for Django Static Files
# ------------------------------------------------------------------------------

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# URL Patterns for Serving Frontend
# ------------------------------------------------------------------------------

if settings.SERVE_FRONTEND:

    class ServeStringView(View):
        def get(self, *args, **kwargs):
            _ = args
            _ = kwargs
            file_path = finders.find("vueapp/index.html")
            with open(file_path, "rt") as inputf:
                content = inputf.read()
                return HttpResponse(content, content_type="text/html")

    urlpatterns += [
        re_path(
            "^-.*",
            ServeStringView.as_view(),
            name="vueapp-entrypoint",
        )
    ]

# URL Patterns for Development
# ------------------------------------------------------------------------------

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
