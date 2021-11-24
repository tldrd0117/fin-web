from app.module.socket.manager import ConnectionManager
from app.module.locator import Locator
from app.scheduler.TaskScheduler import TaskScheduler
from app.service.CrawlingService import CrawlingService
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.StockRepository import StockRepository
from app.repo.FactorRepository import FactorRepository
from app.service.UserService import UserService
from app.service.TaskService import TaskService
from app.service.StockService import StockService
from app.service.FactorService import FactorService
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.router.task import TaskSocketRouter
from app.router.crawling import CrawlingSocketRouter
from app.router.factor import FactorSocketRouter


locator = Locator.getInstance()
manager = ConnectionManager()

# DATASOURCE
stockMongoDataSource = StockMongoDataSource()
factorFileDataSource = FactorFileDataSource()

# REPOSITORY
tasksRepository = TasksRepository(stockMongoDataSource)
crawlerRepository = CrawlerRepository(stockMongoDataSource, tasksRepository)
stockRepository = StockRepository(stockMongoDataSource, tasksRepository)
factorRepository = FactorRepository(stockMongoDataSource, factorFileDataSource)
repositories = {
    "crawlerRepository": crawlerRepository,
    "tasksRepository": tasksRepository,
    "stockRepository": stockRepository,
    "factorRepository": factorRepository
}

# SCHEDULER
taskScheduler = TaskScheduler(stockMongoDataSource.client)

# SERVICE
userService = UserService()
crawlingService = CrawlingService(manager, tasksRepository, crawlerRepository, stockRepository)
taskService = TaskService(manager, tasksRepository, taskScheduler, crawlingService)
stockService = StockService(stockRepository)
factorService = FactorService(manager, factorRepository, tasksRepository, taskService)

taskSocketRouter = TaskSocketRouter(crawlingService, taskService, manager)
crawlingSocketRouter = CrawlingSocketRouter(crawlingService, manager)
factorSocketRouter = FactorSocketRouter(factorService, manager)


locator.register(manager)
locator.register(crawlingService)
locator.register(tasksRepository)
locator.register(crawlerRepository)
locator.register(tasksRepository)
locator.register(factorRepository)
locator.register(userService)
locator.register(taskService)
locator.register(factorService)
locator.register(stockMongoDataSource)
locator.register(factorFileDataSource)
locator.register(taskScheduler)
locator.register(taskSocketRouter)
locator.register(crawlingSocketRouter)
locator.register(stockRepository)
locator.register(stockService)
locator.register(factorSocketRouter)
