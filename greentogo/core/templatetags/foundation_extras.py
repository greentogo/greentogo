from django import template

register = template.Library()


@register.inclusion_tag("foundation/form_field.html")
def form_field(field, label=None):
    return {'field': field, 'label': label}


@register.filter(name='getitem')
def getitem(value, arg):
    return value[arg]
