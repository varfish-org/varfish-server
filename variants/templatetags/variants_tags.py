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


@register.filter
def smallvar_description(entry):
    """Return small variant description from query result"""
    keys = ("release", "chromosome", "position", "reference", "alternative", "ensembl_gene_id")
    if isinstance(entry, dict):
        return "-".join(map(str, (entry[key] for key in keys)))
    else:
        return "-".join(map(str, (getattr(entry, key) for key in keys)))


#: Mapping of small variant flag value to font awesome icon.
FLAG_VALUE_TO_FA = {
    "positive": "fa-thumbs-up",
    "uncertain": "fa-question",
    "negative": "fa-thumbs-up",
    "empty": "fa-remove",
}


@register.filter
def flag_value_to_fa(value):
    return FLAG_VALUE_TO_FA.get(value, "fa-remove")


@register.filter
def flag_class(row):
    """Return CSS class to used based on the flag of ``row``.

    Overall, select the flag value of {visual, validation, phenotype_match}
    with the lowest scoring that is not "empty".  If the summary flag has been
    set, use this value.
    """
    if row.flag_summary != "empty":
        return row.flag_summary  # short-circuit
    values = ("negative", "uncertain", "positive", "empty")
    flags = ("visual", "validation", "phenotype_match")
    indexes = []
    for flag in flags:
        flag_name = "flag_%s" % flag
        flag_value = getattr(row, flag_name)
        if flag_value != "empty":
            indexes.append(values.index(flag_value))
    return values[min(indexes, default=3)]


@register.simple_tag
def chrx_het_hom_ratio(case, sample):
    """Return het./hom. ratio of ``sample`` in ``case``."""
    return case.chrx_het_hom_ratio(sample)
