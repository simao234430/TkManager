# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext,Template
from django.http import HttpResponse, StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command

import os
import json
import random
import base64
import traceback
import time
from pyExcelerator import *
from datetime import datetime
from TkManager.util.permission_decorator import page_permission
from TkManager.util.constant import *
from TkManager.review.employee_models import check_employee, is_review_manager
from TkManager.review import data_views
from TkManager.review import data_query
from TkManager.review.models import Review, Employee, ReviewRecord, Label
from TkManager.juxinli.models import *
from TkManager.order.apply_models import Apply, ExtraApply
from TkManager.order.models import BankCard, ContactInfo, Chsi, CheckStatus, IdCard, Profile, AddressBook, CallRecord, User, Chsiauthinfo, SubChannel
from TkManager.collection.models import RepaymentInfo, InstallmentDetailInfo
from TkManager.common.tk_log_client import TkLog
from TkManager.common.dict import dict_addcount, dict_addmap
from TkManager.util.tkdate import *
from TkManager.review import bind_client, rc_client, redis_client, message_client#, gearman_client#, ip_client
from Crypto.Cipher import AES
from TkManager.review import mongo_client
from django.core import serializers
from threading import Timer
from TkManager.review import push_client_object
from TkManager.risk_server.utils import send_message_weixin


@page_permission(check_employee)
def get_all_review_view(request):
    if request.method == 'GET':
        columns = data_views.get_all_review_columns()
        page= render_to_response('review/review_all.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_mine_review_view(request):
    if request.method == 'GET':
        columns = data_views.get_my_review_columns()
        #columns = data_views.get_rt_order_columns()
        page= render_to_response('review/review_mine.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

@page_permission(check_employee)
def get_review_id_view(request):
    if request.method == 'GET':
        columns = data_views.get_order_columns()
        #columns = review_views.get_review_columns()
        page= render_to_response('review/order_review.html', {"columns" : columns, "datatable" : []},
                                 context_instance=RequestContext(request))
        return page

def _get_user_info(request, user):
    '''
        获取用户的相关信息
    '''
    start = time.time()
    TkLog().debug("start get user data: %f" % start)
    applyer = user
    profiles = Profile.objects.filter(owner = applyer)
    profile = profiles[0] if len(profiles) == 1 else None
    chsis = Chsi.objects.filter(user=applyer).order_by('-id')[:1]
    for chsi in chsis:
        if chsi.chsi_name.startswith("file"):
            chsi.chsi_name_img = chsi.chsi_name
            chsi.chsi_name = ""
    TkLog().debug("chsi %f" % (time.time() - start))
    idcards = IdCard.objects.filter(owner = applyer)
    idcard = idcards[0] if len(idcards) == 1 else None
    contacts = ContactInfo.objects.filter(owner = applyer).order_by('-id')
    if len(contacts) > 3:
        contacts = contacts[0:3]
        contacts.reverse()
    contacts_data = []
    for contact in contacts:
        same_ids = ContactInfo.objects.filter(Q(phone_no = contact.phone_no) & ~Q(owner = contact.owner))
        contact.contact_repeat = len(same_ids)
        contact.contacts = same_ids[:10]
        name_inaddressbook = AddressBook.objects.filter(owner=applyer, phone_number=contact.phone_no)
        addressbook_name = name_inaddressbook[0].name if name_inaddressbook else ''
        contact_data = (contact, addressbook_name,)
        contacts_data.append(contact_data)
    TkLog().debug("3 contract %f" % (time.time() - start))
    bankcards = BankCard.objects.filter(Q(user=applyer) & ~Q(card_type=4))
    for bankcard in bankcards:
        same_ids = BankCard.objects.filter(Q(number = bankcard.number) & ~Q(user = bankcard.user))
        bankcard.card_repeat = len(same_ids)
        bankcard.cards = same_ids[:10]
    TkLog().debug("bankcard %f" % (time.time() - start))
    check_status = CheckStatus.objects.get(owner = applyer)
    #if check_status.auto_check_status == 0:
    #    check_status = None
    same_ids = User.objects.filter(device_id = applyer.device_id)
    device_id_repeat = len(same_ids)
    ids = same_ids[:10]
    TkLog().debug("same id %f" % (time.time() - start))
    register_ip = redis_client.hget("USER_INFO:%d" % applyer.id, "ip")
    try:
        register_ip = redis_client.hget("USER_INFO:%d" % applyer.id, "ip")
    except Exception, e:
        TkLog().error(u"call redis error")
    TkLog().debug("register ip %f" % (time.time() - start))
    ip_address = ""
    chsi_auths = Chsiauthinfo.objects.filter(user_id=applyer.id).order_by("-id")
    chsi_auth = chsi_auths[0] if len(chsi_auths) == 1 else None
    if chsi_auth and chsi_auth.username:
        try:
            cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_KEY)
            chsi_auth.username = cipher.decrypt(base64.b64decode(chsi_auth.username.strip('\0')))
        except:
            chsi_auth.username = ''
    #if register_ip:
    #    ip_address = ip_client.ip2address(register_ip)
    #call_records = PhoneCall.objects.filter(owner = applyer)
    #call_records_count = len(call_records)
    review_dict = {"user":applyer, "contacts": contacts_data, "bankcards":bankcards, 'oss_url': settings.OSS_URL, "check_status" : check_status,
            "chsis":chsis, 'profile':profile, "idcard":idcard, 'chsi_auth': chsi_auth, "device_id_repeat": device_id_repeat, "ids" : ids,
             "register_ip": register_ip, "ip_address": ip_address}

    # get data from data_server
    if profile.job == 2:
        review_dict["has_ebusiness"] = True
    else:
        review_dict["has_ebusiness"] = False
    try:
        has_new_data = redis_client.hget("USER_INFO:%d" % applyer.id, "mobile_record")
    except Exception, e:
        TkLog().error(u"call redis error")
    #start = time.time()
    #TkLog().debug("get data from dataserver: %f" % start)
    TkLog().debug("get basic data done, next from dataserver: %f" % (time.time() - start))
    if has_new_data and settings.USE_DATA_SERVER:
        review_dict["new_data"] = True

        basic_data = data_query.basic_data.copy()
        basic_data["user_id"] = applyer.id
        phone_basics = data_query.get_phonebasic_data(basic_data)
        review_dict["phone_basics"] = phone_basics
        TkLog().debug("phone basic %f" % (time.time() - start))

        phone_data = data_query.phone_data.copy()
        phone_data["user_id"] = applyer.id
        phone_data["contact"] = []
        for contact in contacts:
            phone_data["contact"].append({"contact_name" : contact.name, "contact_type" : contact.relationship, "contact_tel" : contact.phone_no})
        contact_phone_calls, contact_phone_call_columns = data_query.get_phonecall_data(phone_data)
        contact_phone_data = None
        if contact_phone_calls:
            contact_phone_data = []
            for phone_call, featrue in contact_phone_calls:
                name_inaddressbook = AddressBook.objects.filter(owner=applyer, phone_number=phone_call)
                contact_name = name_inaddressbook[0].name if name_inaddressbook else ''
                contact_phone_data.append((phone_call, featrue, contact_name,))
        review_dict["contact_phone_call_columns"] = contact_phone_call_columns
        review_dict["contact_phone_calls"] = contact_phone_data

        corp_data = data_query.corp_data.copy()
        corp_data["user_id"] = applyer.id
        (corp_contact_phone_calls, corp_contact_phone_call_columns) = data_query.get_corp_phonecall_data(corp_data)
        review_dict["corp_contact_phone_call_columns"] = corp_contact_phone_call_columns
        review_dict["corp_contact_phone_calls"] = corp_contact_phone_calls
        TkLog().debug("corp contact %f" % (time.time() - start))

        ebusiness_data = data_query.ebusiness_data.copy()
        ebusiness_data["user_id"] = applyer.id
        e_business = data_query.get_ebusiness_data(ebusiness_data)
        review_dict["e_business"] = e_business
        TkLog().debug("ebusiness %f" % (time.time() - start))

        deliver_data = data_query.deliver_data.copy()
        deliver_data["user_id"] = applyer.id
        e_deliver = data_query.get_deliver_data(deliver_data)
        review_dict["e_deliver"] = e_deliver
        TkLog().debug("edeliver %f" % (time.time() - start))

        phone_location_data = data_query.phone_location_data.copy()
        phone_location_data["user_id"] = applyer.id
        phone_location = data_query.get_phone_location_data(phone_location_data)
        review_dict["phone_location"] = phone_location
        TkLog().debug("phone location %f" % (time.time() - start))
        addresses = AddressBook.objects.filter(owner=applyer).order_by('id')
        address = addresses[:10]
        review_dict["addressbook"] = address
        review_dict["addressbooks"] = addresses
    else:
        #TODO: 延迟加载address和callrecord
        addresses = AddressBook.objects.filter(owner=applyer).order_by('id')
        address = addresses[:10]
        TkLog().debug("addressbook %f" % (time.time() - start))
        call = CallRecord.objects.filter(owner = applyer).order_by('-duration')[:10]
        TkLog().debug("callrecord %f" % (time.time() - start))
        review_dict["callrecord"] = call
        review_dict["addressbook"] = address
        review_dict['addressbooks'] = addresses
        #print "位置", phone_location
        #print "电话", phone_basics
        #print "联系人", contact_phone_calls
        #print "公司", corp_contact_phone_calls
        #print "电商", e_business
        #print "快递", e_deliver
    TkLog().debug("end %f" % (time.time() - start))
    return review_dict

def _get_review_label():
    labels = Label.get_all_label()
    return {"labels" : labels}

def _get_review_info(request, apply):
    reviews = Review.objects.filter(order = apply)
    #TODO: 延迟加载review
    show_reviews = {}
    labels = []
    if len(reviews) >= 1:
        show_reviews["id_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='i').order_by("id")
        show_reviews["work_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='w').order_by("id")
        show_reviews["chsi_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='c').order_by("id")
        show_reviews["family_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='f').order_by("id")
        show_reviews["bank_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='b').order_by("id")
        show_reviews["action_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='a').order_by("id")
        show_reviews["pic_front_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='p').order_by("id")
        show_reviews["pic_back_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='o').order_by("id")
        show_reviews["pic_hand_review"] = ReviewRecord.objects.filter(review__in = reviews, review_type='q').order_by("id")
        labels = reviews[len(reviews) - 1].get_label_list()
    return {"apply" : apply, "reviews":show_reviews, "labels":labels}


def _get_info_by_apply(request, apply_id):
    apply_info = Apply.objects.get(pk=apply_id)
    apply_dict = _get_review_info(request, apply_info)
    user_dict = _get_user_info(request, apply_info.create_by)
    all_dict = user_dict.copy()
    all_dict.update(apply_dict)
    return all_dict


def _get_last_basic_apply(user):
    try:
        applys = Apply.objects.filter(create_by=user, type='0').order_by("-id")
        last_apply = applys[0] if len(applys) > 0 else None
        return last_apply
    except Exception, e:
        print e
        traceback.print_exc()
        return None

def _get_last_review(apply_order):
    try:
        reviews = Review.objects.filter(order=apply_order).order_by("-id")
        last_review = reviews[0] if len(reviews) > 0 else None
        return last_review
    except Exception, e:
        print e
        traceback.print_exc()
        return None

def get_info_by_user(request, user_id):
    '''
        返回用户和他最近一次基础信息的审批数据
    '''
    try:
        user = User.objects.get(pk=user_id)
        user_dict = _get_user_info(request, user)
        all_dict = user_dict.copy()
        last_apply = _get_last_basic_apply(user)
        if last_apply:
            apply_dict = _get_review_info(request, last_apply)
            all_dict.update(apply_dict)
        return all_dict
    except Exception, e:
        print e
        return {}

def _get_loan_info(request, apply_id):
    apply = Apply.objects.get(pk = apply_id)
    repaymentinfo_list = RepaymentInfo.objects.filter(user=apply.create_by).order_by('-apply_time')

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
        for installment in installment_list:
            install_temp_dict = dict()
            install_temp_dict['installment_number'] = installment.installment_number
            install_temp_dict['should_repay_time'] = installment.should_repay_time.strftime("%Y-%m-%d %H:%M:%S") if installment.should_repay_time is not None else ""
            install_temp_dict['real_repay_time'] = installment.real_repay_time.strftime("%Y-%m-%d %H:%M:%S") if installment.real_repay_time is not None else ""
            install_temp_dict['should_repay_amount'] = round(float(installment.should_repay_amount)/100,2)
            install_temp_dict['real_repay_amount'] =  round(float(installment.real_repay_amount)/100,2) if installment.real_repay_amount != -1 else 0
            install_temp_dict['repay_status'] = installment.get_repay_status_display()
            repay_temp_dict['install_list'].append(install_temp_dict)

        data_list.append(repay_temp_dict)

    output_data = {'data': data_list}
    return output_data

# 审批modal页面
@page_permission(check_employee)
def get_review_info_view(request, apply_id):
    if request.method == 'GET':
        apply_info = Apply.objects.get(pk=apply_id)
        if apply_info.status == 'b':
            review_dict = _read_snapshot_apply(request, apply_id)
        else:
            review_dict = _get_info_by_apply(request, apply_id)
        labels = _get_review_label()
        review_dict.update(labels)
        if review_dict['check_status'].auto_check_status in (2, 3, 4, -11,):
            review_dict['check_status'].auto_check_status = 0
        page = render_to_response('review/modal.html', review_dict, context_instance=RequestContext(request))
        return page

# 查看审批结果modal
@page_permission(check_employee)
def get_review_view(request, apply_id):
    if request.method == 'GET':
        apply_info = Apply.objects.get(pk=apply_id)
        review_dict = _read_snapshot_apply(request, apply_id)
        if apply_info.status == '0' and review_dict['apply'].status == 'r':
            review_dict = _get_info_by_apply(request, apply_id)
        else:
            review_dict = _read_snapshot_apply(request, apply_id)
        # print 'review_dict:', review_dict
        # review_dict = _get_info_by_apply(request, apply_id)
        if is_review_manager(request):
            if review_dict['apply'].status in ['e', 'w']:
                review_dict["manager"] = False
            else:
                review_dict["manager"] = True
        page = render_to_response('review/view_modal.html', review_dict, context_instance=RequestContext(request))
        return page

# 审批提现信息 modal
@page_permission(check_employee)
def get_review_loan_info_view(request, apply_id):
    if request.method == 'GET':
        all_dict = {}
        try:
            loan_apply = Apply.objects.get(pk = apply_id)
            all_dict = get_info_by_user(request, loan_apply.create_by.id)
            loan_dict = _get_loan_info(request, apply_id)
            all_dict.update(loan_dict)
            all_dict["apply"] = loan_apply
        except Exception, e:
            traceback.print_exc()
            TkLog().error('get_review_loan_info_view failed: %s' % str(e))
        collection_check = redis_client.hget("collection_check", loan_apply.create_by_id)
        if collection_check:
            check_staff = collection_check.split(":")[0]
            if check_staff:
                staff = Employee.objects.get(user__id=check_staff)
            else:
                staff = ''
            check_result = collection_check.split(":")[1]
            if check_result == '0':
                all_dict.update({"collection_check": '<span class="label label-danger">%s的二次提现催收意见为:不允许通过</span>' % staff.username})
            elif check_result == '1':
                all_dict.update({"collection_check": '<span class="label  label-success">%s的二次提现催收意见为:允许通过</span>' % staff.username})
        else:
            all_dict.update({"collection_check": '<span class="label  label-success">默认二次提现催收意见为:允许通过</span>'})
        page = render_to_response('review/modal_loan.html', all_dict, context_instance=RequestContext(request))
        return page

# 查看审批提现信息 modal
@page_permission(check_employee)
def view_loan_info_view(request, apply_id):
    if request.method == 'GET':
        all_dict = {}
        try:
            loan_apply = Apply.objects.get(pk = apply_id)
            all_dict = get_info_by_user(request, loan_apply.create_by.id)
            loan_dict = _get_loan_info(request, apply_id)
            all_dict.update(loan_dict)
            all_dict["apply"] = loan_apply
        except Exception, e:
            traceback.print_exc()
        page= render_to_response('review/view_modal_loan.html', all_dict, context_instance=RequestContext(request))
        return page

# 审批额度提升 modal
@page_permission(check_employee)
def get_review_promote_info_view(request, apply_id):
    if request.method == 'GET':
        apply = Apply.objects.get(pk = apply_id)
        applyer = apply.create_by
        profile = Profile.objects.get(owner = applyer)
        extra_apply = ExtraApply.objects.filter(apply=apply)
        pics = extra_apply[0].extra_pic.split(",") if len(extra_apply) == 1 else []
        page= render_to_response('review/modal_promotion.html', {"apply" : apply, "user":applyer, "profile":profile, 'oss_url': settings.OSS_URL,
                                                                 "pics": pics},
                                 context_instance=RequestContext(request))
        return page

# 查看额度提升 modal
@page_permission(check_employee)
def view_promote_info_view(request, apply_id):
    if request.method == 'GET':
        apply = Apply.objects.get(pk = apply_id)
        applyer = apply.create_by
        profile = Profile.objects.get(owner = applyer)
        reviews = Review.objects.filter(order = apply).order_by("-id")
        review = reviews[0] if len(reviews) > 0 else None
        extra_apply = ExtraApply.objects.filter(apply=apply)
        pics = extra_apply[0].extra_pic.split(",") if len(extra_apply) == 1 else []
        page= render_to_response('review/view_modal_promotion.html', {"apply" : apply, "user":applyer, "profile":profile, 'oss_url': settings.OSS_URL, 'review':review,
                                                                      "pics" : pics},
                                 context_instance=RequestContext(request))
        return page

#@page_permission(check_employee)
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
                    if apply.status in ('r', 'w'):
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
                if apply.status in ('w', 'r',):
                    apply.status = 'i'
                    apply.save()
        except Exception, e:
            print e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse(json.dumps({"result" : "ok", 'review_id' : review.id}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

def _make_snapshot_apply(request, apply_object):
    try:
        table = mongo_client['snapshot']['basic_apply']
        snapshot_data = table.find_one({"apply_info.id": apply_object.id})
        profiles = Profile.objects.filter(owner=apply_object.create_by)
        user_dict = _get_user_info(request, apply_object.create_by)
        if 'callrecord' in user_dict:
            snapshot_callrecord = json.loads(serializers.serialize('json', user_dict['callrecord']))
        else:
            snapshot_callrecord = []
        callrecord_doc = [i['fields'] for i in snapshot_callrecord]
        if 'addressbooks' in user_dict:
            snap_addressbook = json.loads(serializers.serialize('json', user_dict['addressbooks']))
        else:
            snap_addressbook = []
        addressbook_doc = [i['fields'] for i in snap_addressbook]
        apply_data = json.loads(serializers.serialize('json', [apply_object, ]))[0]
        snap_bankcards = json.loads(serializers.serialize('json', user_dict['bankcards']))
        bankcards_doc = [i['fields'] for i in snap_bankcards]
        snap_chsis = json.loads(serializers.serialize('json', user_dict['chsis']))
        chsis_doc = [i['fields'] for i in snap_chsis]
        contacts_objects = []
        for contact in user_dict['contacts']:
            snap_contact = json.loads(serializers.serialize('json', [contact[0], ]))[0]
            contact_doc = snap_contact['fields']
            contacts_objects.append((contact_doc, contact[1]))
        idcards = IdCard.objects.filter(owner=apply_object.create_by)
        idcard_doc = json.loads(serializers.serialize('json', idcards))[0]['fields']
        check_status = user_dict['check_status']
        check_status_doc = json.loads(serializers.serialize('json', [check_status, ]))[0]['fields']
        profiles_doc = {}
        if profiles:
            profiles_data = json.loads(serializers.serialize('json', profiles))[0]
            profiles_doc = profiles_data['fields']
            profiles_doc['id'] = profiles_data['pk']
        user_data = json.loads(serializers.serialize('json', [apply_object.create_by, ]))[0]
        user_doc = user_data['fields']
        user_doc['id'] = user_data['pk']
        chsi_auths = Chsiauthinfo.objects.filter(user_id=apply_object.create_by.id)
        chsi_auth = chsi_auths[0] if len(chsi_auths) == 1 else None
        chsi_data = {}
        if chsi_auth:
            if chsi_auth.username:
                try:
                    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_KEY)
                    chsi_auth.username = cipher.decrypt(base64.b64decode(chsi_auth.username.strip('\0')))
                except:
                    chsi_auth.username = ''
            chsi_data = json.loads(serializers.serialize('json', [chsi_auth, ]))[0]['fields']
        data = {'apply_info': apply_data['fields'], "user_info": user_doc,
                'chsi_auth': chsi_data, 'addressbook': addressbook_doc, "bankcards": bankcards_doc,
                'chsis': chsis_doc, 'contacts': contacts_objects, 'callrecord': callrecord_doc}
        data['user_info'].update({'profile': profiles_doc,"id_card_info": idcard_doc,
                                  "check_status": check_status_doc})
        data["apply_info"].update({"id": apply_data['pk']})
        try:
            has_new_data = redis_client.hget("USER_INFO:%d" % apply_object.id, "mobile_record")
        except Exception, e:
            print 'make snapshot error:', e
            TkLog().error(u"call redis error")
        profile = profiles[0] if len(profiles) == 1 else None
        if profile.job == 2:
            data['has_ebusiness'] = True
        else:
            data['has_ebusiness'] = False
        if not snapshot_data or has_new_data or 'has_ebusiness' not in snapshot_data:
            print 'new phone_basics'
            data["new_data"] = True
            basic_data = data_query.basic_data.copy()
            basic_data["user_id"] = apply_object.create_by.id
            phone_basics = data_query.get_phonebasic_data(basic_data)
            data["phone_basics"] = phone_basics
            phone_data = data_query.phone_data.copy()
            phone_data["user_id"] = apply_object.create_by.id
            phone_data["contact"] = []
            for contact, names in user_dict['contacts']:
                phone_data["contact"].append({"contact_name": contact.name, "contact_type": contact.relationship, "contact_tel": contact.phone_no})
            contact_phone_calls, contact_phone_call_columns = data_query.get_phonecall_data(phone_data)
            contact_phone_data = None
            if contact_phone_calls:
                contact_phone_data = []
                for phone_call, featrue in contact_phone_calls:
                    name_inaddressbook = AddressBook.objects.filter(owner=apply_object.create_by, phone_number=phone_call)
                    contact_name = name_inaddressbook[0].name if name_inaddressbook else ''
                    contact_phone_data.append((phone_call, featrue, contact_name,))
            data["contact_phone_call_columns"] = contact_phone_call_columns
            data["contact_phone_calls"] = contact_phone_data
            corp_data = data_query.corp_data.copy()
            corp_data["user_id"] = apply_object.create_by.id
            (corp_contact_phone_calls, corp_contact_phone_call_columns) = data_query.get_corp_phonecall_data(corp_data)
            data["corp_contact_phone_call_columns"] = corp_contact_phone_call_columns
            data["corp_contact_phone_calls"] = corp_contact_phone_calls
            ebusiness_data = data_query.ebusiness_data.copy()
            ebusiness_data["user_id"] = apply_object.create_by.id
            e_business = data_query.get_ebusiness_data(ebusiness_data)
            data["e_business"] = e_business
            deliver_data = data_query.deliver_data.copy()
            deliver_data["user_id"] = apply_object.create_by.id
            e_deliver = data_query.get_deliver_data(deliver_data)
            data["e_deliver"] = e_deliver
            phone_location_data = data_query.phone_location_data.copy()
            phone_location_data["user_id"] = apply_object.create_by.id
            phone_location = data_query.get_phone_location_data(phone_location_data)
            data["phone_location"] = phone_location
        if snapshot_data:
            object_id = table.find_one_and_update({"apply_info.id": apply_object.id}, {"$set": data})
            print 'mongo update data:', object_id
            TkLog().debug("TkManager snapshot update apply data: \n%s" % object_id)
        else:
            object_id = table.insert(data)
            print 'mongo insert ObjectId(%s)' % object_id
    except:
        traceback.print_exc()
        TkLog().error("mongo error:%s" % traceback.format_exc())

def _read_snapshot_apply(request, apply_id):
    apply_info = Apply.objects.get(pk=apply_id)
    apply_dict = _get_review_info(request, apply_info)
    try:
        table = mongo_client['snapshot']['basic_apply']
        snapshot_data = table.find_one({"apply_info.id": apply_info.id})
        print 'mongo data:', snapshot_data
        profiles = Profile.objects.filter(owner=apply_info.create_by)
        profiles_keys = Profile._meta.get_all_field_names()
        profiles_keys.pop(profiles_keys.index('owner_id'))
        chsi_auths = Chsiauthinfo.objects.filter(user_id=apply_info.create_by.id)
        chsi_auth = chsi_auths[0] if len(chsi_auths) == 1 else None
        chsi_data = {}
        if chsi_auth:
            if chsi_auth.username:
                try:
                    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_KEY)
                    chsi_auth.username = cipher.decrypt(base64.b64decode(chsi_auth.username.strip('\0')))
                except:
                    chsi_auth.username = ''
            chsi_data = json.loads(serializers.serialize('json', [chsi_auth, ]))[0]['fields']
        snapshot_profile_keys = []
        if not snapshot_data:
            user_dict = _get_user_info(request, apply_info.create_by)
            all_dict = user_dict.copy()
            all_dict.update(apply_dict)
            _make_snapshot_apply(request, apply_info)
            return all_dict
        else:
            if 'user_info' in snapshot_data:
                user_snap = snapshot_data['user_info'].copy()
                print 'snap_user_info:', user_snap
                if 'check_status' in user_snap:
                    user_snap.pop('check_status')
                if 'profile' in user_snap:
                    user_snap.pop('profile')
                if 'id_card_info' in user_snap:
                    user_snap.pop('id_card_info')
                user_object = User(**user_snap)
                if 'profile' in snapshot_data['user_info']:
                    snapshot_profile_keys = snapshot_data['user_info']['profile'].keys()
            else:
                user_object = apply_info.create_by
                user_data = json.loads(serializers.serialize('json', [apply_info.create_by, ]))[0]
                user_doc = user_data['fields']
                user_doc['id'] = user_data['pk']
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {'user_info': user_doc}})
            diff_keys = set(snapshot_profile_keys) ^ set(profiles_keys) if profiles_keys else set(snapshot_profile_keys)
            print diff_keys

            if "owner" in diff_keys:
                diff_keys.remove("owner")
            if diff_keys:
                print 'diff_keys:',diff_keys
                for key in diff_keys:
                    data_key = 'user_info.profile.%s' % key
                    print profiles
                    update_key = "profiles[0].%s" % key
                    if key == 'owner':
                        update_key = apply_info.create_by_id
                        table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {data_key: update_key}})
                    else:
                        table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {data_key: eval(update_key)}})
            if 'chsi_auth' in snapshot_data:
                chsi_auth = Chsiauthinfo(**snapshot_data['chsi_auth'])
            else:
                data_key = 'chsi_auth'
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {data_key: chsi_data}})
            addressbook_objects = []
            if 'addressbook' in snapshot_data:
                if len(snapshot_data['addressbook']) <= 10:
                    user_info = _get_user_info(request, apply_info.create_by)
                    snap_addressbook = json.loads(serializers.serialize('json', user_info['addressbooks']))
                    snap_data = [i['fields'] for i in snap_addressbook]
                    table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {'addressbook': snap_data}})
                print 'snap_addressbook:', snapshot_data['addressbook']
                snapshot_data = table.find_one({"apply_info.id": apply_info.id})
                for data in snapshot_data['addressbook']:
                    data.pop('owner')
                    addressbook_objects.append(AddressBook(owner=apply_info.create_by, **data))
                addressbook_objects = addressbook_objects[:10]
            else:
                user_info = _get_user_info(request, apply_info.create_by)
                snap_addressbook = json.loads(serializers.serialize('json', user_info['addressbooks']))
                snap_data = [i['fields'] for i in snap_addressbook]
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {'addressbook': snap_data}})
                addressbook_objects = user_info['addressbook']
            bankcards_objects = []
            if 'bankcards' in snapshot_data:
                print 'snap bankcards', snapshot_data['bankcards']
                for data in snapshot_data['bankcards']:
                    data.pop('user')
                    bankcards_objects.append(BankCard(**data))
            else:
                user_info = _get_user_info(request, apply_info.create_by)
                snap_bankcards = json.loads(serializers.serialize('json', user_info['bankcards']))
                snap_data = [i['fields'] for i in snap_bankcards]
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {'bankcards': snap_data}})
                bankcards_objects = user_info['bankcards']
            chsis_objects = []
            if 'chsis' in snapshot_data:
                print 'snap chsis:',snapshot_data['chsis']
                for data in snapshot_data['chsis']:
                    data.pop('user')
                    chsis_objects.append(Chsi(user=apply_info.create_by, **data))
            else:
                user_info = _get_user_info(request, apply_info.create_by)
                snap_chsis = json.loads(serializers.serialize('json', user_info['chsis']))
                chsis_doc = [i['fields'] for i in snap_chsis]
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {'chsis': chsis_doc}})
                chsis_objects = user_info['chsis']
            contacts_objects = []
            if 'contacts' in snapshot_data:
                print 'snap contacts:', snapshot_data['contacts']
                for data in snapshot_data['contacts']:
                    data[0].pop('owner')
                    same_ids = ContactInfo.objects.filter(Q(phone_no=data[0]['phone_no']) & ~Q(owner=apply_info.create_by))
                    contact = ContactInfo(owner=apply_info.create_by, **data[0])
                    contact.contact_repeat = len(same_ids)
                    contact.contacts = same_ids[:10]
                    contacts_objects.append((contact, data[1]))
            else:
                user_info = _get_user_info(request, apply_info.create_by)
                for contact, names in user_info['contacts']:
                    snap_contact = json.loads(serializers.serialize('json', [contact, ]))[0]
                    contact_doc = snap_contact['fields']
                    contacts_objects.append((contact_doc, names,))
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": {'contacts': contacts_objects}})
                contacts_objects = user_info['contacts']
            if 'profile' in snapshot_data['user_info']:
                print 'snapshot profile:', snapshot_data['user_info']['profile']
                profile_doc = snapshot_data['user_info']['profile']
                if "owner" in profile_doc:
                    profile_doc.pop("owner")
                profile_object = Profile(owner=apply_info.create_by, **profile_doc)
            else:
                profiles = Profile.objects.filter(owner=apply_info.create_by)
                profile_object = profiles
            id_card_doc = {}
            if snapshot_data['user_info'].get('id_card_info', None):
                id_card_doc = snapshot_data['user_info']['id_card_info']
                if 'owner' in id_card_doc:
                    id_card_doc.pop('owner')
            idcard_object = IdCard(owner=apply_info.create_by, **id_card_doc)
            same_ids = User.objects.filter(device_id=apply_info.create_by.device_id)
            device_id_repeat = len(same_ids)
            ids = same_ids[:10]
            try:
                register_ip = redis_client.hget("USER_INFO:%d" % apply_info.create_by.id, "ip")
            except:
                TkLog().error(u"call redis error")
                register_ip = ''
            check_status_data = snapshot_data['user_info']['check_status']
            if check_status_data:
                print 'snapshot check_status:', snapshot_data['user_info']['check_status']
                if 'owner' in check_status_data:
                    check_status_data.pop("owner")
                check_status_object = CheckStatus(owner=apply_info.create_by, **check_status_data)
            else:
                check_status_object = None
            user_dict = {}
            profile = profiles[0] if len(profiles) == 1 else None
            if profile.job == 2:
                user_dict["has_ebusiness"] = True
            else:
                user_dict["has_ebusiness"] = False
            if 'has_ebusiness' in snapshot_data:
                has_ebusiness = snapshot_data['has_ebusiness']
            else:
                has_ebusiness = user_dict['has_ebusiness']
            try:
                has_new_data = redis_client.hget("USER_INFO:%d" % apply_info.id, "mobile_record")
            except Exception, e:
                TkLog().error(u"call redis error")
            if has_new_data or 'new_data' not in snapshot_data:
                user_dict["new_data"] = True
                basic_data = data_query.basic_data.copy()
                basic_data["user_id"] = apply_info.create_by.id
                phone_basics = data_query.get_phonebasic_data(basic_data)
                user_dict["phone_basics"] = phone_basics
                phone_data = data_query.phone_data.copy()
                phone_data["user_id"] = apply_info.create_by.id
                phone_data["contact"] = []
                for contact, names in contacts_objects:
                    phone_data["contact"].append({"contact_name": contact.name, "contact_type": contact.relationship, "contact_tel": contact.phone_no})
                contact_phone_calls, contact_phone_call_columns = data_query.get_phonecall_data(phone_data)
                contact_phone_data = None
                if contact_phone_calls:
                    contact_phone_data = []
                    for phone_call, featrue in contact_phone_calls:
                        name_inaddressbook = AddressBook.objects.filter(owner=apply_info.create_by, phone_number=phone_call)
                        contact_name = name_inaddressbook[0].name if name_inaddressbook else ''
                        contact_phone_data.append((phone_call, featrue, contact_name,))
                user_dict["contact_phone_call_columns"] = contact_phone_call_columns
                user_dict["contact_phone_calls"] = contact_phone_data
                corp_data = data_query.corp_data.copy()
                corp_data["user_id"] = apply_info.create_by.id
                (corp_contact_phone_calls, corp_contact_phone_call_columns) = data_query.get_corp_phonecall_data(corp_data)
                user_dict["corp_contact_phone_call_columns"] = corp_contact_phone_call_columns
                user_dict["corp_contact_phone_calls"] = corp_contact_phone_calls
                ebusiness_data = data_query.ebusiness_data.copy()
                ebusiness_data["user_id"] = apply_info.create_by.id
                e_business = data_query.get_ebusiness_data(ebusiness_data)
                user_dict["e_business"] = e_business
                deliver_data = data_query.deliver_data.copy()
                deliver_data["user_id"] = apply_info.create_by.id
                e_deliver = data_query.get_deliver_data(deliver_data)
                user_dict["e_deliver"] = e_deliver
                phone_location_data = data_query.phone_location_data.copy()
                phone_location_data["user_id"] = apply_info.create_by.id
                phone_location = data_query.get_phone_location_data(phone_location_data)
                user_dict["phone_location"] = phone_location
                table.find_one_and_update({"apply_info.id": apply_info.id}, {"$set": user_dict})
            else:
                user_dict["new_data"] = snapshot_data["new_data"]
                user_dict["phone_basics"] = snapshot_data['phone_basics']
                user_dict["contact_phone_call_columns"] = snapshot_data["contact_phone_call_columns"]
                user_dict["contact_phone_calls"] = snapshot_data["contact_phone_calls"]
                user_dict["corp_contact_phone_call_columns"] = snapshot_data["corp_contact_phone_call_columns"]
                user_dict["corp_contact_phone_calls"] = snapshot_data["corp_contact_phone_calls"]
                user_dict["e_business"] = snapshot_data["e_business"]
                user_dict["e_deliver"] = snapshot_data["e_deliver"]
                user_dict["phone_location"] = snapshot_data["phone_location"]
            update_dict = {"user": user_object, 'profile': profile_object, 'idcard': idcard_object,
                         'device_id_repeat': device_id_repeat, 'has_ebusiness': has_ebusiness, 'register_ip': register_ip, "ip_address": "",
                         'oss_url': settings.OSS_URL, 'chsi_auth': chsi_auth, 'check_status': check_status_object,
                         'addressbook': addressbook_objects, 'ids': ids, 'bankcards': bankcards_objects,
                         'chsis': chsis_objects, 'contacts': contacts_objects}
            user_dict.update(update_dict)
            all_dict = user_dict.copy()
            all_dict.update(apply_dict)
            return all_dict
    except:
        traceback.print_exc()
        user_dict = _get_user_info(request, apply_info.create_by)
        all_dict = user_dict.copy()
        all_dict.update(apply_dict)
        return all_dict

@csrf_exempt
def finish_review(request):
    if request.method == 'POST':
        apply_id = request.POST.get("apply_id")
        review_id = request.POST.get("review_id")
        try:
            apply = Apply.objects.get(pk = apply_id)
            review = Review.objects.get(pk = review_id)
            staff = Employee.objects.get(user = request.user)
            TkLog().info(u"%s submit finish_review: %d)%s %s" %(staff.username, review.order.id, review.order.create_by.name, review.order.create_by.phone_no))
            if apply.create_by.is_register < 0:
                TkLog().info("用户已注销")
                apply.status = 'e' # 取消订单
                apply.save()
                Timer(0, _make_snapshot_apply, (request, apply,)).start()
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
                    #print 'new extra'
                    extra_apply = ExtraApply()
                    extra_apply.apply = apply
                else:
                    #print 'modify extra'
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
                    check_status.set_profile_status("pass")
                    # increase_status = bin(check_status.increase_status)
                    # increase_status = ''.join([increase_status[:-2], '01'])
                    # check_status.increase_status = int(increase_status, 2)
                    # increase_check_status = bin(check_status.increase_check_status)
                    # increase_check_status = ''.join([increase_check_status[:-2], '11'])
                    # increase_check_status = int(increase_check_status, 2)
                    # check_status.increase_check_status = increase_check_status
                    check_status.save()
                    if apply.create_by.channel == u"线下导入":
                        check_status.credit_limit = 200000
                        check_status.base_credit = 200000
                        check_status.max_credit = 680000
                        check_status.credit_score = 500
                    else:
                        try:
                            (res, score, value) = rc_client.init_limit(apply.create_by.id, 0) ## base credit
                            TkLog().info("get credit limit from rc_server res:%s, score:%d, value:%d" % (res, score, value))
                            if res == "0005": #success
                                check_status.credit_limit = value * 100
                                check_status.base_credit = value * 100
                                check_status.max_credit = check_status.credit_limit + 480000
                                check_status.credit_score = score
                                TkLog().info(u"get new score: %s" % check_status.credit_limit)
                            else:
                                check_status.credit_limit = 150000
                                check_status.base_credit = 150000
                                check_status.max_credit = check_status.credit_limit + 480000
                                check_status.credit_score = score
                                TkLog().info(u"get random new score: %s" % check_status.credit_limit)
                        except Exception, e:
                            TkLog().info("get credit limit from rc_server failed %s" % str(e))
                            res = "0"
                    check_status.set_profile_status("pass")
                    try:
                        # limit_msg_id = push_client_object.add_message(apply.create_by.id, 30)
                        if apply.type == '0':
                            pass_msg_id = push_client_object.add_message(apply.create_by.id, 200001)
                            Timer(0, push_client_object.push, (apply.create_by.id, pass_msg_id,)).start()
                            # Timer(0, push_client_object.push, (apply.create_by.id, limit_msg_id,)).start()
                            if apply.create_by.wechat_openid:
                                openid = apply.create_by.wechat_openid
                                params = {
                                    "openid": openid,
                                    "first": '您的认证申请已经通过审核！',
                                    "name": apply.create_by.name,
                                    "phone_no": apply.create_by.phone_no,
                                    "remark": '终于等到您，赶快去提现吧！',
                                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                }
                                url = 'http://devapiwap.hualahuala.com/web/push/authentication_notice'
                                Timer(0, send_message_weixin, (params, url,)).start()
                            Timer(0, message_client.send_message,
                                  (review.order.create_by.phone_no,
                                   u"您提交的信息已经审核完毕，请登录您的花啦花啦账户查看审核结果。如有任何疑问，请联系花啦花啦客服400-606-4728".encode("gbk"),
                                   5,)).start()
                    except Exception, e:
                        print e
                        TkLog().error("push error:%s" % traceback.format_exc())
                elif status == 'r':
                    #打回联系人的话需要删除反向索引
                    check_status.set_profile_status("recheck")
                    # increase_status = bin(check_status.increase_status)
                    # increase_status = ''.join([increase_status[:-2], '01'])
                    # check_status.increase_status = int(increase_status, 2)
                    # increase_check_status = bin(check_status.increase_check_status)
                    # increase_check_status = ''.join([increase_check_status[:-2], '00'])
                    # increase_check_status = int(increase_check_status, 2)
                    # check_status.increase_check_status = increase_check_status
                    if apply.type == '0':
                        return_msg_id = push_client_object.add_message(apply.create_by.id, 200002)
                        Timer(0, push_client_object.push, (apply.create_by.id, return_msg_id,)).start()
                        if apply.create_by.wechat_openid:
                            openid = apply.create_by.wechat_openid
                            params = {
                                        "openid": openid,
                                        "first": '您提交的资料还需要完善一下哦',
                                        "name": apply.create_by.name,
                                        "phone_no": apply.create_by.phone_no,
                                        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        "remark": '快去补充资料，真实的资料能帮助您通过审核！',
                            }
                            url = 'http://devapiwap.hualahuala.com/web/push/authentication_notice'
                            Timer(0, send_message_weixin, (params, url,)).start()
                        Timer(0, message_client.send_message,
                              (review.order.create_by.phone_no,
                               u"您提交的信息有部分存在问题，请在两个工作日内登录花啦花啦按提示进行修改。如有疑问，请联系花啦花啦客服400-606-4728 ".encode("gbk"),
                               5,)).start()
                elif status == 'n':
                    check_status.set_profile_status("deny")
                    # increase_status = bin(check_status.increase_status)
                    # increase_status = ''.join([increase_status[:-2], '01'])
                    # check_status.increase_status = int(increase_status, 2)
                    # increase_check_status = bin(check_status.increase_check_status)
                    # increase_check_status = ''.join([increase_check_status[:-2], '00'])
                    # increase_check_status = int(increase_check_status, 2)
                    # check_status.increase_check_status = increase_check_status
                    #check_status.profile_check_status = 0x3aaa
                    if apply.type == '0':
                        deny_msg_id = push_client_object.add_message(apply.create_by.id, 200003)
                        Timer(0, push_client_object.push, (apply.create_by.id, deny_msg_id,)).start()
                        if apply.create_by.wechat_openid:
                            openid = apply.create_by.wechat_openid
                            params = {
                                        "openid": openid,
                                        "first": '抱歉，您提交的资料没有通过审核',
                                        "name": apply.create_by.name,
                                        "phone_no": apply.create_by.phone_no,
                                        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        "remark": '您可在15日之后重新提交信息申请，如有疑问，请咨询微信在线客服！',
                            }
                            url = 'http://devapiwap.hualahuala.com/web/push/authentication_notice'
                            Timer(0, send_message_weixin, (params, url,)).start()
                        Timer(0, message_client.send_message,
                              (review.order.create_by.phone_no,
                               u"因为系统给出的综合信用评分不足，您的申请未通过审核。如有疑问，请联系花啦花啦客服400-606-4728 ".encode("gbk"),
                               5,)).start()

                check_status.save()
            #print review.id, verify_status
            Timer(0, _make_snapshot_apply, (request, apply,)).start()
            TkLog().info(u"%s finish review: %d)%s  %s %s %s" %(staff.username, review.order.id, review.order.create_by.name, verify_status, apply.get_status_display(), review.order.create_by.phone_no))
            return HttpResponse(json.dumps({"result": u"ok"}))
        except Exception, e:
            print e
            TkLog().error(u"finish_review failed %s" % str(e))
            traceback.print_exc()
            return HttpResponse(json.dumps({"error": u"load failed"}))
    return HttpResponse(json.dumps({"error": u"post only"}))

@csrf_exempt
def reset_review(request):
    if request.method == 'POST':
        apply_id = request.POST.get("apply_id")
        staff = Employee.objects.get(user = request.user)
        TkLog().info("%s reset review %s." % (staff.username, apply_id))
        try:
            order = Apply.objects.get(pk=apply_id)
            order.status = '0'
            order.save()
            repayments = RepaymentInfo.objects.filter(user = order.create_by)
            for repayment in repayments:
                repayment.delete()
                TkLog().info("reset review: delete related repayment %s." % (repayment.order_number))
            TkLog().info("%s reset review %s success." % (staff.username, apply_id))
            return HttpResponse(json.dumps({"result" : u"ok"}))
        except Exception, e:
            print e
            TkLog().error(u"reset_review failed %s" % str(e))
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"reset failed"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
def cancel_review(request):
    if request.method == 'POST':
        try:
            applyid = request.POST.get("apply_id")
            staff = Employee.objects.get(user = request.user)
            apply = Apply.objects.get(pk = applyid)
            TkLog().info(u"%s cancel review: %d)%s" %(staff.username, apply.id, apply.create_by.name))
            reviews = Review.objects.filter(order = apply).order_by("id")
            if len(reviews) <= 0:
                return HttpResponse(json.dumps({"result" : u"no review to cancel"}))
            for r in reviews:
                #print r
                if not r.finish_time:
                    r.delete()
        except Exception, e:
            traceback.print_exc()
            print e
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse(json.dumps({"result" : "ok"}))
    return HttpResponse(json.dumps({"error" : u"post only"}))

@csrf_exempt
def finish_loan_review(request):
    if request.method == 'POST':
        try:
            applyid = request.POST.get("apply_id")
            TkLog().info("start loan review %s"%(applyid))
            #print applyid, 'applyid'
            area_type = "total"
            result = request.POST.get(area_type + "_area_radio")
            apply = Apply.objects.get(pk = applyid)
            apply.status = result
            apply.finish_time = datetime.now()
            apply.save()
            #check = CheckStatus.objects.get(owner = apply.create_by)
            staff = Employee.objects.get(user = request.user)
            reviews = Review.objects.filter(order = apply)
            if len(reviews) > 0:
                review = reviews[0]
                review.reviewer_done = staff
                review.finish_time = datetime.now()
                review.review_res = 'y'
                review.save()
                review_record = ReviewRecord(review = review)
                review_record.review_status = result
                #print review_record.review_status_t, "--", request.POST.get(area_type + "_area_radio")
                review_record.review_note = request.POST.get(area_type + "_area_notes")[:254] if request.POST.get(area_type + "_area_notes") else ""
                review_record.review_message = request.POST.get(area_type + "_area_msg")[:254] if request.POST.get(area_type + "_area_msg") else ""
                review_record.review_type = area_type[0]
                review_record.save()
                if result == 'n':
                    #直接拒绝用户
                    #check.set_profile_status("deny")
                    #check.save()
                    apply.repayment.repay_status = -3
                    apply.repayment.save()
                    if apply.type != 's':
                        loan_msg_id = push_client_object.add_message(apply.create_by.id, 100008)
                        Timer(0, push_client_object.push, (apply.create_by.id, loan_msg_id,)).start()
                        # Timer(0, push_client_object.push, (apply.create_by.id, limit_msg_id,)).start()
                        if apply.create_by.wechat_openid:
                            openid = apply.create_by.wechat_openid
                            params = {
                                "openid": openid,
                                "cash ": apply.repayment.apply_amount,
                                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "status": '未审核通过',
                            }
                            url = 'http://devapiwap.hualahuala.com/web/push/latest_notice'
                            Timer(0, send_message_weixin, (params, url,)).start()
                        Timer(0, message_client.send_message,
                              (review.order.create_by.phone_no,
                               u"您好，您申请的提现未通过审核！感谢您对花啦花啦的支持！如有任何疑问，请联系花啦花啦客服400-606-4728".encode("gbk"),
                               5,)).start()
                        message_client.send_message(review.order.create_by.phone_no, u"很遗憾，您提交的借贷申请被拒绝，如有任何疑问，请联系花啦花啦客服400-606-4728".encode("gbk"), 5)
                elif result == 'y':
                    apply.repayment.repay_status = 6
                    apply.repayment.save()
                    if apply.type != 's':
                        loan_msg_id = push_client_object.add_message(apply.create_by.id, 100007)
                        Timer(0, push_client_object.push, (apply.create_by.id, loan_msg_id,)).start()
                        # Timer(0, push_client_object.push, (apply.create_by.id, limit_msg_id,)).start()
                        if apply.create_by.wechat_openid:
                            openid = apply.create_by.wechat_openid
                            params = {
                                "openid": openid,
                                "cash ": '恭喜，您的资料通过审核！',
                                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "status": '审核通过',
                            }
                            url = 'http://devapiwap.hualahuala.com/web/push/latest_notice'
                            Timer(0, send_message_weixin, (params, url,)).start()
                        Timer(0, message_client.send_message,
                              (review.order.create_by.phone_no,
                               u"您好，您申请的提现已成功通过审核！我们会尽快发放到您指定的银行卡，请注意查收。如有任何疑问，请联系花啦花啦客服400-606-4728".encode("gbk"),
                               5,)).start()
                        message_client.send_message(review.order.create_by.phone_no, u"您提交的借贷申请已经通过，请登录您的花啦花啦账户签署合同。".encode("gbk"), 5)
                else:
                    pass
                TkLog().info("start loan review success %s. res:%s" % (applyid, result))
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            TkLog().error("finish loan error")
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse("ok")
    return HttpResponse("only post allowed")


@csrf_exempt
def finish_promotion_review(request):
    if request.method == 'POST':
        try:
            score = request.POST.get("score")
            applyid = request.POST.get("apply_id")
            type = request.POST.get("apply_type")
            s = int(score)
            if s > 800 or s < 0:
                return HttpResponse(json.dumps({"error" : u"额度超出范围"}))
            print "finish promotion", applyid, score
            apply = Apply.objects.get(pk = applyid)
            apply.finish_time = datetime.now()
            apply.money = int(score) * 100
            apply.status = 'y'
            apply.save()
            staff = Employee.objects.get(user = request.user)
            review = Review.objects.get(order = apply)
            review.reviewer_done = staff
            review.finish_time = datetime.now()
            review.review_res = 'y'
            review.money = int(score)
            review.save()
            #print review.id
            check = CheckStatus.objects.get(owner = apply.create_by)
            check.credit_limit += int(score) * 100
            #微博 人人 通讯录 征信 流水 其他
            offset = int(type) - 1
            check.increase_check_status = check.increase_check_status & ~(0x3 << (2 * offset))
            check.increase_check_status = check.increase_check_status | (0x3 << (2 * offset))
            check.save()
            TkLog().info('incr check status %d' % check.increase_check_status)
            limit_msg_id = push_client_object.add_message(apply.create_by.id, 200011)
            Timer(0, push_client_object.push, (apply.create_by.id, limit_msg_id,)).start()
            # Timer(0, push_client_object.push, (apply.create_by.id, limit_msg_id,)).start()
            if apply.create_by.wechat_openid:
                openid = apply.create_by.wechat_openid
                params = {
                    "openid": openid,
                    "increasement": score,
                    'latest': check.credit_limit,
                    "apply_day": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "reason": '',
                }
                if apply.type == '1':
                    params['reason'] = '绑定微博账号'
                if apply.type == '7':
                    params["reason"] = "绑定京东账号"
                if apply.type == '5':
                    params['reason'] = '增加银行流水信息'
                if apply.type == '4':
                    params['reason'] = '增加征信报告信息'
                url = 'http://devapiwap.hualahuala.com/web/push/limitation_promote'
                Timer(0, send_message_weixin, (params, url,)).start()
            Timer(0, message_client.send_message,
                  (review.order.create_by.phone_no,
                   u"您好，您申请的提现已成功通过审核！我们会尽快发放到您指定的银行卡，请注意查收。如有任何疑问，请联系花啦花啦客服400-606-4728".encode("gbk"),
                   5,)).start()
            #print check.id
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse("ok")
    return HttpResponse("only post allowed")

@csrf_exempt
def get_captcha(request):
    if request.method == 'GET':
        uid = request.GET.get("uid")
        print "get captcha", uid
        TkLog().info("get captcha %s" % (uid))
        try:
            (ret, captcha_pic, msg) = bind_client.rebind_chsi(int(uid))
            msg = msg.decode('utf-8') if msg else ""
            if ret == -1: # 绑定需要验证码
                TkLog().info("get captcha %s %d" % (uid, ret))
                return HttpResponse(json.dumps({"error" : u"ok", "bind": base64.encodestring(captcha_pic)}))
            elif ret == 0: # 直接成功了。。
                TkLog().info("get captcha success")
                return HttpResponse(json.dumps({"error" : u"success"}))
            elif ret == -2: # 内部错误。。放弃吧
                TkLog().error("get captcha failed -2: %s" %msg)
                return HttpResponse(json.dumps({"error" : "内部错误 %s" %msg}))
            elif ret == -3: #
                TkLog().error("get captcha failed -3: %s" %msg)
                return HttpResponse(json.dumps({"error" : "找不到登录信息"}))
            elif ret == -4: #
                TkLog().error("get captcha failed -4: %s" %msg)
                return HttpResponse(json.dumps({"error" : "验证码填写错误 请打回申请重填"}))
            elif ret == -5: #
                TkLog().error("get captcha failed -5: %s" %msg)
                return HttpResponse(json.dumps({"error" : "无学信网信息 可以拒绝该用户"}))
            else:
                TkLog().error("unknown error %s %d" % (uid, ret))
                return HttpResponse(json.dumps({"error" : u"unknown error"}))
        except Exception, e:
            traceback.print_exc()
            TkLog().error("unknown error %s" % e)
            return HttpResponse(json.dumps({"error" : "unknown error"}))
    return HttpResponse(json.dumps({"error" : u"unknown error"}))

@csrf_exempt
def submit_captcha(request):
    if request.method == 'GET':
        try:
            uid = request.GET.get("uid")
            captcha = request.GET.get("captcha")
            print "submit captcha", captcha , type(uid)
            TkLog().info("submit captcha %s, %s" % (uid, captcha))
            (ret, captcha_pic, msg)= bind_client.send_captcha(int(uid), captcha)
            msg = msg.decode('utf-8') if msg else ""
            if ret == -1: # 验证码错误或者密码错误
                TkLog().info(u"submit captcha %s %d %s" % (uid, ret, msg))
                return HttpResponse(json.dumps({"error" : "ok", "bind": base64.encodestring(captcha_pic), "msg":msg}))
            elif ret == 0: # 终于成功了
                TkLog().info("submit captcha success")
                return HttpResponse(json.dumps({"error" : "success"}))
            elif ret == -2: # 内部错误。。放弃吧
                TkLog().error("submit captcha failed -2: %s" %msg)
                return HttpResponse(json.dumps({"error" : "ohoh! 内部错误"}))
            elif ret == -3: #
                TkLog().error("submit captcha failed -3: %s" %msg)
                return HttpResponse(json.dumps({"error" : "找不到登录信息"}))
            elif ret == -4: #
                TkLog().error("submit captcha failed -4: %s" %msg)
                return HttpResponse(json.dumps({"error" : "验证码填写错误 请打回申请重填"}))
            elif ret == -5: #
                TkLog().error("submit captcha failed -5: %s" %msg)
                return HttpResponse(json.dumps({"error" : "无学信网信息 可以拒绝该用户"}))
            else:
                TkLog().error("submit unknown error %d" %ret)
                return HttpResponse(json.dumps({"error" : "unknown error"}))
        except Exception, e:
            traceback.print_exc()
            TkLog().error("submit unknown error %s" % e)
            return HttpResponse(json.dumps({"error" : "unknown error"}))

    return HttpResponse(json.dumps({"error" : "unknown error"}))

@csrf_exempt
def download_addressbook(request):
    if request.method == 'GET':
        uid = request.GET.get("uid")
        apply_id = request.GET.get("pid")
        TkLog().info("download %s addressbook" % uid)
        user = get_object_or_404(User, id=uid)
        addressbook = []
        records = []
        try:
            apply_object = Apply.objects.get(pk=apply_id)
            if apply_object.status not in ['w', 'i', '0']:
                addressbook_objects = []
                callrecord_objects = []
                table = mongo_client['snapshot']['basic_apply']
                if apply_id:
                    snapshot_data = table.find_one({"apply_info.id": apply_object.id})
                else:
                    snapshot_data = None
                if not snapshot_data:
                    addressbook = AddressBook.objects.filter(owner=user)
                    records = CallRecord.objects.filter(owner=user)
                else:
                    if 'addressbook' in snapshot_data:
                        TkLog().info('snap_addressbook: %s' % str(snapshot_data['addressbook']))
                        for data in snapshot_data['addressbook']:
                            data.pop('owner')
                            addressbook_objects.append(AddressBook(owner=apply_object.create_by, **data))
                        addressbook = addressbook_objects
                    if 'callrecord' in snapshot_data:
                        TkLog().info('snap_callrecord: %s' % str(snapshot_data['callrecord']))
                        for data in snapshot_data['callrecord']:
                            data.pop('owner')
                            callrecord_objects.append(CallRecord(owner=apply_object.create_by, **data))
                        records = callrecord_objects
            else:
                addressbook = AddressBook.objects.filter(owner=user)
                records = CallRecord.objects.filter(owner=user)
            w = Workbook()
            ws = w.add_sheet(unicode('手机通讯录', "utf-8"))
            for i, address in enumerate(addressbook):
                ws.write(i, 0, address.phone_number)
                ws.write(i, 1, address.name)#unicode(address.name, 'utf-8'))
                ws.write(i, 2, datetime.fromtimestamp(address.create_time).strftime("%y-%m-%d"))

            rs = w.add_sheet(unicode('手机通话记录', "utf-8"))


            for i, record in enumerate(records):
                rs.write(i, 0, record.phone_number)
                rs.write(i, 1, record.name)
                rs.write(i, 2, record.duration)
                rs.write(i, 3, record.call_time)
                rs.write(i, 4, record.get_call_type_display())

            rs = w.add_sheet(unicode('运营商通话详单',"utf-8"))
            try:
                new_data = redis_client.hget("USER_INFO:%s" % uid, "mobile_record")
            except Exception, e:
                TkLog().error(u"call redis error")
                new_data = False

            if new_data:
                phonecall_rawdata = data_query.phonecall_rawdata.copy()
                phonecall_rawdata["user_id"] = int(uid)
                call_records = data_query.get_phonecall_rawdata(phonecall_rawdata)
                if not call_records or call_records == u'采集失败':
                    call_records = []
                for i, record in enumerate(call_records):
                    #rs.write(i, 0, record["cell_phone"] if record["cell_phone"] else "")
                    rs.write(i, 0, record["other_cell_phone"] if record["other_cell_phone"] else "")
                    rs.write(i, 1, record["call_place"] if record["call_place"] else "")
                    rs.write(i, 2, record["start_time"] if record["start_time"] else "")
                    rs.write(i, 3, record["use_time"] if record["use_time"] else "")
                    rs.write(i, 4, record["call_type"] if record["call_type"] else "")
                    rs.write(i, 5, record["init_type"] if record["init_type"] else "")
            else:
                latest_call = PhoneCall.objects.filter(owner = user).order_by('-id')[:1]
                if len(latest_call) == 1:
                    latest_version = latest_call[0].version
                    call_records = PhoneCall.objects.filter(owner = user, version = latest_version)
                    for i, record in enumerate(call_records):
                        rs.write(i, 0, record.cell_phone if record.cell_phone else "")
                        rs.write(i, 1, record.other_cell_phone if record.other_cell_phone else "")
                        rs.write(i, 2, record.call_place if record.call_place else "")
                        rs.write(i, 3, record.start_time.strftime("%y-%m-%d %H:%M:%S") if record.start_time else "")
                        rs.write(i, 4, record.use_time if record.use_time else "")
                        rs.write(i, 5, record.call_type if record.call_type else "")
                        rs.write(i, 6, record.init_type if record.init_type else "")
            w.save('t.xls')
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error": u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('t.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("t.xls")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % uid
        return response
    return HttpResponse(json.dumps({"error": "get only"}))

def _get_apply_list(request):
    try:
        stime = get_today()
        etime = get_tomorrow()
        timerange =request.GET.get("time")
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

        time_filter = request.GET.get("time_filter")
        query_time = None
        if time_filter == "review":
            query_time = Q(finish_time__lt = etime, finish_time__gt = stime)
        else:
            query_time = Q(create_at__lt = etime, create_at__gt = stime)

        query_status = None
        status =request.GET.get("status")
        if status == "waiting" :
            query_status = Q(status = '0') | Q(status = 'i')
        elif status == "passed" :
            query_status = Q(status = 'y')
        elif status == "rejected" :
            query_status = Q(status = 'n')
        elif status == "auto_rejected" :
            query_status = Q(status = 'b')
        elif status == "back" :
            query_status = Q(status = 'r')
        else :
            query_status = Q()

        review_type =request.GET.get("type")
        query_type = Q(type__lte ='9', type__gte = '0')
        if review_type == 'basic':
            query_type = Q(type = '0')
        elif review_type == 'promotion':
            query_type = Q(type__lte ='8', type__gte = '1')
        elif review_type == 'second':
            query_type = Q(type = 's')
        elif review_type == 'loan':
            query_type = Q(type = '0') | Q(type = 's')
        elif review_type == 'all':
            query_type = Q(type__lte ='9', type__gte = '0') | Q(type = 's')

        #print apply_list, query_time & query_status & query_type
        apply_list = Apply.objects.filter(query_time & query_status & query_type)
        return (apply_list, stime, etime)
    except Exception, e:
        print "excp", e
        traceback.print_exc()
        return ([], "", "")

# 审批绩效考核表(每次审批一条记录)
def download_review_table_1(request):
    if request.method == 'GET':
        apply_list, stime, etime = _get_apply_list(request)
        try :
            w = Workbook()
            ws = w.add_sheet('review')
            ws.write(0, 0, unicode("贷款编号", 'utf-8'))
            ws.write(0, 1, unicode("客户类型", 'utf-8'))
            ws.write(0, 2, unicode("申请日期", 'utf-8'))
            ws.write(0, 3, unicode("处理人姓名", 'utf-8'))
            ws.write(0, 4, unicode("开始时间", 'utf-8'))
            ws.write(0, 5, unicode("结束时间", 'utf-8'))
            ws.write(0, 6, unicode("处理时长", 'utf-8'))
            ws.write(0, 7, unicode("审批结果", 'utf-8'))
            #if is_manager:
            ws.write(0, 8, unicode("审批备注", 'utf-8'))
            i = 1
            for apply in apply_list:
                profiles = Profile.objects.filter(owner = apply.create_by)
                reviews = Review.objects.filter(order=apply)
                if len(reviews) == 0:
                    ws.write(i, 0, apply.id)
                    ws.write(i, 1, profiles[0].get_job_display() if len(profiles) == 1 else "" )
                    ws.write(i, 2, apply.create_at.strftime("%Y-%m-%d %H:%M:%S"))
                    ws.write(i, 7, apply.get_status_display())
                    #ws.write(i, 8, apply.create_by.get())
                    i += 1
                for review in reviews:
                    ws.write(i, 0, apply.id)
                    ws.write(i, 1, profiles[0].get_job_display() if len(profiles) == 1 else "" )
                    ws.write(i, 2, apply.create_at.strftime("%Y-%m-%d %H:%M:%S"))
                    ws.write(i, 3, review.reviewer.username)
                    ws.write(i, 4, review.create_at.strftime("%Y-%m-%d %H:%M:%S") if review.create_at else "")
                    ws.write(i, 5, review.finish_time.strftime("%Y-%m-%d %H:%M:%S") if review.finish_time else "")
                    if review.finish_time:
                        delta = review.finish_time - review.create_at
                        ws.write(i, 6, "%s:%s:%s" % (delta.days, delta.seconds/60, delta.seconds%60))
                    else:
                        ws.write(i, 6, "")
                    ws.write(i, 7, review.get_review_res_display())
                    i += 1
            w.save('t.xls')

        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        response = StreamingHttpResponse(FileWrapper(open('t.xls'), 8192), content_type='application/vnd.ms-excel')
        response['Content-Length'] = os.path.getsize("t.xls")
        response['Content-Disposition'] = 'attachment; filename=%s-%s.xls' % (stime, etime)
        return response
    return HttpResponse(json.dumps({"error" : "get only"}))

# 审批绩效考核表(按照订单提交时间 暂时废弃)
def download_review_table_2(request):
    if request.method == 'GET':
        apply_list, stime, etime = _get_apply_list(request)
        try :
            w = Workbook()
            ws = w.add_sheet('review')
            ws.write(0, 0, unicode("贷款编号", 'utf-8'))
            ws.write(0, 1, unicode("客户类型", 'utf-8'))
            ws.write(0, 2, unicode("申请日期", 'utf-8'))
            ws.write(0, 3, unicode("客户姓名", 'utf-8'))
            ws.write(0, 4, unicode("渠道来源", 'utf-8'))
            ws.write(0, 5, unicode("审批结果", 'utf-8'))
            ws.write(0, 6, unicode("拒绝原因", 'utf-8'))
            i = 1
            for apply in apply_list:
                profiles = Profile.objects.filter(owner = apply.create_by)
                ws.write(i, 0, apply.id)
                ws.write(i, 1, profiles[0].get_job_display() if len(profiles) == 1 else "" )
                ws.write(i, 2, apply.create_at.strftime("%Y-%m-%d %H:%M:%S"))
                ws.write(i, 3, apply.create_by.name)
                ws.write(i, 4, apply.create_by.channel)
                ws.write(i, 5, apply.get_status_display())
                if apply.status == "b": #机器拒绝 输出机器拒绝的原因
                    check_status = CheckStatus.objects.filter(owner = apply.create_by)
                    ws.write(i, 6, check_status[0].get_auto_check_status_display() if len(check_status) == 1 else "")
                else: #人工拒绝打出人工拒绝的标签
                    ws.write(i, 6, "")
                    #reviews =
                i += 1
            w.save('t.xls')
            response = StreamingHttpResponse(FileWrapper(open('t.xls'), 8192), content_type='application/vnd.ms-excel')
            response['Content-Length'] = os.path.getsize("t.xls")
            response['Content-Disposition'] = 'attachment; filename=%s-%s.xls' % (stime, etime)
            return response
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : str(e)}))
    return HttpResponse(json.dumps({"error" : "get only"}))

# BI报表(每个申请一条记录)
def download_review_table_3(request):
    if request.method == 'GET':
        apply_list, stime, etime = _get_apply_list(request)
        try :
            w = Workbook()
            ws = w.add_sheet('review')
            ws.write(0, 0, unicode("贷款编号", 'utf-8'))
            ws.write(0, 1, unicode("订单类型", 'utf-8'))
            ws.write(0, 2, unicode("客户类型", 'utf-8'))
            ws.write(0, 3, unicode("申请日期", 'utf-8'))
            ws.write(0, 4, unicode("客户姓名", 'utf-8'))
            ws.write(0, 5, unicode("渠道来源", 'utf-8'))
            ws.write(0, 6, unicode("审批结果", 'utf-8'))
            ws.write(0, 7, unicode("拒绝原因", 'utf-8'))
            i = 1
            all_dict = {"label":{}}
            account = {}
            reject_count = {"all":0}
            for apply in apply_list:
                profiles = Profile.objects.filter(owner = apply.create_by)
                ws.write(i, 0, apply.id)
                ws.write(i, 1, apply.get_type_display())
                ws.write(i, 2, profiles[0].get_job_display() if len(profiles) == 1 else "" )
                ws.write(i, 3, apply.create_at.strftime("%Y-%m-%d %H:%M:%S"))
                ws.write(i, 4, apply.create_by.name)
                channel = apply.create_by.channel
                ws.write(i, 5, channel)
                ws.write(i, 6, apply.get_status_display())
                dict_addmap(account, channel)
                dict_addmap(account[channel], "label")
                dict_addcount(account[channel], "count")
                dict_addcount(all_dict, "count")
                if apply.status == "y":
                    dict_addcount(account[channel], "pass_count")
                    dict_addcount(all_dict, "pass_count")
                elif apply.status == "n":
                    dict_addcount(account[channel], "reject_count")
                    dict_addcount(all_dict, "reject_count")

                if apply.status == "b": #机器拒绝 输出机器拒绝的原因
                    dict_addcount(account[channel], "mechine_reject_count")
                    dict_addcount(all_dict, "mechine_reject_count")
                    check_status = CheckStatus.objects.filter(owner = apply.create_by)
                    ws.write(i, 7, check_status[0].get_auto_check_status_display() if len(check_status) == 1 else "")
                else: #人工拒绝打出人工拒绝的标签
                    review = _get_last_review(apply)
                    label = ""
                    if review:
                        label = ",".join(l.display() for l in review.get_label_list().all() if l.is_reject())
                        for l in review.get_label_list().all():
                            if l.is_reject():
                                dict_addcount(account[channel]["label"], l.name)
                                dict_addcount(all_dict["label"], l.name)
                    ws.write(i, 7, label)
                i += 1


            ws = w.add_sheet(unicode('统计报表1', "utf-8"))
            i = 0
            ws.write(i, 1, unicode("渠道", 'utf-8'))
            ws.write(i, 2, unicode("总单量", 'utf-8'))
            ws.write(i, 3, unicode("机器拒绝量", 'utf-8'))
            ws.write(i, 4, unicode("人工审批单量", 'utf-8'))
            ws.write(i, 5, unicode("通过量", 'utf-8'))
            ws.write(i, 6, unicode("拒绝量", 'utf-8'))
            ws.write(i, 7, unicode("通过率", 'utf-8'))
            ws.write(i, 8, unicode("拒绝原因", 'utf-8'))
            i += 1
            for (channel, channel_count) in account.items():
                ws.write(i + 1, 1, channel)
                all_apply_count = channel_count["count"] if "count" in channel_count else 0
                mechine_reject_count = channel_count["mechine_reject_count"] if "mechine_reject_count" in channel_count else 0
                apply_count = all_apply_count - mechine_reject_count
                pass_count = channel_count["pass_count"] if "pass_count" in channel_count else 0
                reject_count = channel_count["reject_count"] if "reject_count" in channel_count else 0
                ws.write(i + 1, 2, all_apply_count)
                ws.write(i + 1, 3, mechine_reject_count)
                ws.write(i + 1, 4, apply_count)
                ws.write(i + 1, 5, pass_count)
                ws.write(i + 1, 6, reject_count)
                ws.write(i + 1, 7, "%.2f%%" % (round(float(pass_count)/apply_count, 4) * 100) if apply_count != 0 else 0)
                j = 7
                for (label, count) in sorted(account[channel]["label"].items(), key=lambda d: -d[1]):
                    j += 1
                    ws.write(i, j, "%s" % label)
                    ws.write(i + 1, j, "%.2f%%" % (round(float(count)/reject_count, 4) * 100 if reject_count != 0 else 0))
                i += 2

            ws.write(i + 1, 1, unicode("总计", "utf-8"))
            all_apply_count = all_dict["count"] if "count" in all_dict else 0
            mechine_reject_count = all_dict["mechine_reject_count"] if "mechine_reject_count" in all_dict else 0
            apply_count = all_apply_count - mechine_reject_count
            pass_count = all_dict["pass_count"] if "pass_count" in all_dict else 0
            reject_count = all_dict["reject_count"] if "reject_count" in all_dict else 0
            ws.write(i + 1, 2, all_apply_count)
            ws.write(i + 1, 3, mechine_reject_count)
            ws.write(i + 1, 4, apply_count)
            ws.write(i + 1, 5, pass_count)
            ws.write(i + 1, 6, reject_count)
            ws.write(i + 1, 7, "%.2f%%" % (round(float(pass_count)/apply_count, 4) * 100) if apply_count != 0 else 0)
            j = 7
            for (label, count) in sorted(all_dict["label"].items(), key=lambda d: -d[1]):
                j += 1
                ws.write(i, j, "%s" % label)
                ws.write(i + 1, j, "%.2f%%" % (round(float(count)/reject_count, 4) * 100 if reject_count != 0 else 0))

            #只统计审批报表需要的三大原因
            reasons = (u"与多家贷款公司联系异常", u"催收通话记录"), (u"父母是否虚假",), (u"不符合进件政策", u"三方负面信息", u"与父母无联系")
            ws = w.add_sheet(unicode('统计报表2', "utf-8"))
            i = 0
            ws.write(i, 1, unicode("渠道", 'utf-8'))
            ws.write(i, 2, unicode("总单量", 'utf-8'))
            ws.write(i, 3, unicode("机器拒绝量", 'utf-8'))
            ws.write(i, 4, unicode("人工审批单量", 'utf-8'))
            ws.write(i, 5, unicode("通过量", 'utf-8'))
            ws.write(i, 6, unicode("拒绝量", 'utf-8'))
            ws.write(i, 7, unicode("通过率", 'utf-8'))
            ws.write(i, 8, unicode("详单异常", 'utf-8'))
            ws.write(i, 9, unicode("联系人虚假", 'utf-8'))
            ws.write(i, 10, unicode("其他", 'utf-8'))
            i += 1

            for (channel, channel_count) in account.items():
                ws.write(i + 1, 1, channel)
                all_apply_count = channel_count["count"] if "count" in channel_count else 0
                mechine_reject_count = channel_count["mechine_reject_count"] if "mechine_reject_count" in channel_count else 0
                apply_count = all_apply_count - mechine_reject_count
                pass_count = channel_count["pass_count"] if "pass_count" in channel_count else 0
                reject_count = channel_count["reject_count"] if "reject_count" in channel_count else 0
                ws.write(i + 1, 2, all_apply_count)
                ws.write(i + 1, 3, mechine_reject_count)
                ws.write(i + 1, 4, apply_count)
                ws.write(i + 1, 5, pass_count)
                ws.write(i + 1, 6, reject_count)
                ws.write(i + 1, 7, "%.2f%%" % (round(float(pass_count)/apply_count, 4) * 100) if apply_count != 0 else 0)
                j = 7
                for lables in (reasons):
                    count = 0
                    for label in lables:
                        count += account[channel]["label"][label] if label in account[channel]["label"] else 0
                    j += 1
                    ws.write(i + 1, j, "%.2f%%" % (round(float(count)/reject_count, 4) * 100 if reject_count != 0 else 0))
                i += 2

            ws.write(i + 1, 1, unicode("总计", "utf-8"))
            all_apply_count = all_dict["count"] if "count" in all_dict else 0
            mechine_reject_count = all_dict["mechine_reject_count"] if "mechine_reject_count" in all_dict else 0
            apply_count = all_apply_count - mechine_reject_count
            pass_count = all_dict["pass_count"] if "pass_count" in all_dict else 0
            reject_count = all_dict["reject_count"] if "reject_count" in all_dict else 0
            ws.write(i + 1, 2, all_apply_count)
            ws.write(i + 1, 3, mechine_reject_count)
            ws.write(i + 1, 4, apply_count)
            ws.write(i + 1, 5, pass_count)
            ws.write(i + 1, 6, reject_count)
            ws.write(i + 1, 7, "%.2f%%" % (round(float(pass_count)/apply_count, 4) * 100) if apply_count != 0 else 0)
            j = 7
            for lables in (reasons):
                count = 0
                for label in lables:
                    count += all_dict["label"][label] if label in all_dict["label"] else 0
                j += 1
                ws.write(i + 1, j, "%.2f%%" % (round(float(count)/reject_count, 4) * 100 if reject_count != 0 else 0))

            w.save('t.xls')
            response = StreamingHttpResponse(FileWrapper(open('t.xls'), 8192), content_type='application/vnd.ms-excel')
            response['Content-Length'] = os.path.getsize("t.xls")
            response['Content-Disposition'] = 'attachment; filename=%s-%s.xls' % (stime, etime)
            return response
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : str(e)}))
    return HttpResponse(json.dumps({"error" : "get only"}))

def strbin(s):
    return ''.join(format(ord(i),'0>8b') for i in s)

def get_call(request):
    if request.method == 'GET':
        uid = request.GET.get("uid")
        try:
            #print '{"uid":%s}' % uid
            params = '{"uid":%s}' % uid
            #bin_params = bitarray.bitarray()
            #bin_params = strbin(params)
            call_command('gearman_submit_job', 'get_call', params.encode("utf-8"))
            #result = gearman_client.submit_job("get_call", params, background=True)
        except Exception, e:
            print "excp", e
            traceback.print_exc()
            return HttpResponse(json.dumps({"error" : u"load failed"}))
        return HttpResponse(json.dumps({"error" : "ok"}))
    return HttpResponse(json.dumps({"error" : "get only"}))
