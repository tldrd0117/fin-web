
from typing import List
from app.datasource.FactorMongoDataSource import FactorMongoDataSource
from app.datasource.FactorFileDataSource import FactorFileDataSource
from app.module.logger import Logger
from app.model.dto import KrxFactor


class FactorRepository(object):
    def __init__(self, mongod: FactorMongoDataSource, filed: FactorFileDataSource) -> None:
        super().__init__()
        self.mongod = mongod
        self.filed = filed
        self.logger = Logger("FactorRepository")
    
    def getFactorsInFile(self) -> List[KrxFactor]:
        data = self.filed.loadFactorMerge()
        return list(map(lambda d: KrxFactor(**{
            "code": d["종목코드"],
            "name": d["종목명"],
            "type": "year",
            "key": d["데이터명"],
            "value": (d["데이터값"] * 1000) if d["단위"] == "천원" else d["데이터값"]
        }), data))
    
    def insertFactor(self, li: List[KrxFactor]) -> None:
        self.mongod.insertFactor(li)