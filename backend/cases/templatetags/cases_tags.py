from django import template
from django.conf import settings

from geneinfo.models import GeneIdToInheritance
from variants.models import only_source_name as _models_only_source_name
from variants.models.case import Case

modes_of_inheritance = dict(GeneIdToInheritance.MODES_OF_INHERITANCE)
register = template.Library()


@register.simple_tag
def get_login_page_text():
    return settings.VARFISH_LOGIN_PAGE_TEXT


@register.simple_tag
def get_details_cases(project):
    """Return 5 most recent updated cases for the project details page."""
    return Case.objects.filter(project=project).order_by("-date_modified")[:5]


@register.filter
def only_source_name(full_name):
    """Strip the sample suffix (e.g., ``-N1-DNA1-WES``)."""
    return _models_only_source_name(full_name)


@register.filter
def sex_errors(item, disable_pedigree_sex_check) -> dict[str, list[str]]:
    """Whether there are any sex errors in the case."""
    return item.sex_errors(disable_pedigree_sex_check=disable_pedigree_sex_check)


#: Mapping from case status to icon.
CASE_STATUS_TO_ICON = {
    "initial": "fa-solid:asterisk",
    "active": "fa-solid:filter",
    "closed-solved": "fa-solid:check",
    "closed-uncertain": "fa-solid:question",
    "closed-unsolved": "fa-solid:times",
}


@register.filter
def case_status_to_icon(value):
    """Return icon for the given case by status."""
    return CASE_STATUS_TO_ICON.get(value, "")


#: Mapping from case status to color.
CASE_STATUS_TO_COLOR = {
    "initial": "secondary",
    "active": "info",
    "closed-solved": "success",
    "closed-uncertain": "warning",
    "closed-unsolved": "danger",
}


@register.filter
def case_status_to_color(value):
    """Return color for the given case by status."""
    return CASE_STATUS_TO_COLOR.get(value, "")


#: Mapping from case status to CSS class.
CASE_STATUS_TO_CLASS = {
    "initial": "text-secondary",
    "active": "text-info",
    "closed-solved": "text-success",
    "closed-uncertain": "text-warning",
    "closed-unsolved": "text-danger",
}


@register.filter
def case_status_to_class(value):
    """Return CSS class for the given case by status."""
    return "%s text-%s" % (CASE_STATUS_TO_CLASS.get(value, ""), case_status_to_color(value))


#: Mapping from case status to integer order.
CASE_STATUS_TO_ORDER = {
    "initial": 0,
    "active": 4,
    "closed-solved": 3,
    "closed-unsolved": 1,
    "closed-uncertain": 2,
}


@register.filter
def case_status_to_order(value):
    """Return numeric order for the given case by status."""
    return CASE_STATUS_TO_ORDER.get(value, -1000)
