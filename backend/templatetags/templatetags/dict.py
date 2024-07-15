from django import template

register = template.Library()


@register.filter
def keyvalue(data, key):
    if data is None:
        return None
    elif hasattr(data, "get"):
        return data.get(key)
    else:
        return data[key]
