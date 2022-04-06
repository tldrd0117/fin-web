from typing import Any, Awaitable, Coroutine, Dict, List

from app.module.locator import Locator
from app.base.BaseComponent import BaseComponent
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.model.scrap.model import RunScrap
from app.scrap.base.Scraper import Scraper
from app.model.task.model import ProcessTask, RunTask
from app.util.decorator import eventsDecorator
from app.module.task import Pool, Task, TaskPool
from app.module.logger import Logger
from app.service.base.TaskService import TaskService
import abc
import asyncio
import traceback


class ScrapService(TaskService):

    def onComponentResisted(self) -> None:
        self.crawlingServiceLogger = Logger("ScrapService")
        self.tasksRepository: TasksRepository = self.locator.get(TasksRepository)
        self.crawlerRepository: CrawlerRepository = self.locator.get(CrawlerRepository)
        self.crawlingServiceLogger.info("onComponentResisted")
        return super().onComponentResisted()

    @abc.abstractmethod
    def createScraper(self) -> Scraper:
        pass


    async def taskJob(self, runDto: RunScrap, pool: Pool, taskPool: TaskPool):
        try:
            crawler = self.createScraper()
            crawler.service = self
            eventsDecorator.register(self, crawler.getEventEmitter())
            taskUniqueId = runDto.taskUniqueId
            self.crawlerRepository.addCrawler(taskUniqueId, crawler)
            self.crawlingServiceLogger.info("taskJob", f"taskWorker:{taskUniqueId}")
            await crawler.crawling(runDto)
            taskPool.removeTaskPool(pool)
            self.crawlerRepository.removeCrawler(taskUniqueId)
            eventsDecorator.unregist(self, crawler.getEventEmitter())
        except asyncio.CancelledError:
            self.crawlingServiceLogger.info("taskJob", "cancel")
            self.tasksRepository.cancelTask(runDto)
        except Exception:
            self.crawlingServiceLogger.error("taskJob", f"error: {traceback.format_exc()}")
            self.tasksRepository.errorTask(runDto, traceback.format_exc())


    async def addTask(self, dto: Any):
        runScrap = None
        if isinstance(dto, RunScrap):
            runScrap = dto
        else:
            data = await self.convertRunDto(dto)
            if isinstance(data, list):
                for runScrap in data:
                    await self.addTask(runScrap)
                return
            elif isinstance(data, RunScrap):
                runScrap = data

        workerTask = Task(runScrap.taskUniqueId, self.taskJob, runDto=runScrap)
        if self.tasksRepository.taskRunner:
            if self.tasksRepository.isExistTask(runScrap.taskId, runScrap.taskUniqueId):
                return
            task: ProcessTask = self.createProcessTask(runScrap)
            task.state = "find worker"
            self.tasksRepository.addTask(task)
            self.tasksRepository.runTask(workerTask)
