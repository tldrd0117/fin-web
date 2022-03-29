
import logging
import logging.handlers
import pathlib
from typing import Dict
from uvicorn.config import logger
import sys


class Logger:
    __loggers: Dict[str, logging.Logger] = {}

    @classmethod
    def __getLogger(cls, name: str) -> logging.Logger:
        if name not in cls.__loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            if "pytest" in sys.modules:
                print("logger..pytest")
                return logger

            path = pathlib.Path(f"../app/log/{name}")
            logger.info(path.resolve())

            # fileHandler = logging.handlers.TimedRotatingFileHandler(
            #     filename=path.resolve(),
            #     when='midnight',
            #     interval=1
            # )

            fileHandler2 = logging.handlers.RotatingFileHandler(
                filename=path.resolve(),
                maxBytes=1000000,
                backupCount=100
            )  

            logger.addHandler(fileHandler2)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s'
            )
            fileHandler2.setFormatter(formatter)    # 핸들러에 로깅 포맷 할당

            cls.__loggers[name] = logger
        return cls.__loggers[name]

    def __init__(self, cls: str, name: str = "log") -> None:
        self.cls = cls
        self.logger = self.__getLogger(name)
    
    def info(self, func: str, msg: str = None) -> None:
        if msg is None:
            info = (f"cls: {self.cls}, msg: {func}")[:500]
            self.logger.info(info)
            return
        info = (f"cls: {self.cls}, func: {func}, msg: {msg}")[:500]
        self.logger.info(info)
        logger.info(info)
    
    def error(self, func: str, msg: str) -> None:
        self.logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
        logger.error(f"cls: {self.cls}, func: {func}, msg {msg}")
