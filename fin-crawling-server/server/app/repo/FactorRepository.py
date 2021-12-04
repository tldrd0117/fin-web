
from typing import Dict, List
from app.datasource.FactorMongoDataSource import FactorMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.module.logger import Logger
from app.model.dao import FactorDao


class FactorRepository(object):
    def __init__(self, mongod: FactorMongoDataSource, filed: FactorFileDataSource) -> None:
        super().__init__()
        self.mongod = mongod
        self.filed = filed
        self.logger = Logger("FactorRepository")
    
    # 파일에 있는 팩터 데이터를 읽어온다.
    async def getFactorsInFile(self) -> Dict:
        return await self.filed.loadFactorMerge()
        
    # 팩터 데이터를 db에 저장한다.
    async def insertFactor(self, li: List[FactorDao]) -> None:
        await self.mongod.insertFactor(li)
        