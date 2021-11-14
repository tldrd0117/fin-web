
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.module.logger import Logger


class FactorRepository(object):
    def __init__(self, mongod: StockMongoDataSource, filed: FactorFileDataSource) -> None:
        super().__init__()
        self.mongod = mongod
        self.filed = filed
        self.logger = Logger("FactorRepository")
    
    def getFactorsInFile(self) -> None:
        return self.filed.loadFactorMerge()