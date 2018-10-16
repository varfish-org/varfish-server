from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views import defaults as default_views
from projectroles.views import HomeView

urlpatterns = [
#    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r"^varfish/", include('varfish.main.urls')),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    #url(r'^users/', include('varfish.users.urls', namespace='users')),

    # Your stuff: custom urls includes go here
    url(r'api/auth/', include('knox.urls')),
    url(r'^project/', include('projectroles.urls')),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(
                template_name='users/login.html'), name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
