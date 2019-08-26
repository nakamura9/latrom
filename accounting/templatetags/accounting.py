from django import template
from accounting.models import AccountingSettings
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


@register.filter
def active_currency(number):
    qs = AccountingSettings.objects.first()
    currency = qs.active_currency if qs else None
    if not currency:
        return number
    try:
        number = float(number)
    except:
        return number
    return '{0} {1:0.2f}'.format(currency.symbol, number)
