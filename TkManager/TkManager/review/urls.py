# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from TkManager.review.general_views import *
from TkManager.review.data_views import get_my_review_datatable, get_all_review_datatable

urlpatterns = patterns('TkManager.review',
   ## page view
   (r'^$',  RedirectView.as_view(url='/review/mine')),
   (r'^all$', login_required(get_all_review_view)),
   (r'^mine$', login_required(get_mine_review_view)),

   #modal
   (r'^info/(?P<apply_id>\d+)$', login_required(get_review_info_view)),   # 审批基本信息页面
   (r'^info/promote/(?P<apply_id>\d+)$', login_required(get_review_promote_info_view)), # 审批额度提升页面
   (r'^info/loan/(?P<apply_id>\d+)$', login_required(get_review_loan_info_view)),   # 审批二次提现
   (r'^info/view/(?P<apply_id>\d+)$', login_required(get_review_view)),   # 查看基本信息页面
   (r'^info/view/promote/(?P<apply_id>\d+)$', login_required(view_promote_info_view)),# 查看额度提升页面
   (r'^info/view/loan/(?P<apply_id>\d+)$', login_required(view_loan_info_view)),# 查看二次提现

   ## review action
   (r'^action/add', add_review),
   (r'^action/cancel', cancel_review),
   (r'^action/promotion', finish_promotion_review),
   (r'^action/loan', finish_loan_review),
   (r'^action/finish', finish_review),
   (r'^action/get_captcha', get_captcha),
   (r'^action/submit_captcha', submit_captcha),
   (r'^action/reset_review', reset_review),
   #(r'^action/start', login_required(start_review)),
   #(r'^action/end', login_required(end_review)),

   ## get json data for DataTables
   (r'^my_review_json$', login_required(get_my_review_datatable)),
   (r'^all_review_json$', login_required(get_all_review_datatable)),

   ## download file
   (r'^get_call$', get_call),
   (r'^download_addressbook$', download_addressbook),
   (r'^download_review_table_1$', download_review_table_1),
   (r'^download_review_table_2$', download_review_table_3),
   #(r'^download_record$', download_record),
)
