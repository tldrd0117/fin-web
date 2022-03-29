from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING
from uvicorn.config import logger

if TYPE_CHECKING:
    from app.base.BaseComponent import BaseComponent


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
    
    def register(self, obj: BaseComponent) -> None:
        typeName = type(obj).__name__
        key = None
        if typeName == "type":
            key = obj.__name__
        else:
            key = typeName
        self.store[key] = obj
        obj.onComponentResisted()
        logger.info("Locator: "+key+" registered")
    

    def registerAll(self, li: List[BaseComponent]) -> None:
        from app.base.BaseComponent import BaseComponent
        for item in li:
            typeName = type(item).__name__
            key = None
            if typeName == "type":
                key = item.__name__
            else:
                key = typeName
            self.store[key] = item
        for item in li:
            typeName = type(item).__name__
            key = None
            if typeName == "type":
                key = item.__name__
            else:
                key = typeName
            if isinstance(item, BaseComponent):
                item.onComponentResisted()
            logger.info("Locator: "+key+" registered")

    
    def get(self, obj: Any) -> Any:
        typeName = type(obj).__name__
        if typeName == "type":
            return self.store[obj.__name__]
        elif typeName == "str":
            return self.store[obj]
        else:
            return self.store[typeName]
    
    def getFromName(self, name: str) -> Dict:
        result = {}
        for key in self.store.keys():
            if name in key:
                result[key] = self.store[key]
        return result




