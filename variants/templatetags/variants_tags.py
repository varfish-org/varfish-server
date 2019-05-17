from django import template

from ..models import Case, only_source_name as _models_only_source_name
from projectroles.user_settings import get_user_setting as _get_user_setting

register = template.Library()


# Row colors to use.
ROW_COLORS = {
    "pathogenic": "#dc354533",
    "uncertain": "#ffc10733",
    "benign": "#28a74533",
    "__invalid__": "#FF00FF",
}


@register.simple_tag
def get_row_bgcolor(rating):
    """Return color to use for row background for rating."""
    return ROW_COLORS.get(rating, ROW_COLORS["__invalid__"])


@register.simple_tag
def get_details_cases(project):
    """Return active cases for the project details page"""
    return Case.objects.filter(project=project).order_by("-pk")[:5]


@register.filter
def only_source_name(full_name):
    return _models_only_source_name(full_name)


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
    "positive": "fa-exclamation-circle",
    "uncertain": "fa-question",
    "negative": "fa-minus-circle",
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
    if row.flag_summary and row.flag_summary != "empty":
        return row.flag_summary  # short-circuit
    values = ("negative", "uncertain", "positive", "empty")
    flags = ("visual", "validation", "phenotype_match")
    indexes = []
    for flag in flags:
        flag_name = "flag_%s" % flag
        flag_value = getattr(row, flag_name)
        if flag_value and flag_value != "empty":
            indexes.append(values.index(flag_value))
    return values[min(indexes, default=3)]


@register.simple_tag
def ambiguous_frequency_warning(row, exac, thousandg, gnomad_exomes, gnomad_genomes, inhouse):
    tables = {
        "exac": exac,
        "thousand_genomes": thousandg,
        "gnomad_exomes": gnomad_exomes,
        "gnomad_genomes": gnomad_genomes,
        "inhouse": inhouse,
    }
    ambiguous_tables = []

    if all(tables.values()) or not any(tables.values()):
        return ambiguous_tables

    for table, activated in tables.items():
        if not activated:
            if table == "inhouse":
                hom_field = "inhouse_hom_alt"
            else:
                hom_field = "{}_homozygous".format(table)
            hom_failed = getattr(row, hom_field, 0) > 50
            freq_failed = getattr(row, "{}_frequency".format(table), 0) > 0.1
            if freq_failed or hom_failed:
                ambiguous_tables.append(table)

    return ambiguous_tables


@register.simple_tag
def chrx_het_hom_ratio(case, sample):
    """Return het./hom. ratio of ``sample`` in ``case``."""
    return case.chrx_het_hom_ratio(sample)


# TODO: move to sodar-core
@register.simple_tag
def get_user_setting(user, app_name, setting_name):
    """Return user setting."""
    return _get_user_setting(user, app_name, setting_name)


@register.filter
def allelic_balance(gt):
    """Return allelic balance from genotype value."""
    if not gt.get("dp"):
        return 0.0
    else:
        return gt.get("ad") / gt.get("dp")
