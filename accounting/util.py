from django.template.library import Library

def accounting(number):
    if number > 0:
        return "{0:0.2f}".format(number)
    else:
        return "({0:0.2f})".format(abs(number))

