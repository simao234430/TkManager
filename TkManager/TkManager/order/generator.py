# -*- coding: utf-8 -*-
import random,string,uuid,time,datetime
from TkManager.order.models import *
from TkManager.review.models import Review, Employee
from TkManager.util.decorator import *

from django.http import HttpResponse

#@singleton
class Generator(object):

    _alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    _phone_prefix = ["132", "158", "130", "131", "134"]
    _school = ["pku", "thu", "hust", "whu"]
    _education = [u"本科", u"大专", u"研究生", u"中专", u"高中", u"无"]
    _relation = [u"父亲", u"母亲"]
    _employee_id = [1, 2, 3, 4, 5]
    _user_groups = [u"学生", u"上班族"]
    _source = [u"线下推广", u"搜索引擎", u"应用市场"]

    def random_sample_string(self, len):
        return string.join(random.sample(Generator._alphabet, len)).replace(" ","")

    def random_string(self, len):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(len))

    def random_number_str(self, len):
        return ''.join(random.SystemRandom().choice(string.digits) for _ in range(len))

    def random_number(self, min, max):
        return random.randint(min, max)

    def random_education(self):
        return random.choice(Generator._education)

    def random_relationship(self):
        return random.choice(Generator._relation)

    def random_ip(self):
        return str(random.randint(1, 255)) + "." + str(random.randint(0, 255)) + "." + str(random.randint(0, 255))  + "." + str(random.randint(0, 255))

    def random_school(self):
        return random.choice(Generator._school)

    def random_uuid(self):
        return uuid.uuid1()

    def random_phone(self):
        return random.choice(Generator._phone_prefix) + self.random_number_str(8)

    def random_user(self):
        return self.random_sample_string(8)

    def random_date(self):
        return

    def random_time(self):
        return

    def random_employee(self):
        id = random.choice(Generator._employee_id)
        return Employee.objects.get(pk=id)

    def random_user_group(self):
        return random.choice(Generator._user_groups)

    def random_source(self):
        return random.choice(Generator._source)

    def str_time_prop(self, start, end, format, prop):
        """Get a time at a proportion of a range of two formatted times.

        start and end should be strings specifying times formated in the
        given format (strftime-style), giving an interval [start, end].
        prop specifies how a proportion of the interval to be taken after
        start.  The returned time will be in the specified format.
        """
        stime = time.mktime(time.strptime(start, format))
        etime = time.mktime(time.strptime(end, format))
        ptime = stime + prop * (etime - stime)

        return time.strftime(format, time.localtime(ptime))

    def random_time_str(self, start, end, prop):
        return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', Random.random(a))

    def generate_user(self):
        user = User(name=self.random_user(), phone_no=self.random_phone())
        #user.user_group = self.random_user_group()
        user.channel = self.random_source()
        user.password = self.random_string(20)
        user.payment_password = self.random_string(20)
        user.id_no = self.random_number_str(18);
        user.save()

        profile = Profile(owner=user)
        profile.gender = self.random_number(1, 2)
        profile.job = self.random_number(1, 2)
        profile.company = self.random_string(30)
        profile.work_address = self.random_string(30)
        profile.company_phone = self.random_phone()
        profile.family_address = self.random_string(30)
        profile.expect_amount = self.random_number(3000,10000)
        profile.max_credit = self.random_number(profile.expect_amount,10000)
        profile.save()

        idcard = IdCard(owner=user)
        idcard.id_no = user.id_no
        idcard.id_pic_front = self.random_number_str(10);
        idcard.id_pic_back = self.random_number_str(10);
        idcard.id_pic_self = self.random_number_str(10);
        idcard.id_birth = datetime.datetime.now()
        idcard.id_name = self.random_user()
        idcard.id_address = self.random_string(20)
        idcard.id_ctime = datetime.datetime.now()
        idcard.save()

        status = CheckStatus(owner=user)
        status.profile_status = 0x01010101
        status.profile_check_status = 0
        status.increse_status = 0x01010101
        status.increase_check_status = 0
        status.credit_limit = self.random_number(1000, 10000)
        status.save()

        chsi = Chsi(user=user)
        chsi.chsi_name = self.random_string(8)
        chsi.school = self.random_school()
        chsi.head_img = self.random_string(20)
        chsi.gender = self.random_string(2)
        chsi.id_card_number = self.random_string(20)
        chsi.nation = self.random_string(20)
        chsi.birthday = self.random_string(20)
        chsi.education = self.random_string(20)
        chsi.collage = self.random_string(20)
        chsi.school_class = self.random_string(20)
        chsi.student_id = self.random_string(20)
        chsi.major = self.random_string(20)
        chsi.edu_type = self.random_string(20)
        chsi.enrollment = self.random_string(20)
        chsi.edu_duration = self.random_string(20)
        chsi.edu_status = self.random_string(20)
        chsi.save()

        contacter = ContactInfo(owner=user)
        contacter.name = self.random_user()
        contacter.phone_no = self.random_phone()
        contacter.id_no = self.random_number_str(18)
        contacter.address = self.random_string(40)
        contacter.relationship = self.random_number(0, 3)
        contacter.save()
        print "user id: ", user.id
        return user

    #def review_apply(self, apply, status="y"):
    #    pass

    def generate_review(self, applyid):
        order = Apply.objects.get(pk=applyid)
        order.finish_time = datetime.datetime.now()
        order.status = 'y'
        review = Review()
        review.order = order
        review.create_at = datetime.datetime.now()
        review_t = self.random_number(5, 30)
        review.finish_time = datetime.datetime.now() + datetime.timedelta(minutes=review_t)
        review.reviewer_done = review.reviewer = self.random_employee()
        review.save()
        order.review_id = review.id
        order.save()
        order.create_by= 0xff
        order.create_by.save()

    def generate_apply(self):
        user = self.generate_user()
        apply = Apply(create_by=user)
        apply.ip = self.random_ip()
        apply.type = '0'
        apply.create_at = datetime.datetime.now()
        apply.save()
        print "apply id: ", apply.id
        return user.id

    def generate_promotion(self):
        #if userid == 0:
        user = User.objects.filter(verify_status=0xff).order_by('?')[:1][0]
        #else:
        #    user = User.objects.filter(pk = userid)
        promotion = Apply(create_by=user)
        #promotion.type = str(self.random_number(1,6))
        promotion.type = '1'
        promotion.ip = self.random_ip()
        promotion.create_at = datetime.datetime.now()
        promotion.save()
        print "promotion id: ", promotion.id
        return promotion

    def generate_loan(self):
        user = User.objects.filter().order_by('?')[:1][0]
        #else:
        #    user = User.objects.filter(pk = userid)
        loan = Apply(create_by=user)
        loan.type = 'l'
        loan.ip = self.random_ip()
        loan.create_at = datetime.datetime.now()
        loan.save()
        print "loan id: ", loan.id
        return loan

def generate_apply(request):
    gen = Generator()
    if request.method == 'GET':
        type = request.GET.get("type")
        #print type,request
        if type == "baseapply":
            return gen.generate_apply()
        elif type == "loan":
            applyid = request.GET.get("userid")
            gen.generate_loan()
        elif type == "promotion":
            gen.generate_promotion()
        elif type == "review":
            applyid = request.GET.get("applyid")
            gen.generate_review(applyid)
        return HttpResponse("generate " + type + " Success")
    return HttpResponse("failed")

#if __name__ == "__main__":
#   generate_apply()
