from typing import Dict
from app.module.logger import Logger
from pymongo import ASCENDING, MongoClient, monitoring
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.monitoring import (CommandFailedEvent, CommandStartedEvent,
                                CommandSucceededEvent)

from dotenv import dotenv_values
from app.base.BaseComponent import BaseComponent

log = Logger("MongoDataSource", "mongoDb")
config = dotenv_values('.env')


class CommandLogger(monitoring.CommandListener):

    def started(self, event: CommandStartedEvent) -> None:
        pass
        # log.info("started", "Command {0.command_name} with request id ""{0.request_id} started on server ""{0.connection_id}".format(event))

    def succeeded(self, event: CommandSucceededEvent) -> None:
        pass
        # log.info("succeeded", "Command {0.command_name} with request id ""{0.request_id} on server {0.connection_id} ""succeeded in {0.duration_micros} ""microseconds".format(event))

    def failed(self, event: CommandFailedEvent) -> None:
        pass
        # log.info("failed", "Command {0.command_name} with request id ""{0.request_id} on server {0.connection_id} ""failed in {0.duration_micros} ""microseconds".format(event))


monitoring.register(CommandLogger())


class MongoDataSource():
    def __init__(self) -> None:
        self.host = config["mongodbHost"]
        self.port = config["mongodbPort"]
        self.userName = config["mongodbUserName"]
        self.password = config["mongodbPassword"]
        # self.host = "localhost"
        # self.port = "30001"
        # self.userName = "root"
        # self.password = "tester00"
        self.path = f'mongodb://{self.userName}:{self.password}@{self.host}:{self.port}'
        self.logger = log
        log.info("__init__", f"db connecting... {self.path}")
        try:
            self.client = MongoClient(self.path)
            self.client.server_info()
            self.setupMarcap()
            log.info("__init__", "db connection seccess")
        except Exception as e:
            log.info("__init__", e)
    
    def setupMarcap(self) -> None:
        self.stock = self.client["stock"]
        self.marcap = self.getCollection("marcap")
        self.task = self.getCollection("task")
        self.factor = self.getCollection("factor")
        self.factorDart = self.getCollection("factorDart")
        self.seibroDividend = self.getCollection("seibroDividend")
        self.seibroStockNum = self.getCollection("seibroStockNum")
        self.user = self.getCollection("user")
        
        print(self.marcap.index_information())
        try:
            self.marcap.create_index([("date", ASCENDING), ("code", ASCENDING), ("market", ASCENDING)], unique=True, name="marcapIndex")
            self.task.create_index([("taskUniqueId", ASCENDING)], unique=True, name="taskIndex")
            self.factor.create_index([("dataYear", ASCENDING), ("dataMonth", ASCENDING), ("code", ASCENDING), ("dataName", ASCENDING)], unique=True, name="factorIndex")
            for index in self.factorDart.list_indexes():
                if index["name"] == "factorIndex":
                    self.factorDart.drop_index("factorIndex")
            self.factorDart.create_index([("dataYear", ASCENDING), ("dataMonth", ASCENDING), ("code", ASCENDING), ("dataName", ASCENDING)], unique=True, name="factorDartIndex")
            self.seibroDividend.create_index([("배정기준일", ASCENDING),("현금배당 지급일", ASCENDING),\
                ("결산월", ASCENDING),("배당구분", ASCENDING),("시장구분", ASCENDING),("종목코드", ASCENDING)], unique=True, name="seibroDiviendIndex")
            self.seibroStockNum.create_index([("발행일", ASCENDING), ("기업명", ASCENDING), ("주식종류", ASCENDING), ("발행사유", ASCENDING), ("상장일", ASCENDING), ("발행주식수", ASCENDING)], unique=False, name="seibroStockNumIndex")
            self.user.create_index([("userId", ASCENDING, "email", ASCENDING)], unique=True, name="userIndex")
        except Exception as e:
            print(e)
        print(self.marcap.index_information())

    def isSetupMarcap(self) -> bool:
        return "marcapIndex" in self.marcap.index_information()

    def getDatabase(self) -> Database:
        return self.client["stock"]

    def getCollection(self, name: str) -> Collection:
        return self.getDatabase()[name]
    
    def mergeFindObj(self, target: Dict, inputKey: str, inputValue: str = "*") -> Dict:
        if inputValue == "*":
            return target
        target[inputKey] = inputValue
        return target
    
    def exceptId(self, data: list) -> list:
        newdata = []
        for one in data:
            one['_id'] = str(one["_id"])
            newdata.append(one)
        return newdata
