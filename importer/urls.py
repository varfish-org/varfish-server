"""URL configuration for the ``importer`` app.
"""

from django.conf.urls import url
from . import views

app_name = "importer"

urlpatterns = [url(regex=r"^import-info$", view=views.ImportInfoView.as_view(), name="import-info")]
