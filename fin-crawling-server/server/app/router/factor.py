from fastapi import WebSocket
from app.service.FactorService import FactorService
from app.module.socket.manager import ConnectionManager
from app.model.dto import RunFactorFileConvert
import uuid

REQ_SOCKET_FACTOR_FILE_TO_DB = "factor/convertFileToDb"


class CrawlingSocketRouter(object):
    def __init__(self, factorService: FactorService, manager: ConnectionManager) -> None:
        super().__init__()
        self.factorService = factorService
        self.manager = manager
        self.ee = manager.ee
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on(REQ_SOCKET_FACTOR_FILE_TO_DB, self.convertFileToDb)

    def convertFileToDb(self, data: dict, websocket: WebSocket) -> None:
        dto = RunFactorFileConvert(**{
            "taskId": data["taskId"],
            "taskUniqueId": data["taskId"] + str(uuid.uuid4())
        })
        self.factorService.convertFileToDb(dto)
