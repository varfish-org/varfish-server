from django import template

register = template.Library()


@register.filter
def regmaps_elements(sv_record):
    vals = []
    for k in sv_record.keys():
        if k.startswith("regmap_") and "_element_" in k:
            vals.append(getattr(sv_record, k))
    return str(max(vals or [0]))


@register.filter
def regmaps_interactions(sv_record):
    vals = []
    for k in sv_record.keys():
        if k.startswith("regmap_") and "_interaction_" in k:
            vals.append(getattr(sv_record, k))
    return str(max(vals or [0]))


@register.simple_tag
def get_selected_values(form, prefix, infix, suffix):
    return getattr(form, "cleaned_data", {}).get("%s%s%s" % (prefix, infix, suffix), [])


@register.simple_tag
def get_is_checked(form, prefix, infix, suffix):
    return getattr(form, "cleaned_data", {}).get("%s%s%s" % (prefix, infix, suffix), False)
