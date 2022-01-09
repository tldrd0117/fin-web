from typing import List
from app.repo.StockRepository import StockRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.crawler.MarcapCrawler import MarcapCrawler
from pymitter import EventEmitter
from app.model.dto import StockMarketCapital, StockRunCrawling, \
    StockMarketCapitalResult, StockCrawlingDownloadTask, ProcessTask

from app.module.task import Pool, Task, TaskPool
from app.module.logger import Logger

import asyncio
from datetime import datetime, timedelta
from collections import deque

from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, \
    EVENT_MARCAP_CRAWLING_ON_ERROR, \
    EVENT_MARCAP_CRAWLING_ON_CANCEL, \
    EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA


class StockService:
    def __init__(self, stockRepository: StockRepository, tasksRepository: TasksRepository, crawlerRepository: CrawlerRepository) -> None:
        self.stockRepository = stockRepository
        self.tasksRepository = tasksRepository
        self.crawlerRepository = crawlerRepository
        self.logger = Logger("StockService")

    def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return self.stockRepository.getStockData(market, startDate, endDate)

    def crawlingMarcapStockData(self, dtoList: List[StockRunCrawling]) -> None:
        self.logger.info("crawlingMarcapStockData", str(len(dtoList)))
        for dto in dtoList:
            if dto.taskId == "marcap":
                async def marcapTaskWorker(runDto: StockRunCrawling, pool: Pool, taskPool: TaskPool) -> None:
                    self.logger.info("runCrawling&marcapTaskWorker", "start")
                    marcapCrawler = MarcapCrawler()
                    taskUniqueId = runDto.taskUniqueId
                    self.crawlerRepository.addCrawler(taskUniqueId, marcapCrawler)
                    self.createListners(marcapCrawler.ee)
                    self.logger.info("runCrawling&marcapTaskWorker", f"taskWorker:{taskUniqueId}")
                    await asyncio.create_task(marcapCrawler.crawling(runDto))
                    taskPool.removeTaskPool(pool)
                    self.crawlerRepository.removeCrawler(taskUniqueId)
                workerTask = Task(dto.taskUniqueId, marcapTaskWorker, {"runDto": dto})
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
                    self.tasksRepository.runTask(workerTask)
                    self.logger.info("runMarcapTask", f"runTask {task.json()}")

    def cancelCrawling(self, dto: StockRunCrawling) -> None:
        if dto.taskUniqueId in self.crawlerRepository.getCrawlers():
            self.tasksRepository.taskRunner.cancel(dto.taskUniqueId)
            self.crawlerRepository.getCrawler(dto.taskUniqueId).isCancelled = True
        else:
            task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
            if task is not None:
                self.tasksRepository.deleteTask(task)
        # self.manager.sendBroadCast(RES_SOCKET_CRAWLING_FETCH_TASKS, self.tasksRepository.tasksdto.dict())
    
    def createListners(self, ee: EventEmitter) -> None:
        ee.on(EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA, self.onResultOfStockData)

        ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, self.onConnectingWebDriver)
        ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, self.onStartCrawling)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, self.onDownloadStart)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, self.onDownloadComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, self.onParsingComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_ERROR, self.onError)
        ee.on(EVENT_MARCAP_CRAWLING_ON_CANCEL, self.onCancelled)
    
    # 주식 종목 데이터 크롤링 결과값을 db에 저장한다.
    def onResultOfStockData(self, dto: StockCrawlingDownloadTask, retDto: StockMarketCapitalResult) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "insert to database"
        self.tasksRepository.updateTask(task)
        
        async def completeMarcapTask() -> None:
            await self.stockRepository.insertMarcap(retDto)
            self.tasksRepository.completeStockCrawlingTask(True, retDto, dto)
        asyncio.create_task(completeMarcapTask())

    # 크롤링 중 웹드라이버와 연결되었을 때 이벤트
    def onConnectingWebDriver(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.tasksRepository.updateTask(task)
        self.logger.info("onConnectingWebDriver", task.taskUniqueId)

    # 크롤링이 시작되었을 떄 이벤트
    def onStartCrawling(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onStartCrawling", task.taskUniqueId)
    
    # 크롤링 데이터 다운로드가 시작되었을 때 이벤트
    def onDownloadStart(self, dto: StockCrawlingDownloadTask) -> None:
        # self.logger.info("onDownloadStart: "+dto.json())
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download start"
        self.tasksRepository.updateTask(task)
        self.logger.info("onDownloadStart", task.taskUniqueId)

    # 크롤링 데이터 다운로드가 완료되었을 때 이벤트
    def onDownloadComplete(self, dto: StockCrawlingDownloadTask) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download complete"
        self.tasksRepository.updateTask(task)
        self.logger.info("onDownloadComplete", task.taskUniqueId)

    # 크롤링 데이터 변환이 완료되었을 때 이벤트
    def onParsingComplete(self, isSuccess: bool, retdto: StockMarketCapitalResult, dto: StockCrawlingDownloadTask) -> None:
        self.logger.info("onParsingComplete")
        self.logger.info(f"taskId:{dto.taskId} taskUniqueId{dto.taskUniqueId}")
        tar = self.tasksRepository.tasksdto.tasks[dto.taskId]["list"]
        self.logger.info(f"taskDTO: {tar}")
        if not isSuccess:
            self.tasksRepository.completeStockCrawlingTask(isSuccess, retdto, dto)
    
    # 크롤링이 취소되었을 때 이벤트
    def onCancelled(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.fail(task, task.restCount)
        task.state = "cancelled"
        self.tasksRepository.updateTask(task)
        self.logger.info("onCancelled", task.taskUniqueId)
    
    # 크롤링이 에러가났을 때 이벤트
    def onError(self, dto: StockRunCrawling, errorMsg: str) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.fail(task, task.restCount)
        task.state = "error"
        task.errMsg = errorMsg
        self.tasksRepository.updateTask(task)
        self.logger.error("onError", task.taskUniqueId)

    
