from collections import deque
from datetime import date, timedelta, datetime

class StockCrawlingTaskDTO:
    count = 0
    successCount = 0
    failCount = 0
    restCount = 0
    restTasks = deque()
    failTasks = deque()
    currentTask = ""

    def __init__(self):
        pass

    def setTasks(self, startDateStr, endDateStr):
        startDate = datetime.strptime(startDateStr,"%Y%m%d")
        endDate = datetime.strptime(endDateStr,"%Y%m%d")
        tasks = [startDate + timedelta(days=x) for x in range((endDate-startDate).days + 1)]
        self.count = len(tasks)
        self.successCount = 0
        self.restCount = len(tasks)
        self.restTasks = deque(tasks)
        self.failCount = 0
    
    def reset(self):
        count = 0
        successCount = 0
        restCount = 0
        restTasks = deque()
        currentTask = ""

    def success(self, count):
        self.successCount = self.successCount + count
        self.restCount = self.restCount - count
        for _ in range(count):
            self.restTasks.popleft()
    
    def fail(self, count):
        self.failCount = self.failCount + count
        self.restCount = self.restCount - count
        for _ in range(count):
            left = self.restTasks.popleft()
            self.failTasks.append(left)
    
    def __str__(self):
        return f'count: {self.count}, successCount: {self.successCount}, restCount: {self.restCount}, failCount: {self.failCount}'
    
    def toDict(self):
        return {"count":self.count,"successCount":self.successCount, "restCount":self.restCount, "failCount":self.failCount}