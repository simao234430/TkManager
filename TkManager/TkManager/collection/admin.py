#-*- coding: utf-8 -*-
from django.contrib import admin
from TkManager.collection.models import *
from TkManager.collection.strategy import *
#from django_extensions.admin import ForeignKeyAutocompleteAdmin

class RepaymentInfoAdmin(admin.ModelAdmin):
#class RepaymentInfoAdmin(ForeignKeyAutocompleteAdmin):
  search_fields = ['id', 'user__phone_no', 'user__name']
  ordering = ['-id']
  #raw_id_fields = ("user",)
  raw_id_fields = ["user", "bank_card"]

class InstallmentDetailInfoAdmin(admin.ModelAdmin):
  search_fields = ['id', 'repayment__user__phone_no', 'repayment__user__name']
  ordering = ['-id']
  raw_id_fields = ["repayment"]

class StrategyAdmin(admin.ModelAdmin):
  search_fields = ['strategy_id']
  ordering = ['strategy_id']

admin.site.register(RepaymentInfo, RepaymentInfoAdmin)
admin.site.register(InstallmentDetailInfo, InstallmentDetailInfoAdmin)
admin.site.register(Strategy, StrategyAdmin)
