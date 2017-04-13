# -*- coding: utf-8 -*-
from collections import deque

class ReviewDispatcher(Object):
    def __init__(objects):
        '''
            初始化的队列是按照时间排序的
        '''
        self.job_list = objects
        self.user_list = deque()
        self.max_id = -1
        pass

    def get(self, staff):
        '''
            从工作池中获取一个员工的申请列表
            如果改员工不存在返回空
        '''
        try:
            return self.job_list.get(staff)
        except Exception e:
            return []

    def add(self, staff):
        '''
            向工作池中增加一个员工
        '''
        self.user_list.append(staff)
        self.balance()
        return True

    def remove(self, staff):
        '''
            向工作池中删除一个员工
            如果该员工不存在返回fasle
        '''
        self.user_list.leftpop()
        return True

    def finish_job(self, staff, job):
        '''
            完成一个审批，从员工工作队列中删除job
        '''
        return self.job_list[staff].remove(job)

    def balance(self):
        '''
            重新分配任务列表
        '''
        new_jobs_size = self.job_list.size() / self.user_list.size()
        for staff in self.job_list.keys():
            job_liststaff.

    def reload(self):
        '''
            从数据库load新的数据
        '''
        pass

