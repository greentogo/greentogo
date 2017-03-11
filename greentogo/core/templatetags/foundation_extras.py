from django import template

register = template.Library()


@register.inclusion_tag("foundation/form_field.html")
def form_field(field):
    return {'field': field}
