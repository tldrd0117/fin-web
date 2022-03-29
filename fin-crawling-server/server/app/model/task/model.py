from typing import List
from pydantic import BaseModel

class RunTask(BaseModel):
    taskId: str
    taskUniqueId: str


class ProcessTask(BaseModel):
    count: int = 0
    successCount: int = 0
    failCount: int = 0
    restCount: int = 0
    failTasks: List[str] = []
    state: str = "stop"
    tasks: List[str] = []
    tasksRet: List[int] = []
    index: int = 0
    market: str = ""
    startDateStr: str = ""
    endDateStr: str = ""
    taskUniqueId: str = ""
    percent: float = 0.0
    taskId: str = ""
    errMsg: str = ""

class TaskPoolInfo(BaseModel):
    poolSize: int = 0
    poolCount: int = 0
    runCount: int = 0
    queueCount: int = 0