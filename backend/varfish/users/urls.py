from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.UserListView.as_view(), name="list"),
    path("~redirect/", view=views.UserRedirectView.as_view(), name="redirect"),
    path("<str:username>/", view=views.UserDetailView.as_view(), name="detail"),
    path("~update/", view=views.UserUpdateView.as_view(), name="update"),
]
