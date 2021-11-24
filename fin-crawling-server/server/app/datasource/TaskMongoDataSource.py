
from uvicorn.config import logger
from app.model.dao import ListLimitDao, ListLimitDataDao
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from pymongo import DESCENDING


class TaskMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()

    def getCompletedTask(self, dto: ListLimitDao) -> ListLimitDataDao:
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
            
            res = ListLimitDataDao(**{
                "taskId": dto["taskId"],
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
