from django import template

register = template.Library()

@register.filter
def keyvalue(data, key):    
    return data[key]