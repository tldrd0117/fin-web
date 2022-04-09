
from typing import Dict, List
from app.module.logger import Logger
from app.datasource.MongoDataSource import MongoDataSource
from app.util.DateUtils import getNow
import traceback
import asyncio


class SeibroDividendDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("SeibroDividendDataSource")
    

    async def insertSeibrodiviendData(self, li: List[Dict]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            self.logger.info(li)
            for dataLi in li:
                for one in dataLi:
                    await asyncio.create_task(self.insertSeibrodiviendDataOne(one))
        except Exception as e:
            self.logger.error("insertSeibrodiviendData", traceback.format_exc())
            raise e
    
    async def insertSeibrodiviendDataOne(self, one: Dict) -> None:
        try:
            self.logger.info(one)
            one["updatedAt"] = getNow()
            self.seibroDividend.update_one({
                "배정기준일": one["배정기준일"],
                "현금배당 지급일": one["현금배당 지급일"],
                "결산월": one["결산월"],
                "배당구분": one["배당구분"],
                "시장구분": one["시장구분"],
                "종목코드": one["종목코드"]
            }, {
                "$set": one,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
        except Exception as e:
            self.logger.error("insertSeibrodiviendDataOne", traceback.format_exc())
            raise e