# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from TkManager.audit.general_views import *
from TkManager.audit.data_views import *

urlpatterns = patterns('TkManager.audit',
    ## page view
    (r'^$',  login_required(get_check_page_view)),
    (r'^check$', login_required(get_check_page_view)),
    (r'^receivables$', login_required(get_table3_view)),
    (r'^received$', login_required(get_received_page_view)),

    ## modal
    (r'^info/check/(?P<apply_id>\d+)$', login_required(get_check_modal_view)),     #复核页面

    ## action
    (r'^action/do_confirm_check', confirm_check),
    (r'^action/do_back_check', back_check),
    ## TODO:fixit
    (r'^table1$', login_required(get_table1_view)),
    (r'^table2$', login_required(get_table2_view)),
    (r'^table3$', login_required(get_table3_view)),

    #(r'^download_collection_table_1$', download_collection_table_1),

    ## get json data for DataTables
    (r'^check_repay_json$', login_required(get_check_datatable)),
    #(r'^all_collection_json$', login_required(get_all_collection_datatable)),

    #(r'^get_collection_record_json$', login_required(get_collection_record_data)),
)
