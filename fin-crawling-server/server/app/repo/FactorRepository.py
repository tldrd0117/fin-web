
from typing import List
from app.datasource.FactorMongoDataSource import FactorMongoDataSource
from app.datasource.FactorDartMongoDataSource import FactorDartMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.module.logger import Logger
from app.model.dao import FactorDao
from app.model.dto import FactorData
from app.base.BaseComponent import BaseComponent


class FactorRepository(BaseComponent):
    
    def onComponentResisted(self) -> None:
        self.factorMongod = self.get(FactorMongoDataSource)
        self.factorDartMongod = self.get(FactorDartMongoDataSource)
        self.filed = self.get(FactorFileDataSource)
        self.logger = Logger("FactorRepository")
        return super().onComponentResisted()
    
    async def getFactor(self, code: str, year: str, month: str, source: str) -> List[FactorData]:
        if(source == "factor"):
            return await self.factorMongod.getFactor(year, month, code)
        elif(source == "factorDart"):
            return await self.factorDartMongod.getFactor(year, month, code)
        return list()
    
    # 파일에 있는 팩터 데이터를 읽어온다.
    async def getFactorsInFile(self) -> List:
        return await self.filed.loadFactorMerge()
        
    # 팩터 데이터를 db에 저장한다.
    async def insertFactor(self, li: List[FactorDao]) -> None:
        await self.factorMongod.insertFactor(li)
    
    async def insertFactorDart(self, li: List[FactorDao]) -> None:
        await self.factorDartMongod.insertFactor(li)

        