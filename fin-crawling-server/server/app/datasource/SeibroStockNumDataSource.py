
from typing import Dict, List
from app.module.logger import Logger
from app.datasource.MongoDataSource import MongoDataSource
from app.util.DateUtils import getNow
import traceback
import asyncio


class SeibroStockNumDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("SeibroStockNumDataSource")
    

    async def insertSeibroStockNumData(self, li: List[Dict]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            self.logger.info(li)
            for dataLi in li:
                for one in dataLi:
                    await asyncio.create_task(self.insertSeibroStockNumDataOne(one))
        except Exception as e:
            self.logger.error("insertSeibroStockNumData", traceback.format_exc())
            raise e
    
    async def insertSeibroStockNumDataOne(self, one: Dict) -> None:
        try:
            self.logger.info(one)
            one["updatedAt"] = getNow()
            self.seibroStockNum.update_one({
                "code": one["code"],
                "발행일": one["발행일"],
                "기업명": one["기업명"],
                "주식종류": one["주식종류"],
                "발행형태": one["발행형태"],
                "횟수": one["횟수"],
                "발행사유": one["발행사유"],
                "액면가": one["액면가"],
                "1주당발행가": one["1주당발행가"],
                "상장일": one["상장일"],
                "발행주식수": one["발행주식수"],
            }, {
                "$set": one,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
        except Exception as e:
            self.logger.error("insertSeibroStockNumDataOne", traceback.format_exc())
            raise e