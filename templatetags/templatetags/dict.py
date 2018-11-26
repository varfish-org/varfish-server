from django import template

register = template.Library()


@register.filter
def keyvalue(data, key):
    if hasattr(data, 'get'):
        return data.get(key)
    else:
        return data[key]
