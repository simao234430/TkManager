from django import template

register = template.Library()

@register.filter
def math_div(num):
    if not num:
        return 0
    try:
        #assume, that timestamp is given in seconds with decimal point
        new_num = round(float(num)/100,2)
        return new_num
    except ValueError:
        return None
