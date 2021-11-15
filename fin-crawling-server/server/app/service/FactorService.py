from app.repo.FactorRepository import FactorRepository
from app.module.socket.manager import ConnectionManager

RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_START = "factor/convertFileToDbStart"
RES_SOCKET_FACTOR_UPDATE_STATE_RES = "factor/updateConvertStateRes"
RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_END = "factor/convertFileToDbEnd"


class FactorService:
    def __init__(self, manager: ConnectionManager, factorRepository: FactorRepository) -> None:
        self.manager = manager
        self.factorRepository = factorRepository
    
    def convertFileToDb(self) -> None:
        self.manager.sendBroadCast(RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_START, dict())
        data = self.factorRepository.getFactorsInFile()
        self.manager.sendBroadCast(RES_SOCKET_FACTOR_UPDATE_STATE_RES, dict())
        # update Db
        self.factorRepository.insertFactor(data)
        self.manager.sendBroadCast(RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_END, dict())
    
