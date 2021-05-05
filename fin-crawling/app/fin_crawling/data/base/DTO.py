from collections import deque
import datetime
from typing import Any


class DTO:
    def __str__(self) -> str:
        data = {}
        for key in self.__dict__:
            value = self.__dict__[key]
            data[key] = self.toDictValue(value)
        return str(data)

    def toDictValue(self, value: Any) -> Any:
        if type(value) is deque:
            return list(map(lambda x: self.toDictValue(x), list(value)))
        elif type(value) is dict:
            for key in value:
                value[key] = self.toDictValue(value[key])
            return value
        elif isinstance(value, DTO):
            return value.toDict()
        elif type(value) is datetime.datetime:
            return value.strftime("%Y%m%d")
        else:
            return value
    
    def toDict(self) -> Any:
        data = dict()
        for key in self.__dict__:
            value = self.__dict__[key]
            data[key] = self.toDictValue(value)
        return data

    