#encoding=utf-8

import sys
import os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'gen-py'))

from email.mime.text import MIMEText

from message_service import MessageService
from message_service.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

class MessageClient(object):
    def __init__(self, server_ip, server_port, timeout_ms = 500, debug=False):
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout_ms = timeout_ms
        self.debug = debug

    def send_message(self, phone_number, content, msg_type):
        if self.debug:
            return True

        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport.setTimeout(self.timeout_ms)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = MessageService.Client(protocol)

        try:
            transport.open()
            request = SendMessageRequest()
            request.phone_number = phone_number
            request.content = content
            request.msg_type = msg_type
            send_result = client.send_message(request)
            transport.close()
        except Exception,e:
            print e
            return False
        if send_result == 0:
            return True
        return False

    def send_email(self, receiver, content):
        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport.setTimeout(self.timeout_ms)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = MessageService.Client(protocol)

        try:
            transport.open()
            request = SendEmailRequest()
            request.receiver = receiver
            request.content = content
            send_result = client.send_email(request)
            transport.close()
        except:
            return False
        if send_result == 0:
            return True
        return False

    def send_contract(self, url, user_id, to_email):
        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport.setTimeout(self.timeout_ms)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = MessageService.Client(protocol)

        try:
            transport.open()
            request = SendContractRequest()
            request.contract_url = url
            request.user_id = user_id
            request.to_email = to_email
            send_result = client.send_contract(request)
            transport.close()
        except Exception,e:
            print e
            return False
        if send_result == 0:
            return True
        return False


if __name__ == '__main__':
    client = MessageClient('127.0.0.1', 9090, 500)
    url = 'http://mmec.yunsign.com/mmecenterprise/?index.php&g=Home&m=InterfaceType&a=downContract&info={"orderID": "2015051113462924", "appID": "3212sg4G2y", "time": 1431758803, "md5": "47bf9cc366d6e129dd44af5d9fcdaf2c", "ucid": "24"}'
    print client.send_contract(url, 24, 'liuxiaojun.333@qq.com')

    #print client.send_email('liuxiaojun.333@qq.com', '')
