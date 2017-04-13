# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from TkManager.custom.general_views import *
from TkManager.custom.data_views import get_feedback_datatable, get_report_datatable

urlpatterns = patterns('TkManager.operation',
   ## page view
   (r'^$',  RedirectView.as_view(url='/custom/user_view')),
   (r'^user_view$', login_required(get_user_view)),
   (r'^record$', login_required(get_record_view)),
   (r'^feedback$', login_required(get_feedback_view)),
   (r'^query/$', login_required(get_query_view_result)),
   (r'^query_detail/$', login_required(get_query_detail)),
   (r'^query_user/$', login_required(get_query_detail_view)),
   (r'^send_info/$', login_required(get_info_detail)),
   (r'^test/$', test),
   (r'^addremark/$', addremark),
   (r'^send_message/$', send_message),

   #get json data
   (r'^get_feedback_json$', login_required(get_feedback_datatable)),
   (r'^get_record_json$', login_required(get_report_datatable)),
   (r'^get_loan_data$', login_required(get_loan_data)),
   ('gen_apply_repay_type',gen_apply_repay_type),
)
