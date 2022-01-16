
from app.model.dao import ListLimitDao, ListLimitDataDao
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from app.module.logger import Logger
from pymongo import DESCENDING
import traceback


class TaskMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("TaskMongoDataSource")

    def getCompletedTask(self, dto: ListLimitDao) -> ListLimitDataDao:
        try:
            data = dto.dict()
            cursor = self.task.find({"$or": [
                        {"state": "success"}, 
                        {"state": "fail"},
                        {"state": "complete"}, 
                        {"state": "error"},
                        {"state": "cancelled"}
                    ]}
                ).sort("createdAt", DESCENDING)\
                .skip(data["offset"])\
                .limit(data["limit"])
            
            count = self.task.find({"$or": [
                        {"state": "success"}, 
                        {"state": "fail"},
                        {"state": "complete"}, 
                        {"state": "error"},
                        {"state": "cancelled"}
                    ]}
                ).count()
            print("res:start")
            res = ListLimitDataDao(**{
                "taskId": data["taskId"],
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
