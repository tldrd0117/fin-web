from typing import List

from app.model.dto import StockMarketCapital, ListLimitData, ListLimitResponse
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from pymongo import DESCENDING
from app.module.logger import Logger
import traceback
import asyncio


class StockMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("StockMongoDataSource")

    async def insertMarcap(self, li: List[StockMarketCapital]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            for one in li:
                asyncio.create_task(self.insertMarpcapOne(one))
        except Exception:
            self.logger.error("insertMarcap", traceback.format_exc())
    
    async def insertMarpcapOne(self, one: StockMarketCapital) -> None:
        try:
            data = one.dict()
            data["updatedAt"] = getNow()
            self.marcap.update_one({
                "code": data["code"],
                "date": data["date"],
                "market": data["market"]
            }, {
                "$set": data,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
        except Exception:
            self.logger.error("insertMarpcapOne", traceback.format_exc())
        
    async def getMarcap(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            cursor = self.marcap.find({"$and": [{"date": {"$gte": startDate, "$lte": endDate}}, {"market": market}]})
            return list(map(lambda data: StockMarketCapital(**{
                "date": data["date"],
                "market": data["market"],
                "code": data["code"],
                "name": data["name"],
                "close": data["close"],
                "diff": data["diff"],
                "percent": data["percent"],
                "open": data["open"],
                "high": data["high"],
                "low": data["low"],
                "volume": data["volume"],
                "price": data["price"],
                "marcap": data["marcap"],
                "number": data["number"]
            }), list(cursor)))
        except Exception:
            self.logger.error("getMarcap", traceback.format_exc())
            return list()

    def getCompletedTask(self, dto: ListLimitData) -> ListLimitResponse:
        try:
            data = dto.dict()
            cursor = self.task.find({"$or": [
                        {"state": "complete"}, 
                        {"state": "error"},
                        {"state": "cancelled"}
                    ]}
                ).sort("createdAt", DESCENDING)\
                .skip(data["offset"])\
                .limit(data["limit"])
            
            count = self.task.find({"$or": [
                        {"state": "complete"}, 
                        {"state": "error"},
                        {"state": "cancelled"}
                    ]}
                ).count()
            
            res = ListLimitResponse(**{
                "count": count,
                "offset": data["offset"],
                "limit": data["limit"],
                "data": self.exceptId(list(cursor))
            })
            
            return res
        except Exception:
            self.logger.error("getCompletedTask", traceback.format_exc())
        return []
    
    def getAllTaskState(self, taskId: str, market: str) -> list:
        try:
            cursor = self.task.find({
                "taskId": taskId,
                "market": market
                # "$or": [{"state": "success"}, {"state": "fail"}, {"state": "error"}]
            }, projection=["tasks", "tasksRet"])
            return list(cursor)
        except Exception:
            self.logger.error("getAllTaskState", traceback.format_exc())
        return []

    def upsertTask(self, value: dict) -> None:
        try:
            value["updatedAt"] = getNow()
            self.task.update_one({
                "taskUniqueId": value["taskUniqueId"]
            }, {
                "$set": value,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
        except Exception:
            self.logger.error("upsertTask", traceback.format_exc())
