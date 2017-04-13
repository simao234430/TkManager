#encoding=utf-8
from datetime import datetime, timedelta
from TkManager.common import tk_date
from django.db import models
import math

class CapitalChannel(models.Model):
    name = models.CharField(max_length=255, help_text="")                  # 渠道名称
    capital_intrest = models.FloatField(help_text="")     # 请款利率 (根据这个利率计算出请款金额)
    capital_channel = models.IntegerField(help_text="")       # 资金渠道 1:信托 2:米饭
    risk_reserve = models.FloatField(help_text="")        # 风险计提准备金率

class Strategy(models.Model):
    strategy_id = models.IntegerField(primary_key=True, help_text="唯一ID")
    pre_factorage = models.FloatField(help_text="前置手续费率")
    post_factorage = models.FloatField(help_text="后置手续费率")
    interest = models.FloatField(help_text="利率(后置)")
    installment_count = models.IntegerField(help_text="分期 期数")
    installment_days = models.IntegerField(help_text="一期的天数/月数")
    installment_type = models.IntegerField(help_text="第一位 是否可以重复借贷， 第二位 是否可以提前还款  第三位 日利率计算  第四位 按天计算还款日/每月定时还款")
    overdue_factorage = models.IntegerField(help_text="逾期手续费")
    overdue_interest = models.FloatField(help_text="逾期m1利率 (日)")
    overdue_m2_interest = models.FloatField(help_text="逾期m2利率 (日)")
    overdue_m3_interest = models.FloatField(help_text="逾期m3利率 (一次性 委外)")
    m1_days = models.IntegerField(help_text="m1计算时间")
    m2_days = models.IntegerField(help_text="m2计算时间")
    m3_days = models.IntegerField(help_text="m3计算时间")
    discount = models.IntegerField(help_text="折扣 (历史残留 看起来暂时没用了)")
    description = models.CharField(max_length=255, help_text="描述文字 (返回前端展示)")
    strategy_description = models.CharField(max_length=255, help_text="策略描述文字 (返回前端展示)")
    active = models.BooleanField(default=False, help_text="是否使用")

    class Meta:
        db_table = u'strategy2'

    def __unicode__(self):
        return u'%d)%s'%(self.strategy_id,self.description)

    #下一个还款日  + timedetal
    def get_next_repay_time(self, day):
        if self.is_day_percentage():
            return day + timedelta(days = self.installment_days)
        else:
            return tk_date.get_forword_month_day(day, 1)

    #第i期还款金额
    def get_installment_amount(self, amount, i):
        factorage = int(round(amount * self.post_factorage * self.installment_days))
        if i == 1:
            total = int (round(amount * (1 + self.get_interest_rate())))
            installment_amount = int (round(amount * (1 + self.get_interest_rate()) / self.installment_count))
            return total -  installment_amount * (self.installment_count - 1)  + factorage
        else:
            return int (round(amount * (1 + self.get_interest_rate()) / self.installment_count)) + factorage

    #第i期还款时间(预计)  T+1 + timedelta * i
    def get_installment_date(self, i, day=datetime.now()):
        day = tk_date.get_next_workdaytime(day)

        if self.is_day_percentage():
            if i > 0 and i <= self.installment_count:
                return day + timedelta(days = self.installment_days * i)
            elif i == 0:
                return day
            else:
                return None
        else:
            if i > 0 and i <= self.installment_count:
                return tk_date.get_forword_month_day(day, i)
            elif i == 0:
                return day
            else:
                return None

    #前置费率 用来计算到帐金额  本金 * (1 - 前置费率) = 到帐金额
    def get_pre_rate(self):
        #前置费率没有等额本息的情况, 只考虑固定利率
        return self.installment_count * self.installment_days * self.pre_factorage * self.discount

    #后置利率率 用来计算还款金额  本金 * (1 + 后置利率 + 后置服务费<F5>) = 还款金额
    def get_interest_rate(self):
        if self.is_average_capital_plus_interest():
            factorage = math.pow((1 + self.interest), self.installment_count)
            res =  (self.interest * factorage / (factorage - 1)) * self.installment_count
            return res - 1
        else:
            res = self.installment_count * self.installment_days * (self.interest)
            return res

    def get_factorage_rate(self):
        return self.installment_days * self.installment_count* self.post_factorage * self.discount

    #总金额
    def get_pay_amount(self, amount):
        print self.get_interest_rate(), self.get_factorage_rate()
        total = int (round(amount * (1 + self.get_interest_rate()))) + int(round(amount * self.get_factorage_rate()))
        return total

    def get_repayment_amount(self, amount):
        pass

    # 获取逾期利率
    def get_overdue_rate(self, day):
        if day <=0 :
            return 0
        elif day > self.m1_days:
            return self.m1_days * self.overdue_interest + (day - self.m1_days) * self.overdue_m2_interest
        else:
            return self.m1_days * self.overdue_interest

    #综合服务费率
    def get_total_rate(self):
        if self.is_pre():
            return self.get_pre_rate()
        else:
            return self.get_interest_rate() + self.get_factorage_rate()

    #总利息率
    def get_interest(self):
        if self.is_average_capital_plus_interest():
            factorage = math.pow((1 + self.interest), self.installment_count)
            res =  (self.interest * factorage / (factorage - 1)) * self.installment_count * self.discount
            return res - 1
        else:
            return self.interest * self.installment_days * self.installment_count * self.discount

    ##向信托申请的金额比例 本金 * 信托费率 = 请款金额
    #def get_xt_rate(self):
    #    if self.is_average_capital_plus_interest() :
    #        factorage = math.pow((1 + self.xt_factorage), self.installment_count)
    #        return (factorage - 1) / (self.xt_factorage * factorage)
    #    else:
    #        return 1 + self.xt_factorage

    ## 风险备用金
    #def get_risk_backup(self, amount):
    #    return (get_xt_rate - 1) * risk_reserve

    #第一位 0不能重复借贷 1可以重复借贷
    def is_reloanable(self):
        return self.installment_type & 0b1 != 0

    #第二维 0表示前置 1表示后置费率
    def is_pre(self):
        return self.installment_type & 0b10 != 0

    ##第三位 0按天计算利率 1按月计算利率
    def is_day_percentage(self):
        return self.installment_type & 0b100 == 0

    #第二位 0不能提前还款 1可以提前还款
    def is_advanced_repayment(self):
        return self.installment_type & 0b1000 != 0

    ## 第五位 0表示固定利率 1表示等额本息
    def is_average_capital_plus_interest(self):
        return self.installment_type & 0b10000 != 0

    def get_interest_type(self):
        return u"日" if self.is_day_percentage() else u"月"


