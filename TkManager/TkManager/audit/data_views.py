# -*- coding: utf-8 -*-
import json
from django.db.models import Q
from TkManager.order.apply_models import Apply, CheckApply
from TkManager.order.models import Chsi, CheckStatus, Profile
from TkManager.review.models import Review, Employee
from TkManager.util.tkdate import *
from TkManager.util.data_provider import DataProvider
from TkManager.common.tk_log_client import TkLog
from TkManager.util.permission_decorator import page_permission
from TkManager.review.employee_models import check_employee
from django.http import HttpResponse, StreamingHttpResponse
from TkManager.review.models import *
from TkManager.collection.models import *

class CheckApplyProvider(DataProvider):
    """
        所有催收
    """
    def object_filter(self, request):
        """
            time status 两个选择维度
        """
        stime = get_today()
        etime = get_tomorrow()
        timerange = request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "twodays" :
            stime = get_yestoday()
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

        if timerange == "all" :
            query_time = Q()
        else:
            query_time = Q(create_at__lt = etime, create_at__gt = stime)

        apply_type =request.GET.get("type")
        query_type = None
        if apply_type == "topublic" :
            query_type = Q(type=CheckApply.CHECK_TOPUBLIC)
        elif apply_type == "alipay" :
            query_type = Q(type=CheckApply.CHECK_ALIPAY)
        else :
            query_type = Q()

        apply_status = request.GET.get("status")
        query_status = None
        if apply_status == "waiting" :
            query_status = Q(status=CheckApply.WAIT)
        elif apply_status == "success" :
            query_status = Q(status=CheckApply.CHECK_SUCCESS)
        elif apply_status == "failed" :
            query_status = Q(status=CheckApply.CHECK_FAILED)
        else :
            query_status = Q()

        apply_list = CheckApply.objects.filter(query_time & query_type & query_status)
        return apply_list

    def get_columns(self):
        return [u"申请ID", u"用户ID", u"用户名", u"还款方式", u"提交时间", u"提交人", u"处理状态", u"操作"]

    def get_query(self):
        return ["repayment__user__id__iexact", "create_by__username__icontains", "repayment__user__name__icontains", "repayment__user__phone_no__iexact", "repayment__order_number__iexact"]

    def fill_data(self, query_set):
        data_set = []
        today = datetime.combine(date.today(), datetime.max.time())
        for result in query_set.values():
            apply = CheckApply.objects.get(pk = result["id"])
            staff = apply.create_by
            user = apply.repayment.user
            operation_url = u"<a class='do_check' name='%d' href='#'>复核</a>" % (apply.id)
            data = [apply.id,
                    user.id,
                    user.name,
                    apply.get_type_display(),
                    apply.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    staff.username,
                    apply.get_status_display(),
                    operation_url]
            data_set.append(data)
        return data_set

class ReceivablesProvider(DataProvider):
    def object_filter(self, request):
        stime = get_today()
        etime = get_tomorrow()
        timerange = request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "twodays" :
            stime = get_yestoday()
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

        if timerange == "all" :
            query_time = Q()
        else:
            query_time = Q(create_at__lt = etime, create_at__gt = stime)

        apply_type =request.GET.get("type")
        query_type = None
        if apply_type == "m0" :
            query_type = Q(type='a')
        elif apply_type == "m1" :
            query_type = Q(type='b')
        elif apply_type == "m2" :
            query_type = Q(type='c')
        elif apply_type == "m3" :
            query_type = Q(type='d')
        elif apply_type == "m4" :
            query_type = Q(type='e')
        else :
            query_type = Q(type__in=['a', 'b', 'c', 'd', 'e'])

        apply_status = request.GET.get("status")
        query_status = None
        if apply_status == "waiting":
            query_status = Q(status = "0")
        elif apply_status == "processing":
            query_status = Q(status = "i") | Q(status = "c") | Q(status = "d")
        elif apply_status == "done":
            query_status = Q(status = "8") | Q(status = "9")
        else:
            query_status = Q()

        #print query_status, ",", query_type, ",", query_time
        owner_id =request.GET.get("owner_id")
        query_owner = Q (review__reviewer__user__id = owner_id)
        apply_list = Apply.objects.filter(query_owner & query_type & query_time & query_status).distinct()
        return apply_list

    def get_columns(self):
        return [u"ID", u"用户名", u"客户类型", u"应还日期", u"逾期天数", u"承诺还款时间", u"贷款金额", u"处理状态", u"操作"] #u"应还本息合计"

    def get_query(self):
        return ["id__iexact", "create_by__name__icontains", "create_by__phone_no__icontains"]

    def fill_data(self, query_set):
        data_set = []
        today = datetime.combine(date.today(), datetime.max.time())
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            status_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='dispatch_collection' name='%d' href='#'>分配</a>" % (apply.id, apply.id)
            operation_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='do_collection' name='%d' href='#'>催收</a>" % (apply.id, apply.id)
            chsi = Chsi.objects.filter(user=user)
            profile = Profile.objects.filter(owner=user)
            check = CheckStatus.objects.filter(owner=user)
            review = Review.objects.filter(order=apply)

            installments = InstallmentDetailInfo.objects.filter(repayment=apply.repayment, installment_number=apply.money + 1)
            installment = None
            if len(installments) == 1:
                installment = installments[0]
            repay_day = installment.should_repay_time if installment else ""
            pay_done = (installment.repay_status == RepaymentInfo.DONE) or (installment.repay_status == RepaymentInfo.OVERDUE_DONE)
            overdu_days = (today - repay_day).days if repay_day and not pay_done else 0
            if pay_done and installment:
                try:
                    overdu_days = (datetime.combine(installment.real_repay_time, datetime.min.time()) - datetime.combine(installment.should_repay_time, datetime.min.time())).days
                except Exception, e:
                    overdu_days = 0
            data = [apply.id,
                    user.name,
                    user.profile.get_job_display(),
                    repay_day.strftime("%Y-%m-%d"),
                    overdu_days,
                    apply.last_commit_at.strftime("%Y-%m-%d %H时") if apply.last_commit_at else "",
                    apply.repayment.apply_amount/100.0,
                    apply.get_status_display(),
                    operation_url]
            data_set.append(data)
        return data_set

class ReceivedProvider(DataProvider):
    def object_filter(self, request):
        stime = get_today()
        etime = get_tomorrow()
        timerange = request.GET.get("time")
        if timerange == "today" :
            stime = get_today()
            etime = get_tomorrow()
        elif timerange == "twodays" :
            stime = get_yestoday()
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

        if timerange == "all" :
            query_time = Q()
        else:
            query_time = Q(create_at__lt = etime, create_at__gt = stime)

        apply_type =request.GET.get("type")
        query_type = None
        if apply_type == "m0" :
            query_type = Q(type='a')
        elif apply_type == "m1" :
            query_type = Q(type='b')
        elif apply_type == "m2" :
            query_type = Q(type='c')
        elif apply_type == "m3" :
            query_type = Q(type='d')
        elif apply_type == "m4" :
            query_type = Q(type='e')
        else :
            query_type = Q(type__in=['a', 'b', 'c', 'd', 'e'])

        apply_status = request.GET.get("status")
        query_status = None
        if apply_status == "waiting":
            query_status = Q(status = "0")
        elif apply_status == "processing":
            query_status = Q(status = "i") | Q(status = "c") | Q(status = "d")
        elif apply_status == "done":
            query_status = Q(status = "8") | Q(status = "9")
        else:
            query_status = Q()

        #print query_status, ",", query_type, ",", query_time
        owner_id =request.GET.get("owner_id")
        query_owner = Q (review__reviewer__user__id = owner_id)
        apply_list = Apply.objects.filter(query_owner & query_type & query_time & query_status).distinct()
        #apply_list = Apply.objects.filter(query_time & query_type & query_status)
        return apply_list

    def get_columns(self):
        #return [u"ID", u"用户名", u"逾期类型", u"贷款方式", u"贷款金额", u"逾期金额", u"催收人", u"操作"]
        return [u"ID", u"用户名", u"客户类型", u"应还日期", u"逾期天数", u"承诺还款时间", u"贷款金额", u"处理状态", u"操作"] #u"应还本息合计"

    def get_query(self):
        return ["id__iexact", "create_by__name__icontains", "create_by__phone_no__icontains"]

    def fill_data(self, query_set):
        data_set = []
        today = datetime.combine(date.today(), datetime.max.time())
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            status_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='dispatch_collection' name='%d' href='#'>分配</a>" % (apply.id, apply.id)
            operation_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='do_collection' name='%d' href='#'>催收</a>" % (apply.id, apply.id)
            chsi = Chsi.objects.filter(user=user)
            profile = Profile.objects.filter(owner=user)
            check = CheckStatus.objects.filter(owner=user)
            review = Review.objects.filter(order=apply)

            installments = InstallmentDetailInfo.objects.filter(repayment=apply.repayment, installment_number=apply.money + 1)
            installment = None
            if len(installments) == 1:
                installment = installments[0]
            repay_day = installment.should_repay_time if installment else ""
            pay_done = (installment.repay_status == RepaymentInfo.DONE) or (installment.repay_status == RepaymentInfo.OVERDUE_DONE)
            overdu_days = (today - repay_day).days if repay_day and not pay_done else 0
            if pay_done and installment:
                try:
                    overdu_days = (datetime.combine(installment.real_repay_time, datetime.min.time()) - datetime.combine(installment.should_repay_time, datetime.min.time())).days
                except Exception, e:
                    overdu_days = 0
            data = [apply.id,
                    user.name,
                    user.profile.get_job_display(),
                    repay_day.strftime("%Y-%m-%d"),
                    overdu_days,
                    apply.last_commit_at.strftime("%Y-%m-%d %H时") if apply.last_commit_at else "",
                    apply.repayment.apply_amount/100.0,
                    apply.get_status_display(),
                    operation_url]
            data_set.append(data)
        return data_set


def get_receivables_datatable(request):
    return ReceivablesProvider().get_datatable(request)

def get_received_datatable(request):
    return ReceivedProvider().get_datatable(request)

def get_check_datatable(request):
    return CheckApplyProvider().get_datatable(request)



def get_receivables_columns():
    return ReceivablesProvider().get_columns()

def get_received_columns():
    return ReceivedProvider().get_columns()

def get_check_columns():
    return CheckApplyProvider().get_columns()
