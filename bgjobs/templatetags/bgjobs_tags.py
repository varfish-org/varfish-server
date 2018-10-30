from django import template

from ..models import BackgroundJob

register = template.Library()


@register.simple_tag
def get_details_backgroundjobs(project, user):
    """Return active user zones for the project details page"""
    return BackgroundJob.objects.filter(project=project, user=user).order_by("-pk")
