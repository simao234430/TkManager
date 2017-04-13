#encoding=utf-8

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'gen-py'))

from bind_thirdparty import BindThirdpartyService
from bind_thirdparty.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class BindThirdpartyClient(object):
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def bind_thirdparty(self, uid, access_token, bind_type, user_id):
        request = BindThirdpartyRequest()
        request.uid = uid
        request.access_token = access_token
        request.bind_type = bind_type
        request.user_id = user_id

        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BindThirdpartyService.Client(protocol)

        try:
            transport.open()
            send_result = client.bind_thirdparty(request)
            transport.close()
        except Exception,e:
            print e
            return None
        print 'bind done'
        return send_result

    def send_captcha(self, user_id, captcha):
        request = SendCaptchaRequest()
        request.user_id = user_id
        request.captcha = captcha

        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BindThirdpartyService.Client(protocol)
        try:
            transport.open()
            result = client.send_captcha(request)
            transport.close()
        except Exception,e:
            print e
            return None
        print 'send done'
        return (result.retcode, result.captcha, result.errmsg)

    def rebind_chsi(self, user_id):
        transport = TSocket.TSocket(self.server_ip, self.server_port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = BindThirdpartyService.Client(protocol)
        try:
            transport.open()
            result = client.rebind_chsi(user_id)
            transport.close()
        except Exception,e:
            print e
            return None
        print 'rebind done'
        return (result.retcode, result.captcha, result.errmsg)


if __name__ == '__main__':
    #client = BindThirdpartyClient('127.0.0.1', 9092)
    client = BindThirdpartyClient('121.43.146.31', 9092)
    #client = BindThirdpartyClient('58.96.189.77', 9092)
    #client.bind_thirdparty('088972865925', '', 4, 1846)
    #client.bind_thirdparty('justice07@qq.com', 'zz13579', 3, 22)
    print "rebind chsi:", client.rebind_chsi(64)
    #client.bind_thirdparty('13205811255', 'shadow', 3, 22)
    print "send chsi:", client.send_captcha(64, 'prifed')
