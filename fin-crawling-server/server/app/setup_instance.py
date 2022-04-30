from app.module.socket.manager import ConnectionManager
from app.module.locator import Locator
from app.scheduler.TaskScheduler import TaskScheduler
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.StockRepository import StockRepository
from app.repo.FactorRepository import FactorRepository
from app.repo.UserRepository import UserRepository
from app.service.api.UserApiService import UserApiService
from app.service.api.TaskApiService import TaskApiService
from app.service.api.StockApiService import StockApiService
from app.service.api.FactorApiService import FactorApiService
from app.service.scrap.FactorDartScrapService import FactorDartScrapService
from app.service.scrap.FactorFileScrapService import FactorFileScrapService
from app.service.scrap.MarcapScrapService import MarcapScrapService
from app.service.scrap.SeibroDividendScrapService import SeibroDividendScrapService
from app.service.scrap.SeibroStockNumScrapService import SeibroStockNumScrapService
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.datasource.FactorMongoDataSource import FactorMongoDataSource
from app.datasource.FactorDartMongoDataSource import FactorDartMongoDataSource
from app.datasource.SeibroDividendDataSource import SeibroDividendDataSource
from app.datasource.SeibroStockNumDataSource import SeibroStockNumDataSource
from app.datasource.TaskMongoDataSource import TaskMongoDataSource
from app.datasource.UserDataSource import UserDataSource
from app.router.socket.task import TaskSocketRouter


locator = Locator.getInstance()

locator.registerAll([
    ConnectionManager(), 
    # DATASOURCE
    StockMongoDataSource(),
    FactorMongoDataSource(),
    FactorFileDataSource(),
    FactorDartMongoDataSource(),
    TaskMongoDataSource(),
    SeibroDividendDataSource(),
    SeibroStockNumDataSource(),
    UserDataSource(),
    # REPOSITORY
    TasksRepository(),
    CrawlerRepository(),
    StockRepository(),
    FactorRepository(),
    UserRepository(),
    # SCHEDULER
    TaskScheduler(),
    # SERVICE
    UserApiService(),
    StockApiService(),
    TaskApiService(),
    FactorApiService(),
    FactorDartScrapService(),
    FactorFileScrapService(),
    SeibroDividendScrapService(),
    SeibroStockNumScrapService(),
    MarcapScrapService(),
    TaskSocketRouter()
])

