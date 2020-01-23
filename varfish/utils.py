"""Shared utility code."""

from projectroles.models import Project


class ProjectMixin:
    """Mixin for DRF views.

    Makes the project available in an API view through ``get_project()``.
    """

    #: The ``Project`` model to use.
    project_class = Project

    def get_project(self):
        """Return the project object."""
        return self.project_class.objects.get(sodar_uuid=self.kwargs["project"])
