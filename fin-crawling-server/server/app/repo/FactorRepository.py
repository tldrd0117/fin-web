
from typing import List
from app.datasource.FactorMongoDataSource import FactorMongoDataSource
from app.datasource.FactorDartMongoDataSource import FactorDartMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.module.logger import Logger
from app.model.dao import FactorDao


class FactorRepository(object):
    def __init__(self, factorMongod: FactorMongoDataSource, factorDartMongod: FactorDartMongoDataSource, filed: FactorFileDataSource) -> None:
        super().__init__()
        self.factorMongod = factorMongod
        self.factorDartMongod = factorDartMongod
        self.filed = filed
        self.logger = Logger("FactorRepository")
    
    # 파일에 있는 팩터 데이터를 읽어온다.
    async def getFactorsInFile(self) -> List:
        return await self.filed.loadFactorMerge()
        
    # 팩터 데이터를 db에 저장한다.
    async def insertFactor(self, li: List[FactorDao]) -> None:
        await self.factorMongod.insertFactor(li)
    
    async def insertFactorDart(self, li: List[FactorDao]) -> None:
        await self.factorDartMongod.insertFactor(li)

        