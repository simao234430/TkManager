# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models import Q
from django.db.models.signals import post_migrate#, post_syncdb

post_t = (
    ('ad', u'管理员'),
    ('an', u'数据分析师'),
    ('rm', u'审批经理'),
    ('rz', u'审批主管'),
    ('r2', u'审批组长'),
    ('rs', u'审批专员'),
    ('r3', u'审批质检'),
    ('r4', u'回访专员'),
    ('cm', u'催收经理'),
    ('c1', u'催收主管'),
    ('cs', u'催收专员'),
    ('op', u'运营经理'),
    ('o1', u'运营专员'),
    ('se', u'客服专员'),
    ('au', u'财务会计'),
)

class Employee(models.Model):
    online_t = (
        ('n', 'online'),
        ('f', 'offline'),
    )

    user = models.ForeignKey(User)
    username = models.CharField(max_length=255, help_text=u"员工姓名", default=u"待补充")
    phone_no = models.CharField(blank=True, null=True, max_length=255)
    #online = models.CharField(max_length=1, choices=online_t, default='n')

    post = models.CharField(blank=True, null=True, max_length=2, choices=post_t)

    def __unicode__(self):
        return u'%d)%s: %s'%(self.id,self.get_post_display(), self.user.username )

    def check_page_permission(self, page):
        '''
            每个职位有权限访问的地址按照前缀匹配
        '''
        for permission in EmplyeePermission.objects.filter(post=self.post):
            if page.startswith(permission.url):
                return True
        return False

def create_employee(name, email, post, phone_no, chinese_name):
    users = User.objects.filter(username = name)
    if len(users) == 0:
        user = User.objects.create_user(name, email, '123456')
        Employee(user=user, username=chinese_name, phone_no=phone_no, post=post).save()
    else:
        employees = Employee.objects.filter(user = users[0])
        if len(employees) != 0:
            #TkLog().info("create user:%s failed. user exist already"% name)
            return False
        Employee(user=users[0], username=chinese_name, phone_no=phone_no, post=post).save()
    #TkLog().info("create user:%s success"% name)
    return True

@receiver(post_migrate)#, sender=EmplyeePermission)
def gen_default_user(sender, **kwargs):
    '''
        初始化几个用户做测试
    '''
    create_employee("admin", "admin@tkcash.com", "ad", "12312341234", u"管理员")
    create_employee("tanshaohua", "tanshaohua@tkcash.com", "an", "12312341234", u"谭绍华")
    create_employee("zhaoheng", "zhaoheng@tkcash.com", "rm", "12312341234", u"赵恒")
    create_employee("hujia", "hujia@tkcash.com", "rs", "12312341234", u"胡佳")
    create_employee("liuxiaojun", "liuxiaojun@tkcash.com", "rs", "12312341234", u"刘小军")
    create_employee("xiaojun", "xiaojun@tkcash.com", "cs", "12312341234", u"肖军")
    create_employee("liyanjie", "liyanjie@tkcash.com", "cm", "12312341234", u"李彦洁")

    create_employee("test_ad", "xiaojun@tkcash.com", "ad", "123456", u"测试_ad")
    create_employee("test_an", "xiaojun@tkcash.com", "an", "123456", u"测试_an")
    create_employee("test_rm", "xiaojun@tkcash.com", "rm", "123456", u"测试_rm")
    create_employee("test_r2", "xiaojun@tkcash.com", "r2", "123456", u"测试_r2")
    create_employee("test_rz", "xiaojun@tkcash.com", "rz", "123456", u"测试_rz")
    create_employee("test_rs", "xiaojun@tkcash.com", "rs", "123456", u"测试_rs")
    create_employee("test_r3", "xiaojun@tkcash.com", "r3", "123456", u"测试_r3")
    create_employee("test_r4", "xiaojun@tkcash.com", "r4", "123456", u"测试_r4")
    create_employee("test_cm", "xiaojun@tkcash.com", "cm", "123456", u"测试_cm")
    create_employee("test_c1", "xiaojun@tkcash.com", "c1", "123456", u"测试_c1")
    create_employee("test_cs", "xiaojun@tkcash.com", "cs", "123456", u"测试_cs")
    create_employee("test_op", "xiaojun@tkcash.com", "op", "123456", u"测试_op")
    create_employee("test_o1", "xiaojun@tkcash.com", "o1", "123456", u"测试_o1")
    create_employee("test_se", "xiaojun@tkcash.com", "se", "123456", u"测试_se")
    create_employee("test_au", "xiaojun@tkcash.com", "au", "123456", u"测试_au")
class EmployeeAction(models.Model):
    action_t = (
        ('start_review', 'start_review'),
        ('end_review', 'end_review'),
    )

    user = models.ForeignKey(Employee)
    action = models.CharField(max_length=20, choices=action_t)
    timestamp = models.DateTimeField()

class EmplyeePermission(models.Model):
    post = models.CharField(blank=True, null=True, max_length=2, choices=post_t, help_text="职务")
    url = models.CharField(max_length=255, help_text=u"路径")

    #def ready(self):
    #    post_migrate.connect(gen_default_permission, sender=self)

    def __unicode__(self):
        return u'%d)%s: %s'%(self.id,self.get_post_display(), self.url)

@receiver(post_migrate)#, sender=EmplyeePermission)
def gen_default_permission(sender, **kwargs):
    '''
        初始化权限列表
    '''
    EmplyeePermission.objects.all().delete()
    #('ad', u'管理员'),
    EmplyeePermission(post='ad', url="/order").save()
    EmplyeePermission(post='ad', url="/review/mine").save()
    EmplyeePermission(post='ad', url="/review/all").save()
    EmplyeePermission(post='ad', url="/review/info").save()
    EmplyeePermission(post='ad', url="/review/action").save()
    EmplyeePermission(post='ad', url="/operation").save()
    EmplyeePermission(post='ad', url="/collection").save()
    EmplyeePermission(post='ad', url="/admin").save()
    EmplyeePermission(post='ad', url="/custom").save()
    EmplyeePermission(post='ad', url="/audit").save()

    #('an', u'数据分析师'),
    EmplyeePermission(post='an', url="/order").save()

    #('rm', u'审批经理'),
    EmplyeePermission(post='rm', url="/review/mine").save()
    EmplyeePermission(post='rm', url="/review/all").save()
    EmplyeePermission(post='rm', url="/review/info").save()
    EmplyeePermission(post='rm', url="/review/action").save()
    #EmplyeePermission(post='rz', url="/custom").save()
    EmplyeePermission(post='rm', url="/custom/user_view").save()
    EmplyeePermission(post='rm', url="/custom/query").save()
    EmplyeePermission(post='rm', url="/custom/query_detail").save()
    EmplyeePermission(post='rm', url="/custom/get_loan_data").save()
    EmplyeePermission(post='rm', url="/collection/get_collection_record_json").save()


    #('rm', u'审批主管'),
    EmplyeePermission(post='rz', url="/review/mine").save()
    EmplyeePermission(post='rz', url="/review/all").save()
    EmplyeePermission(post='rz', url="/review/info").save()
    EmplyeePermission(post='rz', url="/review/action").save()
    #EmplyeePermission(post='rz', url="/custom").save()
    EmplyeePermission(post='rz', url="/custom/user_view").save()
    EmplyeePermission(post='rz', url="/custom/query_detail").save()
    EmplyeePermission(post='rz', url="/custom/query").save()
    EmplyeePermission(post='rz', url="/custom/get_loan_data").save()
    EmplyeePermission(post='rz', url="/collection/get_collection_record_json").save()
    #('rs', u'审批专员'),
    EmplyeePermission(post='rs', url="/review/mine").save()
    EmplyeePermission(post='rs', url="/review/info").save()
    EmplyeePermission(post='rs', url="/review/action").save()
    #EmplyeePermission(post='rz', url="/custom").save()
    EmplyeePermission(post='rs', url="/custom/user_view").save()
    EmplyeePermission(post='rs', url="/custom/query").save()
    EmplyeePermission(post='rs', url="/custom/query_detail").save()
    EmplyeePermission(post='rs', url="/custom/get_loan_data").save()
    EmplyeePermission(post='rs', url="/collection/get_collection_record_json").save()

    #('r3', u'审批质检'),
    EmplyeePermission(post='r3', url="/review/mine").save()
    EmplyeePermission(post='r3', url="/review/all").save()
    EmplyeePermission(post='r3', url="/review/info").save()
    EmplyeePermission(post='r3', url="/review/action").save()
    #EmplyeePermission(post='rz', url="/custom").save()
    EmplyeePermission(post='r3', url="/custom/user_view").save()
    EmplyeePermission(post='r3', url="/custom/query").save()
    EmplyeePermission(post='r3', url="/custom/query_detail").save()
    EmplyeePermission(post='r3', url="/custom/get_loan_data").save()
    EmplyeePermission(post='r3', url="/collection/get_collection_record_json").save()

    #('r2', u'审批组长'),
    EmplyeePermission(post='r2', url="/review/mine").save()
    EmplyeePermission(post='r2', url="/review/all").save()
    EmplyeePermission(post='r2', url="/review/info").save()
    EmplyeePermission(post='r2', url="/review/action").save()
    #EmplyeePermission(post='rz', url="/custom").save()
    EmplyeePermission(post='r2', url="/custom/user_view").save()
    EmplyeePermission(post='r2', url="/custom/query").save()
    EmplyeePermission(post='r2', url="/custom/query_detail").save()
    EmplyeePermission(post='r2', url="/custom/get_loan_data").save()
    EmplyeePermission(post='r2', url="/collection/get_collection_record_json").save()


    #('cm', u'催收经理'),
    EmplyeePermission(post='cm', url="/collection").save()
   # EmplyeePermission(post='cm', url="/custom").save()
   # EmplyeePermission(post='cm', url="/review").save()
   # EmplyeePermission(post='cm', url="/operation").save()
    EmplyeePermission(post='cm', url="/custom/user_view").save()
    EmplyeePermission(post='cm', url="/custom/query_detail").save()
    EmplyeePermission(post='cm', url="/custom/query").save()
    EmplyeePermission(post='cm', url="/custom/get_loan_data").save()
    EmplyeePermission(post='cm', url="/collection/get_collection_record_json").save()
    EmplyeePermission(post='cm', url="/review/info/view").save()
    EmplyeePermission(post='cm', url="/review/download_addressbook").save()
    #('cm', u'催收主管'),
    EmplyeePermission(post='c1', url="/collection").save()
   # EmplyeePermission(post='cm', url="/custom").save()
   # EmplyeePermission(post='cm', url="/review").save()
   # EmplyeePermission(post='cm', url="/operation").save()
    EmplyeePermission(post='c1', url="/custom/user_view").save()
    EmplyeePermission(post='c1', url="/custom/query").save()
    EmplyeePermission(post='c1', url="/custom/query_detail").save()
    EmplyeePermission(post='c1', url="/custom/get_loan_data").save()
    EmplyeePermission(post='c1', url="/collection/get_collection_record_json").save()
    EmplyeePermission(post='c1', url="/review/info/view").save()
    EmplyeePermission(post='c1', url="/review/download_addressbook").save()

    #('cs', u'催收专员'),
    EmplyeePermission(post='cs', url="/collection/mine").save()
    EmplyeePermission(post='cs', url="/collection/info").save()
    EmplyeePermission(post='cs', url="/collection/action").save()
    EmplyeePermission(post='cs', url="/collection/my_collection_json").save()
    EmplyeePermission(post='cs', url="/collection/modal").save()
    EmplyeePermission(post='cs', url="/collection/get_collection_record_json").save()
    #EmplyeePermission(post='cs', url="/custom").save()
    EmplyeePermission(post='cs', url="/custom/user_view").save()
    EmplyeePermission(post='cs', url="/custom/query").save()
    EmplyeePermission(post='cs', url="/custom/query_detail").save()
    EmplyeePermission(post='cs', url="/custom/get_loan_data").save()
    EmplyeePermission(post='cs', url="/review/info/view").save()
    EmplyeePermission(post='cs', url="/review/download_addressbook").save()
    #EmplyeePermission(post='cs', url="/review").save()
    #EmplyeePermission(post='cs', url="/operation").save()

    #('op', u'运营经理'),
    EmplyeePermission(post='op', url="/operation").save()
    EmplyeePermission(post='op', url="/custom").save()
    EmplyeePermission(post='op', url="/collection/get_collection_record_json").save()
    #('op1', u'运营专员'),
    EmplyeePermission(post='o1', url="/operation").save()
    EmplyeePermission(post='o1', url="/custom").save()
    EmplyeePermission(post='o1', url="/collection/get_collection_record_json").save()

    #('se', u'客服'),
    #EmplyeePermission(post='se', url="/operation").save()
    #EmplyeePermission(post='se', url="/review/all").save()
    EmplyeePermission(post='se', url="/custom").save()
    EmplyeePermission(post='se', url="/collection/get_collection_record_json").save()
    EmplyeePermission(post='se', url="/operation/repay4custom").save()

    #('r4', u'回访专员'),
    #EmplyeePermission(post='r4', url="/custom").save()
    EmplyeePermission(post='r4', url="/custom/user_view").save()
    EmplyeePermission(post='r4', url="/custom/query").save()
    EmplyeePermission(post='r4', url="/custom/query_detail").save()
    EmplyeePermission(post='r4', url="/custom/get_loan_data").save()
    EmplyeePermission(post='r4', url="/collection/get_collection_record_json").save()
    #('au', u'财务'),
    EmplyeePermission(post='au', url="/audit").save()
   # EmplyeePermission(post='se', url="/custom").save()
   # EmplyeePermission(post='se', url="/custom").save()
    EmplyeePermission(post='au', url="/operation").save()
    EmplyeePermission(post='au', url="/custom/user_view").save()
    EmplyeePermission(post='au', url="/custom/query").save()
    EmplyeePermission(post='au', url="/custom/query_detail").save()
    EmplyeePermission(post='au', url="/custom/get_loan_data").save()
    EmplyeePermission(post='au', url="/collection/get_collection_record_json").save()

def check_employee(request):
    try:
        staff = Employee.objects.get(user = request.user)
        return staff.check_page_permission(request.path)
    except Exception, e:
        return False

def is_review_manager(request):
    try:
        staff = Employee.objects.get(user = request.user)
        #return staff.post == 'rm' or staff.post == "ad"
        return staff.post == "ad" or staff.post == "rz"
    except Exception, e:
        return False

def is_review_group_leader(request):
    try:
        staff = Employee.objects.get(user = request.user)
        return staff.post == 'r2'
    except Exception, e:
        return False

def get_collector_list():
    try:
        collectors = Employee.objects.filter(Q(post="cm") | Q(post="cs"))
        return collectors
    except Exception, e:
        print e
        return []

def is_collection_manager(request):
    try:
        staff = Employee.objects.get(user = request.user)
        return staff.post == 'cm' or staff.post == 'ad'
    except Exception, e:
        return False

def get_employee(request):
    try:
        staff = Employee.objects.get(user = request.user)
        return staff
    except Exception, e:
        return None
