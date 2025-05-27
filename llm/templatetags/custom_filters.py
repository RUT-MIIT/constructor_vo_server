from django import template

register = template.Library()

@register.filter
def is_list(value):
    return isinstance(value, list)

@register.filter
def underscore_to_space(value):
    return str(value).replace("_", " ")
