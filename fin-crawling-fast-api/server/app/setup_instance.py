from app.event.manager import ConnectionManager
from app.module.locator import Locator
from app.service.CrawlingService import CrawlingService
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository
from app.service.UserService import UserService


locator = Locator.getInstance()
manager = ConnectionManager()
crawlerRepository = CrawlerRepository()
tasksRepository = TasksRepository()
crawlingService = CrawlingService(manager, tasksRepository, crawlerRepository)
userService = UserService()

locator.register(manager)
locator.register(crawlingService)
locator.register(tasksRepository)
locator.register(crawlerRepository)
locator.register(tasksRepository)
locator.register(userService)
