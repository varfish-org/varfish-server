from django.conf.urls import url
from . import views

app_name = "main"
urlpatterns = [
    url(regex=r"^$", view=views.MainView.as_view(), name="main"),
    url(
        regex=r"^case/(?P<case_id>[A-Za-z0-9]+)/$",
        view=views.FilterView.as_view(),
        name="filter",
    ),
]
