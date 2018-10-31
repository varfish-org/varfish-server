from django import template

from ..models import Case

register = template.Library()


@register.simple_tag
def get_details_cases(project):
    """Return active cases for the project details page"""
    return Case.objects.filter(project=project).order_by("-pk")
