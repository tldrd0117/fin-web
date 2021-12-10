from __future__ import annotations
import asyncio
import os
import traceback

from datetime import datetime, timedelta
from typing import Dict, TypeVar
from typing_extensions import Final

from pymitter import EventEmitter
import uuid

from app.observer.CmdFileSystemEventHandler import FILE_SYSTEM_HANDLER
from app.module.logger import Logger

# from pathlib import Path
from app.model.dto import DartApiCrawling
from pathlib import Path

from urllib import request
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import OpenDartReader
import pandas as pd

T = TypeVar("T")

EVENT_DART_API_CRAWLING_ON_DOWNLOADING_CODES: Final = "dartApiCrawler/onDownloadingCodes"
EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA: Final = "dartApiCrawler/onCrawlingFactorData"


class DartApiCrawler(object):
    
    def __init__(self) -> None:
        super().__init__()
        self.ee = EventEmitter()
        self.isLock = False
        self.isError = False
        self.logger = Logger("DartApiCrawler")

    def createUUID(self) -> str:
        return str(uuid.uuid4())

    async def downloadCodes(self, isCodeNew: bool, apiKey: str) -> Dict:
        savepath = Path('app/static/factors/codes.zip')
        loadpath = Path('app/static/factors/codes')
        datapath = Path("app/static/factors/codes/CORPCODE.xml")

        if isCodeNew or not os.path.exists(datapath.resolve()):
            url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={apiKey}"
            request.urlretrieve(url, savepath.resolve())
            ZipFile(file=savepath.resolve()).extractall(loadpath.resolve())
        tree = ET.parse(datapath.resolve())
        codes = {}
        for li in tree.findall("list"):
            stockCode = li.find("stock_code").text
            if len(stockCode) == 6:
                codes[stockCode] = li.find("corp_code").text
        return codes

    async def crawling(self, dto: DartApiCrawling) -> Dict:
        if dto.startYear < 2015:
            dto.startYear = 2015
        self.ee.emit(EVENT_DART_API_CRAWLING_ON_DOWNLOADING_CODES)
        codes = await self.downloadCodes(dto.isCodeNew, dto.apiKey)
        self.ee.emit(EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA)
        dart: OpenDartReader = OpenDartReader(dto.apiKey)
        sumDf = pd.DataFrame()
        for year in range(dto.startYear, dto.endYear+1):
            for code in codes:
                df = dart.finstate_all(code, year)
                df["crawling_year"] = year
                df["crawling_code"] = code
                sumDf = pd.concat([sumDf, df])
        return sumDf.to_dict("records")

        

