from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
import django_saml2_auth.views
from djproxy.views import HttpProxy
from projectroles.views import HomeView as ProjectRolesHomeView
from sentry_sdk import last_event_id


def handler500(request, *args, **argv):
    if request.user and "User" in str(type(request.user)):
        return render(request, "500.html", {"sentry_event_id": last_event_id()}, status=500)
    else:
        return HttpResponse(status=500)


# URL Patterns for SAML / Logins
# ------------------------------------------------------------------------------

urlpatterns = [
    # These are the SAML2 related URLs. You can change "^saml2_auth/" regex to
    # any path you want, like "^sso_auth/", "^sso_login/", etc. (required)
    url(r"^saml2_auth/", include("django_saml2_auth.urls")),
    # The following line will replace the default user login with SAML2 (optional)
    # If you want to specific the after-login-redirect-URL, use parameter "?next=/the/path/you/want"
    # with this view.
    url(r"^sso/login/$", django_saml2_auth.views.signin),
    # The following line will replace the admin login with SAML2 (optional)
    # If you want to specific the after-login-redirect-URL, use parameter "?next=/the/path/you/want"
    # with this view.
    url(r"^sso/admin/login/$", django_saml2_auth.views.signin),
    # The following line will replace the default user logout with the signout page (optional)
    url(r"^sso/logout/$", django_saml2_auth.views.signout),
    # The following line will replace the default admin user logout with the signout page (optional)
    url(r"^sso/admin/logout/$", django_saml2_auth.views.signout),
]

# URL Patterns for SODAR Core
# ------------------------------------------------------------------------------

urlpatterns += [url(r"^$", ProjectRolesHomeView.as_view(), name="home")]
HomeView = ProjectRolesHomeView

# URL Patterns for VarFish
# ------------------------------------------------------------------------------

urlpatterns += [
    url(r"^icons/", include("dj_iconify.urls")),
    #    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
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
    url(r"^admin_alerts/", include("adminalerts.urls")),
    url(r"^app_alerts/", include("appalerts.urls")),
    url(r"^siteinfo/", include("siteinfo.urls")),
    url(r"^userprofile/", include("userprofile.urls")),
    url(r"^tokens/", include("tokens.urls")),  # will go to SODAR-core
    # The rendered Sphinx-based manual.
    url(r"^manual/", include("docs.urls")),
    url(r"^su/", include("django_su.urls")),
    url(r"^cohorts/", include("cohorts.urls")),
    url(r"^beaconsite/", include("beaconsite.urls")),
    url(r"^genepanels/", include("genepanels.urls")),
    url(r"^vueapp/", include("varfish.vueapp.urls")),
    url(r"^cases/", include("cases.urls")),
    url(r"^varannos/", include("varannos.urls")),
    url(r"^seqmeta/", include("seqmeta.urls")),
    url(r"^cases-import/", include("cases_import.urls")),
    url(r"^cases-qc/", include("cases_qc.urls")),
]

# Explicitely require v2 analysis endpoints to be enabled.
if settings.VARFISH_GEN2_ANALYSIS:
    urlpatterns += [
        url(r"^cases-analysis/", include("cases_analysis.urls")),
        url(r"^seqvars/", include("seqvars.urls")),
    ]


# URL Patterns for Proxies
# ------------------------------------------------------------------------------

urlpatterns += [
    # Augment url patterns with proxy for genomics england panelapp.
    url(
        r"^proxy/panelapp/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url="https://panelapp.genomicsengland.co.uk/api/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    # Augment url patterns with proxy for variantvalidator.org.
    url(
        r"^proxy/variantvalidator/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url="https://rest.variantvalidator.org/VariantValidator/variantvalidator/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    # Augment URL patterns with proxy for local services.
    url(
        r"^proxy/varfish/annonars/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_ANNONARS,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    url(
        r"^proxy/varfish/mehari/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_MEHARI,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    url(
        r"^proxy/varfish/nginx/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_NGINX,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    # Augment url patterns with proxy for PubTator3
    url(
        r"^proxy/remote/pubtator3-api/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url="https://www.ncbi.nlm.nih.gov/research/pubtator3-api/",
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
    url(
        r"^proxy/varfish/viguno/(?P<url>.*)$",
        HttpProxy.as_view(
            base_url=settings.VARFISH_BACKEND_URL_VIGUNO,
            ignored_request_headers=HttpProxy.ignored_upstream_headers + ["cookie"],
        ),
    ),
]

# URL Patterns for Django Static Files
# ------------------------------------------------------------------------------

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# URL Patterns for Development
# ------------------------------------------------------------------------------

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
