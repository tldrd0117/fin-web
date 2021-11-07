from app.module.socket.manager import ConnectionManager
from app.module.locator import Locator
from app.scheduler.TaskScheduler import TaskScheduler
from app.service.CrawlingService import CrawlingService
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.StockRepository import StockRepository
from app.service.UserService import UserService
from app.service.TaskService import TaskService
from app.service.StockService import StockService
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.router.task import TaskSocketRouter
from app.router.crawling import CrawlingSocketRouter
from app.module.logger import Logger


locator = Locator.getInstance()
manager = ConnectionManager()
userService = UserService()
stockMongoDataSource = StockMongoDataSource()
crawlerRepository = CrawlerRepository(stockMongoDataSource)
tasksRepository = TasksRepository(stockMongoDataSource)
stockRepository = StockRepository(stockMongoDataSource)
crawlingService = CrawlingService(manager, tasksRepository, crawlerRepository)
taskScheduler = TaskScheduler(stockMongoDataSource.client)
taskService = TaskService(manager, tasksRepository, taskScheduler, crawlingService)
stockService = StockService(stockRepository)

taskSocketRouter = TaskSocketRouter(crawlingService, taskService, manager)
crawlingSocketRouter = CrawlingSocketRouter(crawlingService, manager)
logger = Logger()


locator.register(manager)
locator.register(crawlingService)
locator.register(tasksRepository)
locator.register(crawlerRepository)
locator.register(tasksRepository)
locator.register(userService)
locator.register(taskService)
locator.register(stockMongoDataSource)
locator.register(taskScheduler)
locator.register(taskSocketRouter)
locator.register(crawlingSocketRouter)
locator.register(stockRepository)
locator.register(stockService)
locator.register(logger)
