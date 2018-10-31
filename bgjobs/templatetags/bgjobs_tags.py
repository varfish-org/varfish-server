from django import template

from ..models import BackgroundJob

register = template.Library()


@register.simple_tag
def get_details_backgroundjobs(project):
    """Return active background jobs for the project details page"""
    return BackgroundJob.objects.filter(project=project).order_by("-pk")
