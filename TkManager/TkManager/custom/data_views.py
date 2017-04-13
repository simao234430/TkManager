# -*- coding: utf-8 -*-
'''
获取数据，填充数据
'''
import json
from django.db.models import Q

from TkManager.order.models import Feedback, Report, User
from TkManager.util.tkdate import *
from TkManager.util.data_provider import DataProvider
from TkManager.common.tk_log_client import TkLog
import time,datetime

class FeedbackDataProvider(DataProvider):
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

        feedback_list = Feedback.objects.filter(Q(sub_time__lt = etime, sub_time__gt = stime))
        return feedback_list

    def get_columns(self):
        return [u"用户", u"联系方式", u"反馈内容", u"提交时间"]

    def get_query(self):
            return ["contact__icontains"]

    def fill_data(self, query_set):
        data_set = []
        for feedback in query_set:
            data = [feedback.owner.name,
                    feedback.contact,
                    feedback.content,
                    feedback.sub_time.strftime("%Y-%m-%d %H:%M:%S") if feedback.sub_time else ""
                    ]
            data_set.append(data)
        return data_set

def get_feedback_columns():
    return FeedbackDataProvider().get_columns()


def get_feedback_datatable(request):
    return FeedbackDataProvider().get_datatable(request)

class ReportDataProvider(DataProvider):
    def object_filter(self, request):
        stime = int(time.mktime(datetime.datetime.strptime(str(get_today()), "%Y-%m-%d").timetuple()))
        etime = int(time.mktime(datetime.datetime.strptime(str(get_tomorrow()), "%Y-%m-%d").timetuple()))
        timerange =request.GET.get("time")
        if timerange == "today" :
            stime = int(time.mktime(datetime.datetime.strptime(str(get_today()), "%Y-%m-%d").timetuple()))
            etime = int(time.mktime(datetime.datetime.strptime(str(get_tomorrow()), "%Y-%m-%d").timetuple()))
        elif timerange == "twodays" :
            stime = int(time.mktime(datetime.datetime.strptime(str(get_yestoday()), "%Y-%m-%d").timetuple()))
            etime = int(time.mktime(datetime.datetime.strptime(str(get_tomorrow()), "%Y-%m-%d").timetuple()))
        elif timerange == "yestoday" :
            stime = int(time.mktime(datetime.datetime.strptime(str(get_yestoday()), "%Y-%m-%d").timetuple()))
            etime = int(time.mktime(datetime.datetime.strptime(str(get_today()), "%Y-%m-%d").timetuple()))
        elif timerange == "toweek" :
            stime = int(time.mktime(datetime.datetime.strptime(str(get_first_day_of_week()), "%Y-%m-%d").timetuple()))
            etime = int(time.mktime(datetime.datetime.strptime(str(get_tomorrow()), "%Y-%m-%d").timetuple()))
        elif timerange == "tomonth" :
            stime = int(time.mktime(datetime.datetime.strptime(str(get_first_day_of_month()), "%Y-%m-%d").timetuple()))
            etime = int(time.mktime(datetime.datetime.strptime(str(get_tomorrow()), "%Y-%m-%d").timetuple()))
        else:
            stime = int(time.mktime(datetime.datetime.strptime(str(get_today()), "%Y-%m-%d").timetuple()))
            etime = int(time.mktime(datetime.datetime.strptime(str(get_tomorrow()), "%Y-%m-%d").timetuple()))


        report_list = Report.objects.filter(Q(timestamp__lt = etime, timestamp__gt = stime, logid__startswith='c_'))
        return report_list
    def get_columns(self):
            return [u"用户", u"设备", u"版本号", u"操作记录", u"操作时间"]
    def get_query(self):
        return ["uin__icontains"]

    def fill_data(self, query_set):
        data_set = []
        for record in query_set:
            user = User.objects.get(id = record.uin)
            data = [user.name,
                    record.device,
                    record.client_version,
                    record.get_logid_display(),
                    time.strftime("%Y-%m-%d %H:%M:%S" ,time.localtime(record.timestamp)) if record.timestamp else ""
                    ]
            data_set.append(data)
        return data_set

def get_report_columns():
    return ReportDataProvider().get_columns()

def get_report_datatable(request):
    return ReportDataProvider().get_datatable(request)
