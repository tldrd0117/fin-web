
import logging
import logging.handlers
from app.util.DateUtils import getNowDateStr


class Logger:
    def __init__(self, cls: str) -> None:
        self.logger = logging.getLogger("logger")
        self.cls = cls
        self.fileHandler = logging.handlers.TimedRotatingFileHandler()
    
    def renewFileHanadler(self) -> None:
        if self.date != getNowDateStr():
            if self.fileHandler:
                self.logger.removeHandler(self.fileHandler)
            self.date = getNowDateStr()
            self.fileHandler = logging.FileHandler(f"server/log-{self.date}.log")
            self.logger.addHandler(self.fileHandler)
    
    def info(self, func: str, msg: str) -> None:
        self.logger.info(f"cls: {self.cls}, func: {func}, msg: {msg}")
    
    def error(self, func: str, msg: str) -> None:
        self.logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
