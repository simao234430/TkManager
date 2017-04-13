#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: jonyqin
# Created Time: Thu 11 Sep 2014 03:55:41 PM CST
# File Name: Sample.py
# Description: WXBizMsgCrypt 使用demo文件
#########################################################################
from django.conf import settings
from WXBizMsgCrypt import  *
import xml.etree.cElementTree as ET
import time
import json
import httplib
import urllib2
import urllib
from urllib import urlencode
#  下面是米饭正式key
#sCorpID  =  "MFG21b6sh4lFFIZC2j"
#sToken = "dzK5klI"
#sEncodingAESKey =  "zTKo235dYP2qOdqdEPKoDhlJxuuoLrXsEqbXNutHAWN"

#  下面是米饭测试key
if settings.MIFAN_DEBUG == True: 
    sToken = "MyqcUA4"
    sEncodingAESKey = "KWB3nDfmaXGqGPla3NMZ2eQzEDS0hJK5wLaeHH7ns0O"
    sCorpID =  "test1XShXc8YkpO2yN"
else:
    sToken = "1jI1K6U"
    sEncodingAESKey =  "ZBJUvRal6MZxxKJheMYCA1LFoQn2Qrm6f5tQei1L6bD"
    sCorpID =  "MFG22y7S3n7HnxgJ0w"
wxcpt = WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)


def fill_order_confirm(repayment,s):
    jsondata = {}
    jsondata["identifier"] = "花啦花啦"
    #jsondata["serialNo"] = str(int(repayment.order_number) + 559938873)
    jsondata["serialNo"] = repayment.order_number
    jsondata["borrowerName"] = repayment.user.name
    # id_no x 必须大写
    jsondata["borrowerBankAccount"] = repayment.bank_card.number
    jsondata["borrowerBank"] = repayment.bank_card.get_bank_type_display()
    jsondata["receiverName"] = repayment.user.name
    jsondata["receiverBankAccount"] = repayment.bank_card.number
    jsondata["receiverBankAccountType"] = '0'
    jsondata["receiverBank"] = repayment.bank_card.get_bank_type_display()
    jsonstr = json.dumps(jsondata)
    return jsonstr
def fill_order_data_apply(repayment,s):
    jsondata = {}
    jsondata["date"] = repayment.apply_time.strftime("%Y-%m-%d %H:%M:%S") 
    jsondata["appstatus"] =  '0'
    jsondata["identifier"] = "花啦花啦" 
    #jsondata["serialNo"] = str(int(repayment.order_number) + 5599373)
    jsondata["serialNo"] = repayment.order_number
    jsondata["borrowerName"] = repayment.user.name
    # id_no x 必须大写
    jsondata["borrowerID"] = repayment.user.id_no.upper()
    jsondata["borrowerPhone"] = repayment.user.phone_no
    jsondata["borrowerBankAccount"] = repayment.bank_card.number
    jsondata["borrowerBank"] = repayment.bank_card.get_bank_type_display()
    jsondata["amount"] = str(repayment.apply_amount)
    jsondata["tenor"] = s.installment_days if s.is_day_percentage() else s.installment_count
    jsondata["productType"] = '1' if s.is_day_percentage() else "0"
    jsondata["repayment"] = s.get_installment_amount(repayment.apply_amount, 1)
    jsondata["receiverName"] = repayment.user.name
    jsondata["receiverBankAccount"] = repayment.bank_card.number
    jsondata["receiverBankAccountType"] = '0'
    jsondata["receiverBank"] = repayment.bank_card.get_bank_type_display()
    jsondata["receiverBankBranch"] = repayment.bank_card.bank
    jsondata["receiverBankBranchProvince"] = repayment.bank_card.bank_province
    jsondata["receiverBankBranchCity"] = repayment.bank_card.bank_city
    jsonstr = json.dumps(jsondata)
    return jsonstr
def fill_order_data():
    jsondata = {}
    jsondata["date"] =  "2015-09-17 12:30:47"  #申请日期
    jsondata["appstatus"] =  "0"  #状态  默认 0
    jsondata["identifier"] =  "花啦花啦"  #标识
    jsondata["serialNo"] =  "3872787213751392145"  #申请号
    jsondata["borrowerName"] =  "熊勇"  #还款人户名
    jsondata["borrowerID"] =  "511023198207201611"  #还款人证件号
    jsondata["borrowerPhone"] =  "15881076850"  #还款人电话
    jsondata["borrowerBankAccount"] =  "6212264402017536529"  #还款银行卡号
    jsondata["borrowerBank"] =  "工商银行"  #还款银行
    jsondata["amount"] =  "1000"  #审批金额
    jsondata["tenor"] =  "28"  #审批期限
    jsondata["productType"] =  "1"  #产品号
    jsondata["repayment"] =  "1084"  #每期还款
    jsondata["receiverName"] =  "熊勇"  #收款人名称
    jsondata["receiverBankAccount"] =  "6212264402017536529"  #收款银行卡号
    jsondata["receiverBankAccountType"] =  "0"  #收款银行类型
    jsondata["receiverBank"] =  "工商银行"  #收款银行
    jsondata["receiverBankBranch"] =  ""  #收款支行
    jsondata["receiverBankBranchProvince"] =  ""  #收款银行开户省
    jsondata["receiverBankBranchCity"] =  ""  #收款开户行市
    jsonstr = json.dumps(jsondata)
    return jsonstr
def send2mifan_confirm(repayment,s):
    timestamp =  str(int(time.time()))
    nonce = Prpcrypt.get_random_str_6()
    #jsonstr = fill_order_data()
    jsonstr = fill_order_confirm(repayment,s)
    encrypt_body = wxcpt.encryptMsgJSON(jsonstr,timestamp ,nonce)
    encrypt_body_str = json.dumps(encrypt_body)
    encrypt_body_str_utf8 = json.dumps(encrypt_body).encode('UTF-8')
    # 发送数据
    httpClient = None
    try:
        #params = urllib.urlencode(encrypt_body_str.encode('UTF-8'))
        headers = {"Content-type": "application/json"}
        #httpClient = httplib.HTTPConnection("apitest.milijinfu.com", 80, timeout=30)
        #httpClient.request("POST", "/api/asset/importAsset.do", encrypt_body_str.encode('utf-8'), headers)

        if settings.MIFAN_DEBUG == True: 
            httpClient = httplib.HTTPConnection("apitest.milijinfu.com", 80, timeout=30)
        else:
            httpClient = httplib.HTTPConnection("api.milijinfu.com", 80, timeout=30)
        #httpClient = httplib.HTTPConnection("apitest.milijinfu.com", 80, timeout=30)
        #httpClient = httplib.HTTPConnection(settings.MIFAN_URL, 80, timeout=30)
        httpClient.request("POST", "/api/asset/status.do", encrypt_body_str.encode('utf-8'), headers)
        response = httpClient.getresponse()
        #print response.status
        #print response.reason
        resp = response.read()
        return resp
    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()
def send2mifan(repayment,s):
    timestamp =  str(int(time.time()))
    nonce = Prpcrypt.get_random_str_6() 
    #jsonstr = fill_order_data()
    jsonstr = fill_order_data_apply(repayment,s)
    print jsonstr
    encrypt_body = wxcpt.encryptMsgJSON(jsonstr,timestamp ,nonce)
    encrypt_body_str = json.dumps(encrypt_body) 
    print encrypt_body_str
    encrypt_body_str_utf8 = json.dumps(encrypt_body).encode('UTF-8')
    # 发送数据
    httpClient = None
    try:
        #params = urllib.urlencode(encrypt_body_str.encode('UTF-8'))
        headers = {"Content-type": "application/json"}
        if settings.MIFAN_DEBUG == True: 
            httpClient = httplib.HTTPConnection("apitest.milijinfu.com", 80, timeout=30)
        else:
            httpClient = httplib.HTTPConnection("api.milijinfu.com", 80, timeout=30)
        #httpClient = httplib.HTTPConnection("apitest.milijinfu.com", 80, timeout=30)
        httpClient.request("POST", "/api/asset/importAsset.do", encrypt_body_str.encode('utf-8'), headers)

        #httpClient = httplib.HTTPConnection(send_url, 80, timeout=30)
        #httpClient.request("POST", "/api/asset/importAsset.do", encrypt_body_str.encode('utf-8'), headers)
        print httpClient.request
        response = httpClient.getresponse()
        #print response.status
        #print response.reason
        resp = response.read()
        print resp
        return resp
    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()
def getdata4mifan(resp):
#    encrypt_body = response.read()
    try:
        print "decode:::"
        print type(resp)
        print resp
        resp  = resp.replace('null','""')
        print resp
        encryptObject = json.loads(resp)
        #print encryptObject
        signature = encryptObject["signature"]
        #print signature
        encrypt = encryptObject["encrypt"]
        #print encrypt
        nonce = encryptObject["nonce"]
        #print nonce
        timestamp = encryptObject["timestamp"]
        #print timestamp
        code, result = wxcpt.decryptMsgJSON(encrypt,signature, timestamp, nonce)
        print "result"
        print result
        #print type(result)
        return result
    except Exception, e:
        print "getdata4mifan error"
        print e
if __name__ == "__main__":   
    resp =  send2mifan() 
    jsondata = getdata4mifan(resp) 
    print jsondata

