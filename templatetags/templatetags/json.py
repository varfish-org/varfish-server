import json

from django import template

register = template.Library()

@register.filter
def pretty_json(value):
    return json.dumps(json.loads(value), indent=4)
