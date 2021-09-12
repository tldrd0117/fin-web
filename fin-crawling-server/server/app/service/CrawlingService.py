from __future__ import annotations
import asyncio
from typing import Dict, List
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import EVENT_TASK_REPO_TASK_COMPLETE, TasksRepository, EVENT_TASK_REPO_UPDATE_TASKS
from app.module.task import Pool, Task, TaskPool
from app.model.dto import StockCrawlingCompletedTasks, StockCrawlingRunCrawling, StockCrawlingTasks, ListLimitData, ListLimitResponse
from app.crawler.MarcapCrawler import MarcapCrawler
from fastapi import WebSocket
from app.module.socket.manager import ConnectionManager
from uvicorn.config import logger

RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK = "crawling/fetchCompletedTaskRes"
RES_SOCKET_CRAWLING_FETCH_TASKS = "crawling/fetchTasksRes"
RES_SOCKET_CRAWLING_RUN_CRAWLING = "crawling/runCrawlingRes"


class CrawlingService:
    def __init__(self, manager: ConnectionManager, tasksRepository: TasksRepository, crawlerRepository: CrawlerRepository) -> None:
        self.tasksRepository = tasksRepository
        self.crawlerRepository = crawlerRepository
        self.manager = manager
        self.crawlers: Dict = {}
        self.pools: Dict = {}
        self.createTaskRepositoryListener()

    def runCrawling(self, dtoList: List[StockCrawlingRunCrawling]) -> None:
        for dto in dtoList:
            if dto.taskId == "marcap":
                async def taskWorker(runDto: StockCrawlingRunCrawling, pool: Pool, taskPool: TaskPool) -> None:
                    marcapCrawler = MarcapCrawler()
                    self.crawlers[runDto.taskUniqueId] = marcapCrawler
                    self.pools[runDto.taskUniqueId] = pool
                    self.tasksRepository.createListners(marcapCrawler.ee)
                    self.crawlerRepository.createListener(marcapCrawler.ee)
                    logger.info(f"taskWorker:{runDto.taskUniqueId}")
                    await asyncio.create_task(marcapCrawler.crawling(runDto))
                    taskPool.removeTaskPool(pool)
                    del self.crawlers[runDto.taskUniqueId]
                task = Task(taskWorker, {"runDto": dto})
                self.tasksRepository.runMarcapTask(task, dto)
    
    def cancelCrawling(self, dto: StockCrawlingRunCrawling) -> None:
        if dto.taskUniqueId in self.crawlers:
            self.pools[dto.taskUniqueId].cancel()
            self.crawlers[dto.taskUniqueId].isCancelled = True
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
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_UPDATE_TASKS, self.updateTasks)
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_TASK_COMPLETE, self.completeTask)
    
    def updateTasks(self, tasks: StockCrawlingTasks) -> None:
        # logger.info("tasks:"+tasks.json())
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_RUN_CRAWLING, tasks.dict())
    
    def completeTask(self, marcap: str) -> None:
        dto = ListLimitData(**{
            "offset": 0,
            "limit": 20
        })
        tasks: StockCrawlingCompletedTasks = self.tasksRepository.getCompletedTask(dto)
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, tasks.dict())
        
