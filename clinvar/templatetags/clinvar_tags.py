from django import template

register = template.Library()

PATHO_MAP = {
    "benign": -2,
    "likely benign": -1,
    "protective": -1,
    "uncertain significance": 0,
    "association not found": 0,
    "drug response": 0,
    "not provided": 0,
    "other": 0,
    "likely pathogenic": 1,
    "affects": 1,
    "association": 1,
    "conflicting interpretations of pathogenicity": 1,
    "risk factor": 1,
    "confers sensitivity": 1,
    "pathogenic": 2,
}


def _patho_index(entry):
    """Return index of pathogenicity to display"""
    highest_idx = None
    highest_patho = -10
    highest_stars = 0
    for idx in range(len(entry.pathogenicity_arr)):
        patho_str = entry.pathogenicity_arr[idx]
        patho = PATHO_MAP.get(patho_str, -2)
        gold_stars = entry.gold_stars_arr[idx]
        if (patho, gold_stars) > (highest_patho, highest_stars):
            highest_idx = idx
            highest_patho = patho
            highest_stars = gold_stars
    return highest_idx


@register.filter
def clinvar_grading_patho(entry):
    """Return pathogenicity of variant to display"""
    idx = _patho_index(entry)
    if idx is None:
        return None
    else:
        return entry.pathogenicity_arr[idx]


@register.filter
def clinvar_grading_stars(entry):
    """Return star rating of pathogenicity to display"""
    idx = _patho_index(entry)
    if idx is None:
        return None
    else:
        return entry.gold_stars_arr[idx]


@register.filter
def clinvar_grading_vcv(entry):
    """Return VCV ID of pathogenicity to display"""
    idx = _patho_index(entry)
    if idx is None:
        return None
    else:
        return entry.vcv_arr[idx]


@register.filter
def clinvar_grading_review_status(entry):
    """Return VCV review status of pathogenicity to display"""
    idx = _patho_index(entry)
    if idx is None:
        return None
    else:
        return entry.review_status_arr[idx]
