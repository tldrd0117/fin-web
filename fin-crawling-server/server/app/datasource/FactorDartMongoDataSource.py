from typing import Any, Dict, List

from app.model.dao import FactorDao
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from app.model.dto import ListLimitData, ListLimitResponse, FactorData
from app.module.logger import Logger
from pymongo import DESCENDING
import traceback
from app.base.BaseComponent import BaseComponent


class FactorDartMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("FactorDartMongoDataSource")
    
    async def getFactor(self, year: str = "*", month: str = "*", code: str = "*") -> list:
        try:
            findObj: Dict[str, Any] = {}
            self.mergeFindObj(findObj, "dataYear", year)
            self.mergeFindObj(findObj, "dataMonth", month)
            self.mergeFindObj(findObj, "code", code)
            cursor = self.factorDart.find(findObj)
            fields = ["code", "dataMonth", "dataName", "dataYear", "dataId", "dataValue", "name"]
            return list(map(lambda data: FactorData(**{field: data[field] for field in fields}), list(cursor)))
        except Exception:
            self.logger.error("getFactor", traceback.format_exc())
            return list()

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
        except Exception:
            self.logger.error("insertFactor", traceback.format_exc())

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
        except Exception:
            self.logger.error("getCompletedTask", traceback.format_exc())
        return []