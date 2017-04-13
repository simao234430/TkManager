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
        从聚信力获取通话数据
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
                'name' : 'PhoneBasic',
                'path' : 'raw_data/members/transactions:0/basic',
                'data_type' : 'map',
                'trans' : {
                    "cell_phone": "cell_phone",
                    "idcard": "idcard",
                    "real_name": "real_name",
                    "reg_time": "reg_time",
                    "update_time": "update_time"
                },
                'version' : True,
            },
            'call_transformer' : {
                'name' : 'PhoneCall',
                'path' : 'raw_data/members/transactions:0/calls',
                'data_type' : 'list',
                'trans' : {
                    "cell_phone": "cell_phone",
                    "other_cell_phone": "other_cell_phone",
                    "place": "call_place",
                    "start_time": "start_time",
                    "use_time": "use_time",
                    "call_type": "call_type",
                    "init_type": "init_type",
                    "subtotal": "subtotal",
                    "update_time": "update_time"
                },
                'version' : True,
            },
            #'nets_transformer' : {
            #    'name' : 'PhoneNet',
            #    'path' : 'raw_data/members/transactions:0/nets',
            #    'data_type' : 'list',
            #    'trans' : {
            #        "cell_phone": "cell_phone",
            #        "place": "place",
            #        "net_type": "net_type",
            #        "start_time": "start_time",
            #        "use_time": "use_time",
            #        "subflow": "subflow",
            #        "subtotal": "subtotal",
            #        "update_time": "update_time"
            #    },
            #    'version' : True,
            #},
            #'smses_transformer' : {
            #    'name' : 'PhoneSms',
            #    'path' : 'raw_data/members/transactions:0/smses',
            #    'data_type' : 'list',
            #    'trans' : {
            #        "cell_phone": "cell_phone",
            #        "other_cell_phone": "other_cell_phone",
            #        "start_time": "start_time",
            #        "place": "call_place",
            #        "init_type": "init_type",
            #        "subtotal": "subtotal",
            #        "update_time": "update_time"
            #    },
            #    'version' : True,
            #},
            #'transactions_transformer' : {
            #    'name' : 'PhoneTransaction',
            #    'path' : 'raw_data/members/transactions:0/transactions',
            #    'data_type' : 'list',
            #    'trans' : {
            #        "bill_cycle": "bill_cycle",
            #        "cell_phone": "cell_phone",
            #        "plan_amt": "plan_amt",
            #        "total_amt": "total_amt",
            #        "pay_amt": "pay_amt",
            #        "update_time": "update_time"
            #    },
            #    'version' : True,
            #},
        }

    @property
    def task_name(self):
        return 'get_call'

    def do_job(self, job_data):
        params = None
        try:
            TkLog().info("do job: params:%s" % job_data)
            params = json.loads(job_data)
            TkLog().info("do job: user:%d" % params["uid"])
        except Exception, e:
            traceback.print_exc()
            TkLog().error("do job failed %s" % str(e))
            return ERR_PARAMS_ILLEGAL

        try:
            start = datetime.now()
            ret_code = self.get_juxinli_raw_call(params["uid"])
            print 'get_juxinli_raw_call:', ret_code
            end = datetime.now()
            user = User.objects.get(pk=params["uid"])
            GearmanJobRecord(command_type=self.task_name, params=job_data, result=ret_code, start_time=start, end_time=end, owner=user if user else None).save()
            return ret_code
        except Exception, e:
            traceback.print_exc()
            TkLog().error("do job failed %s" % str(e))
            return ERR_OTHER_EXCEPTION

    def get_juxinli_raw_call(self, uid):
        try:
            self.get_juxinli_data(uid, self._access_raw_data_api)
        except Exception, e:
            traceback.print_exc()
            TkLog().error("get juxinli call failed %s" % str(e))
            return ERR_OTHER_EXCEPTION
        return RETURN_SUCCESS
