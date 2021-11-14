from typing import List

from uvicorn.config import logger
from app.model.dto import StockMarketCapital, ListLimitData, ListLimitResponse
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from pymongo import DESCENDING


class StockMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()

    def insertMarcap(self, li: List[StockMarketCapital]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            for one in li:
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
        except Exception as e:
            print(e)
    
    def getMarcap(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
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
        except Exception as e:
            print(e)
            return list()

    def getCompletedTask(self, dto: ListLimitData) -> ListLimitResponse:
        try:
            data = dto.dict()
            cursor = self.task.find({"$or": [
                        {"state": "success"}, 
                        {"state": "fail"}
                    ]}
                ).sort("createdAt", DESCENDING)\
                .skip(data["offset"])\
                .limit(data["limit"])
            
            count = self.task.find({"$or": [
                        {"state": "success"}, 
                        {"state": "fail"}
                    ]}
                ).count()
            
            res = ListLimitResponse(**{
                "count": count,
                "offset": data["offset"],
                "limit": data["limit"],
                "data": self.exceptId(list(cursor))
            })
            
            return res
        except Exception as e:
            print(e)
        return []
    
    def getAllTaskState(self, taskId: str, market: str) -> list:
        try:
            cursor = self.task.find({
                "taskId": taskId,
                "market": market
                # "$or": [{"state": "success"}, {"state": "fail"}, {"state": "error"}]
            }, projection=["tasks", "tasksRet"])
            return list(cursor)
        except Exception as e:
            print(e)
        return []

    def upsertTask(self, value: dict) -> None:
        try:
            value["updatedAt"] = getNow()
            logger.info("upsertTask: "+str(value))
            self.task.update_one({
                "taskUniqueId": value["taskUniqueId"]
            }, {
                "$set": value,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
        except Exception as e:
            logger.error(str(e))
            print(e)
