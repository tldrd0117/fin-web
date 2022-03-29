

import abc
import asyncio
import traceback
from typing import Dict, List
from app.model.task.model import ProcessTask, RunTask
from app.base.BaseComponent import BaseComponent

class TaskService(BaseComponent):
    @abc.abstractmethod
    def createProcessTask(self, taskData: Dict) -> ProcessTask:
        return ProcessTask(**taskData)


    @abc.abstractmethod
    async def convertRunDto(self, runDto: dict) -> RunTask:
        return RunTask(**runDto)
    

    @abc.abstractmethod
    async def convertRunList(self, runDto: dict) -> RunTask:
        return RunTask(**runDto)


    @abc.abstractmethod
    async def addTasks(self, dtos: List):
        pass


    @abc.abstractmethod
    async def addTask(self, dto: Dict):
        pass
