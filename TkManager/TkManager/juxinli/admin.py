#-*- coding: utf-8 -*-
from django.contrib import admin

from TkManager.juxinli.models import *
from TkManager.juxinli.report_model import *

class GearmanJobRecordAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class PhoneBasicAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class PhoneCallAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class PhoneNetAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class PhoneSmsAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class PhoneTransactionAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class PersonAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class DataSourceAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class ApplicationCheckAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class BehaviorCheckAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class ContactRegionAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class ContactListAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class DeliverAddressAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class EbusinessExpenseAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class CellBehaviorAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class RecentNeedAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class TripInfoAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class CollectionContactAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

class MainServiceAdmin(admin.ModelAdmin):
  search_fields = ['id', 'owner__name', 'owner__phone_no']
  ordering = ['-id']

admin.site.register(PhoneBasic, PhoneBasicAdmin)
#admin.site.register(PhoneCall, PhoneCallAdmin)
admin.site.register(PhoneNet, PhoneNetAdmin)
admin.site.register(PhoneSms, PhoneSmsAdmin)
admin.site.register(PhoneTransaction, PhoneTransactionAdmin)
admin.site.register(GearmanJobRecord, GearmanJobRecordAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(ApplicationCheck, ApplicationCheckAdmin)
admin.site.register(BehaviorCheck, BehaviorCheckAdmin)
admin.site.register(ContactRegion, ContactRegionAdmin)
admin.site.register(ContactList, ContactListAdmin)
admin.site.register(DeliverAddress, DeliverAddressAdmin)
admin.site.register(EbusinessExpense, EbusinessExpenseAdmin)
admin.site.register(CellBehavior, CellBehaviorAdmin)
admin.site.register(RecentNeed, RecentNeedAdmin)
admin.site.register(TripInfo, TripInfoAdmin)
admin.site.register(CollectionContact, CollectionContactAdmin)
admin.site.register(MainService, MainServiceAdmin)


