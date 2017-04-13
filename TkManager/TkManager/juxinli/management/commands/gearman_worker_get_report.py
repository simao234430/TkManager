# -*- coding: utf-8 -*-

from django.conf import settings
from TkManager.order.models import User
from TkManager.juxinli.models import *
from TkManager.juxinli.report_model import GearmanJobRecord
from TkManager.juxinli.error_no import *
from TkManager.juxinli.base_command import JuxinliBaseCommand
from TkManager.common.tk_log import TkLog
from datetime import datetime
import json, traceback

class Command(JuxinliBaseCommand):
    """
        从聚信力获取通话报告数据
    """

    def init_config(self):
        #TODO: move it into conf file
        self._transformer = {
            'person_transformer' : {
                'name' : 'Person',
                'path' : 'report_data/person',
                'data_type' : 'map',
                'trans' : {
                    "real_name": "real_name",
                    "id_card_num": "id_card_num",
                    "gender": "gender",
                    "sign": "sign",
                    "age": "age",
                    "province": "province",
                    "city": "city",
                    "region": "region",
                },
                'version' : True,
            },
            'data_source_transformer' : {
                'name' : 'DataSource',
                'path' : 'report_data/data_source',
                'data_type' : 'list',
                'trans' : {
                    "key": "key",
                    "name": "name",
                    "account": "account",
                    "category_name": "category_name",
                    "category_value": "category_value",
                    "status": "status",
                    "reliability": "reliability",
                    "binding_time": "binding_time",
                },
                'version' : True,
            },
        
            'application_check_transformer' : {
                'name' : 'ApplicationCheck',
                'path' : 'report_data/application_check',
                'data_type' : 'list',
                'trans' : {
                    "category": "category",
                    "check_point": "check_point",
                    "result": "result",
                    "evidence": "evidence",
                },
                'version' : True,
            },
            'behavior_check_transformer' : {
                'name' : 'BehaviorCheck',
                'path' : 'report_data/behavior_check',
                'data_type' : 'list',
                'trans' : {
                    "category": "category",
                    "check_point": "check_point",
                    "result": "result",
                    "evidence": "evidence",
                },
                'version' : True,
            },
            'contact_region_transformer' : {
                'name' : 'ContactRegion',
                'path' : 'report_data/contact_region',
                'data_type' : 'list',
                'trans' : {
                    "region_loc": "region_loc",
                    "region_uniq_num_cnt": "region_uniq_num_cnt",
                    "region_call_in_cnt": "region_call_in_cnt",
                    "region_call_out_cnt": "region_call_out_cnt",
                    "region_call_in_time": "region_call_in_time",
                    "region_call_out_time": "region_call_out_time",
                    "region_call_in_cnt_pct": "region_call_in_cnt_pct",
                    "region_call_out_cnt_pct": "region_call_out_cnt_pct",
                    "region_call_in_time_pct": "region_call_in_time_pct",
                    "region_call_out_time_pct": "region_call_out_time_pct",
                },
                'version' : True,
            },
            'contact_list_transformer' : {
                'name' : 'ContactList',
                'path' : 'report_data/contact_list',
                'data_type' : 'list',
                'trans' : {
                    "phone_num": "phone_num",
                    "phone_num_loc": "phone_num_loc",
                    "contact_name": "contact_name",
                    "needs_type": "needs_type",
                    "call_cnt": "call_cnt",
                    "call_len": "call_len",
                    "call_out_cnt": "call_out_cnt",
                    "call_out_len": "call_out_len",
                    "call_in_cnt": "call_in_cnt",
                    "call_in_len": "call_in_len",
                    "p_relation": "p_relation",
                    "contact_1w": "contact_1w",
                    "contact_1m": "contact_1m",
                    "contact_3m": "contact_3m",
                    "contact_early_morning": "contact_early_morning",
                    "contact_morning": "contact_morning",
                    "contact_noon": "contact_noon",
                    "contact_afternoon": "contact_afternoon",
                    "contact_night": "contact_night",
                    "contact_all_day": "contact_all_day",
                    "contact_weekday": "contact_weekday",
                    "contact_weekend": "contact_weekend",
                    "contact_holiday": "contact_holiday",
               },
                'version' : True,
            },
            'deliver_address_transformer' : {
                'name' : 'DeliverAddress',
                'path' : 'report_data/deliver_address',
                'data_type' : 'list',
                'trans' : {
                    "address": "address",
                    "lng": "lng",
                    "lat": "lat",
                    "predict_addr_type": "predict_addr_type",
                    "begin_date": "begin_date",
                    "end_date": "end_date",
                    "total_amount": "total_amount",
                    "total_count": "total_count",
                    "receiver": {
                        "name" : "Receiver",
                        "data_type" : "list",
                        "version" : True,
                        "trans": {
                            "name" : "name",
                            "phone_num_list" : "phone_num_list",
                            "amount" : "amount",
                            "count" : "count",
                        },                       

                    },
                },
                'version' : True,
            },
            'ebusiness_expense_transformer' : {
                'name' : 'EbusinessExpense',
                'path' : 'report_data/ebusiness_expense',
                'data_type' : 'list',
                'trans' : {
                    "trans_mth": "trans_mth",
                    "owner_amount": "owner_amount",
                    "owner_count": "owner_count",
                    "family_amount": "family_amount",
                    "family_count": "family_count",
                    "others_amount": "others_amount",
                    "others_count": "others_count",
                    "all_amount": "all_amount",
                    "all_count": "all_count",
                },
                'version' : True,
            },
            'cell_behavior_transformer' : {
                'name' : 'CellBehavior',
                'path' : 'report_data/cell_behavior:0/behavior',
                'data_type' : 'list',
                'trans' : {
                    "cell_phone_num": "cell_phone_num",
                    "cell_operator": "cell_operator",
                    "cell_loc": "cell_loc",
                    "cell_mth": "cell_mth",
                    "call_in_time": "call_in_time",
                    "call_out_time": "call_out_time",
                    "sms_cnt": "sms_cnt",
                    "net_flow": "net_flow",
                },
                'version' : True,
            },

            'recent_need_transformer' : {
                'name' : 'RecentNeed',
                'path' : 'report_data/recent_need',
                'data_type' : 'list',
                'trans' : {
                    "req_type": "req_type",
                    "req_call_cnt/call_out_cnt": "call_out_cnt",
                    "req_call_cnt/call_in_cnt": "call_in_cnt",
                    "req_call_min/call_out_time": "call_out_time",
                    "req_call_min/call_in_time": "call_in_time",
                    "req_mth": "req_mth",
                    "demands_info": {
                        "name" : "DemandsInfo",
                        "data_type" : "list",
                        "version" : True,
                        "trans": {
                            "demands_name" : "demands_name",
                            "demands_call_out_cnt" : "demands_call_out_cnt",
                            "demands_call_in_cnt" : "demands_call_in_cnt",
                            "demands_call_out_time" : "demands_call_out_time",
                            "demands_call_in_time" : "demands_call_in_time",
                        },                          

                    },
                },
                'version' : True,
            },
            'trip_info_transformer' : {
                'name' : 'TripInfo',
                'path' : 'report_data/trip_info',
                'data_type' : 'list',
                'trans' : {
                    "trip_leave": "trip_leave",
                    "trip_dest": "trip_dest",
                    "trip_transportation": "trip_transportation",
                    "trip_person": "trip_person",
                    "trip_type": "trip_type",
                    "trip_start_time": "trip_start_time",
                    "trip_end_time": "trip_end_time",
                    "trip_data_source": "trip_data_source",
                },
                'version' : True,
            },
            'collection_contact_transformer' : {
                'name' : 'CollectionContact',
                'path' : 'report_data/collection_contact',
                'data_type' : 'list',
                'trans' : {
                    "contact_name": "contact_name",
                    "begin_date": "begin_date",
                    "end_date": "end_date",
                    "total_count": "total_count",
                    "total_amount": "total_amount",
                    "contact_details": "contact_details",
                    "contact_details": {
                        "name" : "ContactDetails",
                        "data_type" : "list",
                        "version" : True,
                        "trans": {
                            "phone_num" : "phone_num",
                            "phone_num_loc" : "phone_num_loc",
                            "call_cnt" : "call_cnt",
                            "call_len" : "call_len",
                            "call_out_cnt" : "call_out_cnt",
                            "call_in_cnt" : "call_in_cnt",
                            "sms_cnt" : "sms_cnt",
                            "trans_start" : "trans_start",
                            "trans_end" : "trans_end",

                        },                          

                    },
                },
                'version' : True,
            },
            'main_service_transformer' : {
                'name' : 'MainService',
                'path' : 'report_data/main_service',
                'data_type' : 'list',
                'trans' : {
                    "company_type": "company_type",
                    "total_service_cnt": "total_service_cnt",
                    "service_details": {
                        "name" : "ServiceDetails",
                        "data_type" : "list",
                        "version" : True,
                        "trans": {
                            "company_name" : "company_name",
                            "service_info" :{
                                "name" : "ServiceInfo",
                                "data_type" : "list",
                                "version" : True,
                                "trans": {
                                    "service_num" : "service_num",
                                    "service_cnt" : "service_cnt",
                                    "mth_details" : {
                                        "name" : "MthDetails",
                                        "data_type" : "list",
                                        "version" : True,
                                        "trans": {
                                            "interact_mth" : "interact_mth",
                                            "interact_cnt" : "interact_cnt",
                                        },

                                    },
                                },
                            },
                          
                        },                          
                    },
                },
                'version' : True,
            },
        }

    @property
    def task_name(self):
        return 'get_report'

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
            ret_code = self.get_juxinli_report(params["uid"])
            print 'get_juxinli_raw_call:', ret_code
            end = datetime.now()
            user = User.objects.get(pk=params["uid"])
            GearmanJobRecord(command_type=self.task_name, params=job_data, result=ret_code, start_time=start, end_time=end, owner=user if user else None).save()
            return ret_code
        except Exception, e:
            traceback.print_exc()
            TkLog().error("do job failed %s" % str(e))
            return ERR_OTHER_EXCEPTION

    def get_juxinli_report(self, uid):
        try:
            self.get_juxinli_data(uid, self._access_report_data_api)
        except Exception, e:
            traceback.print_exc()
            TkLog().error("get juxinli call failed %s" % str(e))
            return ERR_OTHER_EXCEPTION
        return RETURN_SUCCESS

if __name__ == '__main__':
    uid = 16
    user = User.objects.get(pk=uid)
    fp = open('/home/leon/TkManager/TkManager/TkManager/juxinli/management/commands/report_data',"rU")
    raw = fp.readlines()
    fp.close()
    for raw_data in raw: 
        list1 = raw_data.split("\t")
        data = json.loads(list1[-1],encoding='utf-8')
        rep = Command()
        rep.test(user,data)

