from django import template

from ..models import Case

register = template.Library()


@register.simple_tag
def get_details_cases(project):
    """Return active cases for the project details page"""
    return Case.objects.filter(project=project).order_by("-pk")[:5]


@register.filter
def only_source_name(full_name):
    if full_name.count("-") >= 3:
        tokens = full_name.split("-")
        return "-".join(tokens[:-3])
    else:
        return full_name


#: Clinvar status to stars.
STARS = {
    "practice guideline": 4,
    "reviewed by expert panel": 3,
    "criteria provided, multiple submitters, no conflicts": 2,
    "criteria provided, conflicting interpretations": 1,
    "criteria provided, single submitter": 1,
    "no assertion criteria provided": 0,
    "no assertion provided": 0,
}


@register.filter
def status_stars(status):
    return STARS.get(status, 0)


#: Clinvar significance to colour.
COLOURS = {
    "pathogenic": "danger",
    "likely pathogenic": "warning",
    "uncertain significance": "important",
    "likely benign": "secondary",
    "benign": "secondary",
}


@register.filter
def significance_color(sig):
    return COLOURS.get(sig, "secondary")
