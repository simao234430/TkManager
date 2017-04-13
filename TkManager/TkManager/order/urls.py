# -*- coding: utf-8 -*-
#from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from TkManager.order.general_views import *
from TkManager.order.data_views import get_order_datatable, get_apply_order_datatable, get_promotion_order_datatable, get_loan_order_datatable,get_user_info_note_data

urlpatterns = patterns('TkManager.order',
   ## page view
   #(r'^$', RedirectView.as_view(url='/order/all')),
   (r'^$', login_required(get_user_view)),
   (r'^all$', login_required(get_order_view)),
   (r'^apply$', login_required(get_apply_order_view)),
   (r'^promotion$', login_required(get_promotion_view)),
   (r'^loan$', login_required(get_loan_view)),
   (r'^collection$', login_required(get_collection_view)),
   #(r'^production$','views.getProductionView')),

   ## get json data for DataTables
   (r'^all_json$', login_required(get_order_datatable)),
   (r'^apply_json$', login_required(get_apply_order_datatable)),
   (r'^promotion_json$', login_required(get_promotion_order_datatable)),
   (r'^loan_json$', login_required(get_loan_order_datatable)),
   #(r'^collectionjson$', 'views.get_collection_datatable'),
   (r'get_user_info_note_data$', get_user_info_note_data),

   ## popup view
   #(r'^/order/(?P<order_id>\d+)$', 'info_views.get_order_info'),
   #(r'^/review/(?P<review_id>\d+)$', 'info_views.get_reivew_info'),
   #(r'^/loan/(?P<loan_id>\d+)$', 'info_views.get_loan_info'),
   #(r'^/collection/(?P<collection_id>\d+)$', 'info_views.get_collection_info'),

   ## trends insight
   #(r'^trendsinsight$','data_hitory.get_history_info'),
   (r'^trendsinsight$','general_views.get_history_view'),

   ## test generator
   (r'^generate/$','generator.generate_apply'),
   (r'^clear/$','general_views.clear'),
)
