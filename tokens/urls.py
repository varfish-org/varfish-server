from django.conf.urls import url
from . import views

app_name = "tokens"

urlpatterns = [
    url(regex=r"^$", view=views.UserTokenListView.as_view(), name="token-list"),
    url(regex=r"^create/", view=views.UserTokenCreateView.as_view(), name="token-create"),
    url(
        regex=r"^(?P<pk>.+)/delete$", view=views.UserTokenDeleteView.as_view(), name="token-delete"
    ),
]
