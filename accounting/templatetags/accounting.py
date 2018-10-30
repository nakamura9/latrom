from django import template

register = template.Library()

@register.filter
def accounting(number):
    try:
        number = float(number)
    except:
        number =0.0
    if number >= 0:
        return "{0:0.2f}".format(number)
    else:
        return "({0:0.2f})".format(abs(number))

