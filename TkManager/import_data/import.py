# -*- coding: utf-8 -*-

from pyExcelerator import *
from TkManager.order.models import User, CheckStatus, Profile, ContactInfo, BankCard, IdCard
from django.conf import settings
import xlrd
import sys
import re

f_pattern = re.compile(u".*(父亲|爸爸).*")
m_pattern = re.compile(u".*(母亲|妈妈).*")
#m_pattern = re.compile(u".*(母亲|妈妈).*")

def get_relation(relationship, name, user_name, has_parents, has_father):
    #print name, has_father, has_parents
    sure = False
    if f_pattern.match(name):
        sure = True
        relationship = u"父亲"
    if m_pattern.match(name):
        sure = True
        relationship = u"母亲"
    try:
        if not sure and not has_parents and relationship == u"父母":
            name_pattern = re.compile(u"^%s" % (user_name[0]))
            #print user_name, name
            if name_pattern.match(name):
                #print "match first name"
                relationship = u"父亲"
            else:
                #print "not match first name"
                relationship = u"母亲"
    except Exception, e:
        print e

    if relationship == u"父母":
        if not has_parents:
            if has_father:
                return ContactInfo.MOTHER
            else:
                return ContactInfo.FATHER
        else:
            return ContactInfo.RELATIVE
    elif relationship == u"父亲":
        return ContactInfo.FATHER
    elif relationship == u"母亲":
        return ContactInfo.MOTHER
    elif relationship == u"亲戚":
        return ContactInfo.RELATIVE
    elif relationship == u"配偶":
        return ContactInfo.MATE
    elif relationship == u"朋友":
        return ContactInfo.FRIEND
    elif relationship == u"同事":
        return ContactInfo.WORKMATE
    elif relationship == u"同学":
        return ContactInfo.CLASSMATE
    return ContactInfo.UNKNOWN

def is_parent(relationship):
    if relationship == ContactInfo.FATHER or relationship == ContactInfo.MOTHER:
        return True
    return False

def strip_name(name):
    return re.sub(u'([\u4e00-\u9fa5]+).*', '\\1', name)

def strip_address(address):
    address = re.sub(u'四川成都', u'四川省成都市', address)
    address = re.sub(u'贵州贵阳贵阳市', u'贵州省贵阳市', address)
    return address

def get_gender(gender):
    if gender == u"男":
        return Profile.MALE
    elif gender == u"女":
        return Profile.FEMALE
    return Profile.UNKNOWN

def get_job(job):
    if job == u"I类":
        return Profile.WORKING
    elif job == u"S类":
        return Profile.STDUENT
    return Profile.UNKNOWN

def get_marriage(marriage):
    if marriage == u"未婚":
        return Profile.SINGLE
    elif marriage == u"已婚":
        return Profile.MARRIED
    elif marriage == u"已婚无子女":
        #return Profile.MARRIED_NO_CHILD
        return Profile.MARRIED
    elif marriage == u"已婚有子女":
        #return Profile.MARRIED_HAS_CHILD
        return Profile.MARRIED
    elif marriage == u"离异":
        #return Profile.DIVORCED
        return Profile.SINGLE
    elif marriage == u"丧偶":
        #return Profile.WIDOWS
        return Profile.SINGLE
    return Profile.UNKNOWN

def get_bank_type(bank_type):
    if bank_type == u"建设银行":
        return 1
    elif bank_type == u"中国银行":
        return 2
    elif bank_type == u"农业银行":
        return 3
    elif bank_type == u"招商银行":
        return 4
    elif bank_type == u"广发银行":
        return 5
    elif bank_type == u"兴业银行":
        return 6
    elif bank_type == u"工商银行":
        return 7
    elif bank_type == u"光大银行":
        return 8
    elif bank_type == u"中国邮政储蓄" or bank_type == u"邮政储蓄银行":
        return 9
    return 0

def import_from_file(filename):
    wb = xlrd.open_workbook(filename)  #打开文件
    sh = wb.sheet_by_index(0) #获得工作表的方法1
    cellA1Value = sh.cell_value(0, 1) #获得单元格数据
    row_count=sh.nrows #获得行数
    col_count=sh.ncols  #获得列数

    #0  NAME    PASSWORD    PHONE_NO    ID_NO       CREATE_TIME    IMEI
    #6  NAME    ADDRESS     ID_NO       PHONE_NO    RELATIONSHIP
    #11 NAME    ADDRESS     ID_NO       PHONE_NO    RELATIONSHIP
    #16 NAME    ADDRESS     ID_NO       PHONE_NO    RELATIONSHIP
    #21 NAME    ADDRESS     ID_NO       PHONE_NO    RELATIONSHIP
    #26 NAME    ADDRESS     ID_NO       PHONE_NO    RELATIONSHIP
    #31 NAME    ADDRESS     ID_NO       PHONE_NO    RELATIONSHIP
    #36 GENDER  JOB         MARRIAGE    COMPANY     WORK_POST       WORK_ADDRESS    COMPANY_PHONE   FAMILY_ADDRESS
    #44 EXPECT_AMOUNT       EMAIL       QQ          BANK_NUMBER     BANK_TYPE       PHONE_NO        BANK_NAME

    for i in xrange(1, row_count):
    #for i in xrange(1, 4):
        index = 0
        custom_name = sh.cell_value(i, index)
        index += 1
        password = sh.cell_value(i, index)
        index += 1
        phone_no = sh.cell_value(i, index)
        index += 1
        id_no = sh.cell_value(i, index)
        index += 1
        create_time = sh.cell_value(i, index)
        index += 1
        imei = sh.cell_value(i, index)
        index += 1

        exist_users = User.objects.filter(phone_no=phone_no)
        if len(exist_users) != 0:
            #print "exist user %s" % (phone_no)
            #continue
            for exist_user in exist_users:
                try:
                    exist_user.delete()
                except Exception,e:
                    print e

        user = User(name=custom_name, password="e10adc3949ba59abbe56e057f20f883e", phone_no=phone_no, id_no=id_no, channel="线下导入", device_name="", device_id=0, imei=imei, imsi="", android_id="", is_register=1)
        user.save()
        #print user.id

        idcard = IdCard(owner=user, id_no=id_no)
        idcard.save()

        check = CheckStatus(owner=user, apply_status=CheckStatus.NOT_SUBMITTED, profile_status=16405, profile_check_status=16405, credit_limit=100000,
                            increase_status=0, increase_check_status=0, real_id_verify_status=5, auto_check_status=0)
        check.save()

        index = 36
        gender = sh.cell_value(i, index)
        index += 1
        job = sh.cell_value(i, index)
        index += 1
        marriage = sh.cell_value(i, index)
        index += 1
        company = sh.cell_value(i, index)
        index += 1
        work_post = sh.cell_value(i, index)
        index += 1
        work_address = sh.cell_value(i, index)
        index += 1
        company_phone = sh.cell_value(i, index)
        index += 1
        family_address = sh.cell_value(i, index)
        index += 1


        index = 45
        email = sh.cell_value(i, index)
        index += 1
        qq = sh.cell_value(i, index)
        index += 1
        #print gender, company_phone, company, work_address
        profile = Profile(owner=user, gender=get_gender(gender), job=get_job(job), marriage=get_marriage(marriage),
                          company=company, work_post=work_post, company_phone=company_phone, family_address=strip_address(family_address),
                          work_address=strip_address(work_address), email=email, qq=qq)
        profile.save()

        bank_number = sh.cell_value(i, index)
        index += 1
        bank_type = sh.cell_value(i, index)
        index += 1
        bank_phone_no = sh.cell_value(i, index)
        index += 1
        bank_name = sh.cell_value(i, index)
        index += 1
        bankcard = BankCard(user=user, number=bank_number, card_type=BankCard.LOAN_REPAY, bank_type=get_bank_type(bank_type), phone_no=bank_phone_no, bank_name=bank_name)
        bankcard.save()

        index = 6
        saved = 0
        has_parents = False
        has_father = False
        parents_count = 0
        for j in range(0, 6):
            name = sh.cell_value(i, index)
            index += 1
            address = sh.cell_value(i, index)
            index += 1
            id_no = sh.cell_value(i, index)
            index += 1
            phone_no = sh.cell_value(i, index)
            index += 1
            relationship = sh.cell_value(i, index)
            index += 1
            if name == "":
                continue
            real_relationship = get_relation(relationship, name, custom_name, has_parents, has_father)
            #print "haha", real_relationship, has_father, has_parents
            if real_relationship == ContactInfo.FATHER or real_relationship == ContactInfo.MOTHER:
                if real_relationship == ContactInfo.FATHER:
                    has_father = True
                parents_count += 1
                if parents_count >= 2:
                    has_parents = True

            if real_relationship == ContactInfo.FATHER or real_relationship == ContactInfo.MOTHER:
                contract = ContactInfo(owner=user, name=strip_name(name), address=address, id_no=id_no, phone_no=phone_no, relationship=real_relationship)
            else:
                contract = ContactInfo(owner=user, name=name, address=address, id_no=id_no, phone_no=phone_no, relationship=real_relationship)
            contract.save()
            saved += 1
            if saved == 3:
                break
        print "import %s success." % (user.name)

if __name__ == "__main__":
    filenames = settings.IMPORT_FILE
    for xls_file in filenames:
        print "import xls_file", xls_file
        import_from_file(xls_file)
