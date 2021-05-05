from collections import deque
from datetime import timedelta, datetime
from .base.DTO import DTO

SUCCESS = 1
FAIL = 2
WAIT = 0


class StockCrawlingTaskDTO(DTO):

    def __init__(self) -> None:
        self.count = 0
        self.successCount = 0
        self.failCount = 0
        self.restCount = 0
        self.failTasks: deque = deque()
        self.state = "stop"
        self.tasks: deque = deque()
        self.tasksRet: deque = deque()
        self.index = 0
        self.market = ""
        self.startDateStr = ""
        self.endDateStr = ""
        self.taskUniqueId = ""
        self.percent = 0.0

    def setTasks(self, startDateStr: str, endDateStr: str, market: str, taskId: str, taskUniqueId: str) -> None:
        self.startDateStr = startDateStr
        self.endDateStr = endDateStr
        self.taskId = taskId
        self.market = market
        self.taskUniqueId = taskUniqueId
        startDate = datetime.strptime(startDateStr, "%Y%m%d")
        endDate = datetime.strptime(endDateStr, "%Y%m%d")
        tasks = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
        self.count = len(tasks)
        self.successCount = 0
        self.restCount = len(tasks)
        self.failCount = 0
        self.state = "running"
        self.tasks = deque(tasks)
        self.index = 0
        self.tasksRet = deque(([0]*len(tasks)))
        self.percent = 0.0
    
    def reset(self) -> None:
        self.count = 0
        self.successCount = 0
        self.restCount = 0
        self.failTasks = deque()
        self.failCount = 0
        self.state = "stop"
        self.tasks = deque()
        self.index = 0
        self.tasksRet = deque()
        self.startDateStr = ""
        self.endDateStr = ""
        self.percent = 0.0
    
    def setState(self, state: str) -> None:
        self.state = state

    def success(self, count: int) -> None:
        self.successCount = self.successCount + count
        self.restCount = self.restCount - count
        i = 0
        for _ in range(count):
            self.tasksRet[self.index + i] = SUCCESS
            i = i+1
        self.index = self.index + count
        self.percent = (self.successCount+self.failCount)/self.count * 100
        if self.restCount <= 0:
            self.state = "success"
        else:
            self.state = "waiting next task"

    def fail(self, count: int) -> None:
        self.failCount = self.failCount + count
        self.restCount = self.restCount - count
        i = 0
        for _ in range(count):
            left = self.tasks[self.index + i]
            self.failTasks.append(left)
            self.tasksRet[self.index + i] = FAIL
            i = i+1
        self.index = self.index + count
        self.percent = (self.successCount+self.failCount)/self.count * 100
        if self.restCount <= 0:
            self.state = "fail"
        else:
            self.state = "waiting next task"

    # def toDict(self):
    #     return {"count": self.count,
    #             "successCount": self.successCount,
    #             "restCount": self.restCount,
    #             "failCount": self.failCount,
    #             "state": self.state,
    #             "taskId": self.taskId
    #             }
