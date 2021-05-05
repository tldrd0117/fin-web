from .base.DTO import DTO
from collections import deque
from .StockCrawlingTaskDTO import StockCrawlingTaskDTO


class StockCrawlingTasksDTO(DTO):

    def __init__(self) -> None:
        self.tasks: dict = dict()
        self.taskIds: deque = deque()

    def addTask(self, task: StockCrawlingTaskDTO) -> None:
        if "marcap" not in self.tasks:
            self.tasks[task.taskId] = dict()
            self.tasks[task.taskId]["list"] = dict()
            self.tasks[task.taskId]["ids"] = []
            self.taskIds.append("marcap")
        self.tasks[task.taskId]["list"][task.taskUniqueId] = task
        self.tasks[task.taskId]["ids"].append(task.taskUniqueId)
    
    def updateTask(self, task: StockCrawlingTaskDTO) -> None:
        self.tasks[task.taskId]["list"][task.taskUniqueId] = task
    
    def deleteTask(self, task: StockCrawlingTaskDTO) -> None:
        del self.tasks[task.taskId]["list"][task.taskUniqueId]
        self.tasks[task.taskId]["ids"].remove(task.taskUniqueId)
    
