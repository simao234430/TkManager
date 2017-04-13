#encoding=utf-8

import sys
sys.path.append('gen-py')
sys.path.append('..')
import urllib, urllib2
import ConfigParser
import json
import OpenSSL
import binascii
from datetime import datetime
from bs4 import BeautifulSoup
import base64
import random
import xlrd
import chardet

#from common.tk_log import TkLogger
from common import log_client
from model.order_model import BankPayRecord, db

from bank_service import BankService
from bank_service.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

BANK_RET_SUCCESS = '0000'

class BankHandler(object):
    def __init__(self, conf):
        self.online_base_url = conf.get('online', 'base_url')
        self.online_account = conf.get('online', 'account')

        pay_config_num = conf.getint('pay_conf', 'config_num')
        self.key_file = {}
        self.key_file_password = {}
        self.username = {}
        self.password = {}
        self.merchant_id = {}
        self.pay_type = []

        for i in range(pay_config_num):
            conf_suffix = '_' + str(i + 1)
            conf_name = conf.get('pay_conf', 'name' + conf_suffix)
            self.pay_type.append(conf_name)
            self.key_file[conf_name] = conf.get('pay_conf', 'key_file' + conf_suffix)
            self.key_file_password[conf_name] = conf.get('pay_conf', 'key_file_password' + conf_suffix)
            self.username[conf_name] = conf.get('pay_conf', 'username' + conf_suffix)
            self.password[conf_name] = conf.get('pay_conf', 'password' + conf_suffix)
            self.merchant_id[conf_name] = conf.get('pay_conf', 'merchant_id' + conf_suffix)
        self.realtime_pay_template = conf.get('pay_conf', 'realtime_pay_template')
        self.payment_url = conf.get('pay_conf', 'payment_url')
        self.cer_file = conf.get('pay_conf', 'cer_file')

        self.payfor_key_file = conf.get('payfor_conf', 'key_file')
        self.payfor_key_file_password = conf.get('payfor_conf', 'key_file_password')
        self.payfor_cer_file = conf.get('payfor_conf', 'cer_file')
        self.payfor_username = conf.get('payfor_conf', 'username')
        self.payfor_password = conf.get('payfor_conf', 'password')
        self.payfor_merchant_id = conf.get('payfor_conf', 'merchant_id')
        self.realtime_payfor_template = conf.get('payfor_conf', 'realtime_payfor_template')
        self.payfor_url = conf.get('payfor_conf', 'payfor_url')

        self.proportion = conf.getint('pay_conf', 'proportion')
        #self.logger = TkLogger('bank_server', 'bank_server.log').logger
        self.logger = log_client.get_bank_server_logger(conf.getint('general', 'log_level'),
                conf.get('server', 'log_server_ip'), conf.getint('server', 'log_server_port'))

        mysql_host = conf.get('mysql', 'host')
        mysql_user = conf.get('mysql', 'user')
        mysql_password = conf.get('mysql', 'password')
        mysql_db = conf.get('mysql', 'db')
        #db.bind('mysql', host = mysql_host, passwd = mysql_password, user = mysql_user, db = mysql_db)
        #db.generate_mapping(create_tables = True)

        self._init_bank_code(conf.get('server', 'bank_code_file'))

    def _init_bank_code(self, bank_code_file):
        self.bank_map = {}
        xls = xlrd.open_workbook(bank_code_file)
        table = xls.sheets()[0]
        for i in xrange(table.nrows):
            row = table.row_values(i)
            bank_name = row[0]
            idx = bank_name.find('(')
            if idx != -1:
                bank_name = bank_name[:idx]
            card_type = row[15]
            prefix = row[13]
            if card_type == u'借记卡':
                #print chardet.detect(bank_name)
                #self.bank_map[prefix] = base64.b64encode(bank_name)
                self.bank_map[prefix] = bank_name.encode('utf8').strip()
            #self.bank_map[prefix] = bank_name.encode('utf8').strip()
        self.bank_type_map = {'中国建设银行': 1,
                              '中国银行': 2,
                              '中国农业银行': 3,
                              '招商银行': 4,
                              '广发银行': 5,
                              '兴业银行': 6,
                              '中国工商银行': 7,
                              '光大银行': 8,
                              '邮政储蓄银行': 9}

    def _do_http_request(self, url, send_data = None):
        try:
            req = urllib2.Request(url, send_data)
            res = urllib2.urlopen(req)
            rsp = res.read()
            return rsp
        except Exception,e:
            print url, e
            return None

#    def card_verify(self, request):
#        params = {'type': 1,
#                  'userId': request.user_id,
#                  'cardNumber': request.card_id,
#                  'cardName': base64.b64decode(request.owner_name),
#                  'account': self.online_account}
#        url_param = urllib.urlencode(params)
#        url = self.online_base_url + 'authCard?' + url_param
#        print url
#        rsp_data = self._do_http_request(url)
#        response = CardVerifyResponse()
#        if not rsp_data:
#            #TODO:后续需要修改返回值
#            response.retcode = 0
#        else:
#            print rsp_data
#            json_rsp = json.loads(rsp_data)
#            res_code = json_rsp['resCode']
#            res_stat = json_rsp['stat']
#
#            #TODO:根据返回的信息来决定返回值
#            if res_code == '0000' and res_stat == '00':
#                response.retcode = 0
#                return response
#            response.retcode = 0
#        return response

    def card_verify(self, request):
        card_id = request.card_id
        response = CardVerifyResponse()
        response.retcode = -1
        for i in xrange(8, 2, -1):
            prefix = card_id[:i]
            if prefix in self.bank_map:
                response.retcode = 0
                response.bank_name = self.bank_map[prefix]
                response.bank_type = self.bank_type_map[response.bank_name]
                break
        return response

    def _sign_msg(self, raw_data, key_file, key_file_password):
        try:
            tobe_signed = raw_data.replace('<SIGNED_MSG></SIGNED_MSG>', '')
            print key_file, key_file_password
            key_data = open(key_file).read()
            key = OpenSSL.crypto.load_pkcs12(key_data, key_file_password)
            key = key.get_privatekey()
            signed_data = OpenSSL.crypto.sign(key, tobe_signed, 'sha1')
            signed_data = binascii.hexlify(signed_data)
            send_data = raw_data.replace('<SIGNED_MSG></SIGNED_MSG>', '<SIGNED_MSG>' + signed_data + '</SIGNED_MSG>')
            return send_data
        except Exception,e:
            self.logger.error('sign msg failed. raw_data: %s' % raw_data)
            print 'sign msg failed', e
            return None

    def _verify_msg(self, raw_msg):
        try:
            start = raw_msg.find('<SIGNED_MSG>')
            if start == -1:
                self.logger.error('not find signed msg, raw_msg: %s' % raw_msg)
                return True
            end = raw_msg.find('</SIGNED_MSG>')
            signed_msg = raw_msg[start + 12:end]
            tobe_verified_msg = raw_msg[:start] + raw_msg[end + 13:]
            cer_data = open(self.cer_file).read()
            x509_cer = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cer_data)
            signed_data = binascii.unhexlify(signed_msg)
            print len(signed_data)
            OpenSSL.crypto.verify(x509_cer, signed_data, tobe_verified_msg, 'sha1')
            return True
        except Exception,e:
            print 'exception: ', str(e)
            return False

    def realtime_pay(self, request):
        '''实时代收'''
        req_sn = datetime.now().strftime('%Y%m%d%H%M%S%f') + str(request.user_id)
        total_sum = request.amount * 100 * self.proportion / 100
        pay_type = request.pay_type
        if pay_type not in self.pay_type:
            self.logger.error('realtime_pay failed, type %s is not support' % pay_type)
            response.retcode = -1
            return response
        response = CommonResponse()
        #account_name = base64.b64decode(request.account_name)
        try:
            req_template = open(self.realtime_pay_template).read()
            req_data = req_template % (self.username[pay_type], self.password[pay_type],
                                       req_sn, self.merchant_id[pay_type], total_sum,
                                       request.bank_code, request.account_cardid,
                                       request.account_name, total_sum, request.user_id)
        except Exception,e:
            print e
            return None

        print req_data
        send_data = self._sign_msg(req_data, self.key_file[pay_type], self.key_file_password[pay_type])
        if not send_data:
            self.logger.error('sign msg failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            response.retcode = -1
            response.err_msg = 'sign msg fail'
            return response
        rsp_data = self._do_http_request(self.payment_url, send_data)
        if not rsp_data:
            self.logger.error('do http request failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            response.retcode = -2
            response.err_msg = 'http fail'
            return response

        result_file = open('result.txt', 'w')
        result_file.write(rsp_data)
        result_file.close()
        if self._verify_msg(rsp_data):
            try:
                xml_root = BeautifulSoup(rsp_data)
                rsp_code = xml_root.gzelink.info.ret_code.text
                if rsp_code == BANK_RET_SUCCESS:
                    self.logger.error('realtime pay success. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                        request.amount, request.bank_code, request.account_cardid, request.account_name))
                    response.retcode = 0
                    return response
                else:
                    self.logger.error('realtime pay failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                        request.amount, request.bank_code, request.account_cardid, request.account_name))
                    response.retcode = int(rsp_code)
                    response.err_msg = xml_root.gzelink.info.err_msg.text.encode('utf8')
                    return response
            except Exception,e:
                self.logger.error('parse rsp xml failed, xml: %s err: %s' % (rsp_data, str(e)))
                response.retcode = -1
                response.err_msg = 'sign msg fail'
                return response
        else:
            self.logger.error('verify msg failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            response.retcode = -1
            response.err_msg = 'sign msg fail'
            return response

    def realtime_payfor(self, request):
        '''实时代付'''
        req_sn = datetime.now().strftime('%Y%m%d%H%M%S%f') + str(request.user_id)
        total_sum = request.amount * 100 * self.proportion / 100
        try:
            req_template = open(self.realtime_payfor_template).read()
            req_data = req_template % (self.payfor_username, self.payfor_password,
                                       req_sn, self.payfor_merchant_id, total_sum,
                                       request.bank_code, request.account_cardid,
                                       request.account_name, total_sum, request.user_id)
        except:
            self.logger.error('read template failed')
            return None

        response = CommonResponse()
        send_data = self._sign_msg(req_data, self.payfor_key_file, self.payfor_key_file_password)
        if not send_data:
            self.logger.error('sign msg failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            response.retcode = -1
            response.err_msg = 'sign msg fail'
            return response
        rsp_data = self._do_http_request(self.payfor_url, send_data)
        if not rsp_data:
            self.logger.error('do http request failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            response.retcode = -2
            response.err_msg = 'http fail'
            return response

        result_file = open('result_for.txt', 'w')
        result_file.write(rsp_data)
        result_file.close()
        if self._verify_msg(rsp_data):
            try:
                xml_root = BeautifulSoup(rsp_data)
                rsp_code = xml_root.gzelink.info.ret_code.text
                if rsp_code == BANK_RET_SUCCESS:
                    self.logger.error('realtime payfor success. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                        request.amount, request.bank_code, request.account_cardid, request.account_name))
                    response.retcode = 0
                    return response
                else:
                    self.logger.error('realtime payfor failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                        request.amount, request.bank_code, request.account_cardid, request.account_name))
                    response.retcode = int(rsp_code)
                    response.err_msg = xml_root.gzelink.info.err_msg.text.encode('utf8')
                    return response
            except:
                self.logger.error('parse rsp xml failed, xml: %s' % rsp_data)

                response.retcode = -1
                response.err_msg = 'sign msg fail'
                return response
        else:
            self.logger.error('verify msg failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            response.retcode = -1
            response.err_msg = 'sign msg fail'
            return response

    def _get_batch_pay_xml(self, req_sn, param_list):
        total_sum = 0
        for param in param_list:
            total_sum += param['amount']
        total_sum = total_sum * 100 * self.proportion / 100
        xml_header_template = '''
            <?xml version="1.0" encoding="GBK"?>
            <GZELINK>
                <INFO>
                    <TRX_CODE>100001</TRX_CODE>
                    <VERSION>04</VERSION>
                    <DATA_TYPE>2</DATA_TYPE>
                    <LEVEL>0</LEVEL>
                    <USER_NAME>%s</USER_NAME>
                    <USER_PASS>%s</USER_PASS>
                    <REQ_SN>%s</REQ_SN>
                    <SIGNED_MSG></SIGNED_MSG>
                </INFO>
                <BODY>
                    <TRANS_SUM>
                        <BUSINESS_CODE>14901</BUSINESS_CODE>
                        <MERCHANT_ID>%s</MERCHANT_ID>
                        <TOTAL_ITEM>%d</TOTAL_ITEM>
                        <TOTAL_SUM>%d</TOTAL_SUM>
                        <SUBMIT_TIME>%s</SUBMIT_TIME>
                    </TRANS_SUM>
                    <TRANS_DETAILS>
        '''
        xml_data = xml_header_template % (
                self.username,
                self.password,
                req_sn,
                self.merchant_id,
                len(param_list),
                total_sum,
                datetime.now().strftime('%Y%m%d%H%M%S'))
        xml_detail_template = '''
            <TRANS_DETAIL>
                <SN>%04d</SN>
                <BANK_CODE>%s</BANK_CODE>
                <ACCOUNT_NO>%s</ACCOUNT_NO>
                <ACCOUNT_NAME>%s</ACCOUNT_NAME>
                <AMOUNT>%d</AMOUNT>
                <CURRENCY>CNY</CURRENCY>
                <CUST_USERID>%d</CUST_USERID>
            </TRANS_DETAIL>
        '''

        for i, param in enumerate(param_list):
            param['amount'] = param['amount'] * 100 * self.proportion / 100
            xml_detail = xml_detail_template % (
                    i + 1,
                    param['bank_code'],
                    param['account_no'],
                    param['account_name'],
                    param['amount'],
                    param['uin'])
            xml_data += xml_detail
        xml_data += '</TRANS_DETAILS></BODY></GZELINK>'
        return xml_data

    def batch_pay(self, request):
        #批量代付
        req_sn = datetime.now().strftime('%Y%m%d%H%M%S%f') + str(random.randint(100, 10000))
        params = []
        for pay_user in request.pay_user_list:
            param = {}
            param['bank_code'] = pay_user.bank_code
            param['account_no'] = pay_user.account_cardid
            param['account_name'] = pay_user.account_name
            param['amount'] = pay_user.amount
            param['uin'] = pay_user.user_id
            params.append(param)
        if not params:
            return 0

        req_data = self._get_batch_pay_xml(req_sn, params)
        send_data = self._sign_msg(req_data, self.key_file, self.key_file_password)
        if not send_data:
            self.logger.error('sign msg failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            return None
        self.logger.info('xml: %s' % send_data)
        rsp_data = self._do_http_request(self.payment_url, send_data)
        if not rsp_data:
            self.logger.error('do http request failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                request.amount, request.bank_code, request.account_cardid, request.account_name))
            return None

        result_file = open('result.txt', 'w')
        result_file.write(rsp_data)
        result_file.close()
        if self._verify_msg(rsp_data):
            try:
                xml_root = BeautifulSoup(rsp_data)
                rsp_code = xml_root.gzelink.info.ret_code.text
                if rsp_code == BANK_RET_SUCCESS:
                    self.logger.error('batch pay success')
                    #self.logger.error('realtime pay success. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                    #    request.amount, request.bank_code, request.account_cardid, request.account_name))
                    return True
                else:
                    self.logger.error('batch pay failed, rsp_code: %s' % rsp_code)
                    #self.logger.error('realtime pay failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
                    #    request.amount, request.bank_code, request.account_cardid, request.account_name))
                    return None
            except Exception,e:
                self.logger.error('parse rsp xml failed, xml: %s err: %s' % (rsp_data, str(e)))
                return None
        else:
            self.logger.error('batch pay failed, verify msg failed.')
            #self.logger.error('verify msg failed. amount: %d bank_code: %s account_no: %s account_name: %s' % (
            #    request.amount, request.bank_code, request.account_cardid, request.account_name))
            return None



def start_server():
    if len(sys.argv) < 2:
        print 'Usage: %s config_file' % sys.argv[0]
        return

    conf = ConfigParser.ConfigParser()
    conf.read(sys.argv[1])
    port = conf.getint('server', 'port')

    handler = BankHandler(conf)
    processor = BankService.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    #server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

    print 'Starting the server...'
    server.serve()
    print 'done.'

if __name__ == '__main__':
    start_server()
