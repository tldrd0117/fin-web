from fastapi import WebSocket
from app.service.FactorService import FactorService
from app.module.socket.manager import ConnectionManager
from app.module.logger import Logger
from app.model.dto import ListLimitData, RunFactorFileConvert
import uuid

REQ_SOCKET_FACTOR_FILE_TO_DB = "factor/convertFileToDb"
REQ_SOCKET_FACTOR_FETCH_COMPLETED_TASK = "factor/fetchCompletedTask"


class FactorSocketRouter(object):
    def __init__(self, factorService: FactorService, manager: ConnectionManager) -> None:
        super().__init__()
        self.factorService = factorService
        self.manager = manager
        self.ee = manager.ee
        self.logger = Logger("CrawlingSocketRouter")
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on(REQ_SOCKET_FACTOR_FILE_TO_DB, self.convertFileToDb)

    def convertFileToDb(self, data: dict, websocket: WebSocket) -> None:
        self.logger.info("convertFileToDb")
        dto = RunFactorFileConvert(**{
            "taskId": data["taskId"],
            "taskUniqueId": data["taskId"] + str(uuid.uuid4())
        })
        self.factorService.convertFactorFileToDb(dto)
    
    
    
    def fetchCompletedTask(self, data: dict, websocket: WebSocket) -> None:
        dto = ListLimitData(**{
            "offset": data["offset"],
            "limit": data["limit"],
            "taskId": data["taskId"]
        })
        self.factorService.fetchCompletedTask(dto, websocket)
