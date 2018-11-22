"""Code related to ``django-plugins``.

First, it creates a ``ProjectAppPluginPoint`` for the ``bgjobs`` app.

Second, it creates a new plugin point for the registering ``BackgroundJob`` specializations.
"""

from django.dispatch.dispatcher import receiver
from djangoplugins.signals import django_plugin_disabled, django_plugin_enabled
from djangoplugins.point import PluginPoint

from projectroles.plugins import ProjectAppPluginPoint
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with the ``ProjectAppPluginPoint`` from the ``projectroles`` app."""

    name = "bgjobs"
    title = "Background Jobs"
    urls = urlpatterns

    icon = "tasks"

    entry_point_url_id = "bgjobs:jobs-list"

    description = "Jobs executed in the background"

    #: Required permission for accessing the app
    app_permission = "bgjobs.view_data"

    #: Enable or disable general search from project title bar
    search_enable = False

    #: List of search object types for the app
    search_types = []

    #: Search results template
    search_template = None

    #: App card template for the project details page
    details_template = "bgjobs/_details_card.html"

    #: App card title for the project details page
    details_title = "Background Jobs App Overview"

    #: Position in plugin ordering
    plugin_ordering = 100


class BackgroundJobsPluginPoint(PluginPoint):
    """Definition of a plugin point for registering background job types with the ``bgjobs`` app."""

    #: Mapping from job specialization name to specialization class (OneToOneField "inheritance").
    job_specs = {}
