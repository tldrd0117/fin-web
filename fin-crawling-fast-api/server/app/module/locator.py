from __future__ import annotations
from typing import Any, Dict
from uvicorn.config import logger


class Locator(object):
    _instance = None
    store: Dict[str, Any] = dict()

    def __init__(self) -> None:
        super().__init__()
        if not Locator._instance:
            print("__init__ method called but nothing is created")
        else:
            print("instance already created")
    
    @classmethod
    def getInstance(cls) -> Locator:
        if not cls._instance:
            cls._instance = Locator()
        return cls._instance
    
    def register(self, obj: Any) -> None:
        typeName = type(obj).__name__
        key = None
        if typeName == "type":
            key = obj.__name__
        else:
            key = typeName
        self.store[key] = obj
        logger.info("Locator: "+key+" registered")
    
    def get(self, obj: Any) -> Any:
        typeName = type(obj).__name__
        if typeName == "type":
            return self.store[obj.__name__]
        elif typeName == "str":
            return self.store[obj]
        else:
            return self.store[typeName]



