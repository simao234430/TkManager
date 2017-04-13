#encoding=utf-8
import sys
sys.path.append('gen-py')

from message_service import MessageService
from message_service.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def send_message(phone, msg):
    print phone, msg
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = MessageService.Client(protocol)

    transport.open()
    request = SendMessageRequest()
    request.phone_number = phone
    request.content = (u'%s' % msg.decode('utf-8')).encode('gbk')
    request.msg_type = 10
    print client.send_message(request)
    transport.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: %s phone_number message' % sys.argv[0]
    send_message(sys.argv[1], sys.argv[2])
