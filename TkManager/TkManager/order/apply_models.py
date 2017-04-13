# -*- coding: utf-8 -*-
from django.db import models
from TkManager.order.models import User
from TkManager.collection.models import RepaymentInfo
from TkManager.review.employee_models import Employee

# 信息审核申请
class Apply(models.Model):
    WAIT = '0'
    WAIT_DATA = 'w'
    PROCESSING = 'i'
    PASS = 'y'
    BACK = 'r'
    REJECT = 'n'
    ASK_MONEY = '1'
    PAY_SUCCESS = '2'
    PAY_FAILED = '3'
    SEND_MIFAN_FAIL= '4'
    COLLECTION_SUCCESS = '8'
    MECHINE_VERIFIED = 'a'
    MECHINE_REJECT = 'b'
    REPAY_SUCCESS = '9'
    REPAY_FAILED = 'c'
    PARTIAL_SUCCESS = 'd'
    CANCELED = 'e'
    WAIT_CHECK = 'k'

    apply_status_t = (
        (WAIT, u'待处理'),
        (WAIT_DATA, u'等待数据'),
        (PROCESSING, u'处理中'),
        (PASS, u'通过'),
        (BACK, u'返回修改'),
        (REJECT, u'拒绝'),
        (WAIT_CHECK, u'待复核'),

        (ASK_MONEY, u'请款中'),
        (PAY_SUCCESS, u'打款成功'),
        (PAY_FAILED, u'打款失败'),
        (SEND_MIFAN_FAIL, u'请求米饭放款失败'),
        (COLLECTION_SUCCESS, u'催收完成'),
        (MECHINE_VERIFIED, u'机器审核'), # 额度提升中的自动审核
        (MECHINE_REJECT, u'机器拒绝'), # 第一轮风控自动拒绝
        (REPAY_SUCCESS, u'扣款成功'),
        (REPAY_FAILED, u'扣款失败'),
        (PARTIAL_SUCCESS, u'部分成功'),
        (CANCELED, u'取消订单'), # 已注销用户
    )

    NONE_TYPE = 'n'

    PAY_LOAN = 'l'
    COLLECTION_M0 = 'a'
    COLLECTION_M1 = 'b'
    COLLECTION_M2 = 'c'
    COLLECTION_M3 = 'd'
    COLLECTION_M4 = 'e'
    REPAY_LOAN = 'p'
    BASIC = '0'
    WEIBO = '1'
    RENREN = '2'
    PHONE_CALL = '3'
    CREDIT = '4'
    BANK_FLOW = '5'
    OTHER = '6'
    EBUSINESS = '7'
    ALIPAY = '9'
    COMMODITY = 'f'
    SECOND_LOAN = 's'

    apply_type_t = (
        (NONE_TYPE, 'none'),
        (PAY_LOAN, u'提现'),

        (COLLECTION_M0, u'催收m0'),
        (COLLECTION_M1, u'催收m1'),
        (COLLECTION_M2, u'催收m2'),
        (COLLECTION_M3, u'催收m3'),
        (COLLECTION_M4, u'催收委外'),

        (REPAY_LOAN, u'还款'),
        (BASIC, u'基本信息'),
        (WEIBO, u'微博'),
        (RENREN, u'人人'),
        (PHONE_CALL, u'通话记录'),
        (CREDIT, u'征信报告'),
        (BANK_FLOW, u'银行流水'),
        (OTHER, u'其他'),
        (EBUSINESS, u'淘宝/京东'),
        (ALIPAY, u'支付宝'),
        (COMMODITY, u'服务贷'),
        (SECOND_LOAN, u'二次提现'),
    )

    class Meta:
        db_table = u'apply'

    create_by = models.ForeignKey(User, related_name="apply_create_by_user")
    create_at = models.DateTimeField(auto_now_add=True, help_text = "创建时间")
    last_commit_at = models.DateTimeField(blank=True, null=True, auto_now_add=True, help_text = "最近提交时间") # 打回后重新提交/ 在催收apply中用来作为用户的承诺还款时间
    finish_time = models.DateTimeField(blank=True, null=True, help_text="完成时间")

    money = models.IntegerField(help_text="相关金额", default=0)

    status = models.CharField(default="0", max_length = 1, choices = apply_status_t)
    type = models.CharField(default="n", max_length = 1, choices = apply_type_t)
    repayment = models.ForeignKey(RepaymentInfo, blank=True, null=True)

    pic = models.CharField(max_length = 64, help_text="相关图片", blank=True, null=True)

    def __unicode__(self):
        return u'%d)%s %s %s'%(self.id, self.create_by.name, self.get_type_display(), self.get_status_display())

# 催收运营提给财务复核的申请
# 不要问我为什么这个表拆开了，因为上面那一堆表本来就应该拆开，我是偷懒才把上面那些Apply才丢在了一张表里面
class CheckApply(models.Model):
    WAIT = '0'
    CHECK_SUCCESS = 'k'
    CHECK_FAILED = 't'

    apply_status_t = (
        (WAIT, u'等待复核'),
        (CHECK_SUCCESS, u'复核成功'),
        (CHECK_FAILED, u'复核失败'),
    )

    CHECK_ALIPAY = 'f'
    CHECK_TOPUBLIC = 'g'

    apply_type_t = (
        (CHECK_ALIPAY, u'支付宝转账'),
        (CHECK_TOPUBLIC, u'对公转账'),
    )

    REPAY_INSTALLMENT = 0
    REPAY_REPAYMENT = 0
    REPAY_CUSTOM = 0

    repay_type_t = (
        (REPAY_INSTALLMENT, u'期款'),
        (REPAY_REPAYMENT, u'全款'),
        (REPAY_CUSTOM, u'自定义'),
    )

    create_by = models.ForeignKey(Employee, related_name="apply_create_by_user")
    create_at = models.DateTimeField(auto_now_add=True, help_text = "创建时间")
    finish_time = models.DateTimeField(blank=True, null=True, help_text="完成时间")

    money = models.IntegerField(help_text="相关金额", default=0)

    status = models.CharField(default="0", max_length = 1, choices = apply_status_t)
    type = models.CharField(default="n", max_length = 1, choices = apply_type_t)
    notes = models.CharField(max_length = 255, help_text="备注", default="", null=True, blank=True)
    repayment = models.ForeignKey(RepaymentInfo, blank=True, null=True)
    repay_type = models.IntegerField(help_text="结清类型", default=0, choices = repay_type_t)
    installment = models.IntegerField(help_text="当前期数", default=0)
    repay_apply = models.ForeignKey(Apply, help_text="申请订单", blank=True, null=True)

    pic = models.CharField(max_length = 255, help_text="相关图片", blank=True, null=True)

    class Meta:
        db_table = u'check_apply'

    def __unicode__(self):
        return u'%d)%s %s %s'%(self.id, self.create_by.username, self.get_type_display(), self.get_status_display())


class ExtraApply(models.Model):
    class Meta:
        db_table = u'extraapply'

    apply = models.OneToOneField(Apply, primary_key=True)
    review_label = models.CharField(max_length=63, default="", blank=True, null=True, help_text="审批标签")
    extra_pic = models.CharField(max_length=511, default="", blank=True, null=True, help_text="相关图片")
    message_1 = models.CharField(max_length=255, default="", blank=True, null=True, help_text="打回信息1")
    message_2 = models.CharField(max_length=255, default="", blank=True, null=True, help_text="打回信息2")
    message_3 = models.CharField(max_length=255, default="", blank=True, null=True, help_text="打回信息3")
    message_4 = models.CharField(max_length=255, default="", blank=True, null=True, help_text="打回信息4")
    message_5 = models.CharField(max_length=255, default="", blank=True, null=True, help_text="打回信息5")
    message_6 = models.CharField(max_length=255, default="", blank=True, null=True, help_text="打回信息6")

    def __unicode__(self):
        return u')%s'%(self.apply.create_by.name)
