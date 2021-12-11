from typing import List

from app.model.dao import FactorDao
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from app.model.dto import ListLimitData, ListLimitResponse
from pymongo import DESCENDING


class FactorDartMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()

    async def insertFactor(self, li: List[FactorDao]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            for one in li:
                data = one.dict()
                data["updatedAt"] = getNow()
                self.factorDart.update_one({
                    "code": data["code"],
                    "dataYear": data["dataYear"],
                    "dataMonth": data["dataMonth"],
                    "dataName": data["dataName"],
                }, {
                    "$set": data,
                    "$setOnInsert": {"createdAt": getNow()}
                }, upsert=True)
        except Exception as e:
            print(e)

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