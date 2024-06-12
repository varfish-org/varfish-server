from django import template

register = template.Library()

PATHO_MAP = {
    "benign": -2,
    "likely benign": -1,
    "uncertain significance": 0,
    "likely pathogenic": 1,
    "pathogenic": 2,
}


@register.filter
def clinvar_patho_rank(entry):
    if entry.summary_pathogenicity_label:
        return PATHO_MAP.get(entry.summary_pathogenicity_label, -1) + 1
    else:
        return 0


@register.filter
def clinvar_gold_stars(entry):
    if entry.summary_gold_stars:
        return entry.summary_gold_stars + 1
    else:
        return 0
