from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class Crawler(ABC, Generic[T]):
    @abstractmethod
    def crawling(self) -> T:
        raise NotImplementedError
