
import logging
import logging.handlers
import pathlib
from uvicorn.config import logger
import sys


class Logger:

    def __init__(self, cls: str, name: str = "log") -> None:
        self.logger = logging.getLogger("logger"+cls)
        self.logger.setLevel(logging.INFO)
        if "pytest" in sys.modules:
            print("logger..pytest")
            return
        
        self.cls = cls
        path = pathlib.Path(f"../app/log/{name}")
        logger.info(path.resolve())

        self.fileHandler = logging.handlers.TimedRotatingFileHandler(
            filename=path.resolve(),
            when='midnight',
            interval=1
        )
        self.logger.addHandler(self.fileHandler)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s'
        )
        self.fileHandler.setFormatter(formatter)    # 핸들러에 로깅 포맷 할당
    
    def info(self, func: str, msg: str = None) -> None:
        if msg is None:
            self.logger.info(f"cls: {self.cls}, msg: {func}")
            return

        self.logger.info(f"cls: {self.cls}, func: {func}, msg: {msg}")
        logger.info(f"cls: {self.cls}, func: {func}, msg: {msg}")
    
    def error(self, func: str, msg: str) -> None:
        self.logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
        logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
