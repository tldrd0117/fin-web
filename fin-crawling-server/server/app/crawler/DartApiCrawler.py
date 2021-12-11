from __future__ import annotations
import os

from typing import Dict, TypeVar
from typing_extensions import Final

from pymitter import EventEmitter
import uuid

from app.module.logger import Logger

# from pathlib import Path
from app.model.dto import DartApiCrawling
from pathlib import Path

from urllib import request
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import OpenDartReader
import pandas as pd
import sys

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
        if "pytest" in sys.modules:
            savepath = Path('factors/codes.zip')
            loadpath = Path('factors/codes')
            datapath = Path("factors/codes/CORPCODE.xml")
        else:
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
            el = li.find("stock_code")
            if el is not None:
                stockCode = el.text
                if isinstance(stockCode, str) and len(stockCode) == 6:
                    codeEl = li.find("corp_code")
                    if codeEl is not None:
                        codes[stockCode] = codeEl.text
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
                if df is not None:
                    df["crawling_year"] = year
                    df["crawling_code"] = code
                    sumDf = pd.concat([sumDf, df])
        return sumDf.to_dict("records")

        

