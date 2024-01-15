from django import template
from django.conf import settings
from projectroles.app_settings import AppSettingAPI

from geneinfo.models import GeneIdToInheritance, Hpo, HpoName
from variants.models import Case
from variants.models import only_source_name as _models_only_source_name

modes_of_inheritance = dict(GeneIdToInheritance.MODES_OF_INHERITANCE)
register = template.Library()


@register.simple_tag
def get_details_cases(project):
    """Return 5 most recent updated cases for the project details page."""
    return Case.objects.filter(project=project).order_by("-date_modified")[:5]


@register.filter
def only_source_name(full_name):
    return _models_only_source_name(full_name)


CASE_STATUS_TO_COLOR = {
    "initial": "secondary",
    "active": "info",
    "closed-solved": "success",
    "closed-uncertain": "warning",
    "closed-unsolved": "danger",
}


@register.filter
def case_status_to_color(value):
    return CASE_STATUS_TO_COLOR.get(value, "")


CASE_STATUS_TO_CLASS = {
    "initial": "text-secondary",
    "active": "text-info",
    "closed-solved": "text-success",
    "closed-uncertain": "text-warning",
    "closed-unsolved": "text-danger",
}


@register.filter
def case_status_to_class(value):
    return "%s text-%s" % (CASE_STATUS_TO_CLASS.get(value, ""), case_status_to_color(value))


@register.filter
def flag_class(row):
    """Return CSS class to used based on the flag of ``row``.

    Report "wip" class if a flag is set for {visual, validation, phenotype_match}.
    If the summary flag has been set, use this value instead.
    """
    if row.flag_summary and row.flag_summary != "empty":
        return row.flag_summary  # short-circuit
    # Except bookmark flag as it is set automatically if not actively disabled by user.
    bool_flags = (
        "candidate",
        "doesnt_segregate",
        "final_causative",
        "for_validation",
        "no_disease_association",
        "segregates",
    )
    flags = ("visual", "validation", "phenotype_match", "molecular")
    for flag in flags:
        flag_name = "flag_%s" % flag
        flag_value = getattr(row, flag_name)
        if flag_value and flag_value != "empty":
            return "wip"
    for flag in bool_flags:
        flag_name = "flag_%s" % flag
        if getattr(row, flag_name):
            return "wip"
    return "empty"


# TODO: move to sodar-core
@register.simple_tag
def get_user_setting(user, app_name, setting_name):
    """Return user setting."""
    if settings.KIOSK_MODE:
        return
    setting_api = AppSettingAPI()
    return setting_api.get(app_name, setting_name, user=user)


@register.simple_tag
def get_term_description(term):
    """Return HPO, Orphanet, or OMIM description."""
    if term.startswith("HP:"):
        terms = HpoName.objects.filter(hpo_id=term)
        if terms:
            return terms.first().name
        else:
            return None
    else:
        for record in Hpo.objects.filter(database_id=term).order_by("-name"):
            return record.name
        else:
            return None


@register.simple_tag
def same_release(cases):
    """Return whether an iterable of cases has the same genome release."""
    return len({case.release for case in cases}) == 1
