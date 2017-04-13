# -*- coding: utf-8 -*-
from django.db import models
from TkManager.order.models import User

class GearmanJobRecord(models.Model):
    class Meta:
        db_table = u'gearmanjobrecord'

    def __unicode__(self):
        return u'%d)%s %s:%d '%(self.id, self.owner.name if self.owner else "", self.command_type, self.result)

    command_type = models.CharField(max_length=20, blank=True, null=True, help_text="任务类型")
    params = models.CharField(max_length=255, default=0, blank=True, null=True, help_text="提交参数")
    result = models.IntegerField(default=0, blank=True, null=True, help_text="执行结果")
    submit_time = models.DateTimeField(blank=True, null=True, help_text="提交时间")
    start_time = models.DateTimeField(blank=True, null=True, help_text="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, help_text="结束时间")
    owner =  models.ForeignKey(User, blank=True, null=True, help_text="关联用户")
