# -*- coding: utf-8 -*-
import json
from django.db.models import Q,F
from TkManager.order.apply_models import Apply,ExtraApply
from TkManager.order.models import Chsi,Profile,Strategy2,User
from TkManager.review.models import Review, Employee
from TkManager.collection.models import *
from TkManager.util.data_provider import DataProvider
from TkManager.common.tk_log_client import TkLog
from TkManager.util.tkdate import *
from datetime import timedelta,datetime
from numpy import pv
global_time_range = [[], [0,5],[5,15],[15,30],[30,60],[60,999999]]
global_show_th = {
     1:["信托","信托"],
     6:["信托","信托"],
     5:["信托","信托"],
     12:["信托","信托"],
     10:["0.00%","0.30%"],
     11:["0.00%","0.30%"],
     15:["1.67%","4.00%"],
}
def get_card_id_from_apply(apply):
    return apply.create_by.id_no

class PayLoanDataProvider(DataProvider):
    def object_filter(self, request):
        repay_list = []
        query_type =request.GET.get("query_type")
        query_str=request.GET.get("query_str")
        if query_type != 'none':
            if query_type == 'id':
                user_list = User.objects.filter(Q(id_no=query_str))
            if query_type == 'name':
                user_list = User.objects.filter(Q(name__icontains=query_str))
            if query_type == 'phone':
                user_list = User.objects.filter(Q(phone_no=query_str))
            if query_type == 'phone' or query_type == 'name' or query_type == 'id':
                for user in user_list:
                    for repay in  RepaymentInfo.objects.filter(user= user):
                        repay_list.append(repay)
            if query_type == 'order':
                for repay in RepaymentInfo.objects.filter(order_number = query_str):
                    repay_list.append(repay)
       #     print type(repay_list)

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
        elif timerange == "all" :
            stime = get_tomorrow() - timedelta(1000)
            etime = get_tomorrow() + timedelta(1000)
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")
        query_time = Q(create_at__lt = etime, create_at__gt = stime)
        status =request.GET.get("status")
        s = '0'
        if status == "waiting" :
            s = '0'
        elif status == "prepayed" :
            s = '1'
        elif status == "success" :
            s = '2'
        elif status == "failed" :
            s = '3'
        elif status == "mifan_failed" :
            s = '4'
        else:
            s = 'all'
       #如果是米饭status 确认到款请求的 status 默认就是1
        #if request.GET.get("mifan") == "mifan_status":
        #    s = '1'
       #如果是米饭请求的 status 默认就是0
        if request.GET.get("mifan") == "mifan":
            s = '0'
        #添加上面查询条件对应的repayment约束
        query_status = None
        #if s == 'all':
        #    query_status = Q(type = 'l') & ~Q(repayment_id = None) &   Q(order_number_in = repay_list)
        #else:
        #    query_status = Q(type = 'l', status = s) & ~Q(repayment_id = None)  & Q(order_number_in = repay_list)
        if s == 'all':
            if request.GET.get("mifan") == "mifan" or request.GET.get("mifan") == "mifan_status":
                query_status = Q(type = 'l', status__in =  ['1','4'] ) & ~Q(repayment_id = None)
            else:
                query_status = Q(type = 'l') & ~Q(repayment_id = None)
        else:
            query_status = Q(type = 'l', status = s) & ~Q(repayment_id = None)

        channel = request.GET.get("channel")
        c = None
        if channel == "mifan" :
            c = 2
        elif channel == "xintuo" :
            c = 1
        else :
            TkLog().error("unknown channel %s" % channel)
        query_channel = Q(repayment__capital_channel_id = c)
        query_strategy_type =request.GET.get("query_strategy_type")
        query_strategy = Q(repayment__strategy_id = int(query_strategy_type))
        if query_strategy_type == '0':
            apply_list_filter = Apply.objects.filter(query_time & query_status & query_channel ).order_by("-id")
        else:
            apply_list_filter = Apply.objects.filter(query_time & query_status & query_channel &query_strategy).order_by("-id")
        try:
            apply_list_query = Apply.objects.filter(repayment__in = repay_list)
        except Exception,e:
            TkLog().error("access mysql occur a exception:  except:  %s" % str(e))
        if query_type == 'none':
            return apply_list_query | apply_list_filter
        else:
            return apply_list_query & apply_list_filter


    def get_columns(self):
        return [u"申请id", u"用户id", u"订单号", u"用户",u"身份证", u"资金渠道", u"借款金额", u"到账金额", u"借贷方式", u"申请时间", u"起息日", u"状态", u"米饭打款状态",u"银行"]

    def get_query(self):
        return ["create_by__id__iexact", "create_by__name__icontains", "create_by__phone_no__iexact", "create_by__id_no__iexact", "repayment__order_number"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            repay = RepaymentInfo.objects.get(pk = result["repayment_id"])
            try:
                #ea = ExtraApply.objects.get(apply_id= 3501)
                ea = ExtraApply.objects.get(apply_id=apply.id)
                mifan = ea.message_2
            except ExtraApply.DoesNotExist:
                mifan = ""
                #print mifan
                #print "excp", e
                #traceback.print_exc()
            data = {"id":apply.id,
                    "uid":repay.user.id,
                    "order_number":apply.repayment.order_number,
                    "name":repay.user.name,
                    "card_id":get_card_id_from_apply(apply),
                    "channel":repay.get_capital_channel_id_display(),
                    "amount":repay.apply_amount/100.0,
                    "repay_amount":repay.exact_amount/100.0,
                    "strategy":repay.get_strategy_id_display(),
                    #repay.bank_card.get_bank_type_display(),
                    "apply_time":repay.apply_time.strftime("%Y-%m-%d %H:%M:%S") if repay.apply_time else "",
                    "getpay_time":repay.first_repay_day.strftime("%Y-%m-%d %H:%M:%S") if repay.first_repay_day else "",
                    "status":apply.get_status_display(),
                    "mifan_status":mifan,
                    "bank_type":repay.bank_card.get_bank_type_display(),
                    "DT_RowId":apply.id}
            data_set.append(data)
        return data_set

class RepayLoanDataProvider(DataProvider):
    def object_filter(self, request):
        channel = request.GET.get("channel")
        c = None
        if channel == "mifan" :
            c = 2
        elif channel == "xintuo" :
            c = 1
        else :
            TkLog().error("unknown channel %s" % channel)
        query_channel = Q(repayment__capital_channel_id = c)

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
        elif timerange == "all" :
            stime = get_today() - timedelta(1000)
            etime = get_today() + timedelta(5000)
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")
        query_time = Q(create_at__lt = etime, create_at__gt = stime)

        #status =request.GET.get("status")
        #s = '0'
        #if status == "waiting" :
        #    s = '0'
        #elif status == "prepayed" :
        #    s = '1'
        #elif status == "success" :
        #    s = '2'
        #elif status == "failed" :
        #    s = '3'
        #else:
        #    s = 'all'
        #if s == 'all':
        #    apply_list = Apply.objects.filter(Q(create_at__lt = etime, create_at__gt = stime, type = 'p'))
        #else:
        #    apply_list = Apply.objects.filter(Q(create_at__lt = etime, create_at__gt = stime, type = 'p', status = s))
        #repay_list = RepaymentInfo.objects.filter(Q(apply__in = apply_list))

        query_status = None
        status =request.GET.get("status")
        if status == "wait_repay" :
            query_status = Q(status = '0')
        elif status == "repay_success" :
            query_status = Q(status = '9')
        elif status == "repay_failed" :
            query_status = Q(status = 'c')
        elif status == "part_success" :
            query_status = Q(status = 'd')
        elif status == "all" :
            query_status = Q()
        else :
            query_status = Q()

        if request.GET.get("query_status_type") == "batch_repay" and status == "all" :
            query_status = Q(status = '0') | Q(status = 'd') | Q(status = 'c')
        querytype = Q(type = 'p')

        repay_list = []
        query_type =request.GET.get("query_type")
        query_str=request.GET.get("query_str")
        if query_type != 'none':
            if query_type == 'id':
                user_list = User.objects.filter(Q(id_no=query_str))
            if query_type == 'name':
                user_list = User.objects.filter(Q(name__icontains=query_str))
            if query_type == 'phone':
                user_list = User.objects.filter(Q(phone_no=query_str))
            if query_type == 'phone' or query_type == 'name' or query_type == 'id':
                #print user_list
                for user in user_list:
                    #print user
                    for repay in  RepaymentInfo.objects.filter(user= user):
                        repay_list.append(repay)
            if query_type == 'order':
                for repay in RepaymentInfo.objects.filter(order_number = query_str):
                    repay_list.append(repay)

        query_strategy_type =request.GET.get("query_strategy_type")
        query_strategy = Q(repayment__strategy_id = int(query_strategy_type))
        if query_strategy_type == '0':
             apply_list_filter = Apply.objects.filter(query_time & query_status & querytype & query_channel)
             #print 'query sql: ' + str(apply_list_filter.query)
        else:
             #print 'query sql: ' + str(apply_list_filter.query)
             apply_list_filter = Apply.objects.filter(query_time & query_status & querytype & query_strategy & query_channel)
        #print apply_list_filter.count()
        apply_list_query = Apply.objects.filter(repayment__in = repay_list)
        if query_type == 'none':
            return apply_list_query | apply_list_filter
        else:
            return apply_list_query & apply_list_filter


    def get_columns(self):
        return [u"申请ID", u"用户ID", u"订单号", u"用户名字",u"身份证", u"借款金额", u"到账金额", u"借贷方式", "银行名称", u"申请时间", u"起息日", u"状态",u"当前期数"]

    def get_query(self):
        return ["create_by__id__iexact", "create_by__name__icontains", "create_by__phone_no__iexact", "create_by__id_no__iexact", "repayment__order_number"]

    def fill_data(self, query_set):
        data_set = []
        for result in query_set.values():
            apply = Apply.objects.get(pk = result["id"])
            repay = RepaymentInfo.objects.get(pk = result["repayment_id"])
            data = {"id":apply.id,
                    "uid":repay.user.id,
                    "order_number":apply.repayment.order_number,
                    "name":repay.user.name,
                    "card_id":get_card_id_from_apply(apply),
                    "amount":repay.apply_amount/100.0,
                    "repay_amount":repay.exact_amount/100.0,
                    "strategy":repay.get_strategy_id_display(),
                    "bank_data":repay.bank_card.get_bank_type_display(),
                    "apply_time":repay.apply_time.strftime("%Y-%m-%d %H:%M:%S") if repay.apply_time else "",
                    "getpay_time":repay.first_repay_day.strftime("%Y-%m-%d %H:%M:%S") if repay.first_repay_day else "",
                    "status":apply.get_status_display(),
                    "current_peroids":apply.money + 1,
                    "DT_RowId":apply.id}
            data_set.append(data)
        return data_set

def get_over_due_days(install):
    if install.repay_status == 2:
        today  = datetime.now()
        return (today - install.should_repay_time).days
    elif install.repay_status == 8:
        return (install.real_repay_time- install.should_repay_time).days
    else:
        return 0


def get_real_repay_amount(repay):
    i = 0
    installs = InstallmentDetailInfo.objects.filter(Q(repayment__id = repay.id))
    for item in installs:
        if item.should_repay_time > datetime.now():
           continue
        else:
           if item.repay_status != 2:
              i = i+item.real_repay_amount
    return i/100.0

def get_over_due_amount(repay):
    i = 0
    installs = InstallmentDetailInfo.objects.filter(Q(repayment__id = repay.id))
    for item in installs:
        if item.should_repay_time > datetime.now():
           continue
        else:
           if item.repay_status == 2 or  item.repay_status == 8:
              i = i+(item.should_repay_amount -item.real_repay_amount)
    return i/100.0

def get_over_due_peroids(repay):
    i = 0
    installs = InstallmentDetailInfo.objects.filter(Q(repayment__id = repay.id))
    for item in installs:
        if item.should_repay_time > datetime.now():
           continue
        else:
           if item.repay_status == 2 or  item.repay_status == 8:
              i = i+1
    return i

def get_over_due_peroids_rate(repay):
    i = 0
    ii = 0
    installs = InstallmentDetailInfo.objects.filter(Q(repayment__id = repay.id))
    for item in installs:
        if item.should_repay_time > datetime.now():
           continue
        else:
           ii = ii+1
           if item.repay_status == 2 or  item.repay_status == 8:
              i = i+1
    return "%d/%d" % (i,ii)

def get_real_repay_peroids(repay):
    i = 0
    installs = InstallmentDetailInfo.objects.filter(Q(repayment__id = repay.id))
    for item in installs:
        if item.should_repay_time > datetime.now():
           continue
        else:
           if item.repay_status == 2 or  item.repay_status == 8:
              i = i+1
    return i

def get_periods_from_repayment(repay):
    if Strategy2.objects.get(strategy_id=repay.strategy_id).installment_days in (21,28):
        return 1
    else:
        return  Strategy2.objects.get(strategy_id=repay.strategy_id).installment_count

def get_numbers_from_strategy(id):
    return Strategy2.objects.get(strategy_id=id).installment_days

def get_corpus_from_repayment(repay):
    if Strategy2.objects.get(strategy_id=repay.strategy_id).installment_days in (21,28):
        return '%.2f' % ((repay.repay_amount - 200) / ( (1 + 0.00034)**get_numbers_from_strategy(repay.strategy_id) ) /100.0)
    else:
        peroids = Strategy2.objects.get(strategy_id=repay.strategy_id).installment_count
        return  '%.2f' % ( pv( (1.13 ** (1/12.0) -1), peroids,-(repay.repay_amount - 200 * peroids )/3)/100.0 )

def get_taikang_repayment(repay):
    if Strategy2.objects.get(strategy_id=repay.strategy_id).installment_days in (21,28):
        return '%.2f' % ((repay.repay_amount - 200 )/ ( (1 + 0.00034)**get_numbers_from_strategy(repay.strategy_id) ) /100.0 - (repay.apply_amount/100.0) )
    else:
        peroids = Strategy2.objects.get(strategy_id=repay.strategy_id).installment_count
        return  '%.2f' % ( pv( (1.13 ** (1/12.0) -1), peroids,-(repay.repay_amount - 200 * peroids )/3)/100.0 - (repay.apply_amount/100.0) )

def get_should_be_repayment(repay):
    if Strategy2.objects.get(strategy_id=repay.strategy_id).installment_days in (21,28):
        return '%.2f' % ((repay.repay_amount - 200 )/ 100.0)
    else:
        peroids = Strategy2.objects.get(strategy_id=repay.strategy_id).installment_count
        return  '%.2f' % ((repay.repay_amount - 200 * peroids )/3/100.0)

class FundDetailDataProvider(DataProvider):
    def object_filter(self, request):
        custom_type = request.GET.get("custom_type")
        if custom_type == 'all':
            query_custom_type = Q()
        else:
            query_custom_type = Q(user__profile__job = custom_type)
        channel = request.GET.get("channel")
        c = None
        if channel == "mifan" :
            c = 2
            query_channel = Q(capital_channel_id = c)
        elif channel == "xintuo" :
            c = 1
            query_channel = Q(capital_channel_id = c)
        else :
            query_channel = Q()


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
        elif timerange == "all" :
            stime = get_tomorrow() - timedelta(1000)
            etime = get_tomorrow() + timedelta(1000)
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")
        query_time = Q(first_repay_day__lt = etime, first_repay_day__gt = stime)

        repayments = RepaymentInfo.objects.filter(Q(repay_status__in = [0,1,2,3,5]) & query_time & query_channel & query_custom_type).order_by("id")
        #repayments = RepaymentInfo.objects.get(order_number = 370421206753848686)
        #print repayments.user.profile
        #print repayments.user.profile.job

        return repayments
    def get_columns(self):
        return [u"渠道", u"合同",u"姓名",u"类型",u"身份证", u"金额", u"本金", u"期数",u"利率",u"服务费" , u"应还",u"泰康",u"放款日期"]
    def fill_data(self, query_set):
        data_set = []
        for repay in query_set:
            print "***" ,repay.strategy_id
            data = [repay.get_capital_channel_id_display(),
                    repay.order_number,
                    repay.user.name,
                    Profile.objects.get(owner=repay.user).get_job_display(),
                    repay.user.id_no,
                    repay.apply_amount/100.0,
                    get_corpus_from_repayment(repay),
                    repay.get_strategy_id_display(),
                    global_show_th[repay.strategy_id][0],
                    global_show_th[repay.strategy_id][1],
                    get_should_be_repayment(repay),
                    get_taikang_repayment(repay),
                    repay.first_repay_day.strftime("%Y-%m-%d") ]
            data_set.append(data)
        return data_set

class OverDueProvider(DataProvider):
    def object_filter(self, request):
        custom_type = request.GET.get("custom_type")
        if custom_type == 'all':
            query_custom_type = Q()
        else:
            query_custom_type = Q(user__profile__job = custom_type)
        channel = request.GET.get("channel")
        c = None
        if channel == "mifan" :
            c = 2
            query_channel = Q(capital_channel_id = c)
        elif channel == "xintuo" :
            c = 1
            query_channel = Q(capital_channel_id = c)
        else :
            query_channel = Q()


        over_due_type = request.GET.get("over_due_type")
        if over_due_type == 'all':
            query_base= Q(repay_status__in = [2,8])
        elif over_due_type == 'already':
            query_base= Q(repay_status = 8)
        else:
            query_base= Q(repay_status = 2)


        over_due_time_range = request.GET.get("over_due_time_range")
        #if over_due_time_range == time_range
        #query_time_range= Q()
        #repayments = RepaymentInfo.objects.filter(query_base & query_channel & query_custom_type & query_time_range).order_by("id")
        repayments = RepaymentInfo.objects.filter(query_base & query_channel & query_custom_type ).order_by("id")
        return repayments

    def get_columns(self):
        return [u"期数",u"订单号",u"渠道", u"类型", u"借款金额", u"应还日期", u"应还笔数",  u"应还金额",u"实还笔数",u"实还金额",u"逾期笔数",u"逾期金额",u"逾期率"]

    def fill_data(self, query_set):
        data_set = []
        for repay in query_set:
            data = [repay.get_strategy_id_display(),
                    repay.order_number,
                    repay.get_capital_channel_id_display(),
                    Profile.objects.get(owner=repay.user).get_job_display(),
                    repay.apply_amount/100.0,
                    str(repay.first_repay_day),
                    get_periods_from_repayment(repay),
                    repay.repay_amount/100.0,
                    get_real_repay_peroids(repay),
                    get_real_repay_amount(repay),
                    get_over_due_peroids(repay),
                    get_over_due_amount(repay),
                    get_over_due_peroids_rate(repay)]
            data_set.append(data)
        return data_set

class OverDueDetailProvider(DataProvider):
    def object_filter(self, request):
        #repayments = RepaymentInfo.objects.filter(query_base ).order_by("id")

        over_due_type = request.GET.get("over_due_type")
        #print over_due_type

        if over_due_type == 'yet_already':
            query_base= Q(repay_status__in = [2,8])
        elif over_due_type == 'already':
            query_base= Q(repay_status = 8)
        elif over_due_type == 'yet':
            query_base= Q(repay_status = 2)
        elif over_due_type == 'normal':
            query_base= Q(repay_status = 3)
        else:
            query_base= Q()


        timerange =request.GET.get("time")
        if timerange == "all":
            query_time = Q()
        else:
            stime = request.GET.get("stime")
            etime = request.GET.get("etime")
            s = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
            e = datetime.strptime(etime,'%Y-%m-%d %H:%M:%S')
            query_time =Q(should_repay_time__lt = e ) &  Q(should_repay_time__gte = s )


        custom_type = request.GET.get("custom_type")
        if custom_type == 'all':
            query_custom_type = Q()
        else:
            query_custom_type = Q(repayment__user__profile__job = custom_type)
        channel = request.GET.get("channel")
        c = None
        if channel == "mifan" :
            c = 2
            query_channel = Q(repayment__capital_channel_id = c)
        elif channel == "xintuo" :
            c = 1
            query_channel = Q(repayment__capital_channel_id = c)
        else :
            query_channel = Q()
        query_repay_status =  Q(repayment__repay_status__in = [1,2,3,8])
        Installs = InstallmentDetailInfo.objects.filter( query_channel & query_custom_type & query_time & query_base & query_repay_status)
        #print Installs.query, Installs.count()

        over_due_time_range= request.GET.get("over_due_time_range")
        if over_due_time_range == 'all':
            #Installs = InstallmentDetailInfo.objects.filter(Q(should_repay_amount__gt= F('real_repay_amount'))).order_by("id")
            return Installs
        else:
            return_set = []
            for install in Installs:
                i = get_over_due_days(install)
                #print "hah", i
                #print global_time_range[int(over_due_time_range)][0]
                #print global_time_range[int(over_due_time_range)][0]
                if i > global_time_range[int(over_due_time_range)][0] and i < global_time_range[int(over_due_time_range)][1]:
                    return_set.append(install.id)
                else:
                    pass
            return InstallmentDetailInfo.objects.filter(id__in = return_set)

    def get_columns(self):
        return [u"渠道",u"订单号",u"姓名",u"类型",u"身份证", u"借款金额", u"期数",u"还款期数",u"应还日期", u"每期应还",  u"逾期天数",u"滞纳金", u"实还金额",u"逾期状态",u"实还日期"]
        #return [u"渠道", u"合同号",u"姓名",u"类型",u"身份证", u"借款金额", u"期数",u"还款期数",u"应还日期", u"每期应还",  u"逾期天数",u"滞纳金", u"实还金额",u"逾期状态"]

    def fill_data(self, query_set):
        data_set = []
        for install in query_set:
            repay = install.repayment
            data = [repay.get_capital_channel_id_display(),
                    repay.order_number,
                    repay.user.name,
                    Profile.objects.get(owner=repay.user).get_job_display(),
                    repay.user.id_no,
                    repay.apply_amount/100.0,
                    get_periods_from_repayment(repay),
                    install.installment_number,
                    str(install.should_repay_time),
                    install.should_repay_amount/100.0,
                    get_over_due_days(install),
                    install.repay_overdue/100.0,
                    install.real_repay_amount/100.0,
                    install.get_repay_status_display(),
                    str(install.real_repay_time)]
            data_set.append(data)
        return data_set

class OverDueDetail_sum_Provider(OverDueDetailProvider):
    def get_columns(self):
        return [u"时间段",u"逾期笔数",u"正常笔数",u"总笔数",u"逾期金额",u"正常金额",u"总金额",u"逾期比率"]


def get_pay_loan_datatable(request):
    return PayLoanDataProvider().get_datatable(request)

def get_repay_loan_datatable(request):
    return RepayLoanDataProvider().get_datatable(request)

def get_pay_loan_columns():
    return PayLoanDataProvider().get_columns()

def get_repay_loan_columns():
    return RepayLoanDataProvider().get_columns()

def get_table1_datatable(request):
    return FundDetailDataProvider().get_datatable(request)

def get_table1_columns():
    return FundDetailDataProvider().get_columns()

def get_table2_datatable(request):
    return OverDueProvider().get_datatable(request)

def get_table2_columns():
    return OverDueProvider().get_columns()

def get_table3_datatable(request):
    return OverDueDetailProvider().get_datatable(request)

def get_table3_columns():
    return OverDueDetailProvider().get_columns()

def get_table3_result_datatable(request):
    query_set = OverDueDetail_sum_Provider().object_filter(request)
    #print query_set.count()
    timerange =request.GET.get("time")
    if timerange == "all":
        query_time = "所有时间段"
    else:
        stime = request.GET.get("stime")[:10]
	etime = request.GET.get("etime")[:10]
        query_time  = "form:" + stime + "to" + etime
    normal = 0
    normal_amount = 0
    over_due = 0
    over_due_amount = 0
    installs_sum = 0
    installs_sum_amount  = 0
    for install in query_set:
        installs_sum = installs_sum + 1
        installs_sum_amount = installs_sum_amount + install.should_repay_amount
        if install.repay_status == 2 or install.repay_status == 8:
            over_due_amount = over_due_amount + install.should_repay_amount
            over_due = over_due + 1
        else:
            normal = normal + 1
            normal_amount = normal_amount + install.should_repay_amount
    #[u"时间段",u"逾期笔数",u"正常笔数",u"总笔数",u"逾期金额",u"正常金额",u"总金额",u"逾期比率"]
    normal_amount = normal_amount/100.0
    over_due_amount = over_due_amount/100.0
    installs_sum_amount = installs_sum_amount/100.0
    if installs_sum_amount == 0.0:
        result = [query_time,  over_due,normal,installs_sum,over_due_amount,normal_amount,installs_sum_amount,0]
    else:
        result = [query_time,  over_due,normal,installs_sum,over_due_amount,normal_amount,installs_sum_amount,over_due_amount/installs_sum_amount]
    #result = {"qury_time":qury_time, "normal":normal, "normal_amount":normal_amount,"over_due":over_due,"over_due_amount":over_due_amount ,"install_sum":install_sum,"installs_sum_amount":installs_sum_amount}
    return result

def get_table3_result_columns():
    return OverDueDetail_sum_Provider().get_columns()
if __name__ == "__main__":
    print "test:"
