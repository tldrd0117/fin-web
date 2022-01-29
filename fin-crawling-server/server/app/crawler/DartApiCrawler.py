from __future__ import annotations
import os
import traceback

from typing import Any, Dict, TypeVar
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

from app.util.AsyncUtil import asyncRetryNonBlock

T = TypeVar("T")

EVENT_DART_API_CRAWLING_ON_DOWNLOADING_CODES: Final = "dartApiCrawler/onDownloadingCodes"
EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA: Final = "dartApiCrawler/onCrawlingFactorData"
EVENT_DART_API_CRAWLING_ON_COMPLETE_YEAR: Final = "dartApiCrawler/onCompleteYear"
EVENT_DART_API_CRAWLING_ON_RESULT_OF_FACTOR: Final = "dartApiCrawler/onResultOfFactor"
EVENT_DART_API_CRAWLING_ON_CANCEL: Final = "dartApiCrawler/onCancel"


class DartApiCrawler(object):
    
    def __init__(self) -> None:
        super().__init__()
        self.ee = EventEmitter()
        self.isLock = False
        self.isCancelled = False
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
        codes: Dict[str, Any] = {}
        for li in tree.findall("list"):
            el = li.find("stock_code")
            if el is not None:
                stockCode = el.text
                if isinstance(stockCode, str) and len(stockCode) == 6:
                    codeEl = li.find("corp_code")
                    nameEl = li.find("corp_name")
                    if codeEl is not None:
                        codes[stockCode] = {}
                        codes[stockCode]["corp_code"] = codeEl.text
                        if nameEl is not None:
                            codes[stockCode]["corp_name"] = nameEl.text
        return codes

    async def crawling(self, dto: DartApiCrawling) -> None:
        # cpu bound 작업
        try:
            if dto.startYear < 2015:
                dto.startYear = 2015
            self.ee.emit(EVENT_DART_API_CRAWLING_ON_DOWNLOADING_CODES, dto)
            codes = await asyncRetryNonBlock(5, 1, self.downloadCodes, isCodeNew=dto.isCodeNew, apiKey=dto.apiKey)
            # codes = self.downloadCodes(dto.isCodeNew, dto.apiKey)
            self.ee.emit(EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA, dto)
            dart: OpenDartReader = OpenDartReader(dto.apiKey)
            for year in range(dto.startYear, dto.endYear+1):
                self.ee.emit(EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA, dto)
                self.logger.info("crawling", str(len(codes)))
                for code in codes:
                    # newDf = self.getYearDf(dart, code, codes, year)
                    newDf = await asyncRetryNonBlock(5, 1, self.getYearDf, dart, code, codes, year)
                    if self.isCancelled:
                        self.ee.emit(EVENT_DART_API_CRAWLING_ON_CANCEL, dto)
                    if newDf is not None:
                        self.logger.info("crawling", code)
                        self.ee.emit(EVENT_DART_API_CRAWLING_ON_RESULT_OF_FACTOR, dto, year, newDf.to_dict("records"))
                    # yearDf = await self.getYearDf(dart, code, codes, year, yearDf)
                self.ee.emit(EVENT_DART_API_CRAWLING_ON_COMPLETE_YEAR, dto, year)
                self.logger.info("crawling", str(year))
        except Exception as e:
            raise e
        
    async def getYearDf(self, dart: OpenDartReader, code: str, codes: Dict, year: int) -> pd.DataFrame:
        df = None
        try:
            df = dart.finstate_all(code, year)
            # df = await asyncio.create_task(dart.finstate_all(code, year))
            # df = await loop.run_in_executor(self.pool, dart.finstate_all, code, year)
        except Exception as e:
            self.logger.error("getYearDf", traceback.format_exc())
            raise e
        self.logger.info("df", str(df))
        if df is not None:
            df["crawling_year"] = year
            df["crawling_code"] = code
            df["crawling_name"] = codes[code]["corp_name"]
            name = codes[code]["corp_name"]
            self.logger.info("getYearDf", f"{str(year)} {str(code)} {str(name)}")
            return df
            # allCodeDf = pd.concat([allCodeDf, df])
            # return allCodeDf
        return None


        

