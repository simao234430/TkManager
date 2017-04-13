# -*- coding: utf-8 -*-
from django import template
import datetime
register = template.Library()

@register.filter
def match_trans(match_str):
    if match_str == "match":
        return u"匹配"
    elif match_str == "dismatch":
        return u"不匹配"
    elif match_str == "partly miss":
        return u"部分匹配"
    elif match_str == "totally miss":
        return u"无信息"
    return match_str

@register.filter
def yes_trans(yes):
    if yes == 0:
        return u"否"
    else:
        return u"是"

#@register.filter
#def relationship_trans(relation):
#    if relation == -1:
#        return u""
#    elif relation == 1:
#        return u"父亲"
#    elif relation == 2:
#        return u"母亲"
#    elif relation == 3:
#        return u"配偶"
#    elif relation == 4:
#        return u"亲戚"
#    elif relation == 5:
#        return u"朋友"
#    elif relation == 6:
#        return u"同事"
#    elif relation == 7:
#        return u"同学"
#    elif relation == 8:
#        return u"其他"
#    else:
#        return u"未知"
#
