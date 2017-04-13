# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from TkManager.order.models import User
from TkManager.juxinli.models import *
from TkManager.juxinli.report_model import GearmanJobRecord
from TkManager.juxinli.error_no import *
from TkManager.juxinli.base_command import JuxinliBaseCommand
from TkManager.common.tk_log import TkLog
from datetime import datetime
import urllib2, json, traceback

class Command(JuxinliBaseCommand):
    """
        从聚信力获取电商数据
    """
    #def __init__(self):
    #    super(Command, self).__init__()
    #    self._org_name = settings.JUXINLI_CONF['org_name']
    #    self._client_secret = settings.JUXINLI_CONF['client_secret']
    #    self._access_report_data_api = settings.JUXINLI_CONF['access_report_data_api']
    #    self._access_raw_data_api = settings.JUXINLI_CONF['access_raw_data_api']
    #    self._access_report_token_api = settings.JUXINLI_CONF['access_report_token_api']
    #    self._options = {
    #        'update_days'  :  21,
    #        'force_update' : False,
    #    }

    def init_config(self):
        #TODO: move it into conf file
        self._transformer = {
            'basic_transformer' : {
                'name' : 'EbusinessBasic',
                'path' : 'raw_data/members/transactions:0/basic',
                'data_type' : 'map',
                'trans' : {
                    "website_id": "website_id",
                    "nickname": "nickname",
                    "real_name": "real_name",
                    "is_validate_real_name": "is_validate_real_name",
                    "level": "level",
                    "cell_phone": "cell_phone",
                    "email": "email",
                    "security_level": "security_level",
                    "register_date": "register_date",
                    "update_time": "update_time",
                },
                'version' : True,
            },
            'transactions_transformer' : {
                'name' : 'EbusinessTransactions',
                'path' : 'raw_data/members/transactions:0/transactions',
                'data_type' : 'list',
                'trans' : {
                    "order_id": "order_id",
                    "is_success": "is_success",
                    "trans_time": "trans_time",
                    "total_price": "total_price",
                    "payment_type": "payment_type",
                    "bill_title": "bill_title",
                    "bill_type": "bill_type",
                    "receiver_name": "receiver_name",
                    "receiver_title": "receiver_title",
                    "receiver_cell_phone": "receiver_cell_phone",
                    "receiver_phone": "receiver_phone",
                    "receiver_addr": "receiver_addr",
                    "zipcode": "zipcode",
                    "delivery_type": "delivery_type",
                    "delivery_fee": "delivery_fee",
                    "update_time": "update_time",
                    "items": {
                        "name" : "TransactionItems",
                        "data_type" : "list",
                        "version" : True,
                        "trans": {
                            "trans_time" : "trans_time",
                            "product_price" : "product_price",
                            "product_cnt" : "product_cnt",
                            "product_name" : "product_name",
                        },                       

                    },
                },
                'version' : True,
            },
            'address_transformer' : {
                'name' : 'EbusinessAddress',
                'path' : 'raw_data/members/transactions:0/address',
                'data_type' : 'list',
                'trans' : {
                    "province": "province",
                    "update_time": "update_time",
                    "receiver_addr": "receiver_addr",
                    "city": "city",
                    "receiver_cell_phone": "receiver_cell_phone",
                    "zipcode": "zipcode",
                    "receiver_title": "receiver_title",
                    "payment_type": "payment_type",
                    "is_default_address": "is_default_address",
                    "receiver_name": "receiver_name",
                    "receiver_phone": "receiver_phone",
                },
                'version' : True,
            },
        }

    @property
    def task_name(self):
        return 'get_ebusiness'

    def do_job(self, job_data):
        params = None
        try:
            params = json.loads(job_data)
            TkLog().info("do job: user:%d" % params["uid"])
        except Exception, e:
            traceback.print_exc()
            TkLog().error("do job failed %s" % str(e))
            return ERR_PARAMS_ILLEGAL

        try:
            start = datetime.now()
            ret_code = self.get_juxinli_ebusiness(params["uid"])
            print 'get_juxinli_ebusiness:', ret_code
            end = datetime.now()
            user = User.objects.get(pk=params["uid"])
            GearmanJobRecord(command_type=self.task_name, params=job_data, result=ret_code, start_time=start, end_time=end, owner=user if user else None).save()
            return ret_code
        except Exception, e:
            traceback.print_exc()
            TkLog().error("do job failed %s" % str(e))
            return ERR_OTHER_EXCEPTION

    def get_juxinli_ebusiness(self, uid):
        try:
            self.get_juxinli_data(uid, self._access_e_business_raw_data_api)
        except Exception, e:
            traceback.print_exc()
            TkLog().error("get juxinli ebusiness failed %s" % str(e))
            return ERR_OTHER_EXCEPTION
        return RETURN_SUCCESS

