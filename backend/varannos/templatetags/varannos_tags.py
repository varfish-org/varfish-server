from django import template

from varannos.models import VarAnnoSet

register = template.Library()


@register.simple_tag
def get_details_varannosets(project):
    """Return 5 most recent updated variant annotation sets for the project details page."""
    return VarAnnoSet.objects.filter(project=project).order_by("-date_modified")[:5]


@register.filter
def add_chr_prefix(value):
    if str(value).startswith("chr"):
        return value
    else:
        return f"chr{value}"
