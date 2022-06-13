from typing import Dict, List
from app.model.scrap.model import RunScrap
import abc
from app.util.events import eventManage
from app.util.decorator import EventEmitter

class Scraper(object):
    service = None
    def __init__(self, eventTarget) -> None:
        self.ee = EventEmitter(eventTarget, eventManage())

    @abc.abstractmethod
    async def crawling(self, runCrawling: RunScrap) -> None:
        pass

    def getEventEmitter(self) -> eventManage:
        return self.ee
