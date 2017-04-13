# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from datetime import datetime
from TkManager.util.permission_decorator import page_permission
from TkManager.order.apply_models import Apply, CheckApply
from TkManager.review.employee_models import check_employee, get_collector_list, get_employee, is_collection_manager
from TkManager.review.models import CollectionRecord
from TkManager.audit import data_views
from TkManager.operation import data_views as data_views_operation
from TkManager.util.tkdate import *
from TkManager.collection.general_views import _update_related_repay_apply
from TkManager.operation.general_views import _update_related_collection_apply
from TkManager.collection.models import *
from TkManager.common.tk_log_client import TkLog

from TkManager.common.dict import dict_addcount, dict_addmap, dict_addnumber
from TkManager.collection.strategy import Strategy
#from TkManager.order.models import BankCard, ContactInfo
from TkManager.review import message_client, bank_client, risk_client, redis_client
import json, traceback

def get_table1_view(request):
    if request.method == 'GET':
        columns = data_views_operation.get_table1_columns()
        page= render_to_response('operation/table1.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def get_table2_view(request):
    if request.method == 'GET':
        columns = data_views_operation.get_table2_columns()
        page= render_to_response('operation/table2.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def get_table3_view(request):
    if request.method == 'GET':
        columns = data_views_operation.get_table3_columns()
        page= render_to_response('operation/table3.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_check_page_view(request):
    if request.method == 'GET':
        columns = data_views.get_check_columns()
        page= render_to_response('audit/check.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_receivables_page_view(request):
    if request.method == 'GET':
        columns = data_views.get_receivables_columns()
        page= render_to_response('audit/receivables.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_received_page_view(request):
    if request.method == 'GET':
        columns = data_views.get_received_columns()
        page= render_to_response('audit/received.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def hide_amount(amount):
    amount_str = str(round(amount/100.0, 2))
    return amount_str[0:1] + 'XX' + amount_str[3:]

@page_permission(check_employee)
def get_check_modal_view(request, apply_id):
    if request.method == 'GET':
        check_apply = CheckApply.objects.get(pk = apply_id)
        pics = check_apply.pic.split(";")
        invi_amount = hide_amount(check_apply.money)
        page= render_to_response('audit/check_modal.html', {"apply":check_apply, "pics":pics, "amount":invi_amount},
                                 context_instance=RequestContext(request))
        return page

#def get_installment_by_check_apply(check_apply):
#    pass

@csrf_exempt
def confirm_check(request):
    if request.method == 'POST':
        try:
            aid = request.POST.get("aid")
            amount = request.POST.get("amount")
            notes = request.POST.get("notes")
            check_apply = CheckApply.objects.get(pk = aid)
            if not amount:
                return HttpResponse(json.dumps({"error" : u"复核金额不能为空"}))
            check_apply_money = 0
            try:
                check_apply_money = int(float(amount) * 100)
            except Exception, e:
                print e
                traceback.print_exc()
                TkLog().info("confirm_check failed %s" % (str(e)))
                return HttpResponse(json.dumps({"error" : u"复核金额非法"}))
            if check_apply_money == check_apply.money:
                check_apply.status = CheckApply.CHECK_SUCCESS
                if check_apply.repay_apply.type == Apply.REPAY_LOAN:
                    check_apply.repay_apply.status = Apply.REPAY_SUCCESS
                    _update_related_collection_apply(check_apply.repay_apply)
                else : #催收
                    check_apply.repay_apply.status = Apply.COLLECTION_SUCCESS
                    _update_related_repay_apply(check_apply.repay_apply)
                #risk_client.repay_loan()
                #res = risk_client.repay_loan(check_apply.repayment.order_number, check_apply.installment, check_apply.money)
                repay_type = InstallmentDetailInfo.REPAY_TYPE_AUTO
                if check_apply.type == CheckApply.CHECK_ALIPAY:
                    repay_type = InstallmentDetailInfo.REPAY_TYPE_ALIPAY
                elif check_apply.type == CheckApply.CHECK_TOPUBLIC:
                    repay_type = InstallmentDetailInfo.REPAY_TYPE_PUB
                else:
                    TkLog().warn(u"unknown check apply type : %d. use default auto" % check_apply.type)

                res = risk_client.repay_loan(check_apply.repayment.order_number, check_apply.installment, repay_type)
                if not res or res.result_code  != 0:
                    TkLog().info(u"repay_loan to risk_server failed. order_number: %s, installment_number: %d"
                                    % (check_apply.repayment.order_number, check_apply.installment))
                    TkLog().info(u"res:%d" % res.result_code)
                    return HttpResponse(json.dumps({"error" : "更新客户还款状态失败，请联系管理员"}))
                check_apply.save()
                check_apply.repay_apply.save()
                record = CollectionRecord(record_type=CollectionRecord.CHECK_NOTES, object_type=CollectionRecord.SELF, create_by = get_employee(request),
                        collection_note="财务备注:%s" % (notes), promised_repay_time=None, apply=check_apply.repay_apply)
                record.save()
                TkLog().info("confirm_check success %d" % check_apply_money)
                return HttpResponse(json.dumps({"msg" : "金额匹配，复核成功"}))
            else:
                TkLog().info("confirm_check failed %d != %d" % (check_apply_money, check_apply.money))
                return HttpResponse(json.dumps({"error" : u"金额不匹配"}))
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().info("confirm_check failed %s" % (str(e)))
            return HttpResponse(json.dumps({"error" : u"确认复核失败"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
def back_check(request):
    if request.method == 'POST':
        try:
            aid = request.POST.get("aid")
            TkLog().info("check_back failed %s" % (aid))
            notes = request.POST.get("notes")
            if not notes:
                return HttpResponse(json.dumps({"error" : u"打回必须填写原因"}))
            check_apply = CheckApply.objects.get(pk = aid)
            check_apply.status = CheckApply.CHECK_FAILED
            if check_apply.repay_apply.type == Apply.REPAY_LOAN:
                check_apply.repay_apply.status = Apply.WAIT
                _update_related_collection_apply(check_apply.repay_apply, Apply.PROCESSING)
                record = CollectionRecord(record_type=CollectionRecord.CHECK_BACK, object_type=CollectionRecord.SELF, create_by = get_employee(request),
                        collection_note="打回原因:%s" % (notes), promised_repay_time=None, apply=check_apply.repay_apply)
                record.save()
            else : #催收
                check_apply.repay_apply.status = Apply.PROCESSING
                _update_related_repay_apply(check_apply.repay_apply, Apply.WAIT)
                record = CollectionRecord(record_type=CollectionRecord.CHECK_BACK, object_type=CollectionRecord.SELF, create_by = get_employee(request),
                        collection_note="打回原因:%s" % (notes), promised_repay_time=None, apply=check_apply.repay_apply)
                record.save()
            check_apply.save()
            check_apply.repay_apply.save()
            TkLog().info("back_check success")
            return HttpResponse(json.dumps({"error" : "ok", "msg": "success"}))
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().info("check_back failed %s" % (str(e)))
            return HttpResponse(json.dumps({"error" : u"确认复核失败"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))
