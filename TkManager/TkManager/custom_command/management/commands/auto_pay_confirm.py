from django.core.management.base import BaseCommand, CommandError
from django.db import models
#from placeholders import *
import os
import httplib
import urllib2
import urllib
    
class Command(BaseCommand):
     def handle(self, *args, **options):
         req = urllib2.Request('http://manager.hualahuala.com:8000/operation/auto_pay_confirm') 
         response = urllib2.urlopen(req) 
         the_page = response.read()
