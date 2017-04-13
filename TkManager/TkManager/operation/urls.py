# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from TkManager.operation.general_views import *
from TkManager.operation.data_views import get_pay_loan_datatable, get_repay_loan_datatable,get_table1_datatable,get_table2_datatable,get_table3_datatable

urlpatterns = patterns('TkManager.operation',
   ## page view
   (r'^$',  RedirectView.as_view(url='/operation/pay')),
   (r'^pay$', login_required(get_pay_loan_view)),
   (r'^repay$', login_required(get_repay_loan_view)),
   (r'^repay4custom$', login_required(get_repay_loan_view4custom)),
   (r'^pay_modal/(?P<apply_id>\d+)$', (get_pay_modal_view)),
   (r'^repay_modal/(?P<apply_id>\d+)$', (get_repay_modal_view)),
   (r'^repay_modal4custom/(?P<apply_id>\d+)$', (get_repay_modal_view4custom)),
   (r'mifan_confirm_idlist$', (mifan_confirm_idlist)),
   (r'mifan_confirm_account', (get_mifan_confirm_account_view)),
   (r'mifan_confirm', (get_mifan_confirm_view)),
   (r'^table1$', login_required(get_table1_view)),
   (r'^table2$', login_required(get_table2_view)),
   (r'^table3$', login_required(get_table3_view)),
   (r'table3_result', login_required(get_table3_result_view)),
   ## action
   (r'download_pay_loan$', download_pay_loan),
   (r'export_repay_loan_table$', export_repay_loan_table),
   (r'export_pay_loan_table$', export_pay_loan_table),
   (r'download_table1', download_table1),
   (r'download_table2', download_table2),
   (r'download_table3', download_table3),
   (r'^do_pay_loan$', do_realtime_pay_action),
   (r'^do_repay_loan$', do_realtime_repay_action),
   (r'add_collection_record$', add_collection_record),

   ## get json data for DataTables
   (r'^pay_loan_json$', login_required(get_pay_loan_datatable)),
   (r'^repay_loan_json$', login_required(get_repay_loan_datatable)),

   (r'^table1_json$', login_required(get_table1_datatable)),
   (r'^table2_json$', login_required(get_table2_datatable)),
   (r'table3_json', login_required(get_table3_datatable)),

   #(r'gen_excel$', gen_excel),

   (r'mifan_account_confirm_idlist', (mifan_account_confirm_idlist)),
   (r'^repay_batch_idlist', (repay_batch_idlist)),
   (r'^repay_modal_batch', (get_repay_modal_batch_view)),

   (r'test', (test)),
   (r'auto_pay_confirm', (auto_pay_confirm)),
   (r'auto_pay', (auto_pay)),
)
