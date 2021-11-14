from app.module.logger import Logger
from pymongo import ASCENDING, MongoClient, monitoring
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.monitoring import (CommandFailedEvent, CommandStartedEvent,
                                CommandSucceededEvent)

from dotenv import dotenv_values

log = Logger("mongo")
config = dotenv_values('.env')


class CommandLogger(monitoring.CommandListener):

    def started(self, event: CommandStartedEvent) -> None:
        log.debug("Command {0.command_name} with request id ""{0.request_id} started on server ""{0.connection_id}".format(event))

    def succeeded(self, event: CommandSucceededEvent) -> None:
        log.debug("Command {0.command_name} with request id ""{0.request_id} on server {0.connection_id} ""succeeded in {0.duration_micros} ""microseconds".format(event))

    def failed(self, event: CommandFailedEvent) -> None:
        log.debug("Command {0.command_name} with request id ""{0.request_id} on server {0.connection_id} ""failed in {0.duration_micros} ""microseconds".format(event))


monitoring.register(CommandLogger())


class MongoDataSource():
    def __init__(self) -> None:
        self.host = config.mongodbHost
        self.port = config.mongodbPort
        self.userName = config.mongodbUserName
        self.password = config.mongodbPassword
        self.path = f'mongodb://{self.userName}:{self.password}@{self.host}:{self.port}'
        self.logger = log
        log.info(f"db connecting... {self.path}")
        try:
            self.client = MongoClient(self.path)
            self.client.server_info()
            self.setupMarcap()
            log.info("db connection seccess")
        except Exception as e:
            log.info(e)
    
    def setupMarcap(self) -> None:
        self.stock = self.client["stock"]
        self.marcap = self.getCollection("marcap")
        self.task = self.getCollection("task")
        self.factor = self.getCollection("factor")
        print(self.marcap.index_information())
        try:
            self.marcap.create_index([("date", ASCENDING), ("code", ASCENDING), ("market", ASCENDING)], unique=True, name="marcapIndex")
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
