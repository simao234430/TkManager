# -*- coding: utf-8 -*-
from django.db.models import Q
from TkManager.order.apply_models import Apply
from TkManager.order.models import *
from TkManager.util.tkdate import *
from TkManager.util.data_provider import DataProvider
from TkManager.common.tk_log_client import TkLog
from TkManager.review.employee_models import Employee
from django.http import HttpResponse
import json
class OrderDataProvider(DataProvider):
    def object_filter(self, request):
        stime = get_today()
        etime = get_tomorrow()
        timerange =request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "yestoday" :
            stime = get_yestoday()
            etime = get_today()
        elif timerange == "toweek" :
            stime = get_first_day_of_week()
            etime = get_tomorrow()
        elif timerange == "tomonth" :
            stime = get_first_day_of_month()
            etime = get_tomorrow()
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")

        #print stime, etime
        order_list = Apply.objects.filter(Q(create_at__lt = etime, create_at__gt = stime))
        #print Apply.objects.filter(Q(create_at__lt = etime) and Q(create_at__gt = stime)).query
        return order_list

    def get_columns(self):
        return [u"订单ID", u"用户ID", u"用户来源", u"订单类型", u"创建时间", u"处理时间", u"订单状态"]

    def get_query(self):
        return ["id__iexact", "create_by__name__icontains", "create_by__phone_no__icontains"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            chsi = Chsi.objects.filter(user=user)
            data = [apply.id,
                    user.name,
                    chsi[0].school if len(chsi) > 0 else "",
                    apply.get_type_display(),
                    apply.create_at.strftime("%Y-%m-%d %H:%M:%S") if apply.create_at else "",
                    apply.finish_time.strftime("%Y-%m-%d %H:%M:%S") if apply.finish_time else "",
                    apply.get_status_display()]
            data_set.append(data)
        return data_set

def get_order_datatable(request):
    return OrderDataProvider().get_datatable(request)

def get_order_columns():
    return OrderDataProvider().get_columns()

class ApplyOrderDataProvider(DataProvider):
    def object_filter(self, request):
        stime = get_today()
        etime = get_tomorrow()
        timerange =request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "yestoday" :
            stime = get_yestoday()
            etime = get_today()
        elif timerange == "toweek" :
            stime = get_first_day_of_week()
            etime = get_tomorrow()
        elif timerange == "tomonth" :
            stime = get_first_day_of_month()
            etime = get_tomorrow()
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")

        #print stime, etime
        order_list = Apply.objects.filter(Q(type = '0', create_at__lt = etime, create_at__gt = stime))
        #print Apply.objects.filter(Q(create_at__lt = etime) and Q(create_at__gt = stime)).query
        return order_list

    def get_columns(self):
        return [u"订单ID", u"用户ID", u"用户来源", u"订单类型", u"创建时间", u"处理时间", u"订单状态"]

    def get_query(self):
        return ["id__iexact", "create_by__name__icontains", "create_by__phone_no__icontains"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            print "apply", apply
            if apply:
                user = apply.create_by
                chsi = Chsi.objects.filter(user=user)
                data = [apply.id,
                        user.name,
                        chsi[0].school if len(chsi) > 0 else "",
                        apply.get_type_display(),
                        apply.create_at.strftime("%Y-%m-%d %H:%M:%S") if apply.create_at else "",
                        apply.finish_time.strftime("%Y-%m-%d %H:%M:%S") if apply.finish_time else "",
                        apply.get_status_display()]
                data_set.append(data)
        return data_set

def get_apply_order_datatable(request):
    return ApplyOrderDataProvider().get_datatable(request)

def get_apply_order_columns():
    return ApplyOrderDataProvider().get_columns()

class PromotionOrderDataProvider(DataProvider):
    def object_filter(self, request):
        stime = get_today()
        etime = get_tomorrow()
        timerange =request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "yestoday" :
            stime = get_yestoday()
            etime = get_today()
        elif timerange == "toweek" :
            stime = get_first_day_of_week()
            etime = get_tomorrow()
        elif timerange == "tomonth" :
            stime = get_first_day_of_month()
            etime = get_tomorrow()
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")

        #print stime, etime
        order_list = Apply.objects.filter(Q(type__lt = '9', type__gt = '0', create_at__lt = etime, create_at__gt = stime))
        #print Apply.objects.filter(Q(create_at__lt = etime) and Q(create_at__gt = stime)).query
        return order_list

    def get_columns(self):
        return [u"订单ID", u"用户ID", u"用户来源", u"订单类型", u"创建时间", u"处理时间", u"订单状态"]

    def get_query(self):
        return ["id__iexact", "create_by__name__icontains", "create_by__phone_no__icontains"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            chsi = Chsi.objects.filter(user=user)
            data = [apply.id,
                    user.name,
                    chsi[0].school if len(chsi) > 0 else "",
                    apply.get_type_display(),
                    apply.create_at.strftime("%Y-%m-%d %H:%M:%S") if apply.create_at else "",
                    apply.finish_time.strftime("%Y-%m-%d %H:%M:%S") if apply.finish_time else "",
                    apply.get_status_display()]
            data_set.append(data)
        return data_set

def get_promotion_order_datatable(request):
    return PromotionOrderDataProvider().get_datatable(request)

def get_promotion_order_columns():
    return PromotionOrderDataProvider().get_columns()

class LoanOrderDataProvider(DataProvider):
    def object_filter(self, request):
        stime = get_today()
        etime = get_tomorrow()
        timerange =request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "yestoday" :
            stime = get_yestoday()
            etime = get_today()
        elif timerange == "toweek" :
            stime = get_first_day_of_week()
            etime = get_tomorrow()
        elif timerange == "tomonth" :
            stime = get_first_day_of_month()
            etime = get_tomorrow()
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")

        #print stime, etime
        order_list = Apply.objects.filter(Q(type = 'l', create_at__lt = etime, create_at__gt = stime))
        #print Apply.objects.filter(Q(create_at__lt = etime) and Q(create_at__gt = stime)).query
        return order_list

    def get_columns(self):
        return [u"订单ID", u"用户ID", u"借贷金额", u"订单类型", u"创建时间", u"处理时间", u"订单状态"]

    def get_query(self):
        return ["id__iexact", "create_by__name__icontains", "create_by__phone_no__icontains"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            data = [apply.id,
                    user.name,
                    "%d.%d" % (apply.money/100, apply.money%100),
                    apply.get_type_display(),
                    apply.create_at.strftime("%Y-%m-%d %H:%M:%S") if apply.create_at else "",
                    apply.finish_time.strftime("%Y-%m-%d %H:%M:%S") if apply.finish_time else "",
                    apply.get_status_display()]
            data_set.append(data)
        return data_set

def get_loan_order_datatable(request):
    return LoanOrderDataProvider().get_datatable(request)

def get_loan_order_columns():
    return LoanOrderDataProvider().get_columns()

def _get_user_info_note_data(request):
    user_id = request.GET.get("user_id")
    user = User.objects.get(id = user_id)
    data_list = []
    for record in UserExtraInfoRecord.objects.filter(user=user):
        record_dict = dict()
        record_dict['add_time'] = record.create_at.strftime("%Y-%m-%d %H") if record.create_at else ""
        record_dict['add_staff'] = str(record.create_by.username)
        record_dict['notes'] = record.content

        data_list.append(record_dict)
    output_data = {'data': data_list}
    return output_data

def get_user_info_note_data(request):
    if request.method == 'GET':
        output_data = _get_user_info_note_data(request)
        return HttpResponse(json.dumps(output_data))
