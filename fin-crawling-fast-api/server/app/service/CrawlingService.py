from __future__ import annotations
import asyncio
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import EVENT_TASK_REPO_TASK_COMPLETE, TasksRepository, EVENT_TASK_REPO_UPDATE_TASKS
from app.module.task import Task
from app.model.dto import StockCrawlingCompletedTasksDTO, StockCrawlingRunCrawlingDTO, StockCrawlingTasksDTO
from app.crawler.MarcapCrawler import MarcapCrawler
from fastapi import WebSocket
from app.event.manager import ConnectionManager
from uvicorn.config import logger

RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK = "crawling/fetchCompletedTaskRes"
RES_SOCKET_CRAWLING_FETCH_TASKS = "crawling/fetchTasksRes"
RES_SOCKET_CRAWLING_RUN_CRAWLING = "crawling/runCrawlingRes"


class CrawlingService:
    def __init__(self, manager: ConnectionManager, tasksRepository: TasksRepository, crawlerRepository: CrawlerRepository) -> None:
        self.tasksRepository = tasksRepository
        self.crawlerRepository = crawlerRepository
        self.manager = manager
        self.createTaskRepositoryListener()

    def runCrawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        if dto.taskId == "marcap":
            async def taskWorker() -> None:
                marcapCrawler = MarcapCrawler()
                self.tasksRepository.createListners(marcapCrawler.ee)
                self.crawlerRepository.createListener(marcapCrawler.ee)
                await asyncio.create_task(marcapCrawler.crawling(dto))
            task = Task(taskWorker)
            self.tasksRepository.runMarcapTask(task, dto)

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
    
    def completeTask(self) -> None:
        tasks: StockCrawlingCompletedTasksDTO = self.tasksRepository.getCompletedTask()
        self.manager.sendBroadCast(RES_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, tasks.dict())
