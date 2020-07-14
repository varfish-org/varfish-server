from django import template

from variants.models import Case

register = template.Library()


@register.filter
def get_accessible_cases(item, user):
    """Return all accessible for a cohort and user."""
    return getattr(item, "get_accessible_cases_for_user")(user)


@register.filter
def check_accessible_cases(item, user):
    """Check if all cases of a cohort are accessible for a user."""
    if user == item.user or user.is_superuser:
        return True

    return set(item.cases.filter(project__roles__user=user)) == set(item.cases.all())
