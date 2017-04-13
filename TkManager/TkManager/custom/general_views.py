# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext,Template
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q,F
from django.db import models
import json,uuid
from django.forms import forms
from TkManager.util.permission_decorator import page_permission
from TkManager.review.employee_models import check_employee,Employee
from TkManager.review.models import Review,ReviewRecord
from TkManager.review.general_views import get_info_by_user
from TkManager.order.apply_models import Apply
from TkManager.order.models import BankCard, ContactInfo, Chsi, CheckStatus, IdCard, Profile, AddressBook, CallRecord, User,UserExtraInfoRecord 
from TkManager.collection.models import RepaymentInfo, InstallmentDetailInfo
from TkManager.custom import data_views
from TkManager.common.tk_log_client import TkLog
from django.contrib import messages
from TkManager.review import bind_client, rc_client, redis_client, message_client
from datetime import datetime, timedelta, date
from TkManager.review.models import CollectionRecord
from TkManager.operation.data_views import get_over_due_days
import re
import traceback
from TkManager.review import message_client, bank_client, risk_client, redis_client

@csrf_exempt
def send_message(request):
    try:
        phone_no = request.POST.get("phone_no")
        content = str(request.POST.get("content")) + '【花啦花啦】'
        res = message_client.send_message(phone_no, content.encode("gbk"), 8)
        #res = message_client.send_message(phone_no, content.encode("gbk"), 5)
        if res:
            TkLog().info("send message to %s success" % phone_no)
            return HttpResponse(json.dumps({"result" : u"ok"}))
        else:
            TkLog().info("send message to %s faied" % phone_no)
            return HttpResponse(json.dumps({"error" : u"短信发送失败"}))
    except Exception, e:
        print e
        traceback.print_exc()
        return HttpResponse(json.dumps({"error" : u"load failed"}))

def addremark(request):
    try:
        print request.GET.get("content")
        print request.GET.get("user_id")
        print request.user
        staff = Employee.objects.get(user = request.user)
        record = UserExtraInfoRecord(create_by = staff,content = request.GET.get("content"),
                          user = User.objects.get(id = request.GET.get("user_id")))
        record.save()
    except Exception, exception:
        output_data = {"result":str(exception)}
        return HttpResponse(json.dumps(output_data))
    output_data = {"result":"成功添加用户备注！"}
    return HttpResponse(json.dumps(output_data))

def test(request):
    return render_to_response('custom/test.html')

def get_user_status(check_status_list,apply_list):
    user_status = u'未提交信息'

    if check_status_list.count() > 0:
        if check_status_list[0].profile_status != 0:
            user_status = u'已填写未提交审核'

    if apply_list.count() > 0:
        user_status = apply_list[0].get_status_display()

    return user_status

@page_permission(check_employee)
def get_user_view(request):
    if request.method == 'GET':
        columns = data_views.get_feedback_columns()
        page= render_to_response('custom/user_view.html', {'columns':columns},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_feedback_view(request):
    if request.method == 'GET':
        columns = data_views.get_feedback_columns()
        page= render_to_response('custom/feedback_view.html', {"columns" : columns, "datatable" : [], "user" : request.user},
                                 context_instance=RequestContext(request))
        return page

def get_record_view(request):
    if request.method == 'GET':
        columns = data_views.get_report_columns()
        return render_to_response('custom/operation_record.html', {"columns" : columns, "datatable" : [], "user" : request.user},
                                  context_instance=RequestContext(request))

def get_user_detail(user_id):
    '''
    显示用户的详细信息
    '''
    user_list = User.objects.filter(id = user_id)
    for user in user_list:
        print 'user:',user.id
    print 'u:',user_id,type(user_id)
    if user_list.count() != 1:
        return render_to_response('custom/no_user_template.html', {'user_count': user_list.count()})

    user = user_list[0]
    user_extra_info = UserExtraInfoRecord.objects.filter(user=user)
    print user_extra_info
    print user_extra_info.query
    check_status_list = CheckStatus.objects.filter(owner_id=user.id)
    apply_list = Apply.objects.filter(create_by_id=user.id,type=0).order_by('-create_at')
    user_status = check_status_list[0].get_apply_status_display()
    apply_status = get_user_status(check_status_list,apply_list)

    repaymentinfo_list = RepaymentInfo.objects.filter(user_id=user.id).order_by('-apply_time')
    credit_limit = check_status_list[0].credit_limit/100 if check_status_list.count() > 0 else 0

    profile_list = Profile.objects.filter(owner_id=user.id)
    profile = profile_list[0] if profile_list.count() > 0 else dict()
    chsis = Chsi.objects.filter(user_id=user.id)
    idcard_list = IdCard.objects.filter(owner_id=user.id)
    idcard = idcard_list[0] if idcard_list.count() > 0 else dict()
    contacts = ContactInfo.objects.filter(owner_id=user.id).order_by('-id')
    if len(contacts) > 3:
        contacts = contacts[0:3]
        contacts.reverse()
    bankcards = BankCard.objects.filter(user_id=user.id)

    show_reviews = review_info = {}
    apply = dict()
    if apply_list.count() > 0:
        apply = apply_list[0]
        reviews = Review.objects.filter(order = apply)
        if len(reviews) == 1:
            review_info = reviews[0]
            show_reviews["id_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='i').order_by("id")
            show_reviews["chsi_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='c').order_by("id")
            show_reviews["family_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='f').order_by("id")
            show_reviews["bank_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='b').order_by("id")
            show_reviews["action_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='a').order_by("id")
            show_reviews["pic_front_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='p').order_by("id")
            show_reviews["pic_back_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='o').order_by("id")
            show_reviews["pic_hand_review"] = ReviewRecord.objects.filter(review = reviews[0], review_type='q').order_by("id")


    page = render_to_response('custom/user_query_template.html',
                                {'user':user,'user_status':user_status,'repaymentinfo_list':repaymentinfo_list, 'oss_url': settings.OSS_URL,
                                    'credit_limit':credit_limit,'profile':profile,'chsis':chsis,"idcard":idcard, "apply_status":apply_status,
                                "contacts": contacts,"bankcards":bankcards,"reviews":show_reviews,'apply':apply,"user_extra_info":user_extra_info,
                                "phone_no":user.phone_no
                                })

    return page

def get_relate_over_due_days(installment):
    applys =  Apply.objects.filter(Q(repayment=installment.repayment) & Q(money = installment.installment_number - 1 ) &  Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
    if len(applys) > 0 :
        return applys[0].get_type_display()
    else: 
        return "空" 
def get_review_staff_name(installment):
    applys =  Apply.objects.filter(Q(repayment=installment.repayment) & Q(money = installment.installment_number - 1 ) &  Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
    if len(applys) > 0 :
        review = CollectionRecord.objects.filter(apply=applys[0], record_type=CollectionRecord.DISPATCH).order_by("-id")
        if len(review) >= 1:
            return review[0].create_by.username
        else:
            return "无催收"
    else: 
        return "无催收" 
    
def get_strategy_type(installment):
    return installment.repayment.get_strategy_id_display()

def get_relate_colleciton_status(installment):
    applys =  Apply.objects.filter(Q(repayment=installment.repayment) & Q(money = installment.installment_number - 1 ) &  Q(type__in=[Apply.COLLECTION_M0, Apply.COLLECTION_M1, Apply.COLLECTION_M2, Apply.COLLECTION_M3, Apply.COLLECTION_M4]))
    if len(applys) > 0 :
        return applys[0].get_type_display()
    else: 
        return "空" 
@page_permission(check_employee)
def get_query_detail_view(request):
    if request.method == 'GET':
        user_id = request.GET.get("uid")
        review_dict = get_info_by_user(request, user_id)
        print review_dict
        page= render_to_response('custom/view_user_query_template.html', review_dict, context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_query_detail(request):
    '''
    点击用户详情查看用户详细信息
    '''
    if request.method == 'GET':
        user_id = request.GET.get("query_user_id")
        print 'request:',request.GET
        print 'user_id:',user_id,type(user_id)
        return get_user_detail(user_id)

@page_permission(check_employee)
def get_info_detail(request):
    errors = ['短信内容不能为空']
    if 'q' in request.GET:
        q = request.GET.get('q')
        print q
        user_info = User.objects.get(id = q)
        print 'num',user_info.phone_no
        if request.method == 'POST':
            message = request.POST['message']
            if message:
                message_client.send_message(user_info.phone_no, message.encode("gbk"), 5)
            else:
                raise forms.ValidationError('123')


#         print 'info',message_client.send_message(user_info.phone_no, u"我很萌".encode("gbk"), 5)
        return render_to_response('custom/send_info.html',{'user_info':user_info},context_instance=RequestContext(request))
#     return HttpResponseRedirect('/order/all')



@page_permission(check_employee)
def get_query_view_result(request):
    '''
    点击查询，显示结果
    '''
    if request.method == 'GET':
        query_str = request.GET.get("query_str")
        m = re.match(r'\d{18,19}',query_str)
        if m != None and  RepaymentInfo.objects.filter(order_number=query_str).count() == 1:
            user = RepaymentInfo.objects.filter(order_number=query_str)[0].user
            return get_user_detail(user.id)
        user_list = User.objects.filter(Q(name__icontains=query_str) | Q(phone_no=query_str) | Q(id_no=query_str))
        print 'user_list:',type(user_list)
        if user_list.count() == 0:
            return render_to_response('custom/no_user_template.html', {'user_count': user_list.count()},
                                 context_instance=RequestContext(request))
        elif user_list.count() == 1:
            user = user_list[0]
            return get_user_detail(user.id)
        else:
            return render_to_response('custom/user_list_template.html', {'user_list':user_list}, context_instance=RequestContext(request))

def _get_loan_data(request):
    today = datetime.combine(date.today(), datetime.max.time())
    user_id = request.GET.get("user_id")
    repaymentinfo_list = RepaymentInfo.objects.filter(user_id=user_id).order_by('-apply_time')

    data_list = list()
    for repaymentinfo in repaymentinfo_list:
        repay_temp_dict = dict()
        repay_temp_dict['order_number'] = repaymentinfo.order_number
        repay_temp_dict['apply_amount'] = round(float(repaymentinfo.apply_amount)/100,2)
        repay_temp_dict['exact_amount'] = round(float(repaymentinfo.exact_amount)/100,2)
        repay_temp_dict['repay_status'] = repaymentinfo.get_repay_status_display()
        repay_temp_dict['apply_time'] = repaymentinfo.apply_time.strftime("%Y-%m-%d %H:%M:%S") if repaymentinfo.apply_time is not None else ""
        installment_list = InstallmentDetailInfo.objects.filter(repayment_id=repaymentinfo.id).order_by('installment_number')
        repay_temp_dict['install_list'] = list()
        i = 0
        for installment in installment_list:
            repay_day = installment.should_repay_time if installment else ""
            install_temp_dict = dict()
            install_temp_dict['installment_number'] = installment.installment_number
            install_temp_dict['should_repay_time'] = installment.should_repay_time.strftime("%Y-%m-%d %H:%M:%S") if installment.should_repay_time is not None else ""
            install_temp_dict['real_repay_time'] = installment.real_repay_time.strftime("%Y-%m-%d %H:%M:%S") if installment.real_repay_time is not None else ""
            install_temp_dict['should_repay_amount'] = round(float(installment.should_repay_amount)/100,2)
            install_temp_dict['real_repay_amount'] =  round(float(installment.real_repay_amount)/100,2) if installment.real_repay_amount != -1 else 0
            install_temp_dict['repay_status'] = installment.get_repay_status_display()
            repay_day = installment.should_repay_time if installment else ""
            pay_done = (installment.repay_status == RepaymentInfo.DONE) or (installment.repay_status == RepaymentInfo.OVERDUE_DONE)  or (installment.repay_status == RepaymentInfo.PRE_DONE)
	    install_temp_dict['over_due_days'] = get_over_due_days(installment)
	    #install_temp_dict['over_due_days'] = (today - repay_day).days if repay_day and not pay_done else 0
	    install_temp_dict['over_due_status'] = get_relate_colleciton_status(installment)
	    install_temp_dict['stratety_type'] = get_strategy_type(installment)
	    install_temp_dict['over_due_repay'] = installment.repay_overdue/100.0
#	    install_temp_dict['should_repay'] = installment.repay_overdue/100.0 + round(float(installment.should_repay_amount)/100,2) - installment.real_repay_amount/100.0
	    install_temp_dict['should_repay'] = round(float(installment.repay_overdue + installment.should_repay_amount - installment.real_repay_amount)/100.0,2)
	    install_temp_dict['review_staff_name'] = get_review_staff_name(installment)
            if is_repay_apply_exsit(i,repaymentinfo.id):
                install_temp_dict['repay_apply'] = ''
            else:
                token = uuid.uuid1()
                install_temp_dict['repay_apply'] = '<a href="#"  class="btn btn-default" token="' + str(token) +'" id = "test" role="button">生成本期代扣订单</a>'
            repay_temp_dict['install_list'].append(install_temp_dict)
            i = i+1

        data_list.append(repay_temp_dict)

    output_data = {'data': data_list}
    return output_data

def gen_apply_repay_type(request):
    try:
        user = request.user
        staff = Employee.objects.get(user = user)
        print type(staff)
    except Exception, e:
        print e
        TkLog().info(u"获取staff失败%s" % str(e))
    TkLog().info(u"%s 提前生成代扣订单" % staff.username)
    token = request.GET.get("token")
    print "token",token
    try:
        exist_token = redis_client.hget("pay_token",  token)
    except Exception, e:
        TkLog().error(u"call redis error")
    if not exist_token:
        try:
            ret = redis_client.hsetnx("pay_token", token, 1)
        except Exception, e:
            TkLog().error(u"call redis error")
        if ret == 0: #token已经存在
            return HttpResponse(json.dumps({"error" :  "不能重复提交"}))
    else:
        return HttpResponse(json.dumps({"error" : "不能重复提交"}))
    order_number = request.GET.get("order_no")
    money_field = request.GET.get("money_field")
    money_field = int(money_field) - 1
    r = get_repaymentinfo_from_repaymentinfo_order_number(order_number)
    if r ==  None:
        msg = "已经有对应的repay类型的代扣订单存在"
    else:
        new_apply = Apply(create_by = r.user,repayment = r, create_at=datetime.now(), status='0',
                                    type='p', money=money_field, pic="")
        new_apply.save()
        TkLog().info(u"%s 提前生成代扣订单id: %d 完成" % (staff.username, new_apply.id))
        msg = "生成对应的repay类型的代扣订单成功"
    return HttpResponse(json.dumps({'msg': msg}))

def get_repaymentinfo_from_repaymentinfo_order_number(order_number):
    try:
        r = RepaymentInfo.objects.get(Q(order_number = order_number))
        return r
    except RepaymentInfo.DoesNotExist:
        return None

def is_repay_apply_exsit(i,repayment_id): #i是第几期def is_repay_apply_exsit(i):
    return    Apply.objects.filter(Q(repayment=repayment_id) & Q(money = i) & Q(type='p'))
    #try:
    #    if len(Apply.objects.filter(Q(repayment=repayment_id) & Q(money = i) & Q(type='p')) > 0):
    #        return True
    #    else:
    #        return False
    #except Apply.DoesNotExist:
    #    return False


@page_permission(check_employee)
def get_loan_data(request):
    if request.method == 'GET':
        output_data = _get_loan_data(request)
        return HttpResponse(json.dumps(output_data))
