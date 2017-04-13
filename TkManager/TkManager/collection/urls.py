# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from TkManager.collection.general_views import *
from TkManager.collection.data_views import *

urlpatterns = patterns('TkManager.collection',
    ## page view
    (r'^$',  RedirectView.as_view(url='/collection/mine')),
    (r'^all$', login_required(get_all_collection_view)),
    (r'^mine$', login_required(get_mine_collection_view)),

    ##modal
    (r'^info/(?P<apply_id>\d+)$', login_required(get_collection_info)),     # 催收页面
    (r'^info/view/(?P<apply_id>\d+)$', login_required(get_collection_info_view)), # 催收展示页面改用系统页面
    (r'^modal/dispatch/(?P<apply_id>\d+)$', login_required(dispatch_collection_info_view)), # 催收展示页面改用系统页面
    (r'^modal/message/(?P<apply_id>\d+)$', login_required(get_message_info)), # 短信发送modal
    (r'^modal/reduction/(?P<apply_id>\d+)$', login_required(get_reduction_info)), #减免的modal

    ## review action
    (r'^action/add/', add_review),
    #(r'^action/cancel', cancel_review),
    (r'^action/change', change_reviewer),
    (r'^action/finish', finish_review),
    (r'^action/do_repay_loan', login_required(do_collection_action)),

    (r'^action/sendmessage', send_message),
    (r'^action/reduction', do_reduction),
    (r'^action/add_collection_record', add_record),
    (r'^action/fileupload', upload_file),

    ##
    (r'^download_collection_table_1$', download_collection_table_1),
    #(r'^download_collection_table_2$', download_collection_table_2),

    ## get json data for DataTables
    (r'^my_collection_json$', login_required(get_my_collection_datatable)),
    (r'^all_collection_json$', login_required(get_all_collection_datatable)),

    (r'^get_collection_record_json$', login_required(get_collection_record_data)),
)
