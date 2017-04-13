#encoding=utf-8

import sys, os
import traceback
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'gen-py'))

from bank_service import BankService
from bank_service.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class BankClient(object):
    def __init__(self, server_ip, server_port, debug=False):
        self.server_ip = server_ip
        self.server_port = server_port
        self.debug = debug

    def card_verify(self, card_id, owner_name, user_id, phone_number = ''):
        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BankService.Client(protocol)

        try:
            transport.open()
            request = CardVerifyRequest()
            request.card_id = card_id
            request.owner_name = owner_name
            request.user_id = user_id
            request.phone_number = phone_number
            send_result = client.card_verify(request)
            transport.close()
        except Exception,e:
            print e
            traceback.print_exc()
            return None
        return send_result

    def realtime_pay(self, amount, bank_code, account_cardid, account_name, user_id, pay_type):
        '''实时代扣，name需使用UTF8编码'''
        if self.debug:
            return CommonResponse(0, "ok")

        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BankService.Client(protocol)

        try:
            transport.open()
            request = RealtimePay()
            request.amount = amount
            request.bank_code = bank_code
            #account_name = account_name.decode('utf8').encode('gbk')
            account_name = account_name.encode('gbk')
            request.account_name = account_name
            request.account_cardid = account_cardid
            request.user_id = user_id
            request.pay_type = pay_type
            send_result = client.realtime_pay(request)
            transport.close()
        except Exception,e:
            print e
            traceback.print_exc()
            return None
        return send_result

    def realtime_payfor(self, amount, bank_code, account_cardid, account_name, user_id):
        '''实时代收，name需使用utf8编码'''
        if self.debug:
            return CommonResponse(0, "ok")

        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BankService.Client(protocol)

        try:
            transport.open()
            request = RealtimePayFor()
            request.amount = amount
            request.bank_code = bank_code
            #account_name = account_name.decode('utf8').encode('gbk')
            account_name = account_name.encode('gbk')
            request.account_name = account_name
            request.account_cardid = account_cardid
            request.user_id = user_id
            send_result = client.realtime_payfor(request)
            transport.close()
        except Exception,e:
            print e
            traceback.print_exc()
            return None
        return send_result

    def batch_pay(self, pay_list):
        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BankService.Client(protocol)

        try:
            request = BatchPay()
            pay_user_list = []
            for pay_info in pay_list:
                pay_request = RealtimePay()
                pay_request.amount = pay_info['amount']
                pay_request.bank_code = pay_info['bank_code']
                pay_request.account_cardid = pay_info['account_cardid']
                account_name = pay_info['account_name']
                account_name = account_name.decode('utf8').encode('gbk')
                pay_request.account_name = account_name
                pay_request.user_id = pay_info['user_id']
                pay_user_list.append(pay_request)
            request.pay_user_list = pay_user_list
            transport.open()
            send_result = client.batch_pay(request)
            return send_result
        except Exception,e:
            print e
            traceback.print_exc()
            return -1

if __name__ == '__main__':
    #client = BankClient('58.96.189.77', 9091)
    #client = BankClient('127.0.0.1', 9091)
    client = BankClient('121.43.146.31', 9091)
    #name1 = '刘小军'
    #name2 = '赵恒'
    #params = [{'amount':1, 'bank_code': '308', 'account_cardid': '6226097551182448', 'account_name': name1, 'user_id': 1},
    #        {'amount':2, 'bank_code': '308', 'account_cardid': '6214855711809711', 'account_name': name2, 'user_id': 2}]
    #print client.batch_pay(params)
    #print client.realtime_pay(1, '308', '6226097551182448', '刘小军', 1, 'mifan')
    res = client.realtime_pay(100, '308', '6214855711809711', '赵恒', 1, 'mifan')
    print res
    print res.err_msg.decode("utf-8")
    #result = client.card_verify('6226097551182448', '测试1', 1)
    #print result.bank_name, result.bank_type
