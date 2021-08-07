from __future__ import annotations
import asyncio
from typing import Dict, List
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import EVENT_TASK_REPO_TASK_COMPLETE, TasksRepository, EVENT_TASK_REPO_UPDATE_TASKS
from app.module.task import Pool, Task, TaskPool
from app.model.dto import StockCrawlingCompletedTasksDTO, StockCrawlingRunCrawlingDTO, StockCrawlingTasksDTO
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
        self.createTaskRepositoryListener()

    def runCrawling(self, dtoList: List[StockCrawlingRunCrawlingDTO]) -> None:
        for dto in dtoList:
            if dto.taskId == "marcap":
                async def taskWorker(runDto: StockCrawlingRunCrawlingDTO, pool: Pool, taskPool: TaskPool) -> None:
                    marcapCrawler = MarcapCrawler()
                    self.crawlers[runDto.taskUniqueId] = marcapCrawler
                    self.tasksRepository.createListners(marcapCrawler.ee)
                    self.crawlerRepository.createListener(marcapCrawler.ee)
                    logger.info(f"taskWorker:{runDto.taskUniqueId}")
                    await asyncio.create_task(marcapCrawler.crawling(runDto))
                    taskPool.removeTaskPool(pool)
                task = Task(taskWorker, {"runDto": dto})
                self.tasksRepository.runMarcapTask(task, dto)
    
    def cancelCrawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        self.crawlers[dto.taskUniqueId].isCancelled = True

    def fetchTasks(self, webSocket: WebSocket) -> None:
        self.manager.send(RES_SOCKET_CRAWLING_FETCH_TASKS, self.tasksRepository.tasksdto.dict(), webSocket)
    
    def fetchCompletedTask(self, webSocket: WebSocket) -> None:
        tasks: StockCrawlingCompletedTasksDTO = self.tasksRepository.getCompletedTask()
        logger.info("histories:"+tasks.json())
        self.manager.send(RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, tasks.dict(), webSocket)

    def createTaskRepositoryListener(self) -> None:
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_UPDATE_TASKS, self.updateTasks)
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_TASK_COMPLETE, self.completeTask)
    
    def updateTasks(self, tasks: StockCrawlingTasksDTO) -> None:
        logger.info("tasks:"+tasks.json())
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_RUN_CRAWLING, tasks.dict())
    
    def completeTask(self, marcap: str) -> None:
        tasks: StockCrawlingCompletedTasksDTO = self.tasksRepository.getCompletedTask()
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, tasks.dict())
        
