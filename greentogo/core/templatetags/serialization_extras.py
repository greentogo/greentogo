from django import template
from django.core import serializers
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def jsonify(value):
    return mark_safe(serializers.serialize("json", value))
