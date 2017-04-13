from TkManager.bind_thirdparty_server.bind_thirdparty_client import BindThirdpartyClient
#from TkManager.ip_server.IP_transform_client import IPClient

#TODO: change them to submodule !!
from TkManager.rc_server.rc_client import RCClient
from TkManager.tk_message_server.message_server.message_client import MessageClient
from TkManager.bank_server.bank_client import BankClient

from TkManager.risk_server.rm_client import RiskClient
#from gearman import GearmanClient

from django.conf import settings
import redis
import pymongo
from TkManager.common.tk_log_client import TkLog

bind_client = BindThirdpartyClient(settings.BIND_SERVER["HOST"], settings.BIND_SERVER["PORT"])
rc_client = RCClient(settings.RC_SERVER["HOST"], settings.RC_SERVER["PORT"])
message_client = MessageClient(settings.MESSAGE_SERVER["HOST"], settings.MESSAGE_SERVER["PORT"],logger = None)
#message_client = MessageClient(settings.MESSAGE_SERVER["HOST"], settings.MESSAGE_SERVER["PORT"], debug=settings.MESSAGE_SERVER["DEBUG"])
bank_client = BankClient(settings.BANK_SERVER["HOST"], settings.BANK_SERVER["PORT"], settings.BANK_SERVER["DEBUG"])
#ip_client = IPClient(settings.IP_SERVER["HOST"], settings.IP_SERVER["PORT"])
risk_client = RiskClient(settings.RISK_SERVER["HOST"], settings.RISK_SERVER["PORT"])

redis_client = redis.StrictRedis(host=settings.REDIS["HOST"], port=settings.REDIS["PORT"], password=settings.REDIS["AUTH"])
#gearman_client = GearmanClient(settings.GEARMAN_SERVERS)
if settings.MONGO["USER"]:
    mongo_uri = 'mongodb://%s:%s@%s:%d/%s' % (settings.MONGO["USER"], settings.MONGO["AUTH"],
                                          settings.MONGO["HOST"], settings.MONGO["PORT"],
                                          settings.MONGO["DB"])
else:
    mongo_uri = 'mongodb://%s:%d/%s' % (settings.MONGO["HOST"], settings.MONGO["PORT"],
                                          settings.MONGO["DB"])
mongo_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=30000)
from TkManager.push_server.push_server import push_client

#from pony.orm import Database
#db = Database()
push_client.db.bind('mysql', host=settings.DATABASES['default']['HOST'], passwd=settings.DATABASES['default']['PASSWORD'],
        user=settings.DATABASES['default']['USER'], db=settings.DATABASES['default']['NAME'])
push_client.db.generate_mapping(create_tables=False)
push_client_object = push_client.PushClient(settings.PUSH_SERVER["HOST"],settings.PUSH_SERVER["PORT"], redis_client, logger=TkLog())

