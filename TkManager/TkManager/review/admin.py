#-*- coding: utf-8 -*-
from django.contrib import admin
from TkManager.review.models import *
from TkManager.review.employee_models import *

class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['id', 'username']
    ordering = ['-id']

class ReviewAdmin(admin.ModelAdmin):
    search_fields = ['id', 'order__create_by__name', "reviewer__username"]
    readonly_fields = ['create_at']
    ordering = ['-id']

class LabelAdmin(admin.ModelAdmin):
    ordering = ['-id']

class CollectionRecordAdmin(admin.ModelAdmin):
    readonly_fields = ['create_at']
    ordering = ['-id']
    raw_id_fields = ["apply", "create_by"]

class EmplyeePermissionAdmin(admin.ModelAdmin):
    ordering = ['id']

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(CollectionRecord, CollectionRecordAdmin)
admin.site.register(EmplyeePermission, EmplyeePermissionAdmin)
