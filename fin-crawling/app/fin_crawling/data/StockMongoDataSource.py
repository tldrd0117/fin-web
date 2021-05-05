import logging

from pymongo import ASCENDING, MongoClient, monitoring
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.monitoring import (CommandFailedEvent, CommandStartedEvent,
                                CommandSucceededEvent)

log = logging.getLogger("mongo")


class CommandLogger(monitoring.CommandListener):

    def started(self, event: CommandStartedEvent) -> None:
        log.debug("Command {0.command_name} with request id ""{0.request_id} started on server ""{0.connection_id}".format(event))

    def succeeded(self, event: CommandSucceededEvent) -> None:
        log.debug("Command {0.command_name} with request id ""{0.request_id} on server {0.connection_id} ""succeeded in {0.duration_micros} ""microseconds".format(event))

    def failed(self, event: CommandFailedEvent) -> None:
        log.debug("Command {0.command_name} with request id ""{0.request_id} on server {0.connection_id} ""failed in {0.duration_micros} ""microseconds".format(event))


monitoring.register(CommandLogger())


class StockMongoDataSource:
    def __init__(self, host: str = "mongo", port: str = "27017") -> None:
        self.host = host
        self.port = port
        self.userName = "root"
        self.password = "example"
        self.client = MongoClient(f'mongodb://{self.userName}:{self.password}@{self.host}:{self.port}')
        self.client.server_info()
        self.setupMarcap()

    def setupMarcap(self) -> None:
        self.stock = self.client["stock"]
        self.marcap = self.getCollection("marcap")
        self.task = self.getCollection("task")
        print(self.marcap.index_information())
        try:
            self.marcap.create_index([("date", ASCENDING), ("code", ASCENDING)], unique=True, name="marcapIndex")
            self.task.create_index([("taskUniqueId", ASCENDING)], unique=True, name="taskIndex")
        except Exception as e:
            print(e)
        print(self.marcap.index_information())

    def isSetupMarcap(self) -> bool:
        return "marcapIndex" in self.marcap.index_information()

    def getDatabase(self) -> Database:
        return self.client["stock"]

    def getCollection(self, name: str) -> Collection:
        return self.getDatabase()[name]
    
    def exceptId(self, data: list) -> list:
        newdata = []
        for one in data:
            one['_id'] = str(one["_id"])
            newdata.append(one)
        return newdata

    def insertMarcap(self, data: dict) -> None:
        try:
            if not self.isSetupMarcap():
                self.setupMarcap()
            self.marcap.insert_many(data)
        except Exception as e:
            print(e)

    def selectCompleteTask(self) -> list:
        try:
            cursor = self.task.find({"$or": [{"state": "success"}, {"state": "fail"}]})
            return self.exceptId(list(cursor))
        except Exception as e:
            print(e)
        return []

    def upsertTask(self, value: dict) -> None:
        try:
            self.task.update_one({
                "taskUniqueId": value["taskUniqueId"]
            }, {
                "$set": value
            }, upsert=True)
        except Exception as e:
            print(e)
