
import logging
import logging.handlers
from app.util.DateUtils import getNowDateStr


class Logger:
    def __init__(self, cls: str) -> None:
        self.logger = logging.getLogger("logger")
        self.cls = cls
        self.fileHandler = logging.handlers.TimedRotatingFileHandler(
            filename="server/log/log-",
            when='midnight',
            interval=1
        )
    
    
    def info(self, func: str, msg: str) -> None:
        self.logger.info(f"cls: {self.cls}, func: {func}, msg: {msg}")
    
    def error(self, func: str, msg: str) -> None:
        self.logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
