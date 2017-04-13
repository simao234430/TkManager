# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext,Template
from django.http import HttpResponse, StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db.models import Q

import json, os, math, uuid
import traceback
from pyExcelerator import *
from datetime import datetime
import time
from time import sleep
from TkManager.util.permission_decorator import page_permission
from TkManager.operation import data_views
from TkManager.operation.data_views  import FundDetailDataProvider,get_corpus_from_repayment,get_table3_result_datatable,OverDueDetail_sum_Provider,get_periods_from_repayment,get_over_due_days,PayLoanDataProvider,RepayLoanDataProvider,get_taikang_repayment
from TkManager.collection.models import *
from TkManager.review.employee_models import check_employee
from TkManager.review.models import Review, Employee, ReviewRecord, CollectionRecord
from TkManager.order.apply_models import Apply, ExtraApply, CheckApply
from TkManager.order.models import BankCard, ContactInfo, Chsi, CheckStatus, IdCard, Profile, AddressBook, CallRecord, User, Contract
from TkManager.common.tk_log_client import TkLog
from django.views.decorators.csrf import csrf_exempt
from TkManager.review import message_client, bank_client, risk_client, redis_client

#from report_def import report_table
from TkManager.collection.strategy import Strategy
from util_mifan import *
from TkManager.util.tkdate import *
from TkManager.order.apply_models import Apply
from TkManager.review.employee_models import check_employee, get_collector_list, get_employee
from django.db import connection
from django.utils import timezone
#from django_cron import CronJobBase, Schedule
import logging
logging.basicConfig()
import threading
import calendar
from django.contrib.auth.decorators import login_required

mifan_block_list = settings.MIFAN_BLOCK_LIST
print mifan_block_list
 
def luhn_check(num):
    ''' Number - List of reversed digits '''
    digits = [int(x) for x in reversed(str(num))]
    check_sum = sum(digits[::2]) + sum((dig//10 + dig%10) for dig in [2*el for el in digits[1::2]])
    return check_sum%10 == 0

def auto_pay(request):
    try :
        TkLog().info("auto pay start")
        repayments_list = RepaymentInfo.objects.filter(Q(capital_channel_id = 2))
        applys= Apply.objects.filter(Q(type = 'l') & Q(status = '0') & Q(repayment_id__in = repayments_list ))
        for apply_item in applys:
            #repayments = RepaymentInfo.objects.get(Q(id = apply_item.repayment_id))
            #if repayments.capital_channel_id != 2:
            #   continue
            if apply_item.repayment.user.phone_no in mifan_block_list:
                jsondata[str(apply_item.id)] = u"内部黑名单，无法向米饭请款"
                jsondata[str(apply_item.id) + 'errorCode'] = "10000"
                TkLog().info("pay_loan mifan id number: %d result error code: %s and error message: %s " %(apply_item.id,  "10000",u"内部黑名单，无法向米饭请款"))
                # 持久化米饭返回结果 message_1 :errorcode , message_2: error message
                extra_apply = ExtraApply(apply = apply_item, message_1 = "1000",message_2 = u"内部黑名单，无法向米饭请款")
                extra_apply.save()
                continue
            if luhn_check(apply_item.repayment.bank_card.number):
                if apply_item.status == 'y' or apply_item.status == '0':
                    repayment = apply_item.repayment
                    s = Strategy.objects.get(pk = repayment.strategy_id)
                    TkLog().info("send to  mifan data start on id number: %d"  %(apply_item.id))
                    ret = json.loads(getdata4mifan(send2mifan(repayment,s)))
                    TkLog().info("send to  mifan data end   on id number: %d"  %(apply_item.id))
                    if ret["errorMsg"] == "success":
                        apply_item.status = '1'
                        apply_item.save()
                    else:
                        apply_item.status = '4'
                        apply_item.save()
                    TkLog().info("start Persistence result on id number: %d"  %(apply_item.id))
                    TkLog().info("pay_loan mifan id number: %d result error code: %s and error message: %s " %(apply_item.id,  ret["errorCode"], ret["errorMsg"]))
                    # 持久化米饭返回结果 message_1 :errorcode , message_2: error message
                    extra_apply = ExtraApply(apply = apply_item, message_1 = ret['errorCode'],message_2 = ret['errorMsg'])
                    extra_apply.save()
                    TkLog().info("end Persistence result on id number: %d"  %(apply_item.id))
                else:
                    pass
            else:
                apply_item.status = '4'
                apply_item.save()
                extra_apply = ExtraApply(apply = apply_item, message_1 = "银行卡校验出错,提醒用户更新银行卡信息",message_2 = "90000")
                extra_apply.save()
        return HttpResponse("auto_pay done")
    except Exception, e:
        print "excp", e
        traceback.print_exc()
        return HttpResponse("error happen")
def auto_pay_confirm(request):
    try :
        TkLog().info("auto pay confirm start")
        apply_list  = Apply.objects.filter(Q(type = 'l') & Q(status = '1'))
        for apply_item in apply_list:
                if apply_item.repayment.user.phone_no in mifan_block_list:
                    continue
                repayment = apply_item.repayment
                s = Strategy.objects.get(pk = repayment.strategy_id)
                ret = json.loads(getdata4mifan(send2mifan_confirm(repayment,s)))
                #mifan 无法判断到账状态，所以米饭已打款就认为打款成功 104 or 105
                if ret['errorCode'] == 104 or ret['errorCode'] == 105:
                    apply_item.status = '2'
                    apply_item.save()
                    risk_client.pay_loan(repayment.order_number)
                    bank_card = BankCard.get_pay_card(repayment.user)
                    repay_date = repayment.next_repay_time.strftime("%y-%m-%d")
                    if settings.MIFAN_DEBUG == False:
                        res = message_client.send_message(repayment.user.phone_no, (u"您申请的贷款已经完成打款，卡号:%s，还款日期：%s，借贷信息已提交央行征信。花啦客服热线400-606-4728 " % (bank_card.number, repay_date)).encode("gbk"), 5)
                        TkLog().info("send message %s " % res)
                else:
                    pass
                TkLog().info("pay_loan mifan account confirm id number: %d result error code: %s and error message: %s " %(apply_item.id,  ret["errorCode"], ret["errorMsg"]))
                # 持久化米饭返回结果 message_1 :errorcode , message_2: error message
                extra_apply = ExtraApply(apply = apply_item, message_1 = ret['errorCode'],message_2 = ret['errorMsg'])
                extra_apply.save()
        return HttpResponse("auto_pay done")
    except Exception, e:
        print "excp", e
        traceback.print_exc()
        return HttpResponse("error happen")

def dosomething_out():
    lt = time.localtime()
    d = 60 * (59 - lt[4]) + 60 - lt[5]
    timer = threading.Timer(d, dosomething)
    timer.start()

def dosomething():
    TkLog().info('开始一次自动代付')
    now = datetime.datetime.now()
    TkLog().info(now.strftime('%Y-%m-%d %H:%M:%S'))
    auto_pay()
    auto_pay_confirm()
    timer = threading.Timer(60*60, dosomething)
    timer.start()

#dosomething_out()


def get_related_collection_apply_id(apply_id):
    apply = get_object_or_404(Apply, id=apply_id)
    collection_applys = Apply.objects.filter(Q(repayment=apply.repayment) & Q(money=apply.money) & Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
    if len(collection_applys) >= 1:
        collection_apply = collection_applys[0]
        return str(collection_apply.id)
    else:
        return 'null'

@csrf_exempt
@page_permission(check_employee)
def add_collection_record(request):
    if request.method == 'POST':
        try:
            emplyee = get_employee(request)
            collection_to = request.POST.get("object")
            will_repay_time = request.POST.get("time")
            content = request.POST.get("content")
            aid = request.POST.get("apply")
            #res = message_client.send_message(phone_no, content.encode("gbk"), 5)
            repay_apply = Apply.objects.get(id=aid)
            record = CollectionRecord(record_type=CollectionRecord.COMMENT, object_type=CollectionRecord.SELF, create_by = emplyee,
                                      collection_note=content, promised_repay_time=None, apply=repay_apply)
            record.save()
            collection_applys = Apply.objects.filter(Q(repayment=repay_apply.repayment) & Q(money=repay_apply.money) & Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
            if len(collection_applys) >0:
                record = CollectionRecord(record_type=CollectionRecord.COMMENT, object_type=CollectionRecord.SELF, create_by = emplyee, collection_note=content, promised_repay_time=None, apply=collection_applys[0])
                record.save()
            res=True
            if res:
                TkLog().info("add collection record success %s" % emplyee.username)
                #return HttpResponse(json.dumps({"result" : u"ok"}))
                return HttpResponse(json.dumps({"error" : u"催记添加成功"}))
            else:
                TkLog().info("add collection record failed %s" % emplyee.username)
                return HttpResponse(json.dumps({"error" : u"催记添加失败"}))
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().info("add collection record failed %s %s" % (emplyee.username, str(e)))
            return HttpResponse(json.dumps({"error" : u"催记添加异常"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

def get_table1_view(request):
    if request.method == 'GET':
        columns = data_views.get_table1_columns()
        page= render_to_response('operation/table1.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def get_table2_view(request):
    if request.method == 'GET':
        columns = data_views.get_table2_columns()
        page= render_to_response('operation/table2.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def get_table3_view(request):
    if request.method == 'GET':
        columns = data_views.get_table3_columns()
        page= render_to_response('operation/table3.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def get_table3_result_view(request):
    if request.method == 'GET':
        columns = data_views.get_table3_result_columns()
        result_columns = get_table3_result_datatable(request)
        page= render_to_response('operation/table3_result.html', {"result_columns":result_columns,"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_repay_modal_batch_view(request):
    if request.method == 'GET':
        token = uuid.uuid1()
        columns = [u"id", u"用户id",u"订单号",u"用户",u"身份证", u"借款金额", u"到账金额", u"借贷方式",u"银行名称", u"申请时间", u"起息日", u"状态"]
        columns = data_views.get_repay_loan_columns()
        page= render_to_response('operation/repay_modal_batch.html', {"token":token,"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page
@page_permission(check_employee)
def get_pay_loan_view(request):
    if request.method == 'GET':
        columns = data_views.get_pay_loan_columns()
        page= render_to_response('operation/pay_loan.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_repay_loan_view(request):
    if request.method == 'GET':
        columns = data_views.get_repay_loan_columns()
        page= render_to_response('operation/repay_loan.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_repay_loan_view4custom(request):
    if request.method == 'GET':
        columns = data_views.get_repay_loan_columns()
        page= render_to_response('operation/repay_loan4custom.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_advance_loan_view(request):
    if request.method == 'GET':
        columns = [] #data_views.get_advanced_loan_columns()
        page= render_to_response('operation/advanced_loan.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def mifan_account_confirm_idlist(request):
    if request.method == 'GET':

        token = request.GET.get("token")
        exist_token = redis_client.hget("pay_token",  token)
        if not exist_token:
            ret = redis_client.hsetnx("pay_token", token, 1)
            if ret == 0: #token已经存在
                return HttpResponse(json.dumps({"error" :  "不能重复提交"}))
        else:
            return HttpResponse(json.dumps({"error" : "不能重复提交"}))

        jsondata = {};
        aid_list = json.loads(request.GET[u'id_list'])
        try :
            apply_list  = Apply.objects.filter(Q(id__in = aid_list))
            for apply_item in apply_list:
                    repayment = apply_item.repayment
                    s = Strategy.objects.get(pk = repayment.strategy_id)
                    ret = json.loads(getdata4mifan(send2mifan_confirm(repayment,s)))
                    #mifan 无法判断到账状态，所以米饭已打款就认为打款成功 104
                    if ret['errorCode'] == 104 or ret['errorCode'] == 105:
                        apply_item.status = '2'
                        apply_item.save()
                        risk_client.pay_loan(repayment.order_number)
                        bank_card = BankCard.get_pay_card(repayment.user)
                        repay_date = repayment.next_repay_time.strftime("%y-%m-%d")
                        if settings.MIFAN_DEBUG == False:
                            res = message_client.send_message(repayment.user.phone_no, (u"您申请的贷款已经完成打款，卡号:%s，还款日期：%s，借贷信息已提交央行征信。花啦客服热线400-606-4728 " % (bank_card.number, repay_date)).encode("gbk"), 5)
                            TkLog().info("send message %s " % res)
                    else:
                        pass
                    jsondata[str(apply_item.id)] = ret["errorMsg"]
                    jsondata[str(apply_item.id) + 'errorCode'] = ret['errorCode']
                    TkLog().info("pay_loan mifan account confirm id number: %d result error code: %s and error message: %s " %(apply_item.id,  ret["errorCode"], ret["errorMsg"]))
                    # 持久化米饭返回结果 message_1 :errorcode , message_2: error message
                    extra_apply = ExtraApply(apply = apply_item, message_1 = ret['errorCode'],message_2 = ret['errorMsg'])
                    extra_apply.save()
            return HttpResponse(json.dumps(jsondata))
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            jsondata["error"] =  u"mifan account confirm failed"
            return HttpResponse(json.dumps(jsondata))


def get_repay_result(aid,user):

    apply = get_object_or_404(Apply, id = aid)
    repayment = apply.repayment
    installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
    installment = None
    #if apply.status == '9':
    #    return HttpResponse(json.dumps({"error" : "ok", "msg": "改扣款已经执行成功，不能重复扣款"}))

    if len(installments) == 1:
        installment = installments[0]
    else:
        return u"未找对应的借款信息"

    bank_card = BankCard.get_repay_card(repayment.user)
    if not bank_card:
        return u"未找到还款银行卡"

    #sleep(1)
    TkLog().info("realtime repay_loan %s " % (aid ))
    #res = bank_client.realtime_pay(repayment.exact_amount, bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, 'mifan')
    #TODO: check repay status & amount

    all_repay_money = rest_repay_money = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue  - installment.reduction_amount
    real_repay_money = 0
    repay_money = 0
    res = None
    msg = ""

    if rest_repay_money == 0:
        _update_related_collection_apply(apply)
        return u"扣款已完成"

    while(rest_repay_money > 0):
        if rest_repay_money > 100000:
            repay_money = 100000
        else:
            repay_money = rest_repay_money

        try:
            print repayment.user.name
            print type(repayment.user.name)
            res = bank_client.realtime_pay(repay_money, bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, 'mifan')
        except Exception, e:
            TkLog().error("access bank service occur a exception:  except:  %s" % str(e))
            traceback.print_exc()
            print e
        msg = res.err_msg if  res and res.err_msg else ""
        TkLog().info(u"repay_for %s %s %s %d %d done " % (bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, repay_money ))
        TkLog().info("do realtime repay res:%s msg:%s" % (res.retcode, msg.decode("utf-8")))

        rest_repay_money -= repay_money
        if res.retcode != 0:
            break
        else:
            real_repay_money += repay_money
    # pay_loan
    #找到对应的催收apply

    try:
        relate_colleciton_apply_id = get_related_collection_apply_id(apply.id)
        staff = Employee.objects.get(user = user)
    except Exception, e:
        traceback.print_exc()
        print e
        TkLog().info(u"获取催收apply 和 user 失败%s" % str(e))
    if res and res.retcode == 0: #扣款成功
        try:
            apply.status = Apply.REPAY_SUCCESS
            apply.save()
            note = u"扣款成功 卡号:%s 金额:%s" % (bank_card.number, real_repay_money)
            record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                  collection_note=note, promised_repay_time=None, apply=apply)
            record.save()
            if relate_colleciton_apply_id != "null":
                relate_apply = Apply.objects.get(id = relate_colleciton_apply_id)
                record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                      collection_note=note, promised_repay_time=None, apply=relate_apply)
                record.save()
            _update_related_collection_apply(apply)
        except Exception, e:
            traceback.print_exc()
            print e
            TkLog().info(u"改订单号状态,添加record,跟新催收过程出错")
        try:
            TkLog().info(u"start update risk_server")
            res = risk_client.repay_loan(repayment.order_number, installment.installment_number)
            if res.result_code  != 0:
                TkLog().info(u"扣款已经成功, server更新失败，请联系管理员 order_number: %s  installment_number: %d"  % (repayment.order_number, installment.installment_number))
                return u"扣款已经成功, server更新失败，请联系管理员"
            TkLog().info(u" server更新成功")
        except Exception, e:
            traceback.print_exc()
            #print res.result_code
            print e
            return u"扣款已经成功, 系统更新失败，请联系管理员"
        return u"扣款成功"
    elif real_repay_money > 0: #部分成功
        try:
            installment.real_repay_amount += real_repay_money
            installment.save()
            apply.status = 'd'
            apply.save()
            note = u"扣款部分成功 卡号:%s 扣款金额:%f 成功金额:%f, 最后一笔失败原因%s" % (bank_card.number, all_repay_money/100.0, real_repay_money/100.0, msg.decode("utf-8"))
            record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                  collection_note=note, promised_repay_time=None, apply=apply)
            record.save()
            if relate_colleciton_apply_id != "null":
                relate_apply = Apply.objects.get(id = relate_colleciton_apply_id)
                record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                      collection_note=note, promised_repay_time=None, apply=relate_apply)
                record.save()
            return u"部分成功"
        except Exception, e:
            traceback.print_exc()
            print e
            TkLog().info(u"改订单号状态,添加record部分扣款成功 过程出错")
    else:
        try:
            apply.status = 'c' #失败
            apply.save()
            note = u"扣款失败 卡号:%s 扣款金额:%f 失败原因:%s" % (bank_card.number, all_repay_money/100.0, msg.decode("utf-8"))
            record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                  collection_note=note, promised_repay_time=None, apply=apply)
            record.save()
            if relate_colleciton_apply_id != "null":
                relate_apply = Apply.objects.get(id = relate_colleciton_apply_id)
                record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                      collection_note=note, promised_repay_time=None, apply=relate_apply)
                record.save()
            return  msg.decode("utf-8")
        except Exception, e:
            traceback.print_exc()
            print e
            TkLog().info(u"改订单号状态,添加record部分扣款失败 过程出错")

@login_required
@page_permission(check_employee)
def repay_batch_idlist(request):
    if request.method == 'GET':
        #print request.GET[u'id_list']
        jsondata = {};
        aid_list = json.loads(request.GET[u'id_list'])
        try :
            token = request.GET.get("token")
            exist_token = redis_client.hget("repay_token",  token)
            if not exist_token:
                ret = redis_client.hsetnx("repay_token", token, 1)
                if ret == 0: #token已经存在
                    return HttpResponse(json.dumps({"error" :  "不能重复提交"}))
            else:
                return HttpResponse(json.dumps({"error" : "不能重复提交"}))

            applys = Apply.objects.filter(Q(id__in = aid_list))
            for apply_item in applys:
                print request.user ,"type user:", type(request.user)
                jsondata[apply_item.id] =  get_repay_result(apply_item.id,request.user)
        except Exception, e:
            print "excp", e
            TkLog().info("do batch repay list confirm fail")
            traceback.print_exc()
            return HttpResponse(json.dumps(jsondata))
        #for item in range(len(ad_list)):
        #   print ad_list[item]
        return HttpResponse(json.dumps(jsondata))

@page_permission(check_employee)
def mifan_confirm_idlist(request):
    if request.method == 'GET':
        #print request.GET[u'id_list']

        token = request.GET.get("token")
        exist_token = redis_client.hget("pay_token",  token)
        if not exist_token:
            ret = redis_client.hsetnx("pay_token", token, 1)
            if ret == 0: #token已经存在
                return HttpResponse(json.dumps({"error" :  "不能重复提交"}))
        else:
            return HttpResponse(json.dumps({"error" : "不能重复提交"}))

        jsondata = {};
        aid_list = json.loads(request.GET[u'id_list'])

        try :
            applys = Apply.objects.filter(Q(id__in = aid_list))
            for apply_item in applys:
                if luhn_check(apply_item.repayment.bank_card.number):
                    if apply_item.status == 'y' or apply_item.status == '0':
                        if apply_item.repayment.user.phone_no in mifan_block_list:
                            jsondata[str(apply_item.id)] = u"内部黑名单，无法向米饭请款"
                            jsondata[str(apply_item.id) + 'errorCode'] = "10000"
                            TkLog().info("pay_loan mifan id number: %d result error code: %s and error message: %s " %(apply_item.id,  "10000",u"内部黑名单，无法向米饭请款"))
                            # 持久化米饭返回结果 message_1 :errorcode , message_2: error message
                            extra_apply = ExtraApply(apply = apply_item, message_1 = "1000",message_2 = u"内部黑名单，无法向米饭请款")
                            extra_apply.save()
                            continue
                        repayment = apply_item.repayment
                        s = Strategy.objects.get(pk = repayment.strategy_id)
                        TkLog().info("send to  mifan data start on id number: %d"  %(apply_item.id))
                        ret = json.loads(getdata4mifan(send2mifan(repayment,s)))
                        TkLog().info("send to  mifan data end   on id number: %d"  %(apply_item.id))
                        if ret["errorMsg"] == "success":
                            apply_item.status = '1'
                            apply_item.save()
                        else:
                            apply_item.status = '4'
                            apply_item.save()
                        TkLog().info("start Persistence result on id number: %d"  %(apply_item.id))
                        jsondata[str(apply_item.id)] = ret["errorMsg"]
                        jsondata[str(apply_item.id) + 'errorCode'] = ret['errorCode']
                        TkLog().info("pay_loan mifan id number: %d result error code: %s and error message: %s " %(apply_item.id,  ret["errorCode"], ret["errorMsg"]))
                        # 持久化米饭返回结果 message_1 :errorcode , message_2: error message
                        extra_apply = ExtraApply(apply = apply_item, message_1 = ret['errorCode'],message_2 = ret['errorMsg'])
                        extra_apply.save()
                        TkLog().info("end Persistence result on id number: %d"  %(apply_item.id))
                    else:
                        pass
                else:
                    apply_item.status = '4'
                    apply_item.save()
                    jsondata[str(apply_item.id)] = "银行卡校验出错,提醒用户更新银行卡信息"
                    jsondata[str(apply_item.id) + 'errorCode'] =  "90000"

        except Exception, e:
            print "excp", e
            traceback.print_exc()
            jsondata["error"] =  u"mifan failed"
            return HttpResponse(json.dumps(jsondata))
        #for item in range(len(ad_list)):
        #   print ad_list[item]
        return HttpResponse(json.dumps(jsondata))
    else:
        jsondata = {'name':'jiang'}
        return HttpResponse(json.dumps(jsondata))

def get_mifan_confirm_view(request):
    if request.method == 'GET':
        token = uuid.uuid1()
        columns = [u"申请id", u"用户", "资金渠道", u"借款金额", u"到账金额", u"借贷方式", u"申请时间", u"起息日", u"状态", u"米饭打款状态码"]
        columns = data_views.get_pay_loan_columns()
        page= render_to_response('operation/mifan_confirm.html', {"token" : token ,"columns" : columns,"datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def get_mifan_confirm_account_view(request):
    if request.method == 'GET':
        token = uuid.uuid1()
        columns = [u"申请id", u"用户", "资金渠道", u"借款金额", u"到账金额", u"借贷方式", u"申请时间", u"起息日", u"状态", u"米饭打款状态码"]
        columns = data_views.get_pay_loan_columns()
        page= render_to_response('operation/mifan_confirm_account.html', {"token" : token, "columns" : columns,"datatable" : []},
                                 context_instance=RequestContext(request))
        return page


def get_pay_modal_view(request, apply_id):
    if request.method == 'GET':
        apply = get_object_or_404(Apply, id=apply_id)
        bank_card = BankCard.get_pay_card(apply.repayment.user)
        columns = [] #data_views.get_advanced_loan_columns()
        page= render_to_response('operation/pay_modal.html', {"columns" : columns, "datatable" : [], "payment": apply.repayment, "apply": apply, "bank_card": bank_card},
                                 context_instance=RequestContext(request))
        return page

def get_repay_modal_view(request, apply_id):
    if request.method == 'GET':
        apply = get_object_or_404(Apply, id=apply_id)
        repayment = apply.repayment
        strategy = Strategy.objects.get(pk = repayment.strategy_id)
        installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
        installment = None
        if len(installments) == 1:
            installment = installments[0]
        else:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))
        rest_repay_money = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue
        #installment["rest_repay_amount"] = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue
        #installment["repay_all"] = installment.should_repay_amount + installment.repay_overdue
        #installment["base_amount"] = repayment.apply_amount / strategy.installment_count
        #installment["base_interest"] = installment.should_repay_amount - installment.base_amount
        installment_more = {}
        installment_more["rest_repay_amount"] = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue - installment.reduction_amount
        installment_more["repay_all"] = installment.should_repay_amount + installment.repay_overdue -  installment.reduction_amount
        installment_more["base_amount"] = repayment.apply_amount / strategy.installment_count
        installment_more["base_interest"] = installment.should_repay_amount - installment_more["base_amount"]
        #print installment_more
        bank_card = BankCard.get_repay_card(apply.repayment.user)
        columns = [] #data_views.get_advanced_loan_columns()
        token = uuid.uuid1()
        #collection_apply_id = get_related_collection_apply_id(apply_id)
        page= render_to_response('operation/repay_modal.html', {"apply_id" :apply_id,"installment": installment, "columns" : columns, "datatable" : [], "payment": apply.repayment, "apply": apply, "installment_more": installment_more,
                                 "bank_card": bank_card, "rest_amount": rest_repay_money, "token":token},
                                 context_instance=RequestContext(request))
        return page

def get_repay_modal_view4custom(request, apply_id):
    if request.method == 'GET':
        apply = get_object_or_404(Apply, id=apply_id)
        repayment = apply.repayment
        strategy = Strategy.objects.get(pk = repayment.strategy_id)
        installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
        installment = None
        if len(installments) == 1:
            installment = installments[0]
        else:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))
        rest_repay_money = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue
        #installment["rest_repay_amount"] = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue
        #installment["repay_all"] = installment.should_repay_amount + installment.repay_overdue
        #installment["base_amount"] = repayment.apply_amount / strategy.installment_count
        #installment["base_interest"] = installment.should_repay_amount - installment.base_amount
        installment_more = {}
        installment_more["rest_repay_amount"] = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue - installment.reduction_amount
        installment_more["repay_all"] = installment.should_repay_amount + installment.repay_overdue -  installment.reduction_amount
        installment_more["base_amount"] = repayment.apply_amount / strategy.installment_count
        installment_more["base_interest"] = installment.should_repay_amount - installment_more["base_amount"]
        print installment_more
        bank_card = BankCard.get_repay_card(apply.repayment.user)
        columns = [] #data_views.get_advanced_loan_columns()
        token = uuid.uuid1()
        #collection_apply_id = get_related_collection_apply_id(apply_id)
        page= render_to_response('operation/repay_modal4custom.html', {"apply_id" :apply_id,"installment": installment, "columns" : columns, "datatable" : [], "payment": apply.repayment, "apply": apply, "installment_more": installment_more,
                                 "bank_card": bank_card, "rest_amount": rest_repay_money, "token":token},
                                 context_instance=RequestContext(request))
        return page
@csrf_exempt
def do_realtime_pay_action(request):
    if request.method == 'GET':
        aid = request.GET.get("aid")
        type = request.GET.get("type")
        apply = get_object_or_404(Apply, id = aid)
        repayment = apply.repayment
        bank_card = BankCard.get_pay_card(repayment.user)
        if not bank_card:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找到借款款银行卡"}))
        #sleep(1)
        if type == 'realtime_pay':
            TkLog().info("realtime pay_loan %s start" % aid)
            try:
                res = message_client.send_message(repayment.user.phone_no, (u"您申请的贷款已经完成打款，卡号:%s，借贷信息已提交央行征信。花啦花啦客服400-606-4728" % bank_card.number).encode("gbk"), 5)
            except Exception,e:
                TkLog().error("call message service occur a exception:  except:  %s" % str(e))

            TkLog().info("send message %s " % res)
            res = bank_client.realtime_payfor(repayment.exact_amount, bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id)
            TkLog().info(u"pay_for %s %s %s %d %d done" % (bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, repayment.exact_amount))
            TkLog().info("realtime pay_loan %s done" % aid)
            #res = {}
            #res['err_msg'] = u"成功"
            #return HttpResponse(json.dumps({"error" : "failed", "msg": res['err_msg']}))
            msg = res.err_msg if  res.err_msg else ""
            if res.retcode == 0:
                apply.status = '2'
                apply.save()
                risk_client.pay_loan(repayment.order_number)
            else:
                apply.status = '3'
                apply.save()
            return HttpResponse(json.dumps({"error" : "ok", "msg": msg}))
        elif type == 'comfirm_success':
            TkLog().info("comfirm pay_loan success %s " % aid)
            if apply.status != '2':
                apply.status = '2'
                apply.save()
                risk_client.pay_loan(repayment.order_number)
                repay_date = repayment.next_repay_time.strftime("%y-%m-%d")
                res = message_client.send_message(repayment.user.phone_no, (u"您申请的贷款已经完成打款，卡号:%s，还款日期：%s，借贷信息已提交央行征信。花啦客服热线400-606-4728 " % (bank_card.number, repay_date)).encode("gbk"), 5)
                TkLog().info("send message %s " % res)
            else:
                risk_client.pay_loan(repayment.order_number)
            return HttpResponse(json.dumps({"error" : "ok", "msg": ""}))
        elif type == 'comfirm_failed':
            TkLog().info("comfirm pay_loan failed %s " % aid)
            apply.status = '3'
            apply.save()
            return HttpResponse(json.dumps({"error" : "ok", "msg": ""}))
    return HttpResponse(json.dumps({"error" : "get only"}))

def _update_related_collection_apply(apply, status=None):
    collection_applys = Apply.objects.filter(Q(repayment=apply.repayment) & Q(money=apply.money) & Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
    if len(collection_applys) >= 1:
        collection_apply = collection_applys[0]
        if not status:
            if collection_apply.type == Apply.COLLECTION_M0:
                collection_apply.status = Apply.REPAY_SUCCESS
            else:
                collection_apply.status = Apply.COLLECTION_SUCCESS
        else:
            collection_apply.status = status
        collection_apply.save()

@login_required
@csrf_exempt
def do_realtime_repay_action(request):
    if request.method == 'GET':
        aid = request.GET.get("aid")
        channel = request.GET.get("channel")
        type = request.GET.get("type")
        token = request.GET.get("token")

        exist_token = redis_client.hget("repay_token",  token)
        if not exist_token:
            ret = redis_client.hsetnx("repay_token", token, 1)
            if ret == 0: #token已经存在
                TkLog().info("realtime repay_loan %s duplicate token %s" % (aid, token))
                return HttpResponse(json.dumps({"error" : "pass", "msg": "不能重复提交"}))
        else:
            TkLog().info("realtime repay_loan %s duplicate token %s" % (aid, token))
            return HttpResponse(json.dumps({"error" : "pass", "msg": "不能重复提交"}))

        apply = get_object_or_404(Apply, id = aid)
        repayment = apply.repayment
        installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
        installment = None
        #if apply.status == '9':
        #    return HttpResponse(json.dumps({"error" : "ok", "msg": "改扣款已经执行成功，不能重复扣款"}))

        if len(installments) == 1:
            installment = installments[0]
        else:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))

        bank_card = BankCard.get_repay_card(repayment.user)
        if not bank_card:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找到还款银行卡"}))

        #sleep(1)
        if channel == 'realtime_repay':
            TkLog().info("realtime repay_loan %s start %s" % (aid, token))
            #res = bank_client.realtime_pay(repayment.exact_amount, bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, 'mifan')
            #TODO: check repay status & amount
            amount = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue
            all_repay_money = rest_repay_money = amount
            real_repay_money = 0
            repay_money = 0
            res = None
            msg = ""

            if rest_repay_money == 0:
                _update_related_collection_apply(apply)
                return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款已完成,请勿重复扣款"}))
            while(rest_repay_money > 0):
                if rest_repay_money > 100000:
                    repay_money = 100000
                else:
                    repay_money = rest_repay_money

                res = bank_client.realtime_pay(repay_money, bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, 'mifan')
                msg = res.err_msg if  res and res.err_msg else ""
                TkLog().info(u"repay_for %s %s %s %d %d done %s" % (bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, repay_money, token))
                TkLog().info("do realtime repay res:%s msg:%s" % (res.retcode, msg.decode("utf-8")))

                rest_repay_money -= repay_money
                #添加运营扣款record
                record_content = ""
                if res.retcode != 0:
                    break
                else:
                    real_repay_money += repay_money
            # pay_loan
            #找到对应的催收apply
            try:
                relate_colleciton_apply_id = get_related_collection_apply_id(apply.id)
                user = request.user
                staff = Employee.objects.get(user = user)
            except Exception, e:
                traceback.print_exc()
                print e
                TkLog().info(u"获取催收apply 和 user 失败%s" % str(e))

            if res and res.retcode == 0: #扣款成功
                try:
                    apply.status = Apply.REPAY_SUCCESS
                    apply.save()
                    note = u"扣款成功 卡号:%s 金额:%s" % (bank_card.number, real_repay_money)
                    record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                          collection_note=note, promised_repay_time=None, apply=apply)
                    record.save()
                    if relate_colleciton_apply_id != "null":
                        relate_apply = Apply.objects.get(id = relate_colleciton_apply_id)
                        record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                              collection_note=note, promised_repay_time=None, apply=relate_apply)
                        record.save()
                    _update_related_collection_apply(apply)
                except Exception, e:
                    traceback.print_exc()
                    print e
                    TkLog().info(u"改订单号状态,添加record,跟新催收过程出错")
                try:
                    TkLog().info(u"start update risk_server")
                    res = risk_client.repay_loan(repayment.order_number, installment.installment_number)
                    if res.result_code  != 0:
                        TkLog().info(u"扣款已经成功, server更新失败，请联系管理员 order_number: %s  installment_number: %d"  % (repayment.order_number, installment.installment_number))
                    TkLog().info(u" server更新成功")
                    #if res != 0:
                    #    return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款已经成功, server更新失败，请联系管理员"}))
                except Exception, e:
                    traceback.print_exc()
                    print e
                    return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款已经成功, 系统更新失败，请联系管理员"}))
                return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款成功"}))
            elif real_repay_money > 0: #部分成功
                try:
                    note = u"扣款部分成功 卡号:%s 扣款金额:%f 成功金额:%f, 最后一笔失败原因%s" % (bank_card.number, all_repay_money/100.0, real_repay_money/100.0, msg.decode("utf-8"))
                    record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                              collection_note=note, promised_repay_time=None, apply=apply)
                    record.save()
                    if relate_colleciton_apply_id != "null":
                        relate_apply = Apply.objects.get(id = relate_colleciton_apply_id)
                        record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                              collection_note=note, promised_repay_time=None, apply=relate_apply)
                        record.save()
                    installment.real_repay_amount += real_repay_money
                    installment.save()
                    apply.status = 'd'
                    apply.save()
                    return HttpResponse(json.dumps({"error" : "ok", "msg": "部分成功"}))
                except Exception, e:
                    traceback.print_exc()
                    print e
                    TkLog().info(u"改订单号状态,添加record部分成功过程出错")
            else:
                try:
                    apply.status = 'c' #失败
                    apply.save()
                    note = u"扣款失败 卡号:%s 扣款金额:%f 失败原因:%s" % (bank_card.number, all_repay_money/100.0, msg.decode("utf-8"))
                    record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                              collection_note=note, promised_repay_time=None, apply=apply)
                    record.save()
                    if relate_colleciton_apply_id != "null":
                        relate_apply = Apply.objects.get(Q(id = relate_colleciton_apply_id))
                        record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                              collection_note=note, promised_repay_time=None, apply=relate_apply)
                        record.save()
                    return HttpResponse(json.dumps({"error" : "ok", "msg": msg.decode("utf-8")}))
                except Exception, e:
                    traceback.print_exc()
                    print e
                    TkLog().info(u"改订单号状态,添加record失败过程出错")
        elif channel == "alipay_repay" or channel == "topublic_repay":
            try:
                url = request.GET.get("url")
                if not url:
                    redis_client.hdel("repay_token",  token)
                    return HttpResponse(json.dumps({"error" : "failed", "msg": "请上传图片"}))
                notes = request.GET.get("notes")
                check_amount = 0
                try:
                    check_amount = request.GET.get("check_amount")
                    check_amount = int(float(check_amount) * 100)
                except Exception, e:
                    traceback.print_exc()
                    TkLog().info(u"illegal amount : %s" % check_amount)
                    redis_client.hdel("repay_token",  token)
                    return HttpResponse(json.dumps({"error" : "failed", "msg": "请填写正确的凭证金额"}))

                staff = Employee.objects.get(user = request.user)
                TkLog().info("%s submit %s, url:%s, check_amount:%d" % (staff.username, channel, url, check_amount))
                #print check_amount, notes, url
                check_type = CheckApply.CHECK_ALIPAY if channel == "alipay_repay" else CheckApply.CHECK_TOPUBLIC
                check_apply = CheckApply(create_by=staff, money=check_amount, repayment=apply.repayment, status=CheckApply.WAIT, pic=url, type=check_type, notes=notes, repay_apply=apply)
                check_apply.save()
                apply.status = Apply.WAIT_CHECK
                apply.save()
                _update_related_collection_apply(apply, Apply.WAIT_CHECK)

                return HttpResponse(json.dumps({"error" : "ok", "msg": "success"}))
            except Exception, e:
                traceback.print_exc()
                print e
                TkLog().info(u"new audit apply failed %s" % str(e))
                return HttpResponse(json.dumps({"error" : "failed", "msg": str(e)}))
    return HttpResponse(json.dumps({"error" : "get only", "msg":"get only"}))

@csrf_exempt
def download_table1(request):
    if request.method == 'GET':
        TkLog().info("download table1")
        repayments = FundDetailDataProvider().object_filter(request)
        try :
            w = Workbook()
            ws = w.add_sheet('table1-%s' % datetime.now().strftime("%y-%m-%d"))
            i = 0
            fnt = Font()
            fnt.name = 'Arial'
            fnt.colour_index = 4
            fnt.bold = True
            fnt.height = 14*0x14
            align = Alignment()
            align.horz = Alignment.HORZ_CENTER
            title_style = XFStyle()
            title_style.font = fnt
            title_style.alignment = align
            if True:
                i += 1
                ws.write(i, 0, unicode("渠道", 'utf-8'))
                ws.write(i, 1, unicode("合同号", 'utf-8'))
                ws.write(i, 2, unicode("姓名", 'utf-8'))
                ws.write(i, 3, unicode("类型", 'utf-8'))
                ws.write(i, 4, unicode("身份证号", 'utf-8'))
                ws.write(i, 5, unicode("借款金额", 'utf-8'))
                ws.write(i, 6, unicode("本金", 'utf-8'))
                ws.write(i, 7, unicode("期数", 'utf-8'))
            #    ws.write(i, 8, unicode("利息", 'utf-8'))
            #    ws.write(i, 9, unicode("服务费", 'utf-8'))
                ws.write(i, 8, unicode("总应还", 'utf-8'))
                ws.write(i, 9, unicode("泰康", 'utf-8'))
                ws.write(i, 10, unicode("放款日期", 'utf-8'))
            for repay in repayments:
                i += 1
                ws.write(i, 0,unicode(repay.get_capital_channel_id_display()))
                ws.write(i, 1,unicode(repay.order_number))
                ws.write(i, 2,unicode(repay.user.name))
                ws.write(i, 3,unicode(Profile.objects.get(owner=repay.user).get_job_display()))
                ws.write(i, 4,unicode(repay.user.id_no))
                ws.write(i, 5,unicode(repay.apply_amount/100.0))
                ws.write(i, 6,unicode(get_corpus_from_repayment(repay)))
                ws.write(i, 7,unicode(repay.get_strategy_id_display()))
            #    ws.write(i, 8,unicode(repay.apply_amount/100.0))
            #    ws.write(i, 9,unicode(repay.apply_amount/100.0))
                ws.write(i, 8,unicode(repay.repay_amount/100.0))
                ws.write(i, 9,unicode(get_taikang_repayment(repay)))
                ws.write(i, 10,unicode(repay.first_repay_day.strftime("%Y-%m-%d")))
            w.save('s.xls')
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('s.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("s.xls")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % '资金明细-%s' % datetime.now().strftime("%y-%m-%d")
        return response

@csrf_exempt
def download_table2(request):
    if request.method == 'GET':
        pass

@csrf_exempt
def export_repay_loan_table(request):
    if request.method == 'GET':
        TkLog().info("download export_repay_loan_table")
        query_set = RepayLoanDataProvider().object_filter(request)
        result_set = RepayLoanDataProvider().fill_data(query_set)
        try :
            w = Workbook()
            ws = w.add_sheet(u'代扣-%s' % datetime.now().strftime("%y-%m-%d"))
            i = 0
            fnt = Font()
            fnt.name = 'Arial'
            fnt.colour_index = 4
            fnt.bold = True
            fnt.height = 14*0x14
            align = Alignment()
            align.horz = Alignment.HORZ_CENTER
            title_style = XFStyle()
            title_style.font = fnt
            title_style.alignment = align
            if True:
                i += 1
                ws.write(i, 0, unicode("id", 'utf-8'))
                ws.write(i, 1, unicode("订单号", 'utf-8'))
                ws.write(i, 2, unicode("用户", 'utf-8'))
                ws.write(i, 3, unicode("身份证", 'utf-8'))
                ws.write(i, 4, unicode("借款金额", 'utf-8'))
                ws.write(i, 5, unicode("到账金额", 'utf-8'))
                ws.write(i, 6, unicode("借贷方式", 'utf-8'))
                ws.write(i, 7, unicode("银行名称", 'utf-8'))
                ws.write(i, 8, unicode("申请时间", 'utf-8'))
                ws.write(i, 9, unicode("起息日", 'utf-8'))
                ws.write(i, 10, unicode("状态", 'utf-8'))
                ws.write(i, 11, unicode("当前期数", 'utf-8'))
            #    ws.write(i, 8, unicode("利息", 'utf-8'))
            #    ws.write(i, 9, unicode("服务费", 'utf-8'))
            for data in result_set:
                i += 1
                ws.write(i,0,data["id"])
                ws.write(i,1,data["order_number"])
                ws.write(i,2,data["name"])
                ws.write(i,3,data["card_id"])
                ws.write(i,4,data["amount"])
                ws.write(i,5,data["repay_amount"])
                ws.write(i,6,data["strategy"])
                ws.write(i,7,data["bank_data"])
                ws.write(i,8,data["apply_time"])
                ws.write(i,9,data["getpay_time"])
                ws.write(i,10,data["status"])
                ws.write(i,11,data["current_peroids"])
            w.save('s.xls')
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('s.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("s.xls")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % '代扣-%s' % datetime.now().strftime("%y-%m-%d")
        return response
@csrf_exempt
def export_pay_loan_table(request):
    if request.method == 'GET':
        TkLog().info("download export_pay_loan_table")
        query_set = PayLoanDataProvider().object_filter(request)
        result_set = PayLoanDataProvider().fill_data(query_set)
        try :
            w = Workbook()
            ws = w.add_sheet(u'代付-%s' % datetime.now().strftime("%y-%m-%d"))
            i = 0
            fnt = Font()
            fnt.name = 'Arial'
            fnt.colour_index = 4
            fnt.bold = True
            fnt.height = 14*0x14
            align = Alignment()
            align.horz = Alignment.HORZ_CENTER
            title_style = XFStyle()
            title_style.font = fnt
            title_style.alignment = align
            if True:
                i += 1
                ws.write(i, 0, unicode("申请id", 'utf-8'))
                ws.write(i, 1, unicode("订单号", 'utf-8'))
                ws.write(i, 2, unicode("用户", 'utf-8'))
                ws.write(i, 3, unicode("身份证", 'utf-8'))
                ws.write(i, 4, unicode("渠道", 'utf-8'))
                ws.write(i, 5, unicode("借款金额", 'utf-8'))
                ws.write(i, 6, unicode("到账金额", 'utf-8'))
                ws.write(i, 7, unicode("借贷方式", 'utf-8'))
                ws.write(i, 8, unicode("申请时间", 'utf-8'))
                ws.write(i, 9, unicode("起息日", 'utf-8'))
                ws.write(i, 10, unicode("状态", 'utf-8'))
                ws.write(i, 11, unicode("米饭打款状态", 'utf-8'))
            #    ws.write(i, 8, unicode("利息", 'utf-8'))
            #    ws.write(i, 9, unicode("服务费", 'utf-8'))
            for data in result_set:
                i += 1
                ws.write(i,0,data["id"])
                ws.write(i,1,data["order_number"])
                ws.write(i,2,data["channel"])
                ws.write(i,3,data["name"])
                ws.write(i,4,data["card_id"])
                ws.write(i,5,data["amount"])
                ws.write(i,6,data["repay_amount"])
                ws.write(i,7,data["strategy"])
                ws.write(i,8,data["apply_time"])
                ws.write(i,9,data["getpay_time"])
                ws.write(i,10,data["status"])
                ws.write(i,11,data["mifan_status"])
            w.save('s.xls')
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('s.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("s.xls")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % '代付-%s' % datetime.now().strftime("%y-%m-%d")
        return response
@csrf_exempt
def download_table3(request):
    if request.method == 'GET':
        TkLog().info("download table3")
        query_set = OverDueDetail_sum_Provider().object_filter(request)
        try :
            w = Workbook()
            ws = w.add_sheet('table3-%s' % datetime.now().strftime("%y-%m-%d"))
            i = 0
            fnt = Font()
            fnt.name = 'Arial'
            fnt.colour_index = 4
            fnt.bold = True
            fnt.height = 14*0x14
            align = Alignment()
            align.horz = Alignment.HORZ_CENTER
            title_style = XFStyle()
            title_style.font = fnt
            title_style.alignment = align
            if True:
                i += 1
                ws.write(i, 0, unicode("渠道", 'utf-8'))
                ws.write(i, 1, unicode("姓名", 'utf-8'))
                ws.write(i, 2, unicode("类型", 'utf-8'))
                ws.write(i, 3, unicode("身份证号", 'utf-8'))
                ws.write(i, 4, unicode("借款金额", 'utf-8'))
                ws.write(i, 5, unicode("期数", 'utf-8'))
                ws.write(i, 6, unicode("还款期数", 'utf-8'))
                ws.write(i, 7, unicode("应还日期", 'utf-8'))
                ws.write(i, 8, unicode("每期应还", 'utf-8'))
                ws.write(i, 9, unicode("逾期天数", 'utf-8'))
            #    ws.write(i, 8, unicode("利息", 'utf-8'))
            #    ws.write(i, 9, unicode("服务费", 'utf-8'))
                ws.write(i, 10, unicode("滞纳金", 'utf-8'))
                ws.write(i, 11, unicode("实还金额", 'utf-8'))
                ws.write(i, 12, unicode("逾期状态", 'utf-8'))
            for install in query_set:
                repay = install.repayment
                i += 1
                ws.write(i, 0,unicode(repay.get_capital_channel_id_display()))
                ws.write(i, 1,unicode(repay.user.name))
                ws.write(i, 2,unicode(Profile.objects.get(owner=repay.user).get_job_display()))
                ws.write(i, 3,unicode(repay.user.id_no))
                ws.write(i, 4,unicode(repay.apply_amount/100.0))
                ws.write(i, 5,unicode(get_periods_from_repayment(repay)))
                ws.write(i, 6,unicode(install.installment_number))
                ws.write(i, 7,unicode(str(install.should_repay_time)))
                ws.write(i, 8,unicode(install.should_repay_amount/100.0))
                ws.write(i, 9,unicode(get_over_due_days(install)))
                ws.write(i, 10,unicode(install.repay_overdue/100.0))
                ws.write(i, 11,unicode(install.real_repay_amount/100.0))
                ws.write(i, 12,unicode(install.get_repay_status_display()))
            w.save('s.xls')
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('s.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("s.xls")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % '未还明细-%s' % datetime.now().strftime("%y-%m-%d")
        return response

@csrf_exempt
def download_pay_loan(request):
    if request.method == 'GET':
        aids = request.GET.get("aid")
        channel = request.GET.get("type")
        TkLog().info("download pay_loan %s %s" % (aids, channel))
        aid_list = aids.split(',')
        try :
            applys = Apply.objects.filter(Q(id__in = aid_list))
            #repayments = RepaymentInfo.objects.filter(Q(id__in = aid_list))
            w = Workbook()
            ws = w.add_sheet('pay_list-%s' % datetime.now().strftime("%y-%m-%d"))
            i = 0

            fnt = Font()
            fnt.name = 'Arial'
            fnt.colour_index = 4
            fnt.bold = True
            fnt.height = 14*0x14
            align = Alignment()
            align.horz = Alignment.HORZ_CENTER
            title_style = XFStyle()
            title_style.font = fnt
            title_style.alignment = align

            if channel == 'xintuo':
                ws.write_merge(0, 0, 0, 19, unicode("信托资金划拨明细", "utf-8"), title_style)
                # TODO: 这里性能可能有问题
                i += 1
                ws.write(i, 0, unicode("序号", 'utf-8'))
                ws.write(i, 1, unicode("合同号", 'utf-8'))
                ws.write(i, 2, unicode("户名", 'utf-8'))
                ws.write(i, 3, unicode("身份证号", 'utf-8'))
                ws.write(i, 4, unicode("贷款本金", 'utf-8'))
                ws.write(i, 5, unicode("贷款金额", 'utf-8'))
                ws.write(i, 6, unicode("借款金额", 'utf-8'))
                ws.write(i, 7, unicode("日贷款服务费", 'utf-8'))
                ws.write(i, 8, unicode("日利率", 'utf-8'))
                ws.write(i, 9, unicode("贷款天数", 'utf-8'))
                ws.write(i, 10, unicode("还款期数", 'utf-8'))
                ws.write(i, 11, unicode("每期还款金额", 'utf-8'))
                ws.write(i, 12, unicode("借款账号", 'utf-8'))
                ws.write(i, 13, unicode("开户银行", 'utf-8'))
                ws.write(i, 14, unicode("开户支行", 'utf-8'))
                ws.write(i, 15, unicode("还款账号", 'utf-8'))
                ws.write(i, 16, unicode("开户银行", 'utf-8'))
                ws.write(i, 17, unicode("开户支行", 'utf-8'))
                for apply in applys:
                    i += 1
                    repayment = apply.repayment
                    #contracts = Contract.objects.filter(owner = repayment.user).order_by("-sign_time")
                    #order_id = contracts[0].contract_id if len(contracts) == 1 else ""
                    ws.write(i, 0, i+1)
                    ws.write(i, 1, repayment.order_number)
                    ws.write(i, 2, repayment.user.name)
                    ws.write(i, 3, repayment.user.id_no)
                    ws.write(i, 4, repayment.apply_amount/100.0)
                    ws.write(i, 5, repayment.apply_amount*(1 - 0.0003 * repayment.get_repayments_days())/100.0)
                    ws.write(i, 6, repayment.exact_amount/100.0)
                    ws.write(i, 7, "%.2f%%" % repayment.get_strategy_rate())
                    ws.write(i, 8, "0.03%")
                    ws.write(i, 9, repayment.get_repayments_days())
                    ws.write(i, 10, repayment.get_repayments_instalments())
                    ws.write(i, 11, repayment.get_first_installments_amount()/100.0)
                    ws.write(i, 12, repayment.bank_card.number)
                    ws.write(i, 13, repayment.bank_card.get_bank_type_display())
                    ws.write(i, 14, "")
                    ws.write(i, 15, repayment.bank_card.number)
                    ws.write(i, 16, repayment.bank_card.get_bank_type_display())
                    ws.write(i, 17, "")
                    if apply.status == '0':
                        apply.status = '1'
                        apply.save()
            elif channel == 'mifan':
                ws.write_merge(0, 0, 0, 19, unicode("米饭P2P资金划拨明细", "utf-8"), title_style)
                i += 1
                ## 哦 新版本
                ws.write(i, 0, unicode("状态", 'utf-8'))
                ws.write(i, 1, unicode("标识", 'utf-8'))
                ws.write(i, 2, unicode("申请单号", 'utf-8'))
                ws.write(i, 3, unicode("还款人户名", 'utf-8'))
                ws.write(i, 4, unicode("还款人证件号", 'utf-8'))
                ws.write(i, 5, unicode("还款人银行卡号", 'utf-8'))
                ws.write(i, 6, unicode("还款银行", 'utf-8'))
                ws.write(i, 7, unicode("审批金额", 'utf-8'))
                ws.write(i, 8, unicode("还款人电话", 'utf-8'))
                ws.write(i, 9, unicode("审批期限", 'utf-8'))
                ws.write(i, 10, unicode("产品号", 'utf-8'))
                ws.write(i, 11, unicode("每期还款", 'utf-8'))
                ws.write(i, 12, unicode("收款人名称", 'utf-8'))
                ws.write(i, 13, unicode("收款银行", 'utf-8'))
                ws.write(i, 14, unicode("收款支行", 'utf-8'))
                ws.write(i, 15, unicode("收款银行卡号", 'utf-8'))
                ws.write(i, 16, unicode("收款银行开户省", 'utf-8'))
                ws.write(i, 17, unicode("收款开户行市", 'utf-8'))
                ws.write(i, 18, unicode("收款银行卡类型", 'utf-8'))
                ws.write(i, 19, unicode("申请日期", 'utf-8'))
                for apply in applys:
                    i += 1
                    repayment = apply.repayment
                    s = Strategy.objects.get(pk = repayment.strategy_id)
                    #print s.get_installment_amount(repayment.apply_amount, 1)
                    #contracts = Contract.objects.filter(owner = repayment.user).order_by("-sign_time")
                    #order_id = contracts[0].contract_id if len(contracts) == 1 else ""
                    ws.write(i, 0, 0)
                    ws.write(i, 1, unicode("花啦花啦", 'utf-8'))
                    ws.write(i, 2, repayment.order_number)
                    ws.write(i, 3, repayment.user.name)
                    ws.write(i, 4, repayment.user.id_no)
                    ws.write(i, 5, repayment.bank_card.number)
                    ws.write(i, 6, repayment.bank_card.get_bank_type_display())
                    ws.write(i, 7, repayment.apply_amount/100.0)
                    ws.write(i, 8, repayment.user.phone_no)
                    ws.write(i, 9, s.installment_days if s.is_day_percentage() else s.installment_count)
                    ws.write(i, 10, '1' if s.is_day_percentage() else "0")
                    ws.write(i, 11, s.get_installment_amount(repayment.apply_amount, 1)/100.0)
                    ws.write(i, 12, repayment.user.name)
                    ws.write(i, 13, repayment.bank_card.get_bank_type_display())
                    ws.write(i, 14, repayment.bank_card.bank)
                    ws.write(i, 15, repayment.bank_card.number)
                    ws.write(i, 16, repayment.bank_card.bank_province)
                    ws.write(i, 17, repayment.bank_card.bank_city)
                    ws.write(i, 18, "0")
                    ws.write(i, 19, repayment.apply_time.strftime("%Y-%m-%d %H:%M:%S") )
                    # 已经有了米饭请款接口,不需要再用以前的接口了，保留这个运营方便倒表
                    #if apply.status == '0':
                    #    apply.status = '1'
                    #    apply.save()
            w.save('s.xls')
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('s.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("s.xls")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % 'pay_list-%s' % datetime.now().strftime("%y-%m-%d")
        return response
    return HttpResponse(json.dumps({"error" : "get only"}))

#@csrf_exempt
#def gen_excel(request):
#    if request.method == 'GET':
#        try :
#            w = Workbook()
#            ws = w.add_sheet('100个最近拒绝的用户-%s' % datetime.now().strftime("%y-%m-%d"))
#            i = 0
#            fnt = Font()
#            fnt.name = 'Arial'
#            fnt.colour_index = 4
#            fnt.bold = True
#            fnt.height = 14*0x14
#            align = Alignment()
#            align.horz = Alignment.HORZ_CENTER
#            title_style = XFStyle()
#            title_style.font = fnt
#            title_style.alignment = align
#
#            #repaymentinfo = RepaymentInfo.objects.get(id= 366)
#            #repay_temp_dict = repaymentinfo.get_repay_status_display()
#            #print  "########"
#            #print  repay_temp_dict
#            repay_status_type_t = {
#                0: '放款中',
#                1: '还款中',
#                2: '逾期',
#                3: '已完成',
#                4: '审核中',
#                5: '已放款',
#                6: '审核通过',
#                7: '---',
#                8: '逾期完成',
#            }
#            i += 1
#           # ws.write(i, 0, unicode("用户id", 'utf-8'))
#           # ws.write(i, 1, unicode("名字", 'utf-8'))
#           # ws.write(i, 2, unicode("银行卡", 'utf-8'))
#            ws.write(i, 0, unicode("用户id", 'utf-8'))
#            ws.write(i, 1, unicode("logid", 'utf-8'))
#            ws.write(i, 2, unicode("时间", 'utf-8'))
#            #ws.write(i, 0, unicode("用户id", 'utf-8'))
#            #ws.write(i, 1, unicode("用户名", 'utf-8'))
#            #ws.write(i, 2, unicode("状态", 'utf-8'))
#            #ws.write(i, 3, unicode("订单号", 'utf-8'))
#            id_list = [442,452]
#            #items = Apply.objects.filter(Q(id__in = id_list))
#            #items = Apply.objects.filter(Q(id = 442))
#            cursor = connection.cursor()
#            #cursor.execute("select user.id ,name , bankcard.number FROM user RIGHT JOIN bankcard   ON  user.id =  bankcard.user_id limit 250")
#            cursor.execute("select uin ,logid ,timestamp from report  where uin in  ( select id  from user where id > 99792)")
#            #cursor.execute("select owner_id ,  (select name from user where id = owner_id )as name  from checkstatus where apply_status =  5 order by id  desc  limit 100")
#            #cursor.execute("select user_id ,(select name from user where id = user_id )as name  ,repay_status , order_number from repaymentinfo where repay_status in (0,1,2,3,5,8)  order by user_id ,id desc limit 200")
#            items = cursor.fetchall()
#            #items = RepaymentInfo.objects.filter(Q(id__in = aid_list))
#            for item in items:
#                i += 1
#                ws.write(i, 0, item[0])
#         #       ws.write(i, 1, item[1])
#               # ws.write(i, 2, item[2])
#                if item[1] in report_table:
#                    ws.write(i, 1, report_table[item[1]])
#                else:
#                    ws.write(i, 1, item[1])
#                timeStamp = int(item[2])
#                dateArray = datetime.utcfromtimestamp(timeStamp)
#                otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
#                ws.write(i, 2, otherStyleTime)
#                #ws.write(i, 2, item[2])
#                #ws.write(i, 2, unicode(repay_status_type_t[int(item[2])], 'utf-8'))
#                #ws.write(i, 3, item[3])
#
#            w.save('s.xls')
#        except Exception, e:
#            print "excp", e
#            traceback.print_exc()
#            return HttpResponse(json.dumps({"error" : u"load failed"}))
#        response = StreamingHttpResponse(FileWrapper(open('s.xls'), 8192), content_type='application/vnd.ms-excel')
#        response['Content-Length'] = os.path.getsize("s.xls")
#        response['Content-Disposition'] = 'attachment; filename=%s.xls' % 'pay_list-%s' % datetime.now().strftime("%y-%m-%d")
#        return response
#    return HttpResponse(json.dumps({"error" : "get only"}))
def get_forword_month_day(start_day=None, i=1):
    if not start_day:
        start_day = datetime.now()
    month = start_day.month - 1 + i
    year = start_day.year + month / 12
    month = month % 12 + 1
    day = min(start_day.day, calendar.monthrange(year,month)[1])
    return datetime(year,month,day)

def get_installment_date(i, day=None,id=10):
    '''
        第i期还款时间(预计)  T+1 + timedelta * i
    '''

    print id
    if id == 10:
        return day + timedelta(21)
    elif id == 11:
        return day + timedelta(28)
    else:
        return get_forword_month_day(day,i )
def test(request):
    print "haha"
#    orders = [
#"2098312963114221559",
#"6052040352590615591",
#"7106670789371903058",
#"5995456529668672283",
#"4835657069435688674",
#"1755985544939777472",
#"7273845457579845587",
#"3955328670400589555",
#"6832117447519989567",
#"7440264783410375721"
#]
#
#    for o in orders:
#        r = RepaymentInfo.objects.get(Q(order_number = str(o)))
#        installs =  InstallmentDetailInfo.objects.filter(repayment_id=r.id)
#        for i in installs:
#    #        i.should_repay_time   =  get_installment_date(i.installment_number, r.first_repay_day,r.strategy_id)
#    #        i.save()
#            print r.order_number,r.user.phone_no,r.strategy_id,i.should_repay_time , r.next_repay_time,r.first_repay_day,r.user.name
#            #print a
#
#    applys= Apply.objects.filter(Q(status = '9') & Q(type = 'p'))
#    for apply in applys:
#        collection_applys = Apply.objects.filter(Q(repayment=apply.repayment) & Q(money=apply.money) & Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
#        if len(collection_applys) >= 1:
#            collection_apply = collection_applys[0]
#            #if collection_apply.status == Apply.REPAY_SUCCESS:
#            if collection_apply.status == Apply.PROCESSING or collection_apply.status == Apply.REPAY_FAILED:
#            #if collection_apply.status == Apply.PROCESSING and collection_apply.type == Apply.COLLECTION_M0:
#                collection_apply.status = Apply.REPAY_SUCCESS
#                collection_apply.save()
#                print apply.repayment.user.name, apply.money + 1,apply.repayment.order_number ,collection_apply.status,collection_apply.type
    """下面的片段是校验生成扣款 apply 的生成时间是否正确"""
#    repayments = RepaymentInfo.objects.filter(Q(capital_channel_id = 2) & Q(repay_status__in  = [1,2,5])).order_by('first_repay_day')
#    print "电话", "放款策略","install 应还时间", "repay 应还时间"
#    for r in repayments:
#        for i in InstallmentDetailInfo.objects.filter(Q(repayment = r)):
#            if r.strategy_id == 10 or r.strategy_id == 11:
#                if (i.should_repay_time.day - r.next_repay_time.day) != 0:
#                    print r.order_number,r.user.phone_no,r.strategy_id,i.should_repay_time , r.next_repay_time,r.first_repay_day,r.user.name
#                    #print r.order_number,r.first_repay_day,r.user.name
#            else:
#                if i.should_repay_time.day !=  r.next_repay_time.day:
#                    print r.order_number,r.user.phone_no,r.strategy_id, i.should_repay_time, r.next_repay_time, r.first_repay_day,r.user.name
                    #print r.order_number,r.first_repay_day,r.user.name
#"""下面的片段是查看逾期客户的审批责任人 """
#    t1 = '2015-11-01'  
#    t = time.strptime(t1,"%Y-%m-%d") #struct_time类型  
#    d1 = datetime(t[0], t[1],t[2]) #datetime类型 
#    t2 = '2015-12-01'  
#    date  = time.strptime(t2,"%Y-%m-%d") #struct_time类型  
#    d2 = datetime(date[0], date[1],date[2]) #datetime类型 
#
#    applys= Apply.objects.filter(Q(create_at__gte =  d1) & Q(create_at__lte =  d2)  & Q(type = 'p'))
#    print 'query sql: ' + str(applys.query)
#    print applys.count()
#    user_list = []
#    for apply in applys:
#        collection_applys = Apply.objects.filter(Q(repayment=apply.repayment) & Q(money=apply.money) & Q(type__in=[Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
#        if len(collection_applys) >= 1:
#            collection_apply = collection_applys[0]
#            #if collection_apply.status == Apply.REPAY_SUCCESS:
#            if  collection_apply.status == Apply.REPAY_FAILED:
#            #if collection_apply.status == Apply.PROCESSING or collection_apply.status == Apply.REPAY_FAILED:
#            #if collection_apply.status == Apply.PROCESSING and collection_apply.type == Apply.COLLECTION_M0:
#                #collection_apply.status = Apply.REPAY_SUCCESS
#                #collection_apply.save()
#                #print apply.repayment.user.id, apply.repayment.user.name, apply.money + 1,apply.repayment.order_number ,collection_apply.status,collection_apply.type
#                print apply.repayment.user.id
#                user_list.append(apply.repayment.user.id)
#    print user_list

#    t1 = '2015-11-01'
#    t = time.strptime(t1,"%Y-%m-%d") #struct_time类型
#    d1 = datetime(t[0], t[1],t[2]) #datetime类型
#    t2 = '2015-12-01'
#    date  = time.strptime(t2,"%Y-%m-%d") #struct_time类型
#    d2 = datetime(date[0], date[1],date[2]) #datetime类型
#
#    applys= Apply.objects.filter(Q(create_at__gte =  d1) & Q(create_at__lte =  d2)  & Q(type = 'p'))
#    print 'query sql: ' + str(applys.query)
#    print applys.count()
#    user_list = []
#    for apply in applys:
#        collection_applys = Apply.objects.filter(Q(repayment=apply.repayment) & Q(money=apply.money) & Q(type__in=[Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
#        if len(collection_applys) >= 1:
#            collection_apply = collection_applys[0]
#            #if collection_apply.status == Apply.REPAY_SUCCESS:
#            if  collection_apply.status == Apply.REPAY_FAILED:
#            #if collection_apply.status == Apply.PROCESSING or collection_apply.status == Apply.REPAY_FAILED:
#            #if collection_apply.status == Apply.PROCESSING and collection_apply.type == Apply.COLLECTION_M0:
#                #collection_apply.status = Apply.REPAY_SUCCESS
#                #collection_apply.save()
#                #print apply.repayment.user.id, apply.repayment.user.name, apply.money + 1,apply.repayment.order_number ,collection_apply.status,collection_apply.type
#                print apply.repayment.user.id
#                user_list.append(apply.repayment.user.id)
#    print user_list
    #    #    print i.repayment.order_number
    return HttpResponse("test")
from django_cron import CronJobBase, Schedule

def my_scheduled_job():
  print 'haha'
  pass

class SimpleTaskCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "TkManager.operation.general_views.SimpleTaskCronJob"

    def do(self):
        print "test"
        pass    # do your thing here
