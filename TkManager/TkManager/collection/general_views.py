# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext,Template
from django.http import HttpResponse, StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db.models import Q

import json, os, uuid, requests
import traceback
from pyExcelerator import *
from datetime import datetime
from TkManager.util.permission_decorator import page_permission
from TkManager.order.apply_models import Apply, CheckApply
from TkManager.review.employee_models import check_employee, get_collector_list, get_employee, is_collection_manager
from TkManager.collection import data_views
from TkManager.util.tkdate import *
from TkManager.collection.models import *
from TkManager.common.tk_log_client import TkLog
from django.views.decorators.csrf import csrf_exempt
from TkManager.review.models import *
from TkManager.common.dict import dict_addcount, dict_addmap, dict_addnumber
from TkManager.collection.strategy import Strategy
from TkManager.order.models import BankCard, ContactInfo,CheckStatus
from TkManager.review import message_client, bank_client, risk_client, redis_client
from TkManager.review.general_views import _get_info_by_apply
from TkManager.review import rc_client
import random
from TkManager.review.general_views import _get_review_label


@page_permission(check_employee)
def get_all_collection_view(request):
    if request.method == 'GET':
        columns = data_views.get_all_collection_columns()
        page= render_to_response('collection/collection_all.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_mine_collection_view(request):
    if request.method == 'GET':
        columns = data_views.get_my_collection_columns()
        #columns = data_views.get_rt_order_columns()
        page= render_to_response('collection/collection_mine.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

# 查看催收modal页面
@page_permission(check_employee)
def get_collection_info_view(request, apply_id):
    if request.method == 'GET':
        collection_dict = _get_info_by_apply(request, apply_id)
        labels = _get_review_label()
        review_dict.update(labels)
        page= render_to_response('collection/view_collection_modal.html', collection_dict, context_instance=RequestContext(request))
        return page

# 分配催收modal页面
def dispatch_collection_info_view(request, apply_id):
    if request.method == 'GET':
        collectors = get_collector_list()
        apply = get_object_or_404(Apply, id=apply_id)
        repayment = apply.repayment
        installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
        installment = None
        bank_card = BankCard.get_repay_card(apply.repayment.user)
        if len(installments) == 1:
            installment = installments[0]
        else:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))
        rest_repay_money = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue - installment.reduction_amount
        page= render_to_response('collection/dispatch_collection_modal.html', {"datatable" : [], "payment": apply.repayment, "apply": apply, "bank_card": bank_card, "rest_amount": rest_repay_money,
            "collectors": collectors}, context_instance=RequestContext(request))
        return page

# 催收modal页面
@page_permission(check_employee)
def get_collection_info(request, apply_id):
    if request.method == 'GET':
        apply = get_object_or_404(Apply, id=apply_id)
        repayment = apply.repayment
        installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
        strategy = Strategy.objects.get(pk = repayment.strategy_id)
        installment = None
        if len(installments) == 1:
            installment = installments[0]
        else:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))
        rest_repay_money = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue - installment.reduction_amount
        bank_card = BankCard.get_repay_card(apply.repayment.user)
        columns = [] #data_views.get_advanced_loan_columns()
        token = uuid.uuid1()
        review = apply.review_set.last()
        records = []
        if review:
            records = review.reviewrecord_set.values()

        installment_more = {}
        installment_more["rest_repay_amount"] = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue - installment.reduction_amount
        installment_more["repay_all"] = installment.should_repay_amount + installment.repay_overdue
        installment_more["base_amount"] = repayment.apply_amount / strategy.installment_count
        installment_more["base_interest"] = installment.should_repay_amount - installment_more["base_amount"]
        #print installment_more
        bank_card = BankCard.get_repay_card(apply.repayment.user)
        columns = [] #data_views.get_advanced_loan_columns()
        token = uuid.uuid1()

        review = apply.review_set.last()
        records = []
        if review:
            records = review.reviewrecord_set.values()

        contacts = ContactInfo.objects.filter(owner=apply.create_by).order_by('-id')
        if len(contacts) > 3:
            contacts = contacts[0:3]
            contacts.reverse()

        collection_check = redis_client.hget("collection_check", apply.create_by_id)
        if collection_check:
            collection_check = collection_check.split(":")[1]
        else:
            collection_check = '1'
        page = render_to_response('collection/collection_modal.html',
                                  {"installment": installment, "columns": columns,
                                   "datatable": [], "payment": apply.repayment,
                                                                       "apply": apply, "installment_more": installment_more,
                                                                       "bank_card": bank_card, "rest_amount": rest_repay_money,
                                                                       "token": token, "contacts": contacts, "collection_check": collection_check},
                                 context_instance=RequestContext(request))
        return page
    return HttpResponse(json.dumps({"error" : u"get only"}))

@page_permission(check_employee)
def get_message_info(request, apply_id):
    if request.method == 'GET':
        try:
            apply = get_object_or_404(Apply, id=apply_id)
            contacts = ContactInfo.objects.filter(owner = apply.create_by).order_by('-id')
            if len(contacts) > 3:
                contacts = contacts[0:3]
                contacts.reverse()

            page= render_to_response('collection/message.html', {"contacts" : contacts, "applyer":apply.create_by},
                                     context_instance=RequestContext(request))
            return page
        except Exception, e:
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"exception %s" % str(e)}))
    return HttpResponse(json.dumps({"error" : u"get only"}))

@page_permission(check_employee)
def get_reduction_info(request, apply_id):
    if request.method == 'GET':
        try:
            apply = get_object_or_404(Apply, id=apply_id)
            repayment = apply.repayment
            installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
            installment = None
            if len(installments) == 1:
                installment = installments[0]
            else:
                return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))
            radio = 1 if is_collection_manager(request) else 0.4
            max_reduction = installment.repay_overdue / 100.0 * radio
            page= render_to_response('collection/reduction.html', {"installment":installment, "max_reduction":max_reduction},
                                     context_instance=RequestContext(request))
            return page
        except Exception, e:
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"exception %s" % str(e)}))
    return HttpResponse(json.dumps({"error" : u"get only"}))

def _get_collection_info():
    collection_info = {}
    return collection_info

@csrf_exempt
def do_pay_overdue_action(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({"error" : "ok"}))
    return HttpResponse(json.dumps({"error" : "get only"}))

def _get_installment_by_apply(re_apply):
    repayment = re_apply.repayment
    installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=re_apply.money + 1)
    installment = None
    if len(installments) == 1:
        installment = installments[0]
    return installment

@csrf_exempt
def do_reduction(request):
    if request.method == 'POST':
        try:
            amount = request.POST.get("amount")
            reason = request.POST.get("reason")
            print "reason", reason
            if not reason:
                return HttpResponse(json.dumps({"error" : u"请填写减免原因"}))
            aid = request.POST.get("apply")
            collection_apply = Apply.objects.get(id=int(aid))
            installment = _get_installment_by_apply(collection_apply)
            reduction_amount = int(float(amount) * 100)
            radio = 1 if is_collection_manager(request) else 0.4
            if reduction_amount >= 0 and reduction_amount <= installment.repay_overdue * radio:
                installment.reduction_amount = reduction_amount
                installment.save()
                record = CollectionRecord(record_type=CollectionRecord.DISCOUNT, object_type=CollectionRecord.SELF, create_by = get_employee(request),
                        collection_note="减免金额:%s,  减免原因:%s" % (amount, reason), promised_repay_time=None, apply=collection_apply)
                record.save()
                TkLog().info("do_reduction success amount:%s, staff:%s apply_id:%s" % (amount, get_employee(request).username, aid))
                return HttpResponse(json.dumps({"result" : u"ok"}))
            else:
                TkLog().info("do_reduction out of range. amount:%s, staff:%s apply_id:%s" % (amount, get_employee(request).username, aid))
                return HttpResponse(json.dumps({"error" : u"减免金额超出权限范围"}))
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().info("do_reduction failed excp:%s" % (str(e)))
            return HttpResponse(json.dumps({"error" : u"减免失败"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        review = Review()
        try:
            apply_id = request.POST.get("apply_id")
            staff = Employee.objects.get(user = request.user)
            apply = Apply.objects.get(pk = apply_id)
            TkLog().info(u"%s start review: %d)%s" %(staff.username, apply.id, apply.create_by.name))
            reviews = Review.objects.filter(order = apply).order_by("-id")
            if len(reviews) > 0:
                if reviews[0].finish_time: #已经完成 新建review
                    review.reviewer = staff
                    review.create_at = datetime.now()
                    review.order = apply
                    review.review_res = 'i'
                    review.save()
                    apply.status = 'i'
                    apply.save()
                elif reviews[0].reviewer == staff: # 重新打开了自己的review
                    review = reviews[0]
                    pass
                else:
                    return HttpResponse(json.dumps({"error" : u"%s审批中" % reviews[0].reviewer.username}))
            else: #没有review 新建
                review.reviewer = staff
                review.create_at = datetime.now()
                review.order = apply
                review.review_res = 'i'
                review.save()
                apply.status = 'i'
                apply.save()
        except Exception, e:
            print e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse(json.dumps({"result" : "ok", 'review_id' : review.id}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

#@csrf_exempt
#def cancel_review(request):
#    if request.method == 'POST':
#        try:
#            applyid = request.POST.get("apply_id")
#            staff = Employee.objects.get(user = request.user)
#            apply = Apply.objects.get(pk = applyid)
#            TkLog().info(u"%s cancel review: %d)%s" %(staff.username, apply.id, apply.create_by.name))
#            reviews = Review.objects.filter(order = apply).order_by("id")
#            if len(reviews) <= 0:
#                return HttpResponse(json.dumps({"result" : u"no review to cancel"}))
#            for r in reviews:
#                #print r
#                if not r.finish_time:
#                    r.delete()
#        except Exception, e:
#            print e
#            return HttpResponse(json.dumps({"error" : u"load failed"}))
#        return HttpResponse(json.dumps({"result" : "ok"}))
#    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
def change_reviewer(request):
    if request.method == 'POST':
        review = Review()
        try:
            apply_id = request.POST.get("apply_id")
            reviewer_id = request.POST.get("reviewer")
            staff = Employee.objects.get(id = reviewer_id)
            apply = Apply.objects.get(pk = apply_id)
            TkLog().info(u"%s got collection review: %d)%s" %(staff.username, apply.id, apply.create_by.name))
            record = CollectionRecord(record_type=CollectionRecord.DISPATCH, object_type=CollectionRecord.SELF, create_by = staff,
                                  collection_note=u"%s 将客户分配给 %s" % (get_employee(request).username, staff.username), promised_repay_time=None, apply=apply)
            record.save()
            reviews = Review.objects.filter(order = apply).order_by("-id")
            if len(reviews) > 0:
                review = reviews[0]
                review.reviewer = staff
                review.save()
            else: #没有review 新建
                review.reviewer = staff
                review.create_at = datetime.now()
                review.order = apply
                review.review_res = 'i'
                review.save()
            apply.status = 'i'
            apply.save()
            #reviews = Review.objects.filter(order = apply).order_by("-id")
            #if len(reviews) > 0:
            #    if reviews[0].finish_time: #已经完成 新建review
            #        review.reviewer = staff
            #        review.create_at = datetime.now()
            #        review.order = apply
            #        review.review_res = 'i'
            #        review.save()
            #        apply.status = 'i'
            #        apply.save()
            #    elif reviews[0].reviewer == staff: # 重新打开了自己的review
            #        review = reviews[0]
            #        pass
            #    else:
            #        return HttpResponse(json.dumps({"error" : u"%s审批中" % reviews[0].reviewer.username}))
            #else: #没有review 新建
            #    review.reviewer = staff
            #    review.create_at = datetime.now()
            #    review.order = apply
            #    review.review_res = 'i'
            #    review.save()
            #    apply.status = 'i'
            #    apply.save()
            TkLog().info(u"%s got collection review: %d)%s success" %(staff.username, apply.id, apply.create_by.name))
        except Exception, e:
            print e
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse(json.dumps({"result" : "ok"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
def finish_review(request):
    if request.method == 'POST':
        try:
            apply_id = request.POST.get("apply_id")
            review_id = request.POST.get("review_id")
            print apply_id, review_id
            apply = Apply.objects.get(pk = apply_id)
            review = Review.objects.get(pk = review_id)
            if apply.create_by.is_register == -1:
                TkLog().info("用户已注销")
                apply.status = 'e' # 取消订单
                apply.save()
                return HttpResponse(json.dumps({"result" : u"ok"}))
            status = 'y'
            for area_type in ("id", "family", "chsi", "bank", "action", "pic_front", "o_pic_back", "q_pic_hand", "work"):
                review_record = ReviewRecord(review = review)
                review_record.review_status = request.POST.get(area_type + "_area_radio")
                #print review_record.review_status_t, "--", request.POST.get(area_type + "_area_radio")
                if status == 'y':
                    if review_record.review_status != 'y':
                        status = review_record.review_status
                elif status == 'r':
                    if review_record.review_status == 'n':
                        status = review_record.review_status
                review_record.review_note = request.POST.get(area_type + "_area_notes")[:254] if request.POST.get(area_type + "_area_notes") else ""
                review_record.review_message = request.POST.get(area_type + "_area_msg")[:254] if request.POST.get(area_type + "_area_msg") else ""
                review_record.review_type = area_type[0]
                review_record.save()
                extra_apply = ExtraApply.objects.filter(apply=apply)
                if len(extra_apply) == 0:
                    print 'new extra'
                    extra_apply = ExtraApply()
                    extra_apply.apply = apply
                else:
                    print 'modify extra'
                    extra_apply = extra_apply[0]
                if area_type == "work":
                    extra_apply.message_1 = review_record.review_message
                elif area_type == "id":
                    extra_apply.message_1 = review_record.review_message
                elif area_type == "chsi":
                    extra_apply.message_2 = review_record.review_message
                elif area_type == "family":
                    extra_apply.message_3 = review_record.review_message
                elif area_type == "pic_front":
                    extra_apply.message_4 = review_record.review_message
                elif area_type == "o_pic_back":
                    extra_apply.message_5 = review_record.review_message
                elif area_type == "q_pic_hand":
                    extra_apply.message_6 = review_record.review_message
                extra_apply.save()
                #print review_record.id, area_type
            staff = Employee.objects.get(user = request.user)
            review.reviewer_done = staff
            review.finish_time = datetime.now()
            #print 'status', status
            review.review_res = status
            review.save()
            label_list = request.POST.get("label")
            review.set_label_list(label_list, apply)
            apply.finish_time = datetime.now()
            apply.status = status
            verify_status = review.to_apply_status()
            apply.save()
            if verify_status != -1:
                check_status = CheckStatus.objects.get(owner = apply.create_by)
                check_status.profile_check_status = verify_status
                #如果审批通过 修改额度
                if status == 'y':
                    if apply.create_by.channel == u"线下导入":
                        check_status.credit_limit = 200000
                        check_status.base_credit = 200000
                        check_status.max_credit = 680000
                        check_status.credit_score = 500
                    else:
                        (res, score, value) = rc_client.init_limit(apply.create_by.id, 0) ## base credit
                        #res='0005'
                        #score=1234
                        #value=500
                        print res, score, value
                        if res == "0005": #success
                            #check_status = CheckStatus.objects.get(owner = apply.create_by)
                            check_status.credit_limit = value * 100
                            check_status.base_credit = value * 100
                            check_status.max_credit = check_status.credit_limit + 480000
                            check_status.credit_score = score
                            #if apply.create_by.invitation:
                            #    apply.create_by.market_score += 100
                            #    apply.create_by.save()
                            #    apply.create_by.invitation.market_score += 100
                            #    apply.create_by.invitation.save()
                            TkLog().info(u"get new score: %s" % check_status.credit_limit)
                        else:
                            #check_status = CheckStatus.objects.get(owner = apply.create_by)
                            check_status.credit_limit = random.randint(100000, 150000)
                            check_status.max_credit = check_status.credit_limit + 480000
                            TkLog().info(u"get random new score: %s" % check_status.credit_limit)
                    check_status.set_profile_status("pass")
                    print message_client.send_message(review.order.create_by.phone_no, u"您提交的信息已经审核完毕，请登录您的花啦花啦账户查看审核结果。如有任何疑问，请联系花啦花啦客服400-606-4728".encode("gbk"), 5)
                elif status == 'r':
                    #打回联系人的话需要删除反向索引
                    check_status.set_profile_status("recheck")
                    print message_client.send_message(review.order.create_by.phone_no, u"您提交的信息有部分存在问题，请在两个工作日内登录花啦花啦按提示进行修改。如有疑问，请联系花啦花啦客服400-606-4728 ".encode("gbk"), 5)
                elif status == 'n':
                    check_status.set_profile_status("deny")
                    #check_status.profile_check_status = 0x3aaa
                    print message_client.send_message(review.order.create_by.phone_no, u"因为系统给出的综合信用评分不足，您的申请未通过审核。如有疑问，请联系花啦花啦客服400-606-4728 ".encode("gbk"), 5)
                check_status.save()
            print review.id, verify_status
            TkLog().info(u"%s finish review: %d)%s  %s %s %s" %(staff.username, review.order.id, review.order.create_by.name, verify_status, apply.get_status_display(), review.order.create_by.phone_no))
            return HttpResponse(json.dumps({"result" : u"ok"}))
        except Exception, e:
            print e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))


@csrf_exempt
@page_permission(check_employee)
def send_message(request):
    if request.method == 'POST':
        try:
            phone_no = request.POST.get("phone_no")
            content = request.POST.get("content")
            aid = request.POST.get("apply")
            repay_apply = Apply.objects.get(id=aid)
            res = message_client.send_message(phone_no, content.encode("gbk"), 8)
            #res = message_client.send_message(phone_no, content.encode("gbk"), 5)
            if res:
                record = CollectionRecord(record_type=CollectionRecord.MESSAGE, object_type=phone_no, create_by = get_employee(request),
                                      collection_note=content, promised_repay_time=None, apply=repay_apply)
                record.save()
                TkLog().info("send message to %s success" % phone_no)
                return HttpResponse(json.dumps({"result" : u"ok"}))
            else:
                TkLog().info("send message to %s faied" % phone_no)
                return HttpResponse(json.dumps({"error" : u"短信发送失败"}))
        except Exception, e:
            print e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
@page_permission(check_employee)
def add_record(request):
    if request.method == 'POST':
        try:
            emplyee = get_employee(request)
            collection_to = request.POST.get("object")
            will_repay_time = request.POST.get("time")
            content = request.POST.get("content")
            aid = request.POST.get("apply")
            repay_apply = Apply.objects.get(id=aid)
            print collection_to, content, will_repay_time
            if will_repay_time:
                promised_repay_time = datetime.strptime(will_repay_time, "%y-%m-%d %H:%M:%S")
                repay_apply.last_commit_at = promised_repay_time
                repay_apply.save()
                record = CollectionRecord(record_type=CollectionRecord.COLLECTION, object_type=collection_to, create_by = emplyee,
                                          collection_note="%s(%s)" % (content, will_repay_time), promised_repay_time=promised_repay_time, apply=repay_apply)
                record.save()
            else:
                record = CollectionRecord(record_type=CollectionRecord.COLLECTION, object_type=collection_to, create_by = emplyee,
                                          collection_note=content, promised_repay_time=None, apply=repay_apply)
                record.save()

            #res = message_client.send_message(phone_no, content.encode("gbk"), 5)
            res=True
            if res:
                TkLog().info("add collection record success %s" % emplyee.username)
                return HttpResponse(json.dumps({"result" : u"ok"}))
            else:
                TkLog().info("add collection record failed %s" % emplyee.username)
                return HttpResponse(json.dumps({"error" : u"催记添加失败"}))
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().info("add collection record failed %s %s" % (emplyee.username, str(e)))
            return HttpResponse(json.dumps({"error" : u"催记添加异常"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

def _update_related_repay_apply(apply, status=None):
    repay_applys = Apply.objects.filter(repayment=apply.repayment, money=apply.money, type=Apply.REPAY_LOAN)
    if len(repay_applys) >= 1:
        repay_apply = repay_applys[0]
        if not status:
            repay_apply.status = Apply.REPAY_SUCCESS
        else:
            repay_apply.status = status
        repay_apply.save()

@csrf_exempt
def do_collection_action(request):
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
        collection_check = request.GET.get("collection_check")
        redis_client.hset("collection_check", apply.create_by_id, '%s:%s' % (request.user.id, collection_check))
        repayment = apply.repayment
        installments = InstallmentDetailInfo.objects.filter(repayment=repayment, installment_number=apply.money + 1)
        installment = None
        print "status,", apply.status
        if apply.status == Apply.COLLECTION_SUCCESS or apply.status == Apply.REPAY_SUCCESS:
            print "status,", apply.status
            return HttpResponse(json.dumps({"error" : "ok", "msg": "该扣款已经执行成功，不能重复扣款"}))

        if len(installments) == 1:
            installment = installments[0]
        else:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找对应的借款信息"}))

        bank_card = BankCard.get_repay_card(repayment.user)
        if not bank_card:
            return HttpResponse(json.dumps({"error" : "ok", "msg": "未找到还款银行卡"}))

        #if installment.repay_status == RepaymentInfo.DONE or installment.repay_status == RepaymentInfo.OVERDUE_DONE:
        #    _update_related_repay_apply(apply)
        #    return HttpResponse(json.dumps({"error" : "ok", "msg": "该笔贷款已经还完，不能重复扣款"}))

        #sleep(1)
        if channel == 'realtime_repay':
            TkLog().info("realtime repay_loan %s start %s" % (aid, token))
            #res = bank_client.realtime_pay(repayment.exact_amount, bank_card.get_bank_code(), bank_card.number, repayment.user.name, repayment.user.id, 'mifan')
            #TODO: check repay status & amount

            all_repay_money = rest_repay_money = installment.should_repay_amount  - installment.real_repay_amount + installment.repay_overdue - installment.reduction_amount
            real_repay_money = 0
            repay_money = 0
            res = None
            msg = ""

            if rest_repay_money == 0:
                apply.status = Apply.COLLECTION_SUCCESS
                apply.save()
                return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款已完成"}))
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
                if res.retcode != 0:
                    break
                else:
                    real_repay_money += repay_money

            if res and res.retcode == 0: #扣款成功
                try:
                    if apply.type == Apply.COLLECTION_M0:
                        apply.status = Apply.REPAY_SUCCESS
                    else:
                        apply.status = Apply.COLLECTION_SUCCESS
                    apply.save()

                    repay_applys = Apply.objects.filter(repayment=apply.repayment, type=Apply.REPAY_LOAN, money=installment.installment_number - 1)
                    if len(repay_applys) == 1:
                        repay_apply = repay_applys[0]
                        repay_apply.status = Apply.REPAY_SUCCESS
                        repay_apply.save()
                    else:
                        TkLog().error("update repay_apply failed count:%d, installment:%d" % (len(repay_applys), installment.installment_number))

                    res = risk_client.repay_loan(repayment.order_number, installment.installment_number)
                    #if res != 0:
                    #    return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款已经成功, server更新失败，请联系管理员"}))

                    staff = Employee.objects.get(user = request.user)
                    note = u"扣款成功 卡号:%s 金额:%s" % (bank_card.number, real_repay_money/100.0)
                    record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                          collection_note=note, promised_repay_time=None, apply=apply)
                    record.save()
                except Exception, e:
                    traceback.print_exc()
                    print e
                    return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款已经成功, 系统更新失败，请联系管理员"}))
                return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款成功"}))
            elif real_repay_money > 0: #部分成功
                try:
                    installment.real_repay_amount += real_repay_money
                    installment.save()
                    apply.status = Apply.PARTIAL_SUCCESS
                    apply.save()
                    staff = Employee.objects.get(user = request.user)
                    note = u"扣款部分成功 卡号:%s 扣款金额:%f 成功金额:%f, 最后一笔失败原因%s" % (bank_card.number, all_repay_money/100.0, real_repay_money/100.0, msg.decode("utf-8"))
                    record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                          collection_note=note, promised_repay_time=None, apply=apply)
                    record.save()
                    return HttpResponse(json.dumps({"error" : "ok", "msg": "部分成功"}))
                except Exception, e:
                    traceback.print_exc()
                    TkLog().error("update apply & record part_success %s" % str(e))
                    return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款部分成功, 系统更新失败，请联系管理员"}))
            else:
                try:
                    apply.status = Apply.REPAY_FAILED #失败
                    apply.save()
                    staff = Employee.objects.get(user = request.user)
                    note = u"扣款失败 卡号:%s 扣款金额:%f 失败原因:%s" % (bank_card.number, all_repay_money/100.0, msg.decode("utf-8"))
                    record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                                  collection_note=note, promised_repay_time=None, apply=apply)
                    record.save()
                    return HttpResponse(json.dumps({"error" : "ok", "msg": msg.decode("utf-8")}))
                except Exception, e:
                    traceback.print_exc()
                    TkLog().error("update apply & record failed %s" % str(e))
                    return HttpResponse(json.dumps({"error" : "ok", "msg": "扣款失败, 系统更新失败，请联系管理员"}))
                apply.status = REPAY_FAILED #失败
                apply.save()
                staff = Employee.objects.get(user = request.user)
                note = u"扣款失败 卡号:%s 失败原因:%s" % (bank_card.number, real_repay_money, msg.decode("utf-8"))
                record = CollectionRecord(record_type=CollectionRecord.REPAY, object_type=CollectionRecord.SELF, create_by = staff,
                                      collection_note=note, promised_repay_time=None, apply=apply)
                record.save()
                return HttpResponse(json.dumps({"error" : "ok", "msg": msg.decode("utf-8")}))
        elif channel == "alipay_repay" or channel == "topublic_repay":
            try:
                url = request.GET.get("url")
                notes = request.GET.get("notes")
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
                _update_related_repay_apply(apply, Apply.WAIT_CHECK)

                return HttpResponse(json.dumps({"error" : "ok", "msg": "success"}))
            except Exception, e:
                traceback.print_exc()
                print e
                TkLog().info(u"new audit apply failed %s" % str(e))
                return HttpResponse(json.dumps({"error" : "failed", "msg": str(e)}))
    return HttpResponse(json.dumps({"error" : "get only", "msg":"get only"}))

def _get_apply_list(request):
    try:
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
        apply_list = Apply.objects.filter(query_time & query_type & query_status).order_by("-id")
        return (apply_list, stime, etime)
    except Exception, e:
        print "excp", e
        traceback.print_exc()
        return ([], "", "")

def _print_collection_data(ws, i, name, collection):
    ws.write(i, 0, name)
    ws.write(i, 1, unicode("米饭", "utf-8"))
    ws.write(i, 2, collection["count"] if "count" in collection else 0)
    ws.write(i, 3, collection["finish_count"] if "finish_count" in collection else 0)
    ws.write(i, 4, collection["unfinish_count"] if "unfinish_count" in collection else 0)
    ws.write(i, 5, collection["amount"] if "amount" in collection else 0)
    ws.write(i, 6, collection["finish_amount"] if "finish_amount" in collection else 0)
    ws.write(i, 7, collection["unfinish_amount"] if "unfinish_amount" in collection else 0)
    ws.write(i, 8, collection["unfinish_amount"] / collection["amount"] if "unfinish_amount" in  collection else 0)

def _print_collector_data(ws, i, name, collection):
    ws.write(i, 0, name)
    ws.write(i, 1, collection["count"] if "count" in collection else 0)
    ws.write(i, 2, collection["finish_count"] if "finish_count" in collection else 0)
    ws.write(i, 3, float(collection["finish_count"]) / collection["count"] if "finish_count" in collection else 0)
    ws.write(i, 4, collection["amount"] if "amount" in collection else 0)
    ws.write(i, 5, collection["finish_amount"] if "finish_amount" in  collection else 0)
    ws.write(i, 6, collection["finish_amount"] / collection["amount"] if "finish_amount" in  collection else 0)

def download_collection_table_1(request):
    if request.method == 'GET':
        apply_list, stime, etime = _get_apply_list(request)
        try :
            w = Workbook()
            ws = w.add_sheet(unicode('数据报表', 'utf-8'))
            ws.write(0, 0, unicode("催收类型", 'utf-8'))
            ws.write(0, 1, unicode("用户名", 'utf-8'))
            ws.write(0, 2, unicode("应还日期", 'utf-8'))
            ws.write(0, 3, unicode("催收人", 'utf-8'))
            ws.write(0, 4, unicode("处理状态", 'utf-8'))
            i = 1
            account = {}
            reviewer_dict = {}
            all_dict = {}
            for apply in apply_list:
                installments = InstallmentDetailInfo.objects.filter(repayment=apply.repayment, installment_number=apply.money + 1)
                installment = None
                if len(installments) == 1:
                    installment = installments[0]
                repay_day = installment.should_repay_time if installment else ""
                pay_done = (installment.repay_status == RepaymentInfo.DONE) or (installment.repay_status == RepaymentInfo.OVERDUE_DONE)
                review = CollectionRecord.objects.filter(apply=apply, record_type=CollectionRecord.DISPATCH).order_by("-id")
                reviewer = review[0].create_by.username if len(review) >= 1 else ""

                ws.write(i, 0, apply.get_type_display())
                ws.write(i, 1, apply.create_by.name)
                ws.write(i, 2, repay_day.strftime("%Y-%m-%d"))
                ws.write(i, 3, reviewer)
                ws.write(i, 4, apply.get_status_display())
                i += 1


                total = (installment.should_repay_amount + installment.repay_overdue) / 100.0
                payed_amount = (installment.real_repay_amount) / 100.0
                rest_amount = total - payed_amount
                #print total, payed_amount, rest_amount

                dict_addmap(account, apply.get_type_display())
                dict_addcount(account[apply.get_type_display()], "count")
                dict_addnumber(account[apply.get_type_display()], "amount", total)
                dict_addcount(all_dict, "count")
                dict_addnumber(all_dict, "amount", total)
                if apply.status == Apply.COLLECTION_SUCCESS or apply.status == Apply.REPAY_SUCCESS:
                    dict_addcount(account[apply.get_type_display()], "finish_count")
                    dict_addnumber(account[apply.get_type_display()], "finish_amount", payed_amount)
                    dict_addcount(all_dict, "finish_count")
                    dict_addnumber(all_dict, "finish_amount", payed_amount)
                else:
                    dict_addcount(account[apply.get_type_display()], "unfinish_count")
                    dict_addnumber(account[apply.get_type_display()], "unfinish_amount", rest_amount)
                    dict_addcount(all_dict, "unfinish_count")
                    dict_addnumber(all_dict, "unfinish_amount", rest_amount)

                if reviewer:
                    dict_addmap(reviewer_dict, reviewer)
                    dict_addcount(reviewer_dict[reviewer], "count")
                    dict_addnumber(reviewer_dict[reviewer], "amount", total)
                    if apply.status == Apply.COLLECTION_SUCCESS or apply.status == Apply.REPAY_SUCCESS:
                        dict_addcount(reviewer_dict[reviewer], "finish_count")
                        dict_addnumber(reviewer_dict[reviewer], "finish_amount", payed_amount)
                    else:
                        dict_addcount(reviewer_dict[reviewer], "unfinish_count")
                        dict_addnumber(reviewer_dict[reviewer], "unfinish_amount", rest_amount)

            ws = w.add_sheet(unicode('汇总报表', 'utf-8'))
            ws.write(0, 0, unicode("催收类型", 'utf-8'))
            ws.write(0, 1, unicode("渠道", 'utf-8'))
            ws.write(0, 2, unicode("总客户数", 'utf-8'))
            ws.write(0, 3, unicode("已还客户数", 'utf-8'))
            ws.write(0, 4, unicode("未还客户数", 'utf-8'))
            ws.write(0, 5, unicode("总金额", 'utf-8'))
            ws.write(0, 6, unicode("已还金额", 'utf-8'))
            ws.write(0, 7, unicode("未还金额", 'utf-8'))
            ws.write(0, 8, unicode("未还金额比例", 'utf-8'))
            i = 1
            unfinish_mp = 0  # m1 - 委外 完成客户数
            all_mp = 0  # m1 - 委外 总客户数
            unfinish_mp2 = 0  # m1 - m3 完成客户数
            all_mp2 = 0  # m1 - m3 总客户数
            for (collection_type, collection) in account.items():
                _print_collection_data(ws, i, collection_type, collection)
                if collection_type != "催收m0":
                    unfinish_mp += collection["unfinish_count"] if "unfinish_count" in collection else 0
                    all_mp += collection["count"] if "count" in collection else 0
                    if collection_type != "催收委外":
                        unfinish_mp2 += collection["unfinish_count"] if "unfinish_count" in collection else 0
                        all_mp2 += collection["count"] if "count" in collection else 0
                i += 1
            _print_collection_data(ws, i, unicode("总计", "utf-8"), all_dict)
            i += 2
            ws.write(i, 0, unicode("违约率(m1+m2+m3)", "utf-8"))
            ws.write(i, 1, float(unfinish_mp)/all_mp if all_mp else 0)
            ws.write(i+1, 0, unicode("违约率(m1+m2+m3+委外)", "utf-8"))
            ws.write(i+1, 1, float(unfinish_mp2)/all_mp2 if all_mp2 else 0)

            ws = w.add_sheet(unicode('催收人员绩效', 'utf-8'))
            ws.write(0, 0, unicode("催收人", 'utf-8'))
            ws.write(0, 1, unicode("总分配案件数", 'utf-8'))
            ws.write(0, 2, unicode("催回客户数", 'utf-8'))
            ws.write(0, 3, unicode("催回客户比例", 'utf-8'))
            ws.write(0, 4, unicode("总分案金额", 'utf-8'))
            ws.write(0, 5, unicode("催回金额", 'utf-8'))
            ws.write(0, 6, unicode("催回金额比例", 'utf-8'))
            i = 1
            for (reviewer, collection) in reviewer_dict.items():
                #print reviewer, collection
                _print_collector_data(ws, i, reviewer, collection)
                i += 1
            _print_collector_data(ws, i, unicode("总计", "utf-8"), all_dict)
            w.save('t.xls')
            #print "time", stime.split(" ")[0], etime.split(" ")[0]
            response = StreamingHttpResponse(FileWrapper(open('t.xls'), 8192), content_type='application/vnd.ms-excel')
            response['Content-Length'] = os.path.getsize("t.xls")
            response['Content-Disposition'] = 'attachment; filename=催收业务报表.xls'
            return response
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
    return HttpResponse(json.dumps({"error" : "get only"}))

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        try:
            #print request.FILES.get("check_file")
            #print dir(request.FILES)
            #print dir(request.FILES.get("file_data"))
            file_data = request.FILES.get("file_data")
            name = request.FILES.get("file_data").name
            res = requests.post("%s/upload/file" % settings.IMAGE_SERVER["URL"], files={"file": file_data})
            result = json.loads(res.content)
            #print result
            resp = HttpResponse(json.dumps({"url": result["url"]}))
            TkLog().info("upload_file success %s" % result["url"])
            return resp
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().info("upload_file failed %s" % (str(e)))
            return HttpResponse(json.dumps({"error" : u"图片上传失败"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))
