# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from TkManager.common.tk_log_client import TkLog
from TkManager.review.employee_models import Employee
# 用户信息
class User(models.Model):
    register_type_t = {
        (-2, u'注销资料'),
        (-1, u'已注销'),
        (0, u'已注册'),
        (1, u'未激活'),
    }

    name = models.CharField(max_length=64, null=True, help_text="用户姓名")
    password = models.CharField(max_length=64, help_text='登录密码')
    phone_no = models.CharField(max_length=20, help_text="用户电话")
    id_no = models.CharField(max_length=20, blank=True, null=True, help_text="身份证号")
    channel = models.CharField(max_length=255, blank=True, null=True, help_text="渠道来源")
    sub_channel = models.ForeignKey("SubChannel", blank=True, null=True, help_text="二级渠道来源")
    payment_password = models.CharField(max_length=64, blank=True, null=True, help_text='支付密码')
    create_time = models.DateTimeField(auto_now_add=True, help_text="注册时间")

    device_name = models.CharField(max_length=255, blank=True, null=True, help_text="设备名称")
    wechat_openid = models.CharField(max_length=255, blank=True, null=True, help_text="微信id")
    bind_wechat_time = models.IntegerField(blank=True, null=True, default=0, help_text="微信绑定时间")
    last_contract_id = models.CharField(max_length=255, blank=True, null=True)
    device_id = models.BigIntegerField(max_length=20)

    invitation = models.ForeignKey("self", blank=True, null=True)
    market_score = models.IntegerField(default = 0)

    imei = models.CharField(max_length=64, blank=True, null=True, help_text="imei")
    imsi = models.CharField(max_length=64, blank=True, null=True, help_text="imsi")
    android_id = models.CharField(max_length=64, blank=True, null=True, help_text="安卓id")
    local_phone_no = models.CharField(max_length=20, blank=True, null=True, help_text="本机号码")

    is_register = models.SmallIntegerField(blank=True, null=True, default=0, choices=register_type_t, help_text="是否注销")

    class Meta:
        db_table = u'user'

    def __unicode__(self):
        return u'%d)%s'%(self.id,self.name)

    def get_status(self):
        return ""

# 用户信息
class SubChannel(models.Model):
    name = models.CharField(max_length=64, null=True, help_text="渠道名称")
    type = models.CharField(max_length=64, help_text='渠道类型')
    generalize_code = models.CharField(max_length=50, help_text="邀请码", null=True, default="")

    class Meta:
        db_table = u'subchannel'

    def __unicode__(self):
        return u'%d)%s-%s'%(self.id, self.name, self.type)

class CheckStatus(models.Model):
    NOT_SUBMITTED = 0
    WAITING = 1
    CHECKING = 2
    APPROVAL = 3
    BACK = 4
    REJECTED = 5
    check_apply_status_t = (
        (NOT_SUBMITTED, "未提交"),
        (WAITING, "等待审批"),
        (CHECKING, "审批中"),
        (APPROVAL, "通过"),
        (BACK, "返回修改"),
        (REJECTED, "拒绝"),
    )

    AUTO_MODEL_NICE = 2
    AUTO_MODEL_GOOD = 3
    AUTO_MODEL_NORMAL = 4
    MECHINE_PASS = 1
    PASS = 0
    TONGDUN = -1
    CHSI = -2
    ID_NO = -3
    RE_SUBMITTED = -4
    PHONE = -5
    EBUSSINESS = -6
    SHENZHOURONG = -7
    BAIDU = -8
    BAIRONG = -9
    NO_EBUSSINESS = -10
    MODEL_LEVEL_FAIL = -11
    auto_check_status_t = (
        (MECHINE_PASS, "机器模型通过"),
        (PASS, "通过"),
        (AUTO_MODEL_NICE, "模型评分优质"),
        (AUTO_MODEL_GOOD, "模型评分良好"),
        (AUTO_MODEL_NORMAL, "模型评分普通"),
        (TONGDUN, "同盾拒绝"),
        (CHSI, "学信网身份证不匹配"),
        (ID_NO, "身份证号已经注册过"),
        (RE_SUBMITTED, "拒绝用户注销后再次提交"),
        (PHONE, "电话非实名"),
        (EBUSSINESS, "电商非实名"),
        (SHENZHOURONG, "神州融拒绝"),
        (BAIDU, "百度拒绝"),
        (BAIRONG, "百融拒绝"),
        (NO_EBUSSINESS, "电商采集失败"),
        (MODEL_LEVEL_FAIL, "机器分级失败"),
    )

    class Meta:
        db_table = u'checkstatus'

    def __unicode__(self):
        return u'%d)%s'%(self.id,self.owner.name)

    owner = models.OneToOneField(User)
    apply_status = models.IntegerField(default=0, help_text="申请审核状态", choices = check_apply_status_t)
    profile_status = models.BigIntegerField(default=0, help_text="用户提交状态")
    profile_check_status = models.BigIntegerField(default=0, help_text="基本信息审批状态")
    increase_status = models.BigIntegerField(default=0, help_text="额度提升提交状态")
    increase_check_status = models.BigIntegerField(default=0, help_text="额度提升审核状态")
    real_id_verify_status = models.BigIntegerField(null=True, blank=True, default=0, help_text="实名认证提交状态")
    auto_check_status = models.BigIntegerField(choices=auto_check_status_t, null=True, blank=True,  default=0, help_text="机器自动审核的结果")
    credit_score = models.IntegerField(default=0, help_text="信用评分")
    credit_limit = models.IntegerField(default=0, help_text="可用信用额度")
    base_credit = models.IntegerField(default=0, help_text="初始信用额度")
    max_credit = models.IntegerField(default=0, help_text="最高额度")

    def set_profile_status(self, status):
        if status == 'pass':
            self.apply_status = 3
        elif status == 'deny':
            self.apply_status = 5
            self.profile_check_status = 0xaaaa
        elif status == 'recheck':
            self.apply_status = 4
        elif status == 'reviewing':
            self.apply_status = 2
        elif status == 'waiting':
            self.apply_status = 1
        self.save()

#额度提升的额外图片资料
class ExtraPic(models.Model):
    extra_pic_type_t = (
        ('bank_credit', u'征信报告'),
        ('bank_flow', u'银行流水'),
        ('other', u'其他'),
        ('phone', u'电话详单'),
    )

    class Meta:
        db_table = u'extrapic'
    owner = models.OneToOneField(User)
    type = models.CharField(max_length = 20, default = 0, choices = extra_pic_type_t)
    pic = models.CharField(max_length = 255)
    score = models.IntegerField(default = 0, help_text = "额度")

class Profile(models.Model):
    UNKNOWN = -1
    MALE = 1
    FEMALE = 2
    gender_t = (
        (UNKNOWN, '未填写'),
        (MALE, u'男'),
        (FEMALE, u'女'),
    )

    MARRIED = 1
    SINGLE = 2
    MARRIED_NO_CHILD = 3
    MARRIED_HAS_CHILD = 4
    WIDOWS = 5
    DIVORCED = 6
    marriage_type_t = (
        (UNKNOWN, u'未填写'),
        (MARRIED, u'已婚'),
        (SINGLE, u'未婚'),
        (MARRIED_NO_CHILD, u'已婚无子女'),
        (MARRIED_HAS_CHILD, u'未婚有子女'),
        (WIDOWS, u'丧偶'),
        (DIVORCED, u'离异'),
    )

    STDUENT = 1
    WORKING = 2
    job_type_t = (
        (STDUENT, u'学生'),
        (WORKING, u'工薪'),
    )

    class Meta:
        db_table = u'profile'

    def __unicode__(self):
        return u'%d)%s'%(self.id,self.owner.name)

    owner = models.OneToOneField(User)
    gender = models.IntegerField(default=-1, help_text="性别", choices=gender_t)
    job = models.IntegerField(blank=True, help_text="工作", choices=job_type_t)
    marriage = models.IntegerField(blank=True, null=True, default=0, help_text="婚姻状况", choices=marriage_type_t)
    company = models.CharField(max_length=255, null=True, blank=True, help_text="公司名称")
    work_post = models.CharField(default="", max_length=255, null=True, blank=True, help_text="工作职位")
    work_address = models.CharField(max_length=255, null=True, blank=True, help_text="公司地址")
    company_phone = models.CharField(max_length=20, null=True, blank=True, help_text="公司电话")
    family_address = models.CharField(max_length=255, null=True, help_text="家庭住址")
    expect_amount = models.IntegerField(null=True, help_text="期望额度")
    email = models.CharField(max_length=255, help_text="邮箱")
    qq = models.CharField(default="", blank=True, null=True, max_length=20, help_text="QQ号")

class IdCard(models.Model):
    class Meta:
        db_table = u'idcard'
    def __unicode__(self):
        return u'%d)%s'%(self.id,self.owner.name)
    owner = models.OneToOneField(User)
    id_no = models.CharField(max_length=20, default="", blank=True, help_text="身份证号")
    id_pic_front = models.CharField(max_length=64, default="", blank=True, help_text="身份证照片正面")
    id_pic_back = models.CharField(max_length=64, default="", blank=True, help_text="身份证照片背面")
    id_pic_self = models.CharField(max_length=64, default="", blank=True, help_text="身份证照片手持")
    id_birth = models.DateTimeField(blank=True, null=True, help_text="身份证生日")
    id_name = models.CharField(max_length=64, default="", blank=True, help_text="身份证姓名")
    id_address = models.CharField(max_length=255, default="", blank=True, help_text="身份证地址")
    id_ctime = models.DateTimeField(blank=True, null=True, help_text="身份证提交时间")

class ContactInfo(models.Model):

    UNKNOWN = 0
    FATHER = 1
    MOTHER = 2
    MATE = 3
    RELATIVE = 4
    FRIEND = 5
    WORKMATE = 6
    CLASSMATE = 7
    PARENT = 8
    contact_type_t = (
        (UNKNOWN, '未填写'),
        (FATHER, u'父亲'),
        (MOTHER, u'母亲'),
        (MATE, u'配偶'),
        (RELATIVE, u'亲戚'),
        (FRIEND, u'朋友'),
        (WORKMATE, u'同事'),
        (CLASSMATE, u'同学'),
        (PARENT, u'父母'),
    )

    in_list_type_t = (
        (0, u'未知'),
        (1, u'是'),
        (2, u'否'),
    )


    class Meta:
        db_table = u'contactinfo'

    def __unicode__(self):
        return u'%d)%s'%(self.id,self.owner.name)

    name = models.CharField(max_length=64, help_text="联系人名")
    address = models.CharField(max_length=255, help_text="联系人地址")
    id_no = models.CharField(max_length=20, blank=True, null=True, help_text="联系人身份证")
    phone_no = models.CharField(max_length=20, help_text="联系人电话")
    relationship = models.IntegerField(help_text="联系人关系", choices = contact_type_t)
    in_addressbook = models.SmallIntegerField(blank=True, null=True, default=0, help_text="联系人是否在通讯录中", choices = in_list_type_t)
    #in_blacklist = models.SmallIntegerField(null=True, default=0, help_text="联系人是否在黑名单中", choices = in_list_type_t)
    call_times = models.IntegerField(blank=True, null=True, default=0, help_text="联系次数")
    owner = models.ForeignKey(User)

# 可选的详细信息
class RenRenInfo(models.Model):
    class Meta:
        db_table = u'renreninfo'
    user = models.ForeignKey(User)
    username = models.CharField(max_length=255)

class WeiboInfo(models.Model):
    class Meta:
        db_table = u'weiboinfo'
    user = models.ForeignKey(User)
    username = models.CharField(max_length=64)
    province = models.IntegerField(default=0)
    city = models.IntegerField(default=0)
    blog_url = models.URLField(default="")
    gender = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)
    statuses_count = models.IntegerField(default=0)
    favourites_count = models.IntegerField(default=0)
    bi_followers_count = models.IntegerField(default=0)
    create_at = models.CharField(max_length=64)
    verified = models.IntegerField(default=False)

class WeiboContent(models.Model):
    class Meta:
        db_table = u'weibocontent'
    user = models.ForeignKey(User)
    username = models.CharField(max_length=64)
    content = models.CharField(max_length=512)
    source = models.CharField(max_length=255)
    create_at = models.CharField(max_length=64)
    comments_count = models.IntegerField()
    reposts_count = models.IntegerField()

#class BankCreditInfo(models.Model):
#    user = models.ForeignKey(User)
#    name = models.CharField(max_length=255)

#class AlipayInfo(models.Model):
#    user = models.ForeignKey(User)
#    username = models.CharField(max_length=255)


class CallRecord(models.Model):
    call_type_t = (
        (0, u'未知'),
        (1, u'呼入'),
        (2, u'呼出'),
        (3, u'未接'),
        (4, u'语音'),
        (10, u'挂断'),
    )

    class Meta:
        db_table = u'callrecord'
    phone_number = models.CharField(max_length=20)
    name = models.CharField(max_length=64, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    call_type = models.IntegerField(choices=call_type_t, default=0)
    call_time = models.CharField(max_length=20, blank=True, null=True)
    owner = models.ForeignKey(User)

class AddressBook(models.Model):
    class Meta:
        db_table = u'addressbook'
    phone_number = models.CharField(max_length=20)
    name = models.CharField(max_length=64, blank=True, null=True)
    create_time = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(User)
    call_times = models.IntegerField(blank=True, null=True, default=0, help_text="联系次数")

class BankCard(models.Model):
    # 银行卡信息

    bank_type_t = (
        (1, '建设银行'),
        (2, '中国银行'),
        (3, '农业银行'),
        (4, '招商银行'),
        (5, '广发银行'),
        (6, '兴业银行'),
        (7, '工商银行'),
        (8, '光大银行'),
        (9, '中国邮政储蓄')
    )

    bank_code = {
        1 : '105',
        2 : '104',
        3 : '103',
        4 : '308',
        5 : '306',
        6 : '309',
        7 : '102',
        8 : '303',
        9 : '403',
    }

    NONE = 0
    LOAN = 1
    REPAY = 2
    LOAN_REPAY = 3
    DELETED = 4
    card_type_t = (
        (NONE, u'未使用'),
        (LOAN, u'借款卡'),
        (REPAY, u'还款卡'),
        (LOAN_REPAY, u'借款卡&还款卡'),
        (DELETED, u'已删除'),
    )

    class Meta:
        db_table = u'bankcard'
    number = models.CharField(max_length=32, help_text="银行卡号")
    user = models.ForeignKey(User)
    bank = models.CharField(max_length=64, default="", blank=True)
    bank_type = models.IntegerField(choices = bank_type_t, help_text="银行类型", blank=True)
    card_type = models.IntegerField(choices = card_type_t, default=3, help_text="借款卡/还款卡")
    phone_no = models.CharField(max_length=20, help_text='银行预留电话', default="", blank=True)
    bank_name = models.CharField(max_length=255, help_text='开户行名称', default="", blank=True)
    bank_province = models.CharField(max_length=20, help_text='开户省', default="", blank=True)
    bank_city = models.CharField(max_length=20, help_text='开户市', default="", blank=True)

    def __unicode__(self):
        return u'%d)%s'%(self.id,self.user.name)

    def get_bank_code(self):
        return BankCard.bank_code[self.bank_type]

    @staticmethod
    def get_pay_card(user):
        cards = BankCard.objects.filter((Q(card_type=1) | Q(card_type=3)) & Q(user = user))
        if len(cards) != 1:
            return None
        else:
            return cards[0]

    @staticmethod
    def get_repay_card(user):
        cards = BankCard.objects.filter((Q(card_type=2) | Q(card_type=3)) & Q(user = user))
        if len(cards) != 1:
            return None
        else:
            return cards[0]

class Chsi(models.Model):
    class Meta:
        db_table = u'chsi'
    def __unicode__(self):
        return u'%d)%s'%(self.id,self.user.name)
    chsi_name = models.CharField(max_length=64, default="", blank=True, help_text="学信网姓名")
    school = models.CharField(max_length=255, default="", blank=True, help_text="学信网学校")
    head_img = models.CharField(max_length=255, default="", blank=True, help_text="学信网照片")
    gender = models.CharField(max_length=20, default="", blank=True, help_text="学信网性别")
    id_card_number = models.CharField(max_length=20, default="", blank=True, help_text="学信网身份证号")
    nation = models.CharField(max_length=255, default="", blank=True, help_text="学信网民族")
    birthday = models.CharField(max_length=20, default="", blank=True, help_text="学信网生日")
    education = models.CharField(max_length=20, default="", blank=True, help_text="学信网学历")
    collage = models.CharField(max_length=255, default="", blank=True, help_text="学信网学院")
    school_class = models.CharField(max_length=255, default="", blank=True, help_text="学信网班级")
    student_id = models.CharField(max_length=255, default="", blank=True, help_text="学信网学号")
    major = models.CharField(max_length=255, default="", blank=True, help_text="学信网专业")
    edu_type = models.CharField(max_length=255, default="", blank=True, help_text="学信网教育形式")
    enrollment = models.CharField(max_length=255, default="", blank=True, help_text="学信网入学时间")
    edu_duration = models.CharField(max_length=64, default="", blank=True, help_text="学信网学制")
    edu_status = models.CharField(max_length=255, default="", blank=True, help_text="学信网学籍状态")
    user = models.ForeignKey(User, help_text="用户")
    create_at = models.DateTimeField(auto_now_add=True)

operation_record = (("AboutAppActivity_click_updata", "设置_关于花啦花啦_检查更新"),
("c_AboutAppActivity_click_next", "设置_关于花啦花啦_检查更新_弹出下载框_取消"),
("c_AccountFrame_chis_agree", "我的账户_学信网认证.同意协议按钮"),
("c_AccountFrame_chis_protext", "我的账户_学信网认证.学信网授权协议"),
("c_AccountFrame_contact_image", "我的账户_完善资料.点击联系人"),
("c_AccountFrame_call_record_image", "我的账户_完善资料.点击通话详单"),
("c_AccountFrame_handled_id_image", "我的账户_完善资料.点击手持身份证"),
("c_AccountFrame_front_id_image", "我的账户_完善资料.点击身份证正面"),
("c_AccountFrame_back_id_image", "我的账户_完善资料.点击身份证背面"),
("c_AccountFrame_basic_info_image", "我的账户_完善资料.点击工作信息"),
("c_AccountFrame_action_btn", "我的账户_完善资料.点击提交审核"),
("c_AccountFrame_loan_record", "我的账户页-贷款记录"),
("c_AccountFrame_credit_score", "我的账户页-信用得分"),
("c_AccountFrame_one_step_action", "我的账户.实名填写.提交"),
("c_AccountFrame_chsi_action_normal", "我的账户.学信网认证.账户密码提交"),
("c_AccountFrame_chsi_action_code", "我的账户.学信网认证.验证码提交"),
("c_AccountFrame_male_text", "我的账户.实名填写.性别男"),
("c_AccountFrame_female_text", "我的账户.实名填写.性别女"),
("c_AccountFrame_reset_code", "我的账户.学信网认证.重发验证码"),
("c_AccountFrame_profile_rate_text", "我的账户.完善资料.点击中间百分比"),
("c_AccountFrame_error_1", "我的账户.实名填写.输入姓名错误"),
("c_AccountFrame_error_2", "我的账户.实名填写.输入身份证为空"),
("c_AccountFrame_error_3", "我的账户.实名填写.输入身份证输入格式有误"),
("c_AccountFrame_error_7", "我的账户.实名填写.未选择性别"),
("c_AccountFrame_error_email", "我的账户.实名填写.邮箱为空"),
("c_AccountFrame_error_email2", "我的账户.实名填写.邮箱格式不对"),
("c_AccountFrame_error_qq", "我的账户.实名填写.qq为空"),
("c_AccountFrame_error_qq2", "我的账户.实名填写.qq格式不对"),
("c_AccountFrame_error_address", "我的账户.实名填写.家庭住址为空"),
("c_AccountFrame_error_chis_1", "我的账户.学信网.账号为空"),
("c_AccountFrame_error_chis_2", "我的账户.学信网.账号过长"),
("c_AccountFrame_error_chis_3", "我的账户.学信网.密码为空"),
("c_AccountFrame_error_chis_4", "我的账户.学信网.验证码为空"),
("c_AccountFrame_error_chis_5", "我的账户.学信网.验证码过长"),
("c_AccountFrame_register", "我的账户.学信网.注册"),
("c_AddContactActivity_action", "我的账户.联系人.提交"),
("c_AddContactActivity_select_contact_1", "我的账户.联系人.第一个选取通讯录联系人"),
("c_AddContactActivity_select_contact_2", "我的账户.联系人.第二个选取通讯录联系人"),
("c_AddContactActivity_select_contact_3", "我的账户.联系人.第三个选取通讯录联系人"),
("c_AddContactActivity_type_1", "我的账户.联系人.第一个选取关系"),
("c_AddContactActivity_type_2", "我的账户.联系人.第二个选取关系"),
("c_AddContactActivity_type_3", "我的账户.联系人.第三个选取关系"),
("c_AddContactActivity_error_1", "我的账户.联系人.第一个姓名错误"),
("c_AddContactActivity_error_2", "我的账户.联系人.第一个手机为空"),
("c_AddContactActivity_error_3", "我的账户.联系人.第一个手机错误"),
("c_AddContactActivity_error_4", "我的账户.联系人.第二个姓名错误"),
("c_AddContactActivity_error_5", "我的账户.联系人.第二个手机为空"),
("c_AddContactActivity_error_6", "我的账户.联系人.第二个手机错误"),
("c_AddContactActivity_error_11", "我的账户.联系人.第三个姓名错误"),
("c_AddContactActivity_error_12", "我的账户.联系人.第三个手机为空"),
("c_AddContactActivity_error_13", "我的账户.联系人.第三个手机错误"),
("c_AddContactActivity_error_8", "我的账户.联系人.联系人姓名不能相同"),
("c_AddContactActivity_error_9", "我的账户.联系人.两个联系人电话不能相同"),
("c_AddContactActivity_error_10", "我的账户.联系人.必须指定联系人关系"),
("c_AddJobInfoActivity_action", "工作信息.信息提交"),
("c_AddJobInfoActivity_error_12", "工作信息.必须正确填写工作职务"),
("c_AddJobInfoActivity_error_9", "工作信息.工作单位填写错误"),
("c_AddJobInfoActivity_error_10", "工作信息.电话号码不正确"),
("c_AddJobInfoActivity_error_11", "工作信息.必须正确填写工作地址"),
("c_AppDetailActivity_lookht", "还款详情.查看借款合同"),
("c_ApplyUpgradeFrame_continue", "额度提升.点击继续提升额度"),
("c_ApplyUpgradeFrame_dismiss", "额度提升.点击关闭继续提升额度弹框"),
("c_ApplyUpgradeFrame_sina", "额度提升.新浪"),
("c_ApplyUpgradeFrame_jd_tb", "额度提升.电商"),
("c_ApplyUpgradeFrame_bank_credit", "额度提升.银行征信报告"),
("c_ApplyUpgradeFrame_bank_bank_business", "额度提升.3个月银行流水"),
("c_BankListActivity_bank_setting", "我的银行卡.银行卡设置按钮"),
("c_BankListActivity__set_borrow_card", "我的银行卡.银行卡弹框.设为借款卡"),
("c_BankListActivity__set_repay_card", "我的银行卡.银行卡弹框.设为还款卡"),
("c_BankListActivity__delete_card", "我的银行卡.银行卡弹框.删除银行卡"),
("c_BindBankCardActivity_error_2", "绑定银行卡.银行卡号为空"),
("c_BindBankCardActivity_action_0", "绑定银行卡.提交"),
("c_BindBankCardActivity_action_3", "绑定银行卡.输入的银行卡号可能不正确"),
("c_BindBankCardActivity_get_phone", "绑定银行卡.点击银行卡号右边imageview"),
("c_BindBankCardActivity_choose_card_type", "绑定银行卡.银行卡类型"),
("c_BindBankCardActivity_agree", "绑定银行卡.同意"),
("c_BindBankCardActivity_back_0", "绑定银行卡.点击返回"),
("c_BindBankCardActivity_continue", "绑定银行卡.绑定成功提示框，继续"),
("c_BindBankCardActivity_dismiss", "绑定银行卡.绑定成功提示框，关闭"),
("c_CallRecordActivity_forget_call_pwd", "通话详单.忘记服务密码"),
("c_CallRecordActivity_psdNull_error", "通话详单.服务密码为空"),
("c_CallRecordActivity_psdNull_error_2", "通话详单.服务密码过长"),
("c_CallRecordActivity_agree_check", "通话详单.同意协议按钮"),
("c_CallRecordActivity_pro_text", "通话详单.点击通讯录上传协议"),
("c_CallRecordActivity_get_code", "通话详单.获取验证码"),
("c_CallRecordActivity_action_btn", "通话详单.提交"),
("c_CallRecordForgetPwdActivity_get_code", "修改服务密码.获取验证码"),
("c_CallRecordForgetPwdActivity_submit_action", "修改服务密码.提交"),
("c_ConfirmCashActivity_confirm", "填写用途.确认提交"),
("c_ConfirmCashActivity_dialog_apply_retry", "填写用途.success重试提交"),
("c_ConfirmCashActivity_dialog_apply_retry_cancel", "填写用途.success重试取消"),
("c_ConfirmCashActivity_dialog_commit_retry", "填写用途.error重试提交"),
("c_ConfirmCashActivity_dialog_commit_back", "填写用途.error重试取消"),
("c_ConfirmCashActivity_dialog_check_retry", "填写用途，支付密码错误重试"),
("c_ConfirmCashActivity_dialog_check_forget", "填写用途，支付密码错误忘记密码"),
("c_ConfirmCashActivity_dialog_second_apply_wait_confirm", "填写用途，二次提现等待确认，点击好的"),
("c_ConfirmCashActivity_turn_to_bank_list", "填写用途，跳到我的银行卡页面"),
("c_ConfirmContractActivity_dialog_check_input", "确认合同.手机验证码错误.重新输入"),
("c_ConfirmContractActivity_dialog_check_resend", "确认合同.手机验证码错误.重发验证码"),
("c_ConfirmContractActivity_action", "确认合同.点击确认提交"),
("c_ConfirmContractActivity_success_dialog_click", "确认合同.借款成功，点击查看我的账户"),
("c_ConfirmContractActivity_dialog_cancel_apply", "确认合同.取消合同对话框，确认"),
("c_ConfirmContractActivity_dialog_cancel_apply_back", "确认合同.取消合同对话框，取消"),
("c_ConfirmPhoneActivity_get_code", "验证手机号.获取验证码"),
("c_ConfirmPhoneActivity_action", "验证手机号.确认提交"),
("c_ConfirmPhoneActivity_error_3", "验证手机号.验证码为空"),
("c_ForgetPayPasswordActivity_error_1", "忘记支付密码.银行卡号不正确"),
("c_ForgetPayPasswordActivity_error_2", "忘记支付密码.姓名不正确"),
("c_ForgetPayPasswordActivity_error_3", "忘记支付密码.身份证号不正确"),
("c_ForgetPayPasswordActivity_error_4", "忘记支付密码.联系人姓名不正确"),
("c_ForgetPayPasswordActivity_error_5", "忘记支付密码.电话号码不正确"),
("c_ForgetPayPasswordActivity_error_6", "忘记支付密码.学信网账号不能为空"),
("c_GetCashFrame_dialog_apply_continue", "快速提现.有待确认的合同.点击去看看"),
("c_GetCashFrame_dialog_to_pay_back_frame", "快速提现.跳转到还款页面"),
("c_GetCashFrame_get_strategy_list", "快速提现.获取还款策略"),
("c_GetCashFrame_amount", "快速提现.点击额度"),
("c_GetCashFrame_see_strategy_detail", "快速提现.查看说明"),
("c_GetCashFramedialog_lift", "快速提现.额度值不足，点击提升额度"),
("c_GetCashFramedialog_dialog_back", "快速提现.额度值不足，点击返回修改"),
("c_GetCashFramedialog_dialog_close", "快速提现.额度值不足，点击关闭对话框"),
("c_GetCashFramedialog_error_1", "快速提现.借款金额未填写"),
("c_GetCashFramedialog_error_2", "快速提现.借款金额少于1000"),
("c_GetCashFramedialog_error_3", "快速提现.未选择还款策略"),
("c_HomeActivity_click_logo", "主界面.点击左上角logo"),
("c_HomeActivity_app_try_exit", "主界面.点击back"),
("c_HomePageFrame_applyCash_1", "首页-立即申请按钮（未填完信息）"),
("c_HomePageFrame_applyCash_2", "首页-立即申请按钮（已填完信息）"),
("c_LoanCalculateActivity_get_strategy_list", "贷款试算.获取还款策略"),
("c_LoanCalculateActivity_see_strategy_detail", "贷款试算.点击描述"),
("c_LoginActivity_register", "登录页注册按钮"),
("c_LoginActivity_forget", "登录页忘记密码按钮"),
("c_LoginActivity_action", "登录页登录按钮"),
("c_LoginActivity_error_1", "登录页手机号为空"),
("c_OpinionActivity_error_1", "意见反馈.意见必须介于15到255个字"),
("c_OpinionActivity_error_2", "意见反馈.联系方式不能为空"),
("c_OpinionActivity_error_3", "意见反馈.联系方式必须为QQ或电话或Email"),
("c_OpinionActivity_action", "意见反馈.提交"),
("c_PayBackFrame_item_1", "贷款查询.借款列表项查看"),
("c_PayBackFrame_turn_to_bank_list", "贷款查询.设置还款卡"),
("c_PaymentPasswordActivity_dialog_check_retry", "输入支付密码界面.支付密码错误，点击重试"),
("c_PaymentPasswordActivity_dialog_check_forget", "输入支付密码界面.支付密码错误，点击忘记密码"),
("c_RegisterActivity_login_0", "注册页1-登录按钮"),
("c_RegisterActivity_action_0", "注册页1-注册按钮"),
("c_RegisterActivity_back_1", "注册页2-返回"),
("c_RegisterActivity_login_1", "注册页2-登录按钮"),
("c_RegisterActivity_get_code", "注册页2-重新发送按钮"),
("c_RegisterActivity_action_1", "注册页2-下一步按钮"),
("c_RegisterActivity_login_2", "注册页3-登录按钮"),
("c_RegisterActivity_back_2", "注册页3-返回"),
("c_RegisterActivity_click_agree", "注册页3-协议勾选按钮"),
("c_RegisterActivity_click_pro", "注册页3-协议点击按钮"),
("c_RegisterActivity_action_2", "注册页3-完成按钮"),
("c_RegisterActivity_error_1", "注册页.手机号为空"),
("c_RegisterActivity_error_2", "注册页.手机号不正确"),
("c_RegisterActivity_error_3", "注册页.手机验证码为空"),
("c_RegisterActivity_error_5", "注册页.登陆密码为空"),
("c_RegisterActivity_error_6", "注册页.登陆密码不正确"),
("c_ResetLoginPasswordActivity_back_0", "重置密码页1-返回"),
("c_ResetLoginPasswordActivity_action_0", "重置密码页1-重置密码按钮"),
("c_ResetLoginPasswordActivity_back_1", "重置密码页2-返回"),
("c_ResetLoginPasswordActivity_action_1", "重置密码页2-下一步"),
("c_ResetLoginPasswordActivity_get_code", "重置密码页2-重新发送按钮"),
("c_ResetLoginPasswordActivity_back_2", "重置密码页3-返回"),
("c_ResetLoginPasswordActivity_action_2", "重置密码页3-完成"),
("c_ResetLoginPasswordActivity_error_1", "重置密码页.手机号为空"),
("c_ResetLoginPasswordActivity_error_2", "重置密码页.手机号不正确"),
("c_ResetLoginPasswordActivity_error_3", "重置密码页.手机验证码为空"),
("c_ResetLoginPasswordActivity_error_5", "重置密码页.登陆密码为空"),
("c_ResetLoginPasswordActivity_error_6", "重置密码页.登陆密码错误"),
("c_SettingActivity_about", "设置.关于哗啦哗啦"),
("c_SettingActivity_exit_account", "设置.点击退出账户"),
("c_SettingActivity_cancellation", "设置.注销账户"),
("c_SettingView_my_bank", "侧边栏.我的银行卡"),
("c_SettingView_my_score", "侧边栏.我的积分"),
("c_SettingView_setting", "侧边栏.设置"),
("c_SettingView_share", "侧边栏.分享"),
("c_SettingView_about", "侧边栏.关于我们"),
("c_SettingView_opinion", "侧边栏.意见反馈"),
("c_SettingView_problem", "侧边栏.常见问题"),
("c_SettingView_loan_try", "侧边栏.贷款试算"),
("c_SettingView_newbee", "侧边栏.新手指引"),
("c_SettingView_call_kefu", "侧边栏.联系客服"),
("c_UpgradeJdTbActivity_upgrade_tbjd_choice_tb", "额度提升电商.选择账户.选择淘宝"),
("c_UpgradeJdTbActivity_upgrade_tbjd_choice_jd", "额度提升电商.选择账户.选择京东"),
("c_UpgradeJdTbActivity_upgrade_tbjd_choice_all", "额度提升电商.选择账户.选择京东淘宝"),
("c_UpgradeJdTbActivity_get_code", "额度提升电商.填写资料.获取验证码"),
("c_UpgradeJdTbActivity_upgrade_tbjd_action1", "额度提升电商.选择账户.确认提交"),
("c_UpgradeJdTbActivity_upgrade_tbjd_action2_1", "额度提升电商.填写资料.确认提交"),
("c_UpgradeJdTbActivity_upgrade_tbjd_action3", "额度提升电商.绑定成功.确认提交"),
("c_UploadIDPhotoActivity_0_upload_layout", "上传身份证正面（1反面2手持）点击上传框"),
("c_UploadIDPhotoActivity_0_submit", "上传身份证正面（1反面2手持）点击确认上传"),
("c_UploadIDPhotoActivity_0_close_btn", "上传身份证正面（1反面2手持）点击删除"),
("c_UploadIDPhotoActivity_0_choice_camera", "上传身份证正面（1反面2手持）选择相机"),
("c_UploadIDPhotoActivity_0_choice_album", "上传身份证正面（1反面2手持）选择相册"),
("c_UploadMorePictureActivity_click_upload", "上传多张图片.点击上传框"),
("c_UploadMorePictureActivity_choice_camera", "上传多张图片.选择相机"),
("c_UploadMorePictureActivity_choice_album", "上传多张图片.选择相册"),
("c_UploadPictureActivity_click_upload", "上传单张图片.点击上传框"),
("c_UploadPictureActivity_click_action", "上传单张图片.点击确认上传"),
("c_UploadPictureActivity_click_close", "上传单张图片.点击删除图片"),
("c_UploadPictureActivity_click_camera", "上传单张图片.点击选择相机"),
("c_UploadPictureActivity_click_album", "上传单张图片.点击选择相册"),
("c_app_start", "应用打开日志"),
("c_app_logout", "账号退出"),
("c_app_try_exit", "尝试退出"),
("c_app_exit", "退出"),
("c_SplashActivity_in", "进入引导页"),
("c_SplashActivity_out", "离开引导页"),
("c_LoginActivity_in", "进入登录页"),
("c_LoginActivity_out", "离开登录页"),
("c_RegisterActivity_in", "进入注册页"),
("c_RegisterActivity_out", "离开注册页"),
("c_WebViewActivity_in", "进入协议页面"),
("c_WebViewActivity_out", "离开协议页面"),
("c_ResetLoginPasswordActivity_in", "进入重置登录密码"),
("c_ResetLoginPasswordActivity_out", "离开重置登录密码"),
("c_HomeActivity_in", "进入一级页面框架"),
("c_HomeActivity_out", "离开一级页面框架"),
("c_HomePageFrame_in", "进入首页"),
("c_HomePageFrame_out", "离开首页"),
("c_AccountFrame_in", "进入我的账户页"),
("c_AccountFrame_out", "离开我的账户页"),
("c_ApplyUpgradeFrame_in", "进入额度提升页面"),
("c_ApplyUpgradeFrame_out", "离开额度提升页面"),
("c_GetCashFrame_in", "进入提现页面"),
("c_GetCashFrame_out", "离现提现页面"),
("c_PayBackFrame_in", "进入还款页面"),
("c_PayBackFrame_out", "离开还款页面"),
("c_AddContactActivity_in", "进入添加联系人页面"),
("c_AddContactActivity_out", "离开添加联系人页面"),
("c_UploadIDPhotoActivity_0_in", "进入上传身份证正面"),
("c_UploadIDPhotoActivity_0_out", "离开上传身份证正面"),
("c_UploadIDPhotoActivity_1_in", "进入上传身份证反面"),
("c_UploadIDPhotoActivity_1_out", "离开上传身份证反面"),
("c_UploadIDPhotoActivity_2_in", "进入上传手持身份证页面"),
("c_UploadIDPhotoActivity_2_out", "离开上传手持身份证页面"),
("c_SinaAuthActivity_in", "进入额度提升-新浪微博授权页"),
("c_SinaAuthActivity_out", "离开额度提升-新浪微博授权页"),
("c_PaymentPasswordActivity_in", "进入支付密码设置页面"),
("c_PaymentPasswordActivity_out", "离开支付密码设置页面"),
("c_BindBankCardActivity_in", "进入银行卡绑定页面"),
("c_BindBankCardActivity_out", "离开银行卡绑定页面"),
("c_ConfirmCashActivity_in", "进入借款用途页面"),
("c_ConfirmCashActivity_out", "离开借款用途页面"),
("c_ConfirmContractActivity_in", "进入借款合同页面"),
("c_ConfirmContractActivity_out", "离开借款合同页面"),
("c_ApplyDetailActivity_in", "进入借款详情页"),
("c_ApplyDetailActivity_out", "离开借款详情页"),
("c_LoanCalculateActivity_in", "进入贷款试算页面"),
("c_LoanCalculateActivity_out", "离开贷款试算页面"),
("c_OpinionActivity_in", "进入意见反馈页"),
("c_OpinionActivity_out", "离开意见反馈页"),
("c_SettingActivity_in", "进入设置页面"),
("c_SettingActivity_out", "离开设置页面"),
("c_UploadMorePictureActivity_in", "进入额度提升上传多张图片页面"),
("c_UploadMorePictureActivity_out", "离开额度提升上传多张图片页面"),
("c_UpgradeJdTbActivity_in", "进入提升电商额度页面"),
("c_UpgradeJdTbActivity_out", "离开提升电商额度页面"),
("c_AddJobInfoActivity_in", "进入填写工作页面"),
("c_AddJobInfoActivity_out", "离开填写工作页面"),
("c_BankListActivity_in", "进入我的银行卡页面"),
("c_BankListActivity_out", "离开我的银行卡页面"),
)

class Report(models.Model):
    logid = models.CharField(max_length=255, choices=operation_record)
    sessionid = models.CharField(max_length=255)
    client_version = models.CharField(max_length=255)
    uin = models.IntegerField()
    client_ip = models.CharField(max_length=255)
    retcode = models.IntegerField(blank=True, null=True)
    platform = models.IntegerField(blank=True, null=True)
    device = models.CharField(max_length=255)
    uuid = models.CharField(max_length=255)
    timestamp = models.IntegerField(blank=True, null=True)
    reserve1 = models.CharField(max_length=255)
    reserve2 = models.CharField(max_length=255)
    reserve3 = models.CharField(max_length=255)
    reserve4 = models.CharField(max_length=255)

    class Meta:
        db_table = 'report'

class Contract(models.Model):
    contract_id = models.CharField(primary_key=True, max_length=255)
    sign_time = models.DateTimeField()
    owner = models.ForeignKey(User)
    order_number = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'contract'

    def __unicode__(self):
        return u'%s)%s'%(self.contract_id, self.owner.name)

#class ContactReverseTimes(models.Model):
#    phone_no = models.CharField(max_length = 20)
#    times = models.IntegerField()
#    class Meta:
#        db_table = 'addressbookreversetimes'
#
#class ContactReverseTimes(models.Model):
#    phone_no = models.CharField(max_length = 20)
#    times = models.IntegerField()
#    class Meta:
#        db_table = 'contactreversetimes'

class Feedback(models.Model):
    content = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    owner = models.ForeignKey(User, null=True)
    sub_time = models.DateTimeField()

    class Meta:
        db_table = 'feedback'

    def __unicode__(self):
        return u'%s)%s'%(self.owner.name, self.sub_time.strftime("%y-%m-%d"))

class RenrenAccountInfo(models.Model):
    owner = models.ForeignKey(User)
    username = models.CharField(max_length=64)
    province = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    is_star = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=255)
    birthday = models.CharField(max_length=255)
    vip_level = models.IntegerField(blank=True, null=True)
    visitor_count = models.IntegerField(blank=True, null=True)
    status_count = models.IntegerField(blank=True, null=True)
    blog_count = models.IntegerField(blank=True, null=True)
    album_count = models.IntegerField(blank=True, null=True)
    share_count = models.IntegerField(blank=True, null=True)
    photo_count = models.IntegerField(blank=True, null=True)
    friend_count = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'renrenaccountinfo'


class RenrenEducation(models.Model):
    school = models.CharField(max_length=255)
    start_year = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    owner = models.ForeignKey(RenrenAccountInfo)

    class Meta:
        db_table = 'renreneducation'


class Chsiauthinfo(models.Model):
    username = models.BinaryField()
    password = models.BinaryField()
    user_id = models.BigIntegerField()
    code = models.CharField(max_length=32, blank=True)

    class Meta:
        db_table = 'chsiauthinfo'

class Strategy2(models.Model):
    strategy_id = models.IntegerField(primary_key=True)
    pre_factorage = models.FloatField()
    post_factorage = models.FloatField()
    interest = models.FloatField()
    installment_count = models.IntegerField()
    installment_days = models.IntegerField()
    installment_type = models.IntegerField()
    overdue_factorage = models.IntegerField()
    overdue_interest = models.FloatField()
    overdue_m2_interest = models.FloatField()
    overdue_m3_interest = models.FloatField()
    m1_days = models.IntegerField()
    m2_days = models.IntegerField()
    m3_days = models.IntegerField()
    discount = models.FloatField()
    description = models.CharField(max_length=255)
    strategy_description = models.CharField(max_length=255)
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'strategy2'


class UserPromotionCashflow(models.Model):
    user = models.ForeignKey(User)
    alipay_no = models.CharField(max_length=255)     #支付宝账号
    total_amount = models.IntegerField(blank=True, null=True)         #可提款总金额
    want_amount = models.IntegerField(blank=True, null=True)         #申请提现金额
    last_day = models.DateTimeField()       #上次打款时间
    process_day = models.DateTimeField()     #处理时间
    status = models.IntegerField(blank=True, null=True)         #状态

    class Meta:
        db_table = 'userpromotioncashflow'


class UserExtraInfoRecord(models.Model):
    content = models.CharField(max_length=1024, help_text="信息内容")
    create_at = models.DateTimeField(auto_now_add=True)
    create_by = models.ForeignKey(Employee, help_text="添加人员")
    user = models.ForeignKey(User)
    class Meta:
        db_table = 'userextrainforecord'
    def __unicode__(self):
        return u'%s)%s - %s'%(self.create_by.username ,self.user.name, self.content)


class Messagetemplate(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    title = models.CharField(max_length=128)
    content = models.CharField(max_length=1024)
    type = models.IntegerField()
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    url = models.CharField(max_length=256, blank=True)
    operation = models.IntegerField(blank=True, null=True)
    reserve = models.CharField(max_length=512, blank=True)
    priority = models.IntegerField(blank=True, null=True)
    img = models.CharField(max_length=256, blank=True)

    class Meta:
        managed = False
        db_table = 'messagetemplate'


class Userattach(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    ios_token = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    le_field1 = models.CharField(max_length=255, blank=True)
    le_field2 = models.CharField(max_length=255, blank=True)
    le_field3 = models.CharField(max_length=255, blank=True)
    le_field4 = models.CharField(max_length=255, blank=True)
    le_field5 = models.CharField(max_length=255, blank=True)
    le_field6 = models.CharField(max_length=255, blank=True)
    le_field7 = models.CharField(max_length=255, blank=True)
    le_field8 = models.CharField(max_length=255, blank=True)
    le_field9 = models.CharField(max_length=255, blank=True)
    le_field10 = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'userattach'


class Messagetemplate(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    title = models.CharField(max_length=128)
    content = models.CharField(max_length=1024)
    type = models.IntegerField()
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    url = models.CharField(max_length=256, blank=True)
    operation = models.IntegerField(blank=True, null=True)
    reserve = models.CharField(max_length=512, blank=True)
    priority = models.IntegerField(blank=True, null=True)
    img = models.CharField(max_length=256, blank=True)

    class Meta:
        managed = False
        db_table = 'messagetemplate'


class Usermessagecenter(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    owner = models.ForeignKey(User)
    msg = models.ForeignKey(Messagetemplate, blank=True, null=True, help_text="消息模板id")
    msg_type = models.IntegerField()
    is_read = models.IntegerField()
    create_at = models.DateTimeField(blank=True, null=True)
    is_reached = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usermessagecenter'


class Useronlinestatus(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    owner = models.ForeignKey(User)
    clientid = models.IntegerField()
    timestamp = models.IntegerField()
    status = models.IntegerField()
    proxyip = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'useronlinestatus'


class Pushrecords(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField()
    msg_id = models.IntegerField()
    is_reached = models.IntegerField()
    push_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pushrecords'


class PushMsg(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    content = models.CharField(max_length=1024, blank=True)
    description = models.CharField(max_length=64, blank=True)

    class Meta:
        managed = False
        db_table = 'push_msg'


class Useronlinestatus(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    owner = models.ForeignKey(User)
    clientid = models.IntegerField()
    timestamp = models.IntegerField()
    status = models.IntegerField()
    proxyip = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'useronlinestatus'

