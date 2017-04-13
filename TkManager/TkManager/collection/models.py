# -*- coding: utf-8 -*-
'''
    借贷相关model 放在催收目录了。。
    RepaymentInfo : 用户的借贷信息
    InstallmentDetailInfo : 用户的每一期借贷详情
    BankRecord : 每一笔银行扣款/打款记录
'''
from django.db import models

from TkManager.order.models import User, BankCard

from TkManager.review.employee_models import Employee
from TkManager.common.tk_log_client import TkLog

class RepaymentInfo(models.Model):
    REJECT = -3
    DELETED = -2
    TO_BE_COMFIRMED = -1
    PAYING = 0
    REPAYING = 1
    OVERDUE = 2
    DONE = 3
    CHECKING = 4
    PAYED =5
    PASS = 6
    PRE_DONE = 7
    OVERDUE_DONE = 8

    repay_status_type_t = (
        (-3, '拒绝'),
        (-2, '已删除'),
        (-1, '合同待确认'),
        (0, '放款中'),
        (1, '还款中'),
        (2, '逾期'),
        (3, '已完成'),
        (4, '审核中'),
        (5, '已放款'),
        (6, '审核通过'),
        #----后面两个状态仅供InstallmentDetailInfo.repay_status使用
        (7, '---'),
        (8, '逾期完成'),
    )

    strategy_type_t = (
        (1, u'28天一次性'),
        (2, u'21天一次性'),
        (3, u'14天一次性'),
        (4, u'7天一次性'),
        (5, u'28天分期'),
        (6, u'21天分期'),
        (7, u'14天分期'),
        (10, u'21天'),
        (11, u'28天'),
        (12, u'三个月'),
        (13, u'六个月'),
        (14, u'十二个月'),
        (15, u'学生三个月'),
    )

    XINTUO = 1
    MIFAN = 2
    capital_type_t = (
        (XINTUO, u'信托'),
        (MIFAN, u'米饭'),
    )

    class Meta:
        db_table = u'repaymentinfo'

    def __unicode__(self):
        return u'%d)%s %d %s'%(self.id, self.user.name, self.apply_amount/100, self.get_repay_status_display())

    order_number = models.CharField(max_length=255, help_text='订单号') #订单号，全局唯一
    repay_status = models.IntegerField(choices=repay_status_type_t, help_text='还款状态')
    apply_amount = models.IntegerField(default=0, help_text='申请金额')
    exact_amount = models.IntegerField(default=0, help_text='实际打款金额')
    repay_amount = models.IntegerField(default=0, help_text='需还金额')
    rest_amount = models.IntegerField(default=0, help_text='剩余未还金额')
    user = models.ForeignKey(User, help_text='贷款人')
    strategy_id = models.IntegerField(choices=strategy_type_t, help_text='策略id')
    capital_channel_id = models.IntegerField(choices=capital_type_t, help_text='资金渠道', default=MIFAN)

    bank_card = models.ForeignKey(BankCard, help_text='此次交易所属的银行卡')
    reason = models.CharField(max_length=255, blank=True, null=True, help_text='用途')
    apply_time = models.DateTimeField(auto_now_add=True, help_text='申请时间')
    first_repay_day = models.DateTimeField(blank=True, null=True, help_text='打款日 (计息日)')
    next_repay_time = models.DateTimeField(blank=True, null=True, help_text='下次还款日')
    last_time_repay = models.DateTimeField(blank=True, null=True, help_text='最后一次还款日期')

    score = models.IntegerField(default=0, help_text='使用积分')

    def get_repayments_days(self):
        if self.strategy_id == 1 or self.strategy_id == 5:
            return 28
        elif self.strategy_id == 2 or self.strategy_id == 6:
            return 21
        elif self.strategy_id == 3 or self.strategy_id == 7:
            return 14
        elif self.strategy_id == 4:
            return 7
        else:
            return -1

    def get_repayments_instalments(self):
        if self.strategy_id >= 1 and self.strategy_id <= 4:
            return 1
        elif self.strategy_id == 5:
            return 4
        elif self.strategy_id == 6:
            return 3
        elif self.strategy_id == 7:
            return 2
        else:
            return -1

    def get_strategy_rate(self):
        if self.strategy_id >= 1 and self.strategy_id <= 4:
            return 0.27
        elif self.strategy_id >= 5 and self.strategy_id <= 7:
            return 0.24
        else:
            return -1


    def get_first_installments_amount(self):
        total = self.apply_amount
        return total - total / self.get_repayments_instalments() * (self.get_repayments_instalments() - 1)

class InstallmentDetailInfo(models.Model):

    repay_status_type_t = (
        (-3, '拒绝'),
        (-2, '已删除'),
        (-1, '合同待确认'),
        (0, '放款中'),
        (1, '还款中'),
        (2, '逾期'),
        (3, '已完成'),
        (4, '审核中'),
        (5, '已放款'),
        (6, '审核通过'),
        #----后面两个状态仅供InstallmentDetailInfo.repay_status使用
        (7, '---'),
        (8, '逾期完成'),
    )

    REPAY_TYPE_AUTO = 1
    REPAY_TYPE_ALIPAY = 3
    REPAY_TYPE_PUB = 4
    repay_channel_type_t = (
        (0, '---'),
        (1, '自动扣款'),
        (2, '手动扣款'),
        (3, '支付宝'),
        (4, '对公还款'),
    )

    repay_app_type_t = (
        (1, '按时还款'),
        (2, '催收m1'),
        (3, '催收m2'),
        (4, '催收m3'),
        (5, '委外'),
    )

    class Meta:
        db_table = u'installmentdetailinfo'

    def __unicode__(self):
        #return u'%s)%d-%d '%(self.repayment.user.name, self.repayment, self.installment_number)
        return u'%d)%s: %d-%d '%(self.id, self.repayment.user.name, self.repayment.id, self.installment_number)

    repayment = models.ForeignKey(RepaymentInfo)                                   #所属的交易
    installment_number = models.IntegerField()                                     #第几期
    should_repay_time = models.DateTimeField()                                     #应还日期
    real_repay_time = models.DateTimeField(blank=True, null=True)                  #实际还款日期
    should_repay_amount = models.IntegerField(help_text="应还金额")                #应还金额
    repay_overdue = models.IntegerField(default=0, help_text="罚金")               #罚金
    real_repay_amount = models.IntegerField(default=0, help_text="实际还款金额")   #实际还款金额
    reduction_amount = models.IntegerField(default=0, help_text="减免金额")        #减免金额

    repay_status = models.IntegerField(choices=repay_status_type_t)       #归还状态
    repay_channel = models.IntegerField(choices=repay_channel_type_t)     #还款途径，比如1表示自助扣款，2表示XX方式还款

class BankRecord(models.Model):
    class Meta:
        db_table = u'bankrecord'
    amount = models.IntegerField(int)                         #扣款金额
    banck_code = models.CharField(max_length=20)              #银行卡号
    status = models.IntegerField()                            #扣款状态
    create_at = models.DateTimeField(auto_now_add=True)       #扣款时间
    related_record = models.ForeignKey(InstallmentDetailInfo) #对应分期记录
