from app.repo.FactorRepository import FactorRepository
from app.repo.TasksRepository import TasksRepository, EVENT_TASK_REPO_TASK_COMPLETE, EVENT_TASK_REPO_UPDATE_TASKS
from app.module.socket.manager import ConnectionManager
from app.model.dao import FactorDao
from fastapi import WebSocket
from app.module.logger import Logger
from app.module.task import Pool, Task, TaskPool
from app.model.dto import ListLimitData, ProcessTask, RunFactorFileConvert, StockCrawlingCompletedTasks
from typing import TYPE_CHECKING, Dict, List
import asyncio
import traceback
if TYPE_CHECKING:
    from app.service.TaskService import TaskService


RES_SOCKET_FACTOR_UPDATE_STATE_RES = "factor/updateConvertStateRes"

RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK = "factor/fetchCompletedTaskRes"
RES_SOCKET_FACTOR_FETCH_TASKS = "factor/fetchTasksRes"


class FactorService:
    def __init__(self, manager: ConnectionManager, factorRepository: FactorRepository, tasksRepository: TasksRepository, taskService: 'TaskService') -> None:
        self.manager = manager
        self.factorRepository = factorRepository
        self.tasksRepository = tasksRepository
        self.taskService = taskService
        self.logger = Logger("FactorService")
    
    # file에 있는 factor를 db에 저장한다.
    def convertFactorFileToDb(self, dto: RunFactorFileConvert) -> None:
        self.logger.info("convertFactorFileToDb")

        async def convertFactorFileToDbTask(pool: Pool, taskPool: TaskPool) -> None:
            try:
                task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
                data = await asyncio.create_task(self.factorRepository.getFactorsInFile())
                task.state = "start insert db"
                self.tasksRepository.updateTask(task)
                daoList = await asyncio.create_task(self.makeFactorDaoList(data))
                await self.factorRepository.insertFactor(daoList)
                task.state = "complete"
                self.tasksRepository.completeFactorConvertFileToDbTask(task)
            except Exception as e:
                self.logger.error("convertFactorFileToDbTask", f"error: {traceback.format_exc()}")
                task.state = "error"
                task.errMsg = traceback.format_exc()
                self.tasksRepository.updateTask(task)
            finally:
                taskPool.removeTaskPool(pool)
        task = ProcessTask(**{
            "market": "",
            "startDateStr": "",
            "endDateStr": "",
            "taskUniqueId": dto.taskUniqueId,
            "taskId": dto.taskId,
            "count": 1,
            "tasks": ["convert"],
            "restCount": 1,
            "tasksRet": [0],
            "state": "start get file"
        })
        self.tasksRepository.addTask(task)
        workerTask = Task(dto.taskUniqueId, convertFactorFileToDbTask)
        self.tasksRepository.runTask(workerTask)
    
    async def makeFactorDaoList(self, data: Dict) -> List[FactorDao]:
        daoList = []
        for one in data:
            dao = FactorDao(**{
                "code": one["종목코드"],       # 종목코드
                "name": one["종목명"],       # 종목이름
                "dataYear": one["년"],      # 결산년
                "dataMonth": one["결산월"],  # 결산월
                "dataName": one["데이터명"],   # 데이터명
                "dataValue": (one["데이터값"] * 1000) if one["단위"] == "천원" else one["데이터값"]  # 데이터값
            })
            daoList.append(dao)
        return daoList

    # def createTaskRepositoryListener(self) -> None:
        # self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_TASK_COMPLETE, self.completeTask)
        # self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_UPDATE_TASKS, self.updateTasks)
    
    # def updateTasks(self) -> None:
        # self.manager.sendBroadCast(RES_SOCKET_FACTOR_FETCH_TASKS, self.tasksRepository.tasksdto.dict())
    
    # def completeTask(self) -> None:
    #     dto = ListLimitData(**{
    #         "offset": 0,
    #         "limit": 20
    #     })
    #     tasks: StockCrawlingCompletedTasks = self.tasksRepository.getCompletedTask(dto)
    #     self.manager.sendBroadCast(RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK, tasks.dict())
    
    # def fetchCompletedTask(self, dto: ListLimitData, webSocket: WebSocket) -> None:
    #     listLimitDao = ListLimitDao(**{
    #         "offset": dto["offset"],
    #         "limit": dto["limit"],
    #         "taskId": "factorFile"
    #     })
    #     tasks: ListLimitDataDao = self.tasksRepository.getCompletedTask(listLimitDao)
    #     # logger.info("histories:"+tasks.json())
    #     self.manager.send(RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK, tasks.dict(), webSocket)