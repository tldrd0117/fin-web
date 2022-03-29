
from typing import Any, TypeVar
from app.module.locator import Locator
from app.module.logger import Logger
import abc

T = TypeVar('T')

class BaseComponent(object):
    def __init__(self) -> None:
        self.locator = Locator.getInstance()
        self.baseLogger = Logger("BaseComponent")

    def get(self, clazz: T) -> T:
        return self.locator.get(clazz)

    @abc.abstractmethod
    def onComponentResisted(self) -> None:
        self.baseLogger.info("base onComponentResisted")
        pass