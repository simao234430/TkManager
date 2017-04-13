from django import template
import datetime
register = template.Library()

@register.filter
def print_timestamp(timestamp):
    if not timestamp :
        return None
    try:
        #assume, that timestamp is given in seconds with decimal point
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts).strftime("%y-%m-%d")

#register.filter(print_timestamp)
