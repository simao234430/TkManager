# -*- coding: utf-8 -*-
import urllib2, json, traceback

from django.conf import settings
from django.db import models
from TkManager.order.models import User
from TkManager.juxinli.models import *
from TkManager.juxinli.error_no import *
from TkManager.common.tk_log import TkLog
from datetime import datetime
from django_gearman_commands import GearmanWorkerBaseCommand
from django.db import transaction
import objgraph

class JuxinliBaseCommand(GearmanWorkerBaseCommand):
    """
        从聚信力获取json数据，然后把数据存入数据库
        init_config  配置数据的存储方式,需要子类自己实现 配置文件格式参看注释
        get_juxinli_data 执行解析存储操作

    """
    def __init__(self):
        super(JuxinliBaseCommand, self).__init__()
        self._org_name = settings.JUXINLI_CONF['org_name']
        self._client_secret = settings.JUXINLI_CONF['client_secret']
        self._access_report_data_api = settings.JUXINLI_CONF['access_report_data_api']
        self._access_raw_data_api = settings.JUXINLI_CONF['access_raw_data_api']
        self._access_report_token_api = settings.JUXINLI_CONF['access_report_token_api']
        self._access_e_business_raw_data_api = settings.JUXINLI_CONF['access_e_business_raw_data_api']
        self._options = {
            'update_days'  :  21,
            'force_update' : False,
        }
        self.init_config()

    def init_config():
        '''
        参考格式:
        self._transformer = {
            'basic_transformer' : {
                'name' : 'PhoneBasic',  # django的Model类名称
                'path' : 'raw_data/members/transactions:0/basic',  #json数据的路径
                'data_type' : 'map',    # 数据的类型如果是单条就是map，如果是多条就是list
                'version' : True,       # 是否使用版本控制，如果是真那么每次拉数据会新增版本号，否则都用版本1
                'trans' : {  #数据的转化格式   source_field(json) -> dest_field(db model)
                    "cell_phone": "cell_phone",
                    "idcard": "idcard",
                    "real_name": "real_name",
                    "reg_time": "reg_time",
                    "update_time": "update_time",
                    "receiver" : {  #如果是外键就用一个嵌套的格式来表示 (嵌套就没必要再用path定位了吧，默认就是当前路径)
                        "name" : "Receiver"

                        "req_call_cnt/data_type" : "list"

                        "version" : True,
                        "trans": {
                            "name" : "name",
                            "phone_num_list" : "phone_num_list",
                            "amount" : "amount",
                            "count" : "count",
                        },
                    },

                },
            },
        }
        '''
        pass

    def test(self,user,data):
        if not data:
            return ERR_GET_RAW_DATA_FAILED
        ret_code = self._save_raw_data(data, user, self._options)
	return ret_code

    def get_juxinli_data(self, uid, url):
        try:
            user = User.objects.get(pk=uid)
            token = self._get_token()
            if not token:
                return ERR_CREATE_TOKEN_FAILED
            data = self._get_juxinli_data(token, user, url)
            if not data:
                return ERR_GET_RAW_DATA_FAILED
            ret_code = self._save_raw_data(data, user, self._options)
            if ret_code != 0:
                return ret_code
            #data = self._get_report_data(token, user)
            #print data
            #print "@@ print ret", ret_code
            return RETURN_SUCCESS
        except Exception, e:
            traceback.print_exc()
            TkLog().error("get juxinli call failed %s" % str(e))
            return ERR_OTHER_EXCEPTION

    def _open_url(self, url):
        '''
            get http request return json
        '''
        req1 = urllib2.Request(url=url)
        html = urllib2.urlopen(req1).read().decode('utf-8')
        return json.loads(html.encode("utf-8"))

    def _get_token(self):
        '''
            生成一个新的用来获取数据的token 失败返回None
        '''
        url = u"%s?client_secret=%s&hours=24&org_name=%s" % (self._access_report_token_api, self._client_secret, self._org_name)
        html = self._open_url(url)
        #if
        try:
            res = html['access_token']
            return res
        except KeyError, e:
            return None

    def _get_juxinli_data(self, access_token, user, url):
        '''
            获取聚信力数据 返回json
        '''
        raw_url = u'%s?client_secret=%s&access_token=%s&name=%s&idcard=%s&phone=%s' % (url, self._client_secret, access_token, user.name, user.id_no, user.phone_no)
       #print raw_url
        try:
            res = self._open_url(raw_url.encode('utf-8'))
           # print res
           # print res['raw_data']['members']['error_msg']
            success = res["success"]
            if success != "true":
                return None
            return res
        except KeyError, e:
            return None
    #def _get_report_data(self, access_token, user):
    #    report_url = u'%s?client_secret=%s&access_token=%s&name=%s&idcard=%s&phone=%s' % (self._access_report_token_api, self._client_secret, access_token, user.name, user.id_no, user.phone_no)
    #    print report_url
    #    res = self._open_url(report_url.encode('utf-8'))
    #    #print res
    #    #print res['raw_data']['members']['error_msg']
    #    return res

    def _allow_overwrite_data(self, user, options):
        return True

    def _get_data_from_path(self, data, path):
        '''
            path语法   / 分割路径   : 选择list中的序号
        '''
        try:
            fields = path.split("/")
            #print fields
            res = data
            for field in fields:
                if field.find(":") != -1:
                    parts = field.split(":")
                    if len(parts) != 2:
                        TkLog().error("field format error %s" % (field))
                        return None
                    res = res[parts[0]][int(parts[1])]
                else:
                    res = res[field]
            return res
        except Exception, e:
            print e
            traceback.print_exc()
            TkLog().error("get data from path failed %s" % str(e))
            return None

    def _save_raw_data(self, data, user, options):
        """
            可以重入，一个用户的信息如果更新时间少于options.update_days天，不会更新db，否则添加记录
        """
        if not self._allow_overwrite_data(user, options):
            return RETURN_CAN_NOT_OVERWRITE
        for transtype in self._transformer.keys():
            adaptor = self._transformer[transtype]
            cls = eval(adaptor["name"])
            version = 0
            objs = cls.objects.filter(owner=user).order_by('-id')[:1]
            if len(objs) == 1:
                version = objs[0].version
                TkLog().info("update %s version %d" % (adaptor["name"], version))
            data_list = self._get_data_from_path(data, adaptor["path"])
            if not data_list:
                TkLog().warn("data not found %s:%s" % (adaptor["name"], adaptor["path"]))
                #return -4 #just skip

            ret_code = self._save_obj(data_list, cls, user, adaptor, version)
            if ret_code != 0:
                return ret_code
        return RETURN_SUCCESS


    @transaction.commit_manually
    def _save_obj(self, data_list, cls, user, adaptor, version=0, parent=None):

        '''
            将一个对象写入数据库
            根据data_type来判断是map还是list
        '''
        if adaptor["data_type"] == "list": #data_list是列表数据

            for record in data_list:

                ret_code = self._save_single_obj(record, cls, user, adaptor, version, parent)
                if ret_code != 0:
                    return ret_code
        elif adaptor["data_type"] == "map": #data_list是单条数据

            record = data_list

            ret_code = self._save_single_obj(record, cls, user, adaptor, version, parent)
            if ret_code != 0:
                return ret_code
        transaction.commit()
        return 0

    def _save_single_obj(self, record, cls, user, adaptor, version = 0, parent=None):
        '''
            将一个条目写入数据库，如果parent不为空，还需要设置parent的外键
            record : 单条json数据条目
            cls : 数据库Model
        '''
        obj = cls()
        for source_field, dest_field in adaptor['trans'].items():
            if isinstance(dest_field,str):
                field_type = obj._meta.get_field(dest_field)
                if "/" in source_field:
                    record[source_field] = self._get_data_from_path(record,source_field)
                if isinstance(field_type, models.CharField):
                    try:
                        if isinstance(record[source_field],list):

                           #setattr(obj, dest_field, "#".join(record[source_field]))
                            setattr(obj, dest_field, record[source_field][0])
                        else:
                            setattr(obj, dest_field, record[source_field])
                    except Exception, e:
                        TkLog().warn("set char field failed %s %s" % (str(e), record[source_field]))
                        return ERR_SETATTR_FAILED
                elif isinstance(field_type, models.IntegerField):
                    try:
                        if not record[source_field]:
                            setattr(obj, dest_field, 0)
                        else:
                            setattr(obj, dest_field, int(record[source_field]))
                    except Exception, e:
                        TkLog().warn("set int field failed %s %s" % (str(e), record[source_field]))
                        return ERR_SETATTR_FAILED
                elif isinstance(field_type, models.BigIntegerField):
                    try:
                        if not record[source_field]:
                            setattr(obj, dest_field, 0)
                        else:
                            setattr(obj, dest_field, long(record[source_field]))
                    except Exception, e:
                        TkLog().warn("set bigint field failed %s %s" % (str(e), record[source_field]))
                        return ERR_SETATTR_FAILED
                elif isinstance(field_type, models.FloatField):
                    try:
                        if not record[source_field]:
                            setattr(obj, dest_field, float(0))
                        else:
                            setattr(obj, dest_field, float(record[source_field]))
                    except Exception, en:
                        TkLog().warn("set float field failed %s %s" % (str(e), record[source_field]))
                        return ERR_SETATTR_FAILED
                elif isinstance(field_type, models.DateTimeField):
                    try:
                        if not record[source_field]:
                            setattr(obj, dest_field, None)
                        else:
                            setattr(obj, dest_field, datetime.strptime(record[source_field], "%Y-%m-%d %H:%M:%S"))
                    except Exception, e:
                        TkLog().warn("set datetime field failed %s %s" % (str(e), record[source_field]))
                        return ERR_SETATTR_FAILED
                elif isinstance(field_type, models.NullBooleanField):
                    try:
                        if not record[source_field]:
                            setattr(obj, dest_field, None)
                        else:
                            setattr(obj, dest_field, record[source_field])
                    except Exception, e:
                        TkLog().warn("set boolean field failed %s %s" % (str(e), record[source_field]))

                        return ERR_SETATTR_FAILED
                else:
                    TkLog().error("unsupported type field:%s" % dest_field)
                    return ERR_UNSUPPORTED_FILED_TYPE
                try:

                    if adaptor['version']:
                        obj.version = version + 1
                    else:
                        obj.version = 0
                    #if parent:
                       #setattr(obj, parent["field"], parent["parent_obj"])

                    obj.owner = user
                    obj.save()
                except Exception, e:
                    print "save error %s" % str(e)
                    return ERR_SAVE_OBJECT

        for source_field, dest_field in adaptor['trans'].items():
            if isinstance(dest_field,dict):
                try:
                    sub_cls = eval(dest_field["name"])
                    self._save_obj(record[source_field], sub_cls, obj, dest_field, version, {"parent_obj":obj, "field":"owner"})
                except Exception, e:

                    TkLog().warn("set foreignkey field failed %s %s" % (str(e), record[source_field]))
        objgraph.show_most_common_types()
	return 0

