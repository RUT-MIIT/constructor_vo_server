from django import template
register = template.Library()

@register.inclusion_tag('render_json_block.html')
def render_json(data, level=0):
    return {'data': data, 'level': level}
