# your_app/templatetags/range_tag.py
from django import template

register = template.Library()

@register.filter
def get_range(value):
    return range(int(value))
