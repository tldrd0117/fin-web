from app.module.socket.manager import ConnectionManager
from app.module.locator import Locator
from app.scheduler.TaskScheduler import TaskScheduler
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
from app.datasource.FactorMongoDataSource import FactorMongoDataSource
from app.router.socket.task import TaskSocketRouter
from app.router.socket.stock import StockSocketRouter
from app.router.socket.factor import FactorSocketRouter


locator = Locator.getInstance()
manager = ConnectionManager()

# DATASOURCE
stockMongoDataSource = StockMongoDataSource()
factorMongoDataSource = FactorMongoDataSource()
factorFileDataSource = FactorFileDataSource()

# REPOSITORY
tasksRepository = TasksRepository(stockMongoDataSource)
crawlerRepository = CrawlerRepository(stockMongoDataSource, tasksRepository)
stockRepository = StockRepository(stockMongoDataSource, tasksRepository)
factorRepository = FactorRepository(factorMongoDataSource, factorFileDataSource)
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
stockService = StockService(stockRepository, tasksRepository, crawlerRepository)
factorService = FactorService(manager, factorRepository, tasksRepository, None)
taskService = TaskService(manager, tasksRepository, taskScheduler, factorService, stockService, crawlerRepository)
factorService.taskService = taskService


taskSocketRouter = TaskSocketRouter(taskService, manager)
factorSocketRouter = FactorSocketRouter(factorService, manager)
stockSocketRouter = StockSocketRouter(stockService, manager)


locator.register(manager)
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
locator.register(stockSocketRouter)
locator.register(stockRepository)
locator.register(stockService)
locator.register(factorSocketRouter)
