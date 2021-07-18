from app.module.socket.manager import ConnectionManager
from app.module.locator import Locator
from app.scheduler.TaskScheduler import TaskScheduler
from app.service.CrawlingService import CrawlingService
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository
from app.service.UserService import UserService
from app.service.TaskService import TaskService
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.router.task import TaskSocketRouter
from app.router.crawling import CrawlingSocketRouter


locator = Locator.getInstance()
manager = ConnectionManager()
userService = UserService()
stockMongoDataSource = StockMongoDataSource()
crawlerRepository = CrawlerRepository(stockMongoDataSource)
tasksRepository = TasksRepository(stockMongoDataSource)
crawlingService = CrawlingService(manager, tasksRepository, crawlerRepository)
taskScheduler = TaskScheduler(stockMongoDataSource.client)
taskService = TaskService(manager, tasksRepository, taskScheduler, crawlingService)

taskSocketRouter = TaskSocketRouter(crawlingService, taskService, manager)
crawlingSocketRouter = CrawlingSocketRouter(crawlingService, manager)


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
