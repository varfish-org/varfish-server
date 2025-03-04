from django.urls import path

from varfish.vueapp import views_ajax

app_name = "vueapp"
ajax_urlpatterns = [
    path(
        "ajax/user-setting/<str:setting_name>/",
        view=views_ajax.UserSettingView.as_view(),
        name="user-setting",
    ),
]

urlpatterns = ajax_urlpatterns
