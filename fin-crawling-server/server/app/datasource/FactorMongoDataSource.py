from typing import List

from app.model.dao import FactorDao
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource


class FactorMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()

    def insertFactor(self, li: List[FactorDao]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            for one in li:
                data = one.dict()
                data["updatedAt"] = getNow()
                self.factor.update_one({
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
    
