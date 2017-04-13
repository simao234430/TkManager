#-*- coding: utf-8 -*-
from django.contrib import admin
from TkManager.order.models import *
from TkManager.order.apply_models import *

class UserAdmin(admin.ModelAdmin):
  search_fields = ['id', 'name', 'phone_no']
  readonly_fields = ['create_time']
  ordering = ['-id']
  raw_id_fields = ["sub_channel", "invitation"]

class ApplyAdmin(admin.ModelAdmin):
  search_fields = ['id', 'create_by__name', 'create_by__phone_no']
  readonly_fields = ['create_at', 'last_commit_at']
  ordering = ['-id']
  raw_id_fields = ['create_by', 'repayment']

class ExtraApplyAdmin(admin.ModelAdmin):
  search_fields = ['id', 'apply__create_by__name', 'apply__create_by__phone_no']

class ContactInfoAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']
  raw_id_fields = ["owner"]

class ProfileAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']
  raw_id_fields = ["owner"]

class IdCardAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']
  raw_id_fields = ["owner"]

class BankCardAdmin(admin.ModelAdmin):
  search_fields = ['id', 'user__name', 'user__phone_no']
  ordering = ['-id']
  raw_id_fields = ["user"]

class ChsiAdmin(admin.ModelAdmin):
  search_fields = ['id', 'user__name', 'user__phone_no']
  readonly_fields = ['create_at']
  ordering = ['-id']
  raw_id_fields = ["user"]

class CheckStatusAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']
  raw_id_fields = ["owner"]

class ContractAdmin(admin.ModelAdmin):
  search_fields = ['contract_id', 'owner__name', 'owner__phone_no']
  raw_id_fields = ["owner"]

class FeedbackAdmin(admin.ModelAdmin):
  search_fields = ['id', 'apply__create_by__name', ]
  ordering = ['-id']

class SubChannelAdmin(admin.ModelAdmin):
  search_fields = ['name', 'id', 'type']
  ordering = ['-id']
#class ExtraPic(models.Model):
#  search_fields = ['id', 'name', 'phone_no']
#  ordering = ['-id']

class CheckApplyAdmin(admin.ModelAdmin):
  search_fields = ['id', 'create_by__username']
  readonly_fields = ['create_at']
  ordering = ['-id']
  raw_id_fields = ['create_by', 'repayment', 'repay_apply']

class UserPromotionCashflowAdmin(admin.ModelAdmin):
  search_fields = ['id', 'user__username']
  ordering = ['-id']

admin.site.register(User, UserAdmin)
admin.site.register(Apply, ApplyAdmin)
admin.site.register(ExtraApply, ExtraApplyAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(IdCard, IdCardAdmin)
admin.site.register(BankCard, BankCardAdmin)
admin.site.register(Chsi, ChsiAdmin)
admin.site.register(CheckStatus, CheckStatusAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(SubChannel, SubChannelAdmin)
admin.site.register(CheckApply, CheckApplyAdmin)
admin.site.register(UserPromotionCashflow, UserPromotionCashflowAdmin)
