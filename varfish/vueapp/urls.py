from django.conf.urls import url

from varfish.vueapp import views_ajax

app_name = "vueapp"
ajax_urlpatterns = [
    url(
        regex=r"^ajax/user-setting/(?P<setting_name>[0-9a-zA-Z\._-]+)/$",
        view=views_ajax.UserSettingView.as_view(),
        name="user-setting",
    ),
]

urlpatterns = ajax_urlpatterns
