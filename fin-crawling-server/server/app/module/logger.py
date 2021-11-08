
import logging
import logging.handlers
from app.util.DateUtils import getNowDateStr
import pathlib
from uvicorn.config import logger


class Logger:
    def __init__(self, cls: str) -> None:
        self.logger = logging.getLogger("logger"+cls)
        self.cls = cls
        path = pathlib.Path("log")
        logger.info(path.resolve())

        self.fileHandler = logging.handlers.TimedRotatingFileHandler(
            filename=path.resolve(),
            when='midnight',
            interval=1
        )
        self.logger.addHandler(self.fileHandler)
    
    
    def info(self, func: str, msg: str) -> None:
        self.logger.info(f"cls: {self.cls}, func: {func}, msg: {msg}")
    
    def error(self, func: str, msg: str) -> None:
        self.logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
