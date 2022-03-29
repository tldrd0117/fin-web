from typing import Any, Dict
from typing_extensions import Final

from app.datasource.StockMongoDataSource import StockMongoDataSource
from pymitter import EventEmitter
from app.repo.TasksRepository import TasksRepository
from app.module.logger import Logger
from app.base.BaseComponent import BaseComponent


EVENT_TASK_REPO_UPDATE_TASKS = "taskRepo/updateTasks"
EVENT_TASK_REPO_TASK_COMPLETE = "taskRepo/completeTask"
EVENT_TASK_REPO_UPDATE_POOL_INFO = "taskRepo/updatePoolInfo"
EVENT_CRAWLING_REPO_ON_CRAWLING_COMPLETE: Final = "crawlingRepo/onCrawlingComplete"


class CrawlerRepository(BaseComponent):

    def onComponentResisted(self) -> None:
        self.mongod = self.get(StockMongoDataSource)
        self.tasksRepository = self.get(TasksRepository)
        self.ee = EventEmitter()
        self.logger = Logger("CrawlerRepository")
        self.crawlers: Dict = dict()
        return super().onComponentResisted()

    def createListener(self, ee: EventEmitter) -> None:
        pass
    
    # 크롤러 추가
    def addCrawler(self, uniqueId: str, crawler: Any) -> None:
        self.crawlers[uniqueId] = crawler
    
    # 크롤러 삭제
    def removeCrawler(self, uniqueId: str) -> None:
        del self.crawlers[uniqueId]
    
    # 크롤러 불러오기
    def getCrawlers(self) -> Dict:
        return self.crawlers
    
    # 하나의 크롤러 불러오기
    def getCrawler(self, uniqueId: str) -> Any:
        return self.crawlers[uniqueId]
    
    
    
    

