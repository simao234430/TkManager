# -*- coding: utf-8 -*-
'''
    该文件的所有model如果需要用框架自动导入数据，需要有owner和version两个字段，并且其他的字段类型在Adaptor的适配列表中
'''
from django.db import models
from TkManager.order.models import User
from django.utils.encoding import smart_text

class ListField(models.CharField):
    def to_python(self, value):
        "Returns a Unicode object."
        if value == []:
            return ''
        return smart_text("&".join(value))

class PhoneBasic(models.Model):
    class Meta:
        db_table = u'phonebasic'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True, null=True)
    cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="用户电话")
    real_name = models.CharField(blank=True, null=True, max_length=64, help_text="真实姓名")
    reg_time =  models.DateTimeField(blank=True, null=True, help_text="注册时间")
    idcard = models.CharField(max_length=20, blank=True, null=True, help_text="身份证号")
    update_time =  models.DateTimeField(blank=True, null=True, help_text="更新时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class PhoneCall(models.Model):
    class Meta:
        db_table = u'phonecall'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="手机号码")
    other_cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="对方号码")
    call_place = models.CharField(blank=True, null=True, max_length=255, help_text="通信地点")
    start_time = models.DateTimeField(blank=True, null=True, help_text="电话拨打时间")
    use_time = models.IntegerField(blank=True, null=True, default=0, help_text="通话时间（秒）")
    call_type = models.CharField(max_length=64, blank=True, null=True, help_text="计费类型,本地|漫游")
    init_type = models.CharField(max_length=64, blank=True, null=True, help_text="通话类型,主叫|被叫")
    subtotal = models.FloatField(blank=True, null=True, default=0, help_text="通话费用")
    update_time =  models.DateTimeField(blank=True, null=True, help_text="更新时间")
    owner =  models.ForeignKey(User, blank=True, null=True)
    version = models.IntegerField(default = 0, help_text="版本号")

class PhoneNet(models.Model):
    class Meta:
        db_table = u'phonenet'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True, null=True)
    cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="手机号码")
    place = models.CharField(blank=True, null=True, max_length=255, help_text="上网流量发生地")
    net_type = models.CharField(blank=True, null=True, max_length=255, help_text="上网类型")
    start_time = models.DateTimeField(blank=True, null=True, help_text="上网发起时间")
    use_time = models.IntegerField(blank=True, null=True, default=0, help_text="上网时间（秒）")
    subflow = models.IntegerField(blank=True, null=True, default=0, help_text="上网流量")
    subtotal = models.FloatField(blank=True, null=True, default=0, help_text="上网费用")
    update_time =  models.DateTimeField(blank=True, null=True, help_text="更新时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class PhoneSms(models.Model):
    class Meta:
        db_table = u'phonesms'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True, null=True)
    cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="手机号码")
    other_cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="对方号码")
    start_time = models.DateTimeField(blank=True, null=True, help_text="短信发送时间")
    call_place = models.CharField(blank=True, null=True, max_length=255, help_text="短信发送地点")
    init_type = models.CharField(max_length=255, blank=True, null=True, help_text="短信类型")
    subtotal = models.FloatField(blank=True, null=True, default=0, help_text="短信费用")
    update_time =  models.DateTimeField(blank=True, null=True, help_text="更新时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class PhoneTransaction(models.Model):
    class Meta:
        db_table = u'phonetransaction'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True, null=True)
    bill_cycle = models.DateTimeField(blank=True, null=True, help_text="账单计费开始时间")
    cell_phone = models.CharField(blank=True, null=True, max_length=20, help_text="电话号码")
    plan_amt = models.IntegerField(blank=True, null=True, default=0, help_text="套餐金额")
    total_amt = models.IntegerField(blank=True, null=True, default=0, help_text="总金额")
    pay_amt = models.IntegerField(blank=True, null=True, default=0, help_text="实际缴费金额")
    update_time =  models.DateTimeField(blank=True, null=True, help_text="更新时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class Person(models.Model):
    class Meta:
        db_table = u'person'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True, null=True)
    real_name = models.CharField(blank=True, null=True, max_length=20, help_text="真实姓名")
    id_card_num = models.CharField(blank=True ,null=True ,max_length=20 ,help_text="身份证号码")
    gender = models.CharField(blank=True, null=True ,max_length=20, help_text="性别")
    sign = models.CharField(blank=True, null=True ,max_length=20, help_text="星座")
    age = models.CharField(blank=True, null=True ,max_length=20,help_text="年龄")
    province = models.CharField(blank=True, null=True, max_length=20 ,help_text="出生省份")
    city = models.CharField(blank=True, null=True, max_length=20, help_text="出生城市")
    region = models.CharField(blank=True, null=True, max_length=20, help_text="出生县")
    version = models.IntegerField(default = 0, help_text="版本号")

class DataSource(models.Model):
    class Meta:
        db_table = u'data_source'
    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    key = models.CharField(blank=True, null=True ,max_length=255 ,help_text="数据源标识")
    name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="数据源名称")
    account = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="账号名称")
    category_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="数据源类型")
    category_value = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="数据源类型名称")
    status = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="数据有效性")
    reliability = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="数据可靠性")
    binding_time = models.DateTimeField(blank=True ,null=True ,help_text="绑定时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class ApplicationCheck(models.Model):
    class Meta:
        db_table = u'application_check'
    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    category = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="检查点类别")
    check_point = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="检查项目")
    result = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="检查结果")
    evidence = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="证据")
    version = models.IntegerField(default = 0, help_text="版本号")

class BehaviorCheck(models.Model):
    class Meta:
        db_table = u'behavior_check'
    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    category = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="检查点类别")
    check_point = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="检查项目")
    result = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="检查结果")
    evidence = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="证据")
    version = models.IntegerField(default = 0, help_text="版本号")

class ContactRegion(models.Model):
    class Meta:
        db_table = u'contact_region'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    region_loc = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="号码归属地")
    region_uniq_num_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="联系人号码数量")
    region_call_in_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="电话呼入次数")
    region_call_out_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="电话呼出次数")
    region_call_in_time = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="电话呼入时间")
    region_call_out_time = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="电话呼出时间")
    region_avg_call_in_time = models.FloatField(blank=True ,null=True ,default=0 ,help_text="平均电话呼入时间")
    region_avg_call_out_time = models.FloatField(blank=True ,null=True ,default=0 ,help_text="平均电话呼出时间")
    region_call_in_cnt_pct = models.FloatField(blank=True ,null=True ,default=0 ,help_text="电话呼入次数百分比")
    region_call_out_cnt_pct = models.FloatField(blank=True ,null=True ,default=0 ,help_text="电话呼出次数百分比")
    region_call_in_time_pct = models.FloatField(blank=True ,null=True ,default=0 ,help_text="电话呼入时间百分比")
    region_call_out_time_pct = models.FloatField(blank=True ,null=True ,default=0 ,help_text="电话呼出时间百分比")
    version = models.IntegerField(default = 0, help_text="版本号")

class ContactList(models.Model):
    class Meta:
        db_table = u'contact_list'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    phone_num = models.CharField(blank=True ,null=True ,max_length=20 ,help_text="号码")
    phone_num_loc = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="号码归属地")
    contact_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="号码标注")
    needs_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="需求类别")
    call_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="通话次数")
    call_len = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="通话时长")
    call_out_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼出次数")
    call_out_len = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼出时间")
    call_in_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼入次数")
    call_in_len = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼入时间")
    p_relation = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="关系推测")
    contact_1w = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="最近一周联系次数")
    contact_1m = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="最近一月联系次数")
    contact_3m = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="最近三月联系次数")
    contact_early_morning = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="凌晨联系次数")
    contact_morning = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="上午联系次数")
    contact_noon = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="中午联系次数")
    contact_afternoon = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="下午联系次数")
    contact_night = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="晚上联系次数")
    contact_all_day = models.NullBooleanField(blank=True ,null=True,default=None ,help_text="是否全天联系")
    contact_weekday = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="周中联系次数")
    contact_weekend = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="周末联系次数")
    contact_holiday = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="节假日联系次数")
    version = models.IntegerField(default = 0, help_text="版本号")

class DeliverAddress(models.Model):
    class Meta:
        db_table = u'deliver_address'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    address = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货地址")
    lng = models.FloatField(blank=True ,null=True ,default=0 ,help_text="经度")
    lat = models.FloatField(blank=True ,null=True ,default=0 ,help_text="纬度")
    predict_addr_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="地址类型")
    begin_date = models.DateTimeField(blank=True ,null=True ,help_text="开始送货时间")
    end_date = models.DateTimeField(blank=True ,null=True ,help_text="结束送货时间")
    total_amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="总送货金额")
    total_count = models.FloatField(blank=True ,null=True ,default=0 ,help_text="总送货次数")
    version = models.IntegerField(default = 0, help_text="版本号")

class Receiver(models.Model):
    class Meta:
        db_table = u'receiver'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner = models.ForeignKey(DeliverAddress, blank=True ,null=True)
    name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人姓名")
    phone_num_list = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人电话号码列表")
    amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="送货金额")
    count = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="送货次数")
    version = models.IntegerField(default = 0, help_text="版本号")

class EbusinessExpense(models.Model):
    class Meta:
        db_table = u'ebusiness_expense'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    trans_mth = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="汇总月份")
    owner_amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="本人购物金额")
    owner_count = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="本人购物次数")
    family_amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="家庭购物金额")
    family_count = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="家庭购物次数")
    others_amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="其他消费金额")
    others_count = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="其他消费次数")
    all_amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="总购物金额")
    all_count = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="其他消费次数")
    version = models.IntegerField(default = 0, help_text="版本号")

class CellBehavior(models.Model):
    class Meta:
        db_table = u'cell_behavior'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    cell_phone_num = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="手机号码")
    cell_operator = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="手机运营商")
    cell_loc = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="手机归属地")
    cell_mth = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="月份")
    call_in_time = models.FloatField(blank=True ,null=True ,default=0 ,help_text="月被叫通话时间")
    call_out_time = models.FloatField(blank=True ,null=True ,default=0 ,help_text="月主叫通话时间")
    sms_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="月短信条数")
    net_flow = models.FloatField(blank=True ,null=True ,default=0 ,help_text="月流量")
    version = models.IntegerField(default = 0, help_text="版本号")

class RecentNeed(models.Model):
    class Meta:
        db_table = u'recent_need'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    req_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="需求类型")
    call_out_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="总主叫次数")
    call_in_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="总被叫次数")
    call_out_time = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="总主叫时间")
    call_in_time = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="总被叫时间")
    req_mth = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="需求发生月")
    version = models.IntegerField(default = 0, help_text="版本号")

class DemandsInfo(models.Model):

    class Meta:
        db_table = u'demands_info'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner = models.ForeignKey(RecentNeed, blank=True ,null=True)
    demands_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="需求名称")
    demands_call_out_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="主叫次数")
    demands_call_in_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="被叫次数")
    demands_call_out_time = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="主叫时间")
    demands_call_in_time = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="被叫时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class TripInfo(models.Model):

    class Meta:
        db_table = u'trip_info'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    trip_leave = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="出发地")
    trip_dest = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="目的地")
    trip_transportation = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="多种出行交通工具")
    trip_person = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="多个同行人")
    trip_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="出行时间类型")
    trip_start_time = models.DateTimeField(blank=True ,null=True ,help_text="出行开始时间")
    trip_end_time = models.DateTimeField(blank=True ,null=True ,help_text="出行结束时间")
    trip_data_source = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="多个数据来源")
    version = models.IntegerField(default = 0, help_text="版本号")

class CollectionContact(models.Model):
    class Meta:
        db_table = u'collection_contact'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    contact_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="联系人姓名")
    begin_date = models.DateTimeField(blank=True ,null=True ,help_text="最早出现时间")
    end_date = models.DateTimeField(blank=True ,null=True ,help_text="最晚出现时间")
    total_count = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="电商送货总数")
    total_amount = models.FloatField(blank=True ,null=True ,default=0 ,help_text="电商送货总金额")
    version = models.IntegerField(default = 0, help_text="版本号")

class ContactDetails(models.Model):
    class Meta:
        db_table = u'contact_details'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(CollectionContact, blank=True ,null=True)
    phone_num = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="电话号码")
    phone_num_loc = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="号码归属地")
    call_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼叫次数")
    call_len = models.FloatField(blank=True ,null=True ,default=0 ,help_text="呼叫时长")
    call_out_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼出次数")
    call_in_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="呼入次数")
    sms_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="短信条数")
    trans_start = models.DateTimeField(blank=True ,null=True ,help_text="最早沟通时间")
    trans_end = models.DateTimeField(blank=True ,null=True ,help_text="最晚沟通时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class MainService(models.Model):
    class Meta:
        db_table = u'main_service'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner =  models.ForeignKey(User, blank=True ,null=True)
    total_service_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="总联系次数")
    company_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="公司类型")
    version = models.IntegerField(default = 0, help_text="版本号")


class ServiceDetails(models.Model):
    class Meta:
        db_table = u'service_details'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner = models.ForeignKey(MainService, blank=True ,null=True)
    company_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="服务商名字")
    version = models.IntegerField(default = 0, help_text="版本号")

class ServiceInfo(models.Model):
    class Meta:
        db_table = u'service_info'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner = models.ForeignKey(ServiceDetails, blank=True ,null=True)
    service_num = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="服务商号码")
    service_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="联系次数")
    version = models.IntegerField(default = 0, help_text="版本号")

class MthDetails(models.Model):
    class Meta:
        db_table = u'mth_details'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)

    owner = models.ForeignKey(ServiceInfo, blank=True ,null=True)
    interact_mth = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="联系月份")
    interact_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="月联系次数")
    version = models.IntegerField(default = 0, help_text="版本号")

class EbusinessBasic(models.Model):
    class Meta:
        db_table = u'ebusiness_basic'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)
    
    owner =  models.ForeignKey(User, blank=True ,null=True)
    website_id = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="电商注册账号名称")
    nickname = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="在页面上显示的昵称")
    real_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="用户认证的真实姓名")
    is_validate_real_name = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="用户是否被实名认证")
    level = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="用户的会员等级")
    cell_phone = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="账号绑定的手机号码")
    email = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="账号绑定的邮箱")
    security_level = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="账号的安全等级")
    register_date = models.DateTimeField(blank=True ,null=True ,help_text="电商提供的注册日期")
    update_time = models.DateTimeField(blank=True ,null=True ,help_text="抓取时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class EbusinessTransactions(models.Model):
    class Meta:
        db_table = u'ebusiness_transactions'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)
    
    owner =  models.ForeignKey(User, blank=True ,null=True)
    order_id = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="订单编号")
    is_success = models.NullBooleanField(blank=True ,null=True ,default=None ,help_text="订单是否交易成功")
    trans_time = models.DateTimeField(blank=True ,null=True ,help_text="订单下单时间")
    total_price = models.FloatField(blank=True ,null=True ,default=0 ,help_text="订单总价")
    payment_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="订单付款方式")
    bill_title = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="订单开具发票的抬头")
    bill_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="订单开具发票的类型")
    receiver_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人的名字")
    receiver_title = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人的称呼")
    receiver_cell_phone = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人手机号码")
    receiver_phone = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人电话号码")
    receiver_addr = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人地址")
    zipcode = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人邮编")
    delivery_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="订单快递类型")
    delivery_fee = models.FloatField(blank=True ,null=True ,default=0 ,help_text="订单的快递费用")
    update_time = models.DateTimeField(blank=True ,null=True ,help_text="抓取时间")
    version = models.IntegerField(default = 0, help_text="版本号")

class TransactionItems(models.Model):
    class Meta:
        db_table = u'transaction_items'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)
    
    owner =  models.ForeignKey(EbusinessTransactions, blank=True ,null=True)
    trans_time = models.DateTimeField(blank=True ,null=True ,help_text="订单交易时间")
    product_price = models.FloatField(blank=True ,null=True ,default=0 ,help_text="产品单价")
    product_cnt = models.IntegerField(blank=True ,null=True ,default=0 ,help_text="购买产品的数量")
    product_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="产品名称")
    version = models.IntegerField(default = 0, help_text="版本号")

class EbusinessAddress(models.Model):
    class Meta:
        db_table = u'ebusiness_address'

    def __unicode__(self):
        return u'%d)%s:%d'%(self.id, self.owner.name, self.version)
    
    owner =  models.ForeignKey(User, blank=True ,null=True)
    province = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货地址对应的省份")
    update_time = models.DateTimeField(blank=True ,null=True ,help_text="抓取时间")
    receiver_addr = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货地址名称")
    city = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货地址对应的城市")
    receiver_cell_phone = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人手机号码")
    zipcode = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人邮编")
    receiver_title = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人的称呼")
    payment_type = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="订单付款方式")
    is_default_address = models.NullBooleanField(blank=True ,null=True ,default=None ,help_text="该地址是否是默认订单地址")
    receiver_name = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人的名字")
    receiver_phone = models.CharField(blank=True ,null=True ,max_length=255 ,help_text="收货人电话号码")
    version = models.IntegerField(default = 0, help_text="版本号")
