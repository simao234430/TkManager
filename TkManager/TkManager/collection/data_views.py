# -*- coding: utf-8 -*-
import json
from django.db.models import Q
from TkManager.order.apply_models import Apply
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

class AllCollectionDataProvider(DataProvider):
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
            query_status = Q(status = "i") | Q(status = "c") | Q(status = "d") | Q(status = "k")
        elif apply_status == "done":
            query_status = Q(status = "8") | Q(status = "9")
        else:
            query_status = Q()

        #print query_status, ",", query_type, ",", query_time
        apply_list = Apply.objects.filter(query_time & query_type & query_status)
        return apply_list

    def get_columns(self):
        #return [u"ID", u"用户名", u"应还日期", u"贷款方式", u"贷款金额", u"应还金额",  u"催收人", u"操作"]
        return [u"ID", u"用户id", u"用户名", u"客户类型", u"应还日期", u"逾期天数", u"贷款金额", u"催收人", u"处理状态", u"操作"]

    def get_query(self):
        return ["create_by__id__iexact", "create_by__name__icontains", "create_by__phone_no__iexact", "repayment__order_number__iexact", "repayment__bank_card__number__iexact"]

    def fill_data(self, query_set):
        data_set = []
        today = datetime.combine(date.today(), datetime.max.time())
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            #status_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='dispatch_collection' name='%d' href='#'>分配</a>" % (apply.id, apply.id)
            #operation_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='dispatch_collection' name='%d' href='#'>分配</a>" % (apply.id, apply.id)
            operation_url = u"<a class='view_review' name='%d' href='#'>查看</a> <a class='do_collection' name='%d' href='#'>催收</a>" % (apply.id, apply.id)
            chsi = Chsi.objects.filter(user=user)
            profile = Profile.objects.filter(owner=user)
            check = CheckStatus.objects.filter(owner=user)
            review = CollectionRecord.objects.filter(apply=apply, record_type=CollectionRecord.DISPATCH).order_by("-id")
            dispatch_url = u"<a class='dispatch_collection' name='%d' href='#'>未分配</a>" % (apply.id)
            if len(review) >= 1:
                dispatch_url = u"<a class='dispatch_collection' name='%d' href='#'>%s</a>" % (apply.id, review[0].create_by.username)
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
                    user.id,
                    user.name,
                    user.profile.get_job_display(),
                    repay_day.strftime("%Y-%m-%d"),
                    overdu_days,
                    apply.repayment.apply_amount/100.0,
                    dispatch_url,
                    apply.get_status_display(),
                    operation_url]
            data_set.append(data)
        return data_set

class MyCollectionDataProvider(DataProvider):
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
        return [u"ID", u"用户ID", u"用户名", u"客户类型", u"应还日期", u"逾期天数", u"承诺还款时间", u"贷款金额", u"处理状态", u"操作"] #u"应还本息合计"

    def get_query(self):
        return ["create_by__id__iexact", "create_by__name__icontains", "create_by__phone_no__iexact", "repayment__order_number__iexact", "repayment__bank_card__number__iexact"]

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
                    user.id,
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

def get_all_collection_datatable(request):
    return AllCollectionDataProvider().get_datatable(request)

def get_my_collection_datatable(request):
    return MyCollectionDataProvider().get_datatable(request)

def get_all_collection_columns():
    return AllCollectionDataProvider().get_columns()

def get_my_collection_columns():
    return MyCollectionDataProvider().get_columns()

def _get_record_data(request):
    apply_id = request.GET.get("apply_id")
    record_type = request.GET.get("record_type") or "all"
    query_type = None
    if record_type == "record" :
        query_type = Q(record_type=CollectionRecord.COLLECTION)
    elif record_type == "dispatch" :
        query_type = Q(record_type=CollectionRecord.DISPATCH)
    elif record_type == "message" :
        query_type = Q(record_type=CollectionRecord.MESSAGE)
    elif record_type == "repay" :
        query_type = Q(record_type=CollectionRecord.REPAY)
    else :
        query_type = Q()
    #print apply_id
    collection_apply = Apply.objects.get(id=apply_id)
    data_list = []
    for record in collection_apply.collectionrecord_set.filter(query_type).order_by("-id"):
        record_dict = dict()
        record_dict['id'] = record.id
        record_dict['record_type'] = record.get_record_type_display()
        record_dict['collector'] = record.create_by.username
        record_dict['add_time'] = record.create_at.strftime("%Y-%m-%d %H") if record.create_at else ""
        record_dict['promised_repay_time'] = record.promised_repay_time.strftime("%Y-%m-%d %H") if record.promised_repay_time else ""
        record_dict['notes'] = record.collection_note

        data_list.append(record_dict)
    output_data = {'data': data_list}
    return output_data

@page_permission(check_employee)
def get_collection_record_data(request):
    if request.method == 'GET':
        output_data = _get_record_data(request)
        return HttpResponse(json.dumps(output_data))
