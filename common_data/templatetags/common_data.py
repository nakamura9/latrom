from django import template
register = template.Library()

@register.filter
def subtract(number, other):
    return number - other