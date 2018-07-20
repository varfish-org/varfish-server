from django.conf.urls import url
from . import views

app_name = "main"
urlpatterns = [
    url(regex=r"^$", view=views.MainView.as_view(), name="main")
]
