# -*- coding: utf-8 -*-
import json
from django.db.models import Q
from TkManager.order.apply_models import Apply
from TkManager.order.models import Chsi, CheckStatus, Profile
from TkManager.review.models import Review, Employee
from TkManager.util.tkdate import *
from TkManager.util.data_provider import DataProvider
from TkManager.common.tk_log_client import TkLog
from datetime import timedelta
from TkManager.review import mongo_client
import traceback


class ReviewDataProvider(DataProvider):
    def object_filter(self, request):
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

        #print timerange, etime, stime
        time_filter = request.GET.get("time_filter")
        query_time = None
        if time_filter == "review":
            query_time = Q(finish_time__lt = etime, finish_time__gt = stime)
        else:
            query_time = Q(create_at__lt = etime, create_at__gt = stime)

        query_status = None
        status =request.GET.get("status")
        if status == "waiting" :
            query_status = Q(status = '0') | Q(status = 'i') | Q(status = 'w')
        elif status == "passed" :
            query_status = Q(status = 'y')
        elif status == "rejected" :
            query_status = Q(status = 'n') | Q(status = 'b')
        elif status == "mrejected" :
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
            query_type = Q(type = 's') | Q(type = '0')
        elif review_type == 'all':
            query_type = Q(type__lte ='9', type__gte = '0') | Q(type = 's') | Q(type='e')

        #print query_time
        apply_list = Apply.objects.filter(query_time & query_status & query_type)

        return apply_list

    def get_columns(self):
        return [u"申请ID", u"用户ID", u"用户名", u"订单类型", u"提交时间", u"完成时间", u"审批人", u"金额", u"订单状态"]

    def get_query(self):
        return ["create_by__id__iexact", "create_by__name__icontains", "create_by__phone_no__iexact", "create_by__id_no__iexact"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            status_url = ""
            user_name = ""
            if apply.status == '0' or apply.status == "i" or apply.status == 'w':   #等待审批
                if apply.type == '0' and apply.status == 'e':
                    status_url = u"<a class='view_review label label-warning' name='%d' href='#'>基本信息快照</a>" %(apply.id)
                elif apply.type == '0': #基本额度
                    status_url = u"<a class='view_review' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                elif apply.type == 's': #二次提现
                    status_url = u"<a class='view_second' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                else: #额度提升
                    status_url = u"<a class='view_promote' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                if apply.status == 'w': #基本信息审
                    status_url = u"<a class='view_review' name='%d' href='#'>等待数据</a>" % (apply.id)
                user_name = user.name
            else:
                user_name = user.name
                if apply.type == '0' and apply.status in ['r', 'e', 'b']:
                    try:
                        table = mongo_client['snapshot']['basic_apply']
                        user_data = table.find_one({"apply_info.id": apply.id},
                                                   {"user_info.name": 1, "user_info.channel": 1})
                        if user_data:
                            if user_data['user_info']:
                                user_name = user_data['user_info']['name']
                    except:
                        traceback.print_exc()
                        print "mongo error"
                        TkLog().error("mongo error:%s" % traceback.format_exc())
                        user_name = user.name
                    if apply.status == 'e':
                        status_url = u"<a class='view_review label label-warning' name='%d' href='#'>基本信息快照</a>" %(apply.id)
                    elif apply.status == 'r':
                        status_url = u"<a class='view_review label label-warning' name='%d' href='#'>返回修改快照</a>" %(apply.id)
                    else:
                        status_url = u"<a class='view_review' name='%d' href='#'>机器拒绝</a>" %(apply.id)
                elif apply.type == '0': #基本信息审
                    status_url = u"<a class='view_review' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                elif apply.type == 's': #二次提现
                    status_url = u"<a class='view_second' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                else:   # 额度提升审批
                    status_url = u"<a class='view_promote' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
            profile = Profile.objects.filter(owner=user)
            check = CheckStatus.objects.filter(owner=user)
            review = Review.objects.filter(order = apply).order_by("-id")
            data = [apply.id,
                    user.id,
                    user_name,
                    apply.get_type_display(),
                    apply.create_at.strftime("%Y-%m-%d %H:%M:%S") if apply.create_at else "",
                    apply.finish_time.strftime("%Y-%m-%d %H:%M:%S") if apply.finish_time else "",
                    review[0].reviewer.username if len(review) > 0 else "",
                    "%d/%d" % (check[0].credit_limit/100 if len(check) == 1 else 0, profile[0].expect_amount if len(profile) == 1 and profile[0].expect_amount else 0),
                    status_url]
                    #u"<a class='review_manual' name='%d' href='#'>审批</a> <a class='review_auto' name=%d href='#'>自动</a>"  % (apply.id, apply.id)
                    #       if apply.status == '0' else apply.get_status_display()]
            data_set.append(data)
        return data_set

class MyReviewDataProvider(DataProvider):
    def object_filter(self, request):
        stime = get_tomorrow() - timedelta(14)
        etime = get_tomorrow()
        query_time = Q(create_at__lt = etime, create_at__gt = stime)

        query_status = None
        status =request.GET.get("status")
        if status == "waiting" :
            query_status = Q(status = '0') | Q(status = 'i') | Q(status = 'w')
        elif status == "passed" :
            query_status = Q(status = 'y')
        elif status == "rejected" :
            query_status = Q(status = 'n') | Q(status = 'b')
        elif status == "back" :
            query_status = Q(status = 'r')
        else :
            query_status = Q()

        query_owner = None

        query_type = Q(type__lte ='9', type__gte = '0') | Q(type = 's')

        owner =request.GET.get("owner")
        if owner == "mine" :
            owner_id =request.GET.get("owner_id")
            query_owner = Q(review__reviewer__user__id = owner_id)
        else:
            query_owner = Q()

        apply_list = Apply.objects.filter(query_time & query_status & query_type & query_owner).distinct()
        #print apply_list
        return apply_list

    def get_columns(self):
        return [u"申请ID", u"用户ID", u"用户名", u"订单类型", u"渠道来源", u"提交时间", u"完成时间", u"审批人", u"订单状态"]

    def get_query(self):
        return ["create_by__id__iexact", "create_by__name__icontains", "create_by__phone_no__iexact", "create_by__id_no__iexact"]

    def fill_data(self, query_set):
        data_set = []
        user_name = ''
        user_channel = ''
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            user = apply.create_by
            status_url = ""
            if apply.status == '0' or apply.status == "i":   #等待审批
                if apply.type == '0': #基本信息审
                    status_url = u"<a class='review_manual' name='%d' href='#'>基本信息审批</a>" % (apply.id)
                elif apply.type == 's': #二次提现
                    status_url = u"<a class='review_loan' name='%d' href='#'>二次提现申请</a>" % (apply.id)
                else:   # 额度提升审批
                    status_url = u"<a class='review_promote' name='%d' href='#'>额度提升审批</a>" % (apply.id)
                    # status_url = u"<a class='review_manual' name='%d' href='#'>等待数据</a>" % (apply.id)
                    #status_url = u"<a class='review_promote_manual' name='%d' href='#'>审批</a> <a class='review_auto' name=%d href='#'>自动</a>" % (apply.id, apply.id)
                user_name = user.name
                user_channel = user.channel
            else:  #已经完成审批，点击查看状态
                user_name = user.name
                user_channel = user.channel
                if apply.type == '0' and apply.status in ['r', 'e', 'b']:
                    try:
                        table = mongo_client['snapshot']['basic_apply']
                        user_data = table.find_one({"apply_info.id": apply.id},
                                                   {"user_info.name": 1, "user_info.channel": 1})
                        if user_data:
                            if 'user_info' in user_data:
                                user_name = user_data['user_info']['name']
                                user_channel = user_data['user_info']['channel']
                    except:
                        traceback.print_exc()
                        print "mongo error"
                        TkLog().error("mongo error:%s" % traceback.format_exc())
                        user_name = user.name
                        user_channel = user.channel
                    if apply.status == 'e':
                        status_url = u"<a class='view_review label label-warning' name='%d' href='#'>基本信息快照</a>" %(apply.id)
                    elif apply.status == 'r':
                        status_url = u"<a class='view_review label label-warning' name='%d' href='#'>返回修改快照</a>" %(apply.id)
                    else:
                        status_url = u"<a class='view_review' name='%d' href='#'>机器拒绝</a>" %(apply.id)
                elif apply.type == '0': #基本信息审
                    status_url = u"<a class='view_review' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                elif apply.type == 's': #二次提现
                    status_url = u"<a class='view_second' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
                else:   # 额度提升审批
                    status_url = u"<a class='view_promote' name='%d' href='#'>%s</a>" %(apply.id, apply.get_status_display())
            # chsi = Chsi.objects.filter(user=user)
            review = Review.objects.filter(order=apply).order_by("-id")
            if apply.status != 'w':
                data = [apply.id,
                    user.id,
                    user_name,
                    #chsi[0].school if len(chsi) > 0 else "",
                    apply.get_type_display(),
                    user_channel,
                    apply.create_at.strftime("%Y-%m-%d %H:%M:%S") if apply.create_at else "",
                    apply.finish_time.strftime("%Y-%m-%d %H:%M:%S") if apply.finish_time else "",
                    #apply.reviewer
                    review[0].reviewer.username if len(review) > 0 else "",
                    status_url]
                    #u"<a class='review_manual' name='%d' href='#'>审批</a> <a class='review_auto' name=%d href='#'>自动</a>"  % (apply.id, apply.id)
                    #       if apply.status == '0' else apply.get_status_display()]
                data_set.append(data)
        return data_set

def get_all_review_datatable(request):
    return ReviewDataProvider().get_datatable(request)

def get_my_review_datatable(request):
    return MyReviewDataProvider().get_datatable(request)

def get_all_review_columns():
    return ReviewDataProvider().get_columns()

def get_my_review_columns():
    return MyReviewDataProvider().get_columns()
