from typing import Dict, List
from app.model.scrap.model import RunScrap
import abc
from pymitter import EventEmitter

class Scraper(object):
    service = None
    def __init__(self) -> None:
        self.ee = EventEmitter()
        pass

    @abc.abstractmethod
    async def crawling(self, runCrawling: RunScrap) -> None:
        pass

    def getEventEmitter(self) -> EventEmitter:
        return self.ee
