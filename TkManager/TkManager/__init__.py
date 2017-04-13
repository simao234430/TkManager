from django.conf import settings
#from TkManager.common.tk_log_client import TkLog
#import logging
#
#host = settings.LOG_SERVER["HOST"]
#port = settings.LOG_SERVER["PORT"]
#name = settings.LOG_SERVER["LOG_NAME"]
#filename = settings.LOG_SERVER["LOG_FILE"]
#TkLog().init_log_include_local_file(name, logging.DEBUG, host, port,filename, 1024)
#TkLog().info('Starting the tk_manager log ...')
#TkLog().info("init settings done.")

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'TkManager'))
#RedisClient()

import threading

def test():
    print "I was at the"
    import schedule
    import time
    def job():
        print("I'm working...")

    schedule.every(1).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

#t1 = threading.Thread(target=test)
#t1.setDaemon(True)
#t1.start()
