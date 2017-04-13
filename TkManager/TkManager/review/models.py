# -*- coding: utf-8 -*-
from django.db import models

from TkManager.order.apply_models import Apply, ExtraApply
from TkManager.review.employee_models import Employee
from TkManager.common.tk_log_client import TkLog

from django.dispatch import receiver
from django.db.models.signals import post_migrate, post_syncdb

review_status_t = (
    ('w', u'等待审批'),
    ('i', u'审批中'),
    ('r', u'打回修改'),
    ('y', u'通过 '),
    ('n', u'拒绝 '),
)

REVIEW_STATUS_PASS = 0xff

class Review(models.Model):
    order = models.ForeignKey(Apply, help_text="审批订单")
    reviewer = models.ForeignKey(Employee, related_name="reviewer", help_text="当前审批人员")
    reviewer_done = models.ForeignKey(Employee, related_name="reviewer_done", help_text="完成审批人员", blank=True, null=True) #废弃了 一个reviewer对应一个review
    create_at = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)

    review_res = models.CharField(max_length=1, help_text="审批结果", default="n", choices=review_status_t)
    money = models.IntegerField(help_text="相关金额", default=0)

    labels = models.ManyToManyField('Label', help_text="审批标签")

    def __unicode__(self):
        return u'%s)%s - %s'%(self.reviewer.username ,self.order.create_by.name, self.order.id)

    def status_to_int(self, status):
        if status == 'y' : #通过
            return 3
        elif status == 'n' : #拒绝
            return 2
        elif status == 'r' : #打回修改
            return 0
        elif status == 'i' : #审批中
            return 1
        else:
            return -1

    def set_label_list(self, label_list, apply):
        if len(label_list) == 0:
            return
        labels = label_list.split(",")
        for label in labels:
            #print label
            l = Label.objects.get(label_id = label)
            if l.label_id == 402: #无借款用途
                extra_apply = ExtraApply.objects.filter(apply=apply)
                if len(extra_apply) == 0:
                    extra_apply = ExtraApply()
                    extra_apply.apply = apply
                else:
                    extra_apply = extra_apply[0]
                extra_apply.review_label = "usage"
                extra_apply.save()
            self.labels.add(l)
        self.save()

    def get_label_list(self):
        return self.labels

    # 两位一个状态，从低到高依次是个人基本信息（姓名、身份证号码）、联系人信息、学信网、身份证照片
    def to_apply_status(self):
        try:
            status = 0
            records = ReviewRecord.objects.filter(review = self, review_type = 'i').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 0

            records = ReviewRecord.objects.filter(review = self, review_type = 'f').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 2

            records = ReviewRecord.objects.filter(review = self, review_type = 'c').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 4

            records = ReviewRecord.objects.filter(review = self, review_type = 'p').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 6

            records = ReviewRecord.objects.filter(review = self, review_type = 'o').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 8

            records = ReviewRecord.objects.filter(review = self, review_type = 'q').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 10

            #通话记录暂时全部通过
            status |=  0x3 << 12

            records = ReviewRecord.objects.filter(review = self, review_type = 'w').order_by("-id")
            if len(records) <= 0:
                return -1
            status |= self.status_to_int(records[0].review_status) << 14

            print "to new status:", status
            return status
        except Exception, e:
            print e
            return -1;

review_record_type_t = (
    ('n', u'无'),
#----------基本信息的审批记录类型
    ('i', u'身份信息'),
    ('p', u'身份证照片正面'),
    ('o', u'身份证照片反面'),
    ('q', u'手持身份证照片'),
    ('c', u'学籍信息'),
    ('f', u'联系人信息'),
    ('w', u'工作信息'),
    ('b', u'银行卡信息'),
    ('a', u'用户行为信息'),
)

review_record_status_t = (
    ('r', u'打回修改'),
    ('y', u'通过 '),
    ('n', u'拒绝 '),
)

class ReviewRecord(models.Model):
    review_type = models.CharField(max_length=1, help_text="信息类型", default="n", choices=review_record_type_t)
    review_status = models.CharField(max_length=1, help_text="审批结果", default="n", choices=review_record_status_t)
    review_note = models.CharField(max_length=255, blank=True, null=True, help_text="审批注释")
    review_message = models.CharField(max_length=255, blank=True, null=True, help_text="返回用户提示")
    create_at = models.DateTimeField(auto_now_add=True)

    review = models.ForeignKey(Review)


label_type_t = (
    (0, "拒绝标签"),
    (1, "数据标签"),
)

sub_value_type_t = (
    (0, "---"),
    (1, "真实"),
    (2, "虚假"),
    (3, "未验证"),
    (4, "无目的"),
    (5, "有目的"),
    (6, "是"),
    (7, "否"),
)

model_type_t = (
    ('n', u'无'),
    ('id', u'身份信息'),
    ('front_pic', u'身份证照片正面'),
    ('back_pic', u'身份证照片反面'),
    ('hand_pic', u'手持身份证照片'),
    ('chsi', u'学籍信息'),
    ('contact', u'联系人信息'),
    ('work', u'工作信息'),
    ('bankcard', u'银行卡信息'),
    ('action', u'用户行为信息'),
)

class Label(models.Model):
    name = models.CharField(max_length=63, help_text="标签名称")
    label_id = models.IntegerField(help_text="标签id", unique=True)
    label_type = models.IntegerField(choices=label_type_t, help_text="标签类型")
    section = models.CharField(max_length=15, help_text="所属模块", default="none", choices=model_type_t)
    sub_value = models.IntegerField(default=0, choices=sub_value_type_t, help_text="数据标签的结果")

    def __unicode__(self):
        if self.sub_value == 0:
            return u'%d)%s - %s'%(self.label_id, self.get_section_display(), self.name)
        else:
            return u'%d)%s - %s:%s'%(self.label_id, self.get_section_display(), self.name, self.get_sub_value_display())

    def display(self):
        return self.__unicode__()

    def is_reject(self):
        if self.sub_value == 0 or self.sub_value == 2:
            return True
        else:
            return False

    @staticmethod
    def get_all_label():
        labels_all = Label.objects.all()
        labels = {"check":{}, "radio":{}}
        for label in labels_all:
            if label.label_type == 0:
                if not label.section in labels["check"]:
                    labels["check"][label.section] = []
                #labels["check"][label.section][label.name] = label.label_id
                sub_label = {}
                sub_label["name"] = label.name
                sub_label["value"] = label.label_id
                labels["check"][label.section].append(sub_label)
            elif label.label_type == 1:
                if not label.section in labels["radio"]:
                    labels["radio"][label.section] = {}
                if not label.name in labels["radio"][label.section]:
                    labels["radio"][label.section][label.name] = {}
                    sub_label = {}
                    sub_label["name"] = label.get_sub_value_display()
                    sub_label["value"] = label.label_id
                    sub_label["sub_value"] = label.sub_value
                    labels["radio"][label.section][label.name]["name"] = label.name
                    labels["radio"][label.section][label.name]["sub_value"] = [sub_label]
                else:
                    sub_label = {}
                    sub_label["name"] = label.get_sub_value_display()
                    sub_label["value"] = label.label_id
                    sub_label["sub_value"] = label.sub_value
                    labels["radio"][label.section][label.name]["sub_value"].append(sub_label)
                #labels["radio"][label.section][label.name].append(sub_label)
        #print labels
        return labels

#@receiver(post_migrate)#, sender=EmplyeePermission)
def gen_default_label(sender, **kwargs):
    #Label.objects.all().delete()
    Label(label_id=101, name="不符合进件政策", label_type=0, section='id').save()
    Label(label_id=102, name="冒名申请", label_type=0, section='id').save()
    #Label(label_id=102, name="家庭位置异常", label_type=1, section='id').save()
    Label(label_id=103, name="还款意愿差", label_type=0, section='id').save()
    Label(label_id=104, name="三方负面信息", label_type=0, section='id').save()
    Label(label_id=105, name="其他", label_type=0, section='id').save()

    Label(label_id=201, name="已离职", label_type=0, section='work').save()
    Label(label_id=202, name="单位虚假", label_type=0, section='work').save()
    Label(label_id=203, name="三方负面消息", label_type=0, section='work').save()
    #Label(label_id=100, name="工作位置异常", label_type=1, section='d').save()

    Label(label_id=301, name="父母是否虚假", label_type=1, section='contact', sub_value=1).save()
    Label(label_id=302, name="父母是否虚假", label_type=1, section='contact', sub_value=2).save()
    Label(label_id=304, name="联系人重复出现", label_type=0, section='contact').save()
    Label(label_id=305, name="代偿意愿差", label_type=0, section='contact').save()
    Label(label_id=306, name="多次无法确认", label_type=0, section='contact').save()
    Label(label_id=307, name="三方负面消息", label_type=0, section='contact').save()

    Label(label_id=308, name="催收通话记录", label_type=0, section='contact').save()
    Label(label_id=309, name="本人出现在通话记录", label_type=0, section='contact').save()
    Label(label_id=310, name="与父母无联系", label_type=0, section='contact').save()
    Label(label_id=311, name="无通讯录、通话记录、详单", label_type=0, section='contact').save()
    Label(label_id=312, name="与多家贷款公司联系异常", label_type=0, section='contact').save()
    Label(label_id=314, name="详单是否虚假", label_type=1, section='contact', sub_value=1).save()
    Label(label_id=315, name="详单是否虚假", label_type=1, section='contact', sub_value=2).save()
    Label(label_id=316, name="电话实名不匹配", label_type=0, section='contact').save()

    Label(label_id=401, name="机器ID重复", label_type=0, section='action').save()
    Label(label_id=402, name="借款目的", label_type=1, section='action', sub_value=4).save()
    Label(label_id=403, name="借款目的", label_type=1, section='action', sub_value=5).save()
    Label(label_id=405, name="是否容许再进件", label_type=1, section='action', sub_value=6).save()
    Label(label_id=406, name="是否容许再进件", label_type=1, section='action', sub_value=7).save()

    Label(label_id=501, name="和他人银行卡重复", label_type=0, section='bankcard').save()

    Label(label_id=601, name="身份证虚假", label_type=0, section='front_pic').save()

    Label(label_id=701, name="身份证虚假", label_type=0, section='back_pic').save()

    Label(label_id=801, name="身份证虚假", label_type=0, section='hand_pic').save()

    Label(label_id=901, name="学信网问题", label_type=0, section='chsi').save()
    Label(label_id=902, name="电商数据问题", label_type=0, section='chsi').save()

class CollectionRecord(models.Model):

    COLLECTION = '0'
    MESSAGE = '1'
    REPAY = '2'
    DISPATCH = '3'
    DISCOUNT = '4'
    COMMENT = '5'
    CHECK_BACK = '6'
    CHECK_NOTES = '7'
    collection_record_type_t = (
        (COLLECTION, u'催记'),
        (MESSAGE, u'短信'),
        (REPAY, u'扣款'),
        (DISPATCH, u'分配'),
        (DISCOUNT, u'减免'),
        (COMMENT, u'备注'),
        (CHECK_BACK, u'财务打回'),
        (CHECK_NOTES, u'财务备注')
    )

    SELF = '0'
    THIRD = '1'
    OTHER = '2'
    object_type_t = (
        (SELF, u'本人'),
        (THIRD, u'三方'),
        (OTHER, u'三方'),
    )

    record_type = models.CharField(max_length=1, help_text="信息类型", default="0", choices=collection_record_type_t)
    object_type = models.CharField(max_length=15, help_text="催收对象", default="0", choices=object_type_t)
    collection_note = models.CharField(max_length=255, blank=True, null=True, help_text="催收注释")
    promised_repay_time = models.DateTimeField(help_text="承诺还款时间", blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    create_by = models.ForeignKey(Employee, help_text="催收人员")
    apply = models.ForeignKey(Apply)

    def __unicode__(self):
        return u'%s)%s - %s'%(self.create_by.username ,self.apply.create_by.name, self.get_record_type_display())
