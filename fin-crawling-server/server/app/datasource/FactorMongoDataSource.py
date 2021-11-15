from typing import List

from uvicorn.config import logger
from app.model.dto import KrxFactor
from app.util.DateUtils import getNow
from app.datasource.MongoDataSource import MongoDataSource
from pymongo import DESCENDING


class FactorMongoDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()

    def insertFactor(self, li: List[KrxFactor]) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            for one in li:
                data = one.dict()
                data["updatedAt"] = getNow()
                # code name type
                self.factor.update_one({
                    "code": data["code"],
                    "date": data["date"],
                    "market": data["market"]
                }, {
                    "$set": data,
                    "$setOnInsert": {"createdAt": getNow()}
                }, upsert=True)
        except Exception as e:
            print(e)
    
