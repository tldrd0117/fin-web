from __future__ import annotations
import os
import traceback

from typing import Any, Dict, List, TypeVar, TYPE_CHECKING
from typing_extensions import Final
from app.module.locator import Locator

import uuid

from app.module.logger import Logger

# from pathlib import Path
from app.model.dto import DartApiCrawling
from pathlib import Path

from zipfile import ZipFile
import xml.etree.ElementTree as ET
from app.scrap.base.Scraper import Scraper
from app.repo.FactorRepository import FactorRepository

import pandas as pd
import sys
import aiohttp
import io
import asyncio

if TYPE_CHECKING:
    from app.service.scrap.FactorFileScrapService import FactorFileScrapService


# from fake_useragent import UserAgent


class FactorFileScraper(Scraper):
    EVENT_FACTOR_FILE_ON_GET_FACTORS_INFILE: Final ="FactorFileCrawler/getFactorsInFile"
    EVENT_FACTOR_FILE_ON_MAKE_FACTOR_DATA: Final ="FactorFileCrawler/makeFactorData"
    EVENT_FACTOR_FILE_ON_RESULT_OF_FACTOR: Final ="FactorFileCrawler/onResultOfFactor"

    def __init__(self, eventTarget) -> None:
        super().__init__(eventTarget)
        self.logger = Logger("FactorFileScraper")
        self.service: FactorFileScrapService = eventTarget
    

    async def crawling(self, runCrawling: DartApiCrawling) -> None:
        try:
            await self.ee.emit(self.EVENT_FACTOR_FILE_ON_GET_FACTORS_INFILE, runCrawling)
            li = await self.service.crawlingFactorsInFile()
            await self.ee.emit(self.EVENT_FACTOR_FILE_ON_MAKE_FACTOR_DATA, runCrawling)
            factorData = await self.service.makeFactorLists(li)
            await self.ee.emit(self.EVENT_FACTOR_FILE_ON_RESULT_OF_FACTOR, runCrawling, factorData)
        except Exception as e:
            raise e
        