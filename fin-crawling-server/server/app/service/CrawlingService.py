from __future__ import annotations
import asyncio
from typing import Dict, List
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import EVENT_TASK_REPO_TASK_COMPLETE, TasksRepository, EVENT_TASK_REPO_UPDATE_TASKS
from app.repo.StockRepository import StockRepository
from app.module.task import Pool, Task, TaskPool
from app.model.dto import StockUpdateState, StockCrawlingCompletedTasks, \
    StockRunCrawling, FactorRunCrawling, ProcessTasks, ListLimitData, \
    ListLimitResponse, RunCrawling, ProcessTask
from app.crawler.MarcapCrawler import MarcapCrawler
from fastapi import WebSocket
from app.module.socket.manager import ConnectionManager
from datetime import datetime, timedelta
from collections import deque
from app.module.logger import Logger

RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK = "crawling/fetchCompletedTaskRes"
RES_SOCKET_CRAWLING_FETCH_TASKS = "crawling/fetchTasksRes"
RES_SOCKET_CRAWLING_RUN_CRAWLING = "crawling/runCrawlingRes"


class CrawlingService:
    def __init__(self, manager: ConnectionManager, tasksRepository: TasksRepository, crawlerRepository: CrawlerRepository, stockRepository: StockRepository) -> None:
        self.tasksRepository = tasksRepository
        self.crawlerRepository = crawlerRepository
        self.stockRepository = stockRepository
        self.manager = manager
        self.pools: Dict = {}
        self.logger = Logger("CrawlingService")
        self.createTaskRepositoryListener()

    def runCrawling(self, dtoList: List[RunCrawling]) -> None:
        for dto in dtoList:
            if dto.taskId == "marcap":
                async def marcapTaskWorker(runDto: StockRunCrawling, pool: Pool, taskPool: TaskPool) -> None:
                    self.logger.info("runCrawling&marcapTaskWorker", "start")
                    marcapCrawler = MarcapCrawler()
                    taskUniqueId = runDto.taskUniqueId
                    self.crawlerRepository.addCrawler(taskUniqueId, marcapCrawler)
                    self.pools[runDto.taskUniqueId] = pool
                    self.crawlerRepository.createListener(marcapCrawler.ee)
                    self.stockRepository.createListners(marcapCrawler.ee)
                    self.logger.info("runCrawling&marcapTaskWorker", f"taskWorker:{taskUniqueId}")
                    await asyncio.create_task(marcapCrawler.crawling(runDto))
                    taskPool.removeTaskPool(pool)
                    self.crawlerRepository.removeCrawler(taskUniqueId)
                task = Task(marcapTaskWorker, {"runDto": dto})
                self.runMarcapTask(task, dto)
            elif dto.taskId == "factor":
                async def factorTaskWorker(runDto: FactorRunCrawling, pool: Pool, taskPool: TaskPool) -> None:
                    pass
                task = Task(factorTaskWorker, {"runDto": dto})
    
    def runMarcapTask(self, workerTask: Task, dto: StockRunCrawling) -> None:
        if self.tasksRepository.taskRunner:
            if self.tasksRepository.isExistTask(dto.taskId, dto.taskUniqueId):
                return
            startDate = datetime.strptime(dto.startDateStr, "%Y%m%d")
            endDate = datetime.strptime(dto.endDateStr, "%Y%m%d")
            taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
            task = ProcessTask(**{
                "market": dto.market,
                "startDateStr": dto.startDateStr,
                "endDateStr": dto.endDateStr,
                "taskUniqueId": dto.taskUniqueId,
                "taskId": dto.taskId,
                "count": len(taskDates),
                "tasks": deque(taskDates),
                "restCount": len(taskDates),
                "tasksRet": deque(([0]*len(taskDates))),
            })
            task.state = "find worker"
            self.tasksRepository.addTask(task)
            self.updateTasks(self.tasksRepository.tasksdto)
            self.tasksRepository.runTask(workerTask)
            self.logger.info("runMarcapTask", f"runTask {task.json()}")
    
    def cancelCrawling(self, dto: StockRunCrawling) -> None:
        if dto.taskUniqueId in self.crawlerRepository.getCrawlers():
            self.pools[dto.taskUniqueId].cancel()
            self.crawlerRepository.getCrawler(dto.taskUniqueId).isCancelled = True
        else:
            task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
            if task is not None:
                self.tasksRepository.deleteTask(task)
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_FETCH_TASKS, self.tasksRepository.tasksdto.dict())

    def fetchTasks(self, webSocket: WebSocket) -> None:
        self.manager.send(RES_SOCKET_CRAWLING_FETCH_TASKS, self.tasksRepository.tasksdto.dict(), webSocket)
    
    def fetchCompletedTask(self, dto: ListLimitData, webSocket: WebSocket) -> None:
        tasks: ListLimitResponse = self.tasksRepository.getCompletedTask(dto)
        # logger.info("histories:"+tasks.json())
        self.manager.send(RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, tasks.dict(), webSocket)

    def createTaskRepositoryListener(self) -> None:
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_TASK_COMPLETE, self.completeTask)
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_UPDATE_TASKS, self.updateTasks)
    
    def updateTasks(self, tasks: ProcessTasks) -> None:
        # logger.info("tasks:"+tasks.json())
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_RUN_CRAWLING, tasks.dict())
    
    def completeTask(self, marcap: str, stockUpdateState: StockUpdateState) -> None:
        dto = ListLimitData(**{
            "offset": 0,
            "limit": 20
        })
        tasks: StockCrawlingCompletedTasks = self.tasksRepository.getCompletedTask(dto)
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, tasks.dict())
