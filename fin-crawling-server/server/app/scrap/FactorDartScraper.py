from __future__ import annotations
import os
import traceback

from typing import Any, Dict, List, TypeVar
from typing_extensions import Final


import uuid

from app.module.logger import Logger

# from pathlib import Path
# from app.model.dto import DartApiCrawling
from app.model.scrap.model import FactorDartRunScrap
from pathlib import Path

from zipfile import ZipFile
import xml.etree.ElementTree as ET
from app.scrap.base.Scraper import Scraper

import pandas as pd
import sys
import aiohttp
import io

# from fake_useragent import UserAgent

from app.util.AsyncUtil import asyncRetryNonBlock

T = TypeVar("T")




class FactorDartScraper(Scraper):
    FACTOR_DART_CRAWLER_ON_DOWNLOADING_CODES: Final ="FactorDartCrawler/onDownloadingCodes"
    FACTOR_DART_CRAWLER_ON_CRAWLING_FACTOR_DATA: Final ="FactorDartCrawler/onCrawlingFactorData"
    FACTOR_DART_CRAWLER_ON_COMPLETE_YEAR: Final ="FactorDartCrawler/onCompleteYear"
    FACTOR_DART_CRAWLER_ON_RESULT_OF_FACTOR: Final ="FactorDartCrawler/onResultOfFactor"

    def __init__(self, eventTarget) -> None:
        super().__init__(eventTarget)
        self.isLock = False
        self.isCancelled = False
        self.logger = Logger("DartApiCrawler")
    

    async def downloadCodes(self, isCodeNew: bool, apiKey: str) -> Dict:
        if "pytest" in sys.modules:
            # savepath = Path('factors/codes.zip')
            loadpath = Path('factors/codes')
            datapath = Path("factors/codes/CORPCODE.xml")
        else:
            # savepath = Path('app/static/factors/codes.zip')
            loadpath = Path('app/static/factors/codes')
            datapath = Path("app/static/factors/codes/CORPCODE.xml")

        if isCodeNew or not os.path.exists(datapath.resolve()):
            # user_agent = UserAgent(cache=False, use_cache_server=True)
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'",
                'accept-language': 'ko'
            }
            params = {"crtfc_key": apiKey}
            url = "https://opendart.fss.or.kr/api/corpCode.xml"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    data = await response.read()
                    ZipFile(io.BytesIO(data)).extractall(loadpath.resolve())
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

    async def crawling(self, dto: FactorDartRunScrap) -> None:
        # cpu bound 작업
        try:
            if dto.startYear < 2015:
                dto.startYear = 2015
            await self.ee.emit(self.FACTOR_DART_CRAWLER_ON_DOWNLOADING_CODES, dto)
            codes = await asyncRetryNonBlock(5, 1, self.downloadCodes, isCodeNew=dto.isCodeNew, apiKey=dto.apiKey)
            # codes = self.downloadCodes(dto.isCodeNew, dto.apiKey)
            await self.ee.emit(self.FACTOR_DART_CRAWLER_ON_CRAWLING_FACTOR_DATA, dto)
            for year in range(dto.startYear, dto.endYear+1):
                await self.ee.emit(self.FACTOR_DART_CRAWLER_ON_CRAWLING_FACTOR_DATA, dto)
                self.logger.info("crawling", str(len(codes)))
                for code in codes:
                    # newDf = self.getYearDf(dart, code, codes, year)
                    newDf = await asyncRetryNonBlock(5, 1, self.getYearDf, dto.apiKey, code, codes, year)
                    if self.isCancelled:
                        await self.ee.emit(self.FACTOR_DART_CRAWLER_ON_CANCEL, dto)
                    if newDf is not None:
                        self.logger.info("crawling", code)
                        await self.ee.emit(self.FACTOR_DART_CRAWLER_ON_RESULT_OF_FACTOR, dto, year, newDf.to_dict("records"))
                    # yearDf = await self.getYearDf(dart, code, codes, year, yearDf)
                await self.ee.emit(self.FACTOR_DART_CRAWLER_ON_COMPLETE_YEAR, dto, year)
                self.logger.info("crawling", str(year))
        except Exception as e:
            raise e
        
    async def getYearDf(self, apiKey: str, code: str, codes: Dict, year: int) -> pd.DataFrame:
        self.logger.info("getYearDf", f"crawling: {code}")
        df = None
        try:

            url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'

            # user_agent = UserAgent(cache=False, use_cache_server=True)
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'",
                'accept-language': 'ko',
            }
            params = {
                'crtfc_key': apiKey,
                'corp_code': codes[code]["corp_code"],
                'bsns_year':  year,   # 사업년도
                'reprt_code': "11011",  # "11011": 사업보고서
                'fs_div': "CFS",  # "CFS":연결재무제표, "OFS":재무제표
            }
            connector = aiohttp.TCPConnector(limit=50, force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                timeout = aiohttp.ClientTimeout(total=15)
                # async with session.get(url, params=params, headers=headers) as response:
                async with session.get(url, params=params, timeout=timeout, headers=headers) as response:
                    data = await response.json()
                    if 'list' not in data:
                        return None
                    df = pd.json_normalize(data, 'list')
            # df = dart.finstate_all(code, year)
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


        

