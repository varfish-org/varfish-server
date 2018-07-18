from django.config.urls import url
from . import views

app_name = 'main'
url_patterns = [
    url(regex=r'^$', view=views.MainView.as_view(), name='main'),
]