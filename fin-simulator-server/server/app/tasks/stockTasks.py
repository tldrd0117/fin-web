
from time import sleep
from typing import Any, Dict, Generator, List
import luigi
from luigi.contrib.mongodb import MongoTarget
from pymongo import MongoClient
from pymongo.collection import Collection
import pandas as pd
import numpy as np
from dotenv import dotenv_values
import os
import json
import hashlib
import sys
from app.utils.dateutils import moveMonth, getCurrentDate, getDateArr, getYearArr, getNow
from app.utils.factorutils import op, intersectCode
from app.utils.taskutils import *




config = dotenv_values('.env')


class MongoCollectionTarget(MongoTarget):

    """ Target for existing collection """
    def __init__(self, mongo_client: MongoClient, index: str, collection: str) -> None:
        super(MongoCollectionTarget, self).__init__(mongo_client, index, collection)

    def exists(self) -> bool:
        """
        Test if target has been run
        Target is considered run if the targeted collection exists in the database
        """
        return self.read()

    def read(self) -> bool:
        """
        Return if the target collection exists in the database
        """
        return self._collection in self.get_index().list_collection_names()


class BaseTask(luigi.Task):

    def output(self) -> luigi.LocalTarget:
        path = self.makePath()
        return luigi.LocalTarget(path)
    
    def outputOfPath(self) -> str:
        return self.output().path
    
    def outputOfpd(self) -> Any:
        path = self.output().path
        return pd.read_hdf(path)
    
    def outputOfList(self) -> List:
        return self.outputOfpd().to_list()
    
    def makePath(self) -> str:
        pass

    def makeDirs(self) -> str:
        path = self.makePath()
        print(path)
        return mkdir(path)


class SubTask(luigi.Task):
    def run(self) -> None:
        print("run")
        with self.output().open("w") as f:
            f.write("hello")
        for i in range(10):
            sleep(1)
            print(i+1)
    
    def output(self) -> luigi.LocalTarget:
        return luigi.LocalTarget("test.txt")


# poetry run python -m luigi --module my_module MyTask --x 123 --y 456 --local-scheduler
class TestTask(luigi.Task):
    x = luigi.IntParameter()
    y = luigi.IntParameter()

    def run(self) -> Generator:
        res = yield SubTask()
        with res.open("r") as f:
            lines = f.readlines()
            print(lines)
        print(self.x + self.y)

class MongoGetCollectionTask(luigi.Task):
    """
    몽고디비 클라이언트를 가져온다
    """
    index = luigi.OptionalParameter("")
    collection = luigi.OptionalParameter("")

    def output(self) -> MongoCollectionTarget:
        host = config["mongodbHost"]
        port = config["mongodbPort"]
        userName = config["mongodbUserName"]
        password = config["mongodbPassword"]
        path = f'mongodb://{userName}:{password}@{host}:{port}'
        client = MongoClient(path)
        if "marcap" not in client[self.index].list_collection_names():
            client[self.index].create_collection("marcap")
        if "adjustedMarcap" not in client[self.index].list_collection_names():
            client[self.index].create_collection("adjustedMarcap")
        
        return MongoCollectionTarget(client, self.index, self.collection)


class GetStockYearTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    year = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def requires(self):
        dates = getDateArr(startDateStr=f"{self.year}0101", endDateStr=f"{self.year}1231")
        requireTasks = {}
        for date in dates:
            requireTasks[date] = GetStockDayTask(date=date, markets=self.markets)
        return requireTasks

    def run(self) -> Generator:
        path = self.makeDirs()
        indata = self.input()
        dates = getDateArr(startDateStr=f"{self.year}0101", endDateStr=f"{self.year}1231")
        resultDf = pd.DataFrame()
        for date in dates:
            marcapDf = pd.read_hdf(indata[date].path)
            resultDf = resultDf.append(marcapDf)
        resultDf.to_hdf(path, key='df', mode='w')
    
    def makePath(self) -> str:
        return f'data/stock/year/GetStockYearTask-{self.year}-{encMd5(f"{self.markets}{self.targetJson}{pathToStr(self.targetPath)}")}'

class GetStockMonthTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    year = luigi.OptionalParameter("")
    month = luigi.OptionalParameter("")
    market = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        target = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = target.get_collection()
        cursor = collection.find({"$and": [
            {"date": {"$regex": f"^{self.year}{str(self.month).zfill(2)}", "$options": "i"}}, 
            {"market": self.market}]
        })
        df = pd.DataFrame(list(cursor))
        df["_id"] = df["_id"].astype(str)
        df.to_hdf(path, key='df', mode='w')
        print(df)
    
    def makePath(self) -> str:
        return f'data/stock/month/GetStockMonthTask-{self.market}-{self.year}-{self.month}'


class GetStockDayTask(BaseTask):
    """
    몽고디비에서 일을 기준으로 시가총액 데이터를 가져온다
    """
    date = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")

    def makeQuery(self) -> Dict:
        query = {"$and":[]}
        markets = json.loads(self.markets)
        if len(markets) > 0:
            query["$and"].append({"$or":list(map(lambda market: {"market": market}, markets))})
        query["$and"].append({"date":self.date})
        print(query)
        return query
    

    def requires(self):
        return {
            "GetMarcapCodes": GetMarcapCodes(markets=self.markets)
        }

    def run(self) -> Generator:
        path = self.makeDirs()
        indata = self.input()
        targets = pathToList(indata["GetMarcapCodes"].path)

        client = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = client.get_collection()
        cursor = collection.find(self.makeQuery())
        df = pd.DataFrame(list(cursor))
        if not df.empty:
            print(df.empty)
            df["_id"] = df["_id"].astype(str)
            df = df[df["code"].isin(targets)]
        df.to_hdf(path, key='df', mode='w')

    def makePath(self) -> str:
        return f'data/stock/day/GetStockDayTask-{self.date}-{encMd5(f"{self.markets}")}'


class GetStockRangeTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def requires(self):
        years = getYearArr(startDateStr=self.startDate, endDateStr=self.endDate)
        requireTasks = {}
        for year in years:
            requireTasks[year] = GetStockYearTask(year, markets=self.markets, targetPath=self.targetPath, targetJson=self.targetJson)
        return requireTasks

    def run(self) -> Generator:
        path = self.makeDirs()
        indata = self.input()
        years = getYearArr(startDateStr=self.startDate, endDateStr=self.endDate)
        resultDf = pd.DataFrame()
        for year in years:
            print(year)
            marcapDf = pd.read_hdf(indata[year].path)
            resultDf = resultDf.append(marcapDf)
        print(resultDf)
        resultDf.to_hdf(path, key='df', mode='w', format="table")
    
    def makePath(self) -> str:
        return f'data/stock/range/GetStockRangeTask-{self.startDate}-{self.endDate}-{encMd5(f"{self.markets}{self.targetJson}{pathToStr(self.targetPath)}")}'

class UpdateAdjustedStockTask(BaseTask):
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def requires(self):
        return {
            "GetSeibroStockNumTask": GetSeibroStockNumTask(startDate=self.startDate, endDate=self.endDate, targetJson=self.targetJson, targetPath=self.targetPath),
            "GetSeibroDividendTask": GetSeibroDividendTask(startDate=self.startDate, endDate=self.endDate, targetJson=self.targetJson, targetPath=self.targetPath)
        }

    def run(self):
        path = self.makeDirs()
        indata = self.input()

        stockNumDf: pd.DataFrame = pd.read_hdf(indata["GetSeibroStockNumTask"].path)
        dividendDf: pd.DataFrame = pd.read_hdf(indata["GetSeibroDividendTask"].path)
        # marcapDf["adjustedClose"] = 0
        # marcapDf["dividend"] = 0
        # marcapDf["splitCoeffcient"] = 0

        marcapTarget: MongoCollectionTarget = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collectionTarget: MongoCollectionTarget = yield MongoGetCollectionTask(index="stock", collection="adjustedMarcap")
        adjustedMarcap: Collection = collectionTarget.get_collection()
        marcap: Collection = marcapTarget.get_collection()

        targets = pathToList(self.targetPath)
        for target in targets:
            print(target)
            cursor = marcap.find({"code": target})
            targetDf = pd.DataFrame(list(cursor))
            dividendTargetDf = dividendDf[dividendDf["종목코드"]==target]
            stockNumTargetDf = stockNumDf[stockNumDf["code"]==target]
            last = None

            df: pd.DataFrame = pd.DataFrame()
            if not dividendTargetDf.empty:
                dividendTargetDf = dividendTargetDf[dividendTargetDf["주식종류"]=="보통주"]
                dividendTargetDf.rename(columns = {"주당배당금(일반)":"dividend"}, inplace=True)
                dividendTargetDf = dividendTargetDf[["종목코드", "배정기준일", "dividend"]]
                df = pd.merge(left=targetDf, right=dividendTargetDf, how='left', \
                        left_on=['code','date'], right_on=["종목코드", "배정기준일"], sort=False)
            
            if not stockNumTargetDf.empty:
                stockNumTargetDf = stockNumTargetDf[stockNumTargetDf["주식종류"]=="보통주"]
                stockNumTargetDf = stockNumTargetDf[["code", "발행일", "액면가"]]
                df = pd.merge(left=targetDf, right=stockNumTargetDf, how='left', \
                        left_on=['code','date'], right_on=["code", "발행일"], sort=False)
                df["액면가"] = df["액면가"].fillna(method="bfill")
                df["액면가"] = df["액면가"].fillna(method="ffill")
                last = df.iloc[-1,:]["액면가"]
            
            targetDf["adjClose"] = targetDf["close"]
            targetDf["adjOpen"] = targetDf["open"]
            targetDf["adjHigh"] = targetDf["high"]
            targetDf["adjLow"] = targetDf["low"]
            targetDf["adjDiff"] = targetDf["diff"]

            if len(df) <= 0 or last is None or np.isnan(last):
                self.upsertDf(adjustedMarcap, targetDf)
                continue

            print(f"code: {target} len:{str(len(df))} last:{(str(last))}")
            # dfOne["close"] = dfOne["close"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["open"] = dfOne["open"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["high"] = dfOne["high"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["low"] = dfOne["low"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["diff"] = dfOne["diff"].replace(r'^\s*$', np.nan, regex=True)
            df["close"] = pd.to_numeric(df["close"], errors='coerce')
            df["open"] = pd.to_numeric(df["open"], errors='coerce')
            df["high"] = pd.to_numeric(df["high"], errors='coerce')
            df["low"] = pd.to_numeric(df["low"], errors='coerce')
            df["diff"] = pd.to_numeric(df["diff"], errors='coerce')

            splitCoefficent = last/df["액면가"]
            
            df["adjClose"] = df["close"].astype(float) * splitCoefficent
            df["adjOpen"] = df["open"].astype(float) * splitCoefficent
            df["adjHigh"] = df["high"].astype(float) * splitCoefficent
            df["adjLow"] = df["low"].astype(float) * splitCoefficent
            df["adjDiff"] = df["diff"].astype(float) * splitCoefficent

            self.upsertDf(adjustedMarcap, df)
            print("end")
        
    def upsertDf(self, collection: Collection, dataframe: pd.DataFrame):
        for index, row in dataframe.iterrows():
            row = row.to_dict()
            del row["_id"]
            del row["createdAt"]
            row["updatedAt"] = getNow()
            collection.update_one({
                "code": row["code"],
                "date": row["date"]
            },{
                "$set": row,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
    
    def makePath(self) -> str:
        return f'data/stock/range/UpdateAdjustedStockTask-{self.startDate}-{self.endDate}-{encMd5(f"{self.markets}{self.targetJson}{pathToStr(self.targetPath)}")}'


class GetAdjustedStockRangeTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def requires(self):
        return {
            "GetStockRangeTask": GetStockRangeTask(markets=self.markets, startDate=self.startDate, endDate=self.endDate, targetJson=self.targetJson, targetPath=self.targetPath),
            "GetSeibroStockNumTask": GetSeibroStockNumTask(startDate=self.startDate, endDate=self.endDate, targetJson=self.targetJson, targetPath=self.targetPath),
            "GetSeibroDividendTask": GetSeibroDividendTask(startDate=self.startDate, endDate=self.endDate, targetJson=self.targetJson, targetPath=self.targetPath)
        }
    
    def run(self):
        path = self.makeDirs()
        indata = self.input()
        marcapDf = pd.read_hdf(indata["GetStockRangeTask"].path)
        stockNumDf: pd.DataFrame = pd.read_hdf(indata["GetSeibroStockNumTask"].path)
        dividendDf: pd.DataFrame = pd.read_hdf(indata["GetSeibroDividendTask"].path)
        # marcapDf["adjustedClose"] = 0
        # marcapDf["dividend"] = 0
        # marcapDf["splitCoeffcient"] = 0

        if not dividendDf.empty:
            dividendDf = dividendDf[dividendDf["주식종류"]=="보통주"]
            dividendDf.rename(columns = {"주당배당금(일반)":"dividend"}, inplace=True)
            dividendDf = dividendDf[["종목코드", "배정기준일", "dividend"]]
            df = pd.merge(left=marcapDf, right=dividendDf, how='left', \
                    left_on=['code','date'], right_on=["종목코드", "배정기준일"], sort=False)
        
        if not stockNumDf.empty:
            print("stockNumdf")
            print(marcapDf)
            print(stockNumDf)
            stockNumDf = stockNumDf[stockNumDf["주식종류"]=="보통주"]
            stockNumDf = stockNumDf[["code", "발행일", "액면가"]]
            df = pd.merge(left=marcapDf, right=stockNumDf, how='left', \
                    left_on=['code','date'], right_on=["code", "발행일"], sort=False)

        if len(self.targetJson) > 0:
            targets = json.loads(self.targetJson)
        else:
            targets = pathToList(self.targetPath)
        
        df["adjClose"] = df["close"]
        df["adjOpen"] = df["open"]
        df["adjHigh"] = df["high"]
        df["adjLow"] = df["low"]
        df["adjDiff"] = df["diff"]

        for target in targets:
            dfOne = df[df["code"]==target]
            if len(dfOne) <= 0:
                continue
            dfOne["액면가"] = dfOne["액면가"].fillna(method="bfill")
            dfOne["액면가"] = dfOne["액면가"].fillna(method="ffill")
            last = dfOne.iloc[-1,:]["액면가"]
            if np.isnan(last):
                continue

            print(f"code: {target} len:{str(len(dfOne))} last:{(str(last))}")
            # dfOne["close"] = dfOne["close"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["open"] = dfOne["open"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["high"] = dfOne["high"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["low"] = dfOne["low"].replace(r'^\s*$', np.nan, regex=True)
            # dfOne["diff"] = dfOne["diff"].replace(r'^\s*$', np.nan, regex=True)
            dfOne["close"] = pd.to_numeric(dfOne["close"], errors='coerce')
            dfOne["open"] = pd.to_numeric(dfOne["open"], errors='coerce')
            dfOne["high"] = pd.to_numeric(dfOne["high"], errors='coerce')
            dfOne["low"] = pd.to_numeric(dfOne["low"], errors='coerce')
            dfOne["diff"] = pd.to_numeric(dfOne["diff"], errors='coerce')

            splitCoefficent = last/dfOne["액면가"]
            
            dfOne["adjClose"] = dfOne["close"].astype(float) * splitCoefficent
            dfOne["adjOpen"] = dfOne["open"].astype(float) * splitCoefficent
            dfOne["adjHigh"] = dfOne["high"].astype(float) * splitCoefficent
            dfOne["adjLow"] = dfOne["low"].astype(float) * splitCoefficent
            dfOne["adjDiff"] = dfOne["diff"].astype(float) * splitCoefficent
            df[df["code"]==target] = dfOne
        df.to_hdf(path, key='df', mode='w')

        # if len(self.targetJson) > 0:
        #     targets = json.loads(self.targetJson)
        # else:
        #     targets = pathToList(self.targetPath)

        # for target in targets:
        #     marcapDf[marcapDf["code"]==target] 
    
    def makePath(self) -> str:
        return f'data/stock/range/GetMergedStockRangTask-{self.startDate}-{self.endDate}-{encMd5(f"{self.markets}{self.targetJson}{pathToStr(self.targetPath)}")}'


class GetSeibroDividendTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        if len(self.targetJson) > 0:
            targets = json.loads(self.targetJson)
        else:
            targets = pathToList(self.targetPath)
        client = yield MongoGetCollectionTask(index="stock", collection="seibroDividend")
        collection = client.get_collection()
        cursor = collection.find({
            "$and": [{
                    "배정기준일": {"$gte": self.startDate, "$lte": self.endDate}
                }
            ]
        })
        liCursor = list(cursor)
        df = pd.DataFrame(liCursor)
        if len(liCursor) > 0:
            df = df[df["종목코드"].isin(targets)]
            df["_id"] = df["_id"].astype(str)
        df.to_hdf(path, key='df', mode='w')
    
    def makePath(self) -> str:
        return f'data/factor/dividend/GetSeibroDividendTask-{self.startDate}-{self.endDate}-{encMd5(f"{self.targetJson}{pathToStr(self.targetPath)}")}'


class GetSeibroStockNumTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        if len(self.targetJson) > 0:
            targets = json.loads(self.targetJson)
        else:
            targets = pathToList(self.targetPath)
        client = yield MongoGetCollectionTask(index="stock", collection="seibroStockNum")
        collection = client.get_collection()
        cursor = collection.find({
            "$and": [{
                    "발행일": {"$gte": self.startDate, "$lte": self.endDate}
                }
            ]
        })
        df = pd.DataFrame(list(cursor))
        df = df[df["code"].isin(targets)]
        df["_id"] = df["_id"].astype(str)
        df.to_hdf(path, key='df', mode='w')
        print(df)
    
    def makePath(self) -> str:
        return f'data/factor/stocknum/GetSeibroStockNumTask-{self.startDate}-{self.endDate}-{encMd5(f"{self.targetJson}{pathToStr(self.targetPath)}")}'


class GetStockAdjustedPriceRangeTask(BaseTask):
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def requires(self):
        return {
            "GetStockRangeTask": GetStockRangeTask(markets=self.markets, startDate=self.startDate, endDate=self.endDate, targetJson=self.targetJson)
        }
    
    def run(self):
        path = self.makeDirs()
        indata = self.input()
        df = pd.read_hdf(indata["GetStockRangeTask"].path)
    
    def makePath(self) -> str:
        return f"data/stock/range"


class GetFactorYearTask(BaseTask):
    """
    몽고디비에서 년을 기준으로 팩터 값을 가져온다
    """
    year = luigi.OptionalParameter("")
    month = luigi.OptionalParameter("12")
    names = luigi.OptionalParameter("")
    dataIds = luigi.OptionalParameter("")
    exact = luigi.BoolParameter(True)
    standardYear = luigi.IntParameter(2019)

    def makeAndQuery(self, isDart) -> List:
        query = []
        nameQuery = []
        names = json.loads(self.names) if self.names is not None and len(self.names) > 0 else ""
        dataIds = json.loads(self.dataIds) if self.dataIds is not None and len(self.dataIds) > 0 else ""
        if len(self.year) > 0:
            query.append({
                "dataYear": str(self.year) if isDart else "{:.1f}".format(int(self.year))
            })
        if len(self.month) > 0:
            query.append({
                "dataMonth": self.month
            })
        nameQuery = {"$or":[]}            
        if len(names) == 1:
            if self.exact:
                nameQuery["$or"].append({
                    "dataName": names[0]
                })
            else:
                nameQuery["$or"].append({
                    "dataName": {"$regex": names[0]}
                })
        elif len(names) > 1:
            if self.exact:
                nameQuery["$or"].append({
                    "$or": list(map(lambda name: {"dataName": str(name)}, names))
                })
            else:
                nameQuery["$or"].append({
                    "$or": list(map(lambda name: {"dataName": {"$regex": name} }, names))
                })
        if len(dataIds) == 1:
            nameQuery["$or"].append({
                "dataId": dataIds[0]
            })
        elif len(dataIds) > 1:
            nameQuery["$or"].append({
                "$dataId": list(map(lambda dataId: {"dataId": str(dataId)}, dataIds))
            })
        query.append(nameQuery)
        print(query)
        return query

    def run(self) -> Generator:
        path = self.makeDirs()
        isDart = False
        if int(self.year) >= self.standardYear:
            isDart = True
            client = yield MongoGetCollectionTask(index="stock", collection="factorDart")
        else:
            client = yield MongoGetCollectionTask(index="stock", collection="factor")
        collection = client.get_collection()
        cursor = collection.find({"$and": self.makeAndQuery(isDart)})
        
        df = pd.DataFrame(list(cursor))
        if not df.empty:
            print(df)
            # errors를 coerce로 하면 숫자로 못바꾸는 항목은 NaN으로 설정
            df["_id"] = df["_id"].astype(str)
            df["createdAt"] = df["createdAt"].astype(str)
            df["updatedAt"] = df["updatedAt"].astype(str)
            df["dataValue"] = pd.to_numeric(df["dataValue"], errors="coerce")
            df.dropna(subset=['dataValue'])
        df.to_hdf(path, key='df', mode='w')
        # print(df["dataName"].drop_duplicates())
        # print(df["dataId"].drop_duplicates())
    
    def makePath(self) -> str:
        path = 'data/factor/year/factor-'
        strYear = str(self.year)
        strMonth = str(self.month)
        strStandardYear = str(self.standardYear)
        strName = encMd5(str(self.names))
        if len(strYear) > 0:
            path = path + f"-{strYear}"
        if len(strMonth) > 0:
            path = path + f"-{strMonth}"
        if len(strStandardYear) > 0:
            path = path + f"-{strStandardYear}"
        if len(strName) > 0:
            path = path + f"-{strName}"
        return path


class GetMarcapDayTask(BaseTask):
    """
    몽고디비에서 시가총액을 팩터 형태로 가져온다
    """
    markets = luigi.OptionalParameter("")
    date = luigi.OptionalParameter("")
    dataName = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")

    def requires(self):
        return {
            "GetStockDayTask": GetStockDayTask(date=self.date, targetPath=self.targetPath, markets=self.markets)
        }

    def run(self) -> Generator:
        path = self.makeDirs()
        indata = self.input()
        df = pd.read_hdf(indata["GetStockDayTask"].path)
        print(df)
        if not df.empty and len(self.dataName) > 0:
            newDf = pd.DataFrame()
            newDf["code"] = df["code"]
            newDf["date"] = df["date"]
            newDf["dataYear"] = df["date"].apply(lambda date: date[0:4])
            newDf["dataMonth"] = df["date"].apply(lambda date: date[4:6])
            newDf["dataDay"] = df["date"].apply(lambda date: date[6:8])
            newDf["dataName"] = self.dataName
            newDf["dataValue"] = df[self.dataName].apply(lambda num: float(num) if num.isnumeric() else 0)
            newDf["name"] = df["name"]
            newDf.to_hdf(path, key='df', mode='w')
        else:
            df.to_hdf(path, key='df', mode='w')
    
    def makePath(self) -> str:
        return f'data/marcap/day/GetMarcapDayTask-{self.date}-{self.dataName}-{encMd5(f"{self.markets}{pathToStr(self.targetPath)}")}'


class GetMarcapRangeTask(BaseTask):
    """
    몽고디비에서 시가총액을 팩터 형태로 가져온다
    """
    markets = luigi.OptionalParameter("")
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    dataName = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")

    def requires(self):
        return {
            "GetStockRangeTask": GetStockRangeTask(startDate=self.startDate, endDate=self.endDate, 
                targetPath=self.targetPath, markets=self.markets)
        }

    def run(self) -> Generator:
        path = self.makeDirs()
        indata = self.input()
        df = pd.read_hdf(indata["GetStockRangeTask"].path)
        if len(self.dataName) > 0:
            df[self.dataName] = pd.to_numeric(df[self.dataName], "coerce")
            newDf = pd.DataFrame()
            newDf["code"] = df["code"]
            newDf["date"] = df["date"]
            newDf["dataYear"] = df["date"].apply(lambda date: date[0:4])
            newDf["dataMonth"] = df["date"].apply(lambda date: date[4:6])
            newDf["dataDay"] = df["date"].apply(lambda date: date[6:8])
            newDf["dataName"] = self.dataName
            newDf["dataValue"] = df[self.dataName].apply(lambda num: float(num))
            newDf["name"] = df["name"]
            newDf.to_hdf(path, key='df', mode='w')
            print("df")
            print(df)
            print("newDf")
            print(newDf)
        else:
            df.to_hdf(path, key='df', mode='w')
    
    def makePath(self) -> str:
        return f'data/marcap/range/GetMarcapRangeTask-{self.startDate}-{self.endDate}-{self.dataName}-{encMd5(f"{self.markets}{pathToStr(self.targetPath)}")}'


class GetMarcapCodes(BaseTask):
    """
    달을 기준으로 시가총액데이터에서 종목코드를 가져온다
    """
    markets = luigi.OptionalParameter("")
    year = luigi.OptionalParameter("")
    month = luigi.OptionalParameter("")

    def makeQuery(self) -> Dict:
        query = {}
        markets = json.loads(self.markets)
        if len(markets) > 0:
            query["$or"] = list(map(lambda market: {"market": market}, markets))
        if len(self.year) > 0:
            month = ""
            if len(self.month) > 0:
                month = str(self.month).zfill(2)
            query["date"] = {"$regex": f"^{self.year}{month}", "$options": "i"}
        print(query)
        return query

    def run(self) -> Generator:
        path = self.makeDirs()
        target = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = target.get_collection()
        cursor = collection.distinct("code", self.makeQuery())
        df = pd.Series(list(cursor))
        df.to_hdf(path, key='df', mode='w')
        print(df)

    def makePath(self) -> str:

        result = hashlib.md5(f'{self.markets}'.encode())
        path = f'data/marcap/codes/GetMarcapCodes-{self.year}-{self.month}-{result.hexdigest()}'
        # year인수가 없는 경우는 현재 날짜 기준으로 validate가 필요
        if len(self.year) <= 0:
            path = path + getCurrentDate()
        return path


class GetStockCodeFilteringByFactorRankAndMinMax(BaseTask):
    """
    targets(종목 코드 리스트)에서 해당 팩터를 정렬하여 limit안의 Rank에 속한 종목코드 리스트를 반환한다(includeSame이 True일 경우 동점자도 포함이다)
    """
    date = luigi.OptionalParameter("")
    factors = luigi.OptionalParameter("")
    factorIds = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    isIncludeSame = luigi.BoolParameter(True)
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(float("inf"))

    def requires(self):
        year = int(self.date[:4])
        month = int(self.date[4:6])
        if month <= 4:
            factorTarget = GetFactorYearTask(year=str(year - 1), names=self.factors, dataIds=self.factorIds)
        else:
            factorTarget = GetFactorYearTask(year=str(year), names=self.factors, dataIds=self.factorIds)
        return {
            "GetFactorYearTask": factorTarget
        }

    def run(self) -> Generator:
        path = self.makeDirs()
        limit = int(self.limit)
        targets = pathToList(self.targetPath)
        indata = self.input()
        factorDf: pd.DataFrame = pd.read_hdf(indata["GetFactorYearTask"].path)
        if factorDf.empty:
            return
        newDf = factorDf[factorDf["code"].isin(targets)]
        newDf.sort_values(by="dataValue", ascending=self.isAscending, inplace=True)
        newDf = newDf[newDf["dataValue"]>=self.minValue]
        newDf = newDf[newDf["dataValue"]<=self.maxValue]

        if not self.isIncludeSame:
            newDf = newDf.iloc[0:int(limit)]
        else:
            newDf["rank"] = newDf["dataValue"].rank(method="min", ascending=self.isAscending)
            newDf = newDf[newDf["rank"] <= limit]
        newDf["code"].to_hdf(path, key='df', mode='w')
        # newDf.to_hdf(path, key='df', mode='w')
        print(newDf)
        print(path)

    def makePath(self) -> str:
        return f"data/simul/factor/GetStockCodeFilteringByFactorRank-{self.date}-{self.isAscending}-{self.isIncludeSame}-{self.limit}-{self.minValue}-{self.maxValue}-{encMd5(f'{self.factors}{self.markets}{pathToStr(self.targetPath)}')}"


class GetStockCodeFilteringByVarientRank(BaseTask):
    date = luigi.OptionalParameter("")
    beforeMonth = luigi.IntParameter(-12)
    targetPath = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    """
    해당 날짜를 기준으로 날짜범위의 종가의 분산 값이 낮은(isAscending=True 일 경우) 종목 리스트를 반환한다.
    """
    def requires(self):
        current: pd.Timestamp = strToDate(self.date)
        startDate = moveMonth(current, self.beforeMonth, current.day)
        endDate = current - pd.Timedelta(-1, "D")
        return {
            "marcapClose": GetMarcapRangeTask(dataName="close", startDate=dateToStr(startDate), endDate=dateToStr(endDate), markets=self.markets, targetPath=self.targetPath),
        }

    def run(self) -> None:
        path = self.makeDirs()
        indata = self.input()
        targets = pathToList(self.targetPath)
        dataDf = pd.read_hdf(indata["marcapClose"].path)
        dataDf: pd.DataFrame = dataDf[dataDf["code"].isin(targets)]
        dataDf = dataDf.pivot(index="date", columns="code", values="dataValue")
        raiseDf = (dataDf - dataDf.shift(1)).applymap(lambda val: abs(val))
        variencedf = dataDf.mean()/raiseDf.mean()
        variencedf = variencedf.sort_values(ascending=self.isAscending)
        result = list(variencedf.head(self.limit).index)
        pd.Series(result).to_hdf(path, key="df", mode="w")
    
    def makePath(self) -> str:
        return f"data/simul/stock/GetStockCodeFilteringByVarientRank-{self.date}-{self.beforeMonth}-{self.isAscending}-{self.limit}-{pathToStr(self.targetPath)}"


class GetStockCodeFilteringMarcapDataRankAndMinMax(BaseTask):
    """
    """
    date = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    dataName = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(-float("inf"))
    isIncludeSame = luigi.BoolParameter(True)

    def requires(self):
        return {
            "GetMarcapDayTask": GetMarcapDayTask(date=self.date, markets=self.markets, targetPath=self.targetPath, dataName=self.dataName)
        }
    
    def run(self):
        path = self.makeDirs()
        indata = self.input()
        df = pd.read_csv(indata["GetMarcapDayTask"].path)
        df.sort_values(["dataValue"], ascending=self.isAscending ,inplace=True)
        df = df[df["dataValue"]>=self.minValue]
        df = df[df["dataValue"]<=self.maxValue]

        if not self.isIncludeSame:
            df = df.iloc[0:self.limit]
        else:
            df["rank"] = df["dataValue"].rank(method="min", ascending=self.isAscending)
            df = df[df["rank"] <= self.limit]

        df.to_hdf(path, key="df", mode="w")
        print("df")

    
    def makePath(self):
        md5 = encMd5(f"{self.markets}{pathToStr(self.targetPath)}")
        return f"data/simul/stock/GetStockCodeFilteringMarcapDataRank-{self.date}-{self.dataName}-{self.isAscending}-{self.limit}-{self.minValue}-{self.maxValue}-{md5}"

class GetStockCodeFilteringAltmanZScore(BaseTask):
    """
    해당 날짜에대해서 AltmanZScore의 값을 구하고 minValue보다 높은 종목 리스트를 반환한다.
    """
    date = luigi.OptionalParameter("")
    minValue = luigi.FloatParameter(1.81)
    targetPath = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")

    def requires(self):
        year = int(self.date[:4])
        month = int(self.date[4:6])
        day = int(self.date[6:])
        if month <= 4:
            factorYear = str(year - 1)
        else:
            factorYear = str(year)
        return {
            "floatingAsset": GetFactorYearTask(year=(factorYear), names = json.dumps(["유동자산"]), exact=True),
            "floatingLiablilities": GetFactorYearTask(year=(factorYear), names=json.dumps(["유동부채"]), exact=True),
            "totalAsset": GetFactorYearTask(year=(factorYear), names=json.dumps(["자산"]), exact=True),
            "liablilities": GetFactorYearTask(year=(factorYear), names=json.dumps(["부채"]), exact=True),
            "retainedEarning": GetFactorYearTask(year=(factorYear), names=json.dumps(["이익잉여금"]), exact=True),
            "sales": GetFactorYearTask(year=(factorYear), names=json.dumps(["매출액"]), exact=True),
            "ebit": GetFactorYearTask(year=(factorYear), names=json.dumps(["ebit"]), exact=True),
            "marketValueOfEquity": GetMarcapDayTask(date=self.date, markets=self.markets, dataName="marcap", targetPath=self.targetPath),
        }


    def run(self) -> None:
        path = self.makeDirs()
        indata = self.input()
        targets = pathToList(self.targetPath)

        floatingAsset = pd.read_hdf(indata["floatingAsset"].path)
        floatingLiablilities = pd.read_hdf(indata["floatingLiablilities"].path)
        totalAsset = pd.read_hdf(indata["totalAsset"].path)
        liablilities = pd.read_hdf(indata["liablilities"].path)
        retainedEarning = pd.read_hdf(indata["retainedEarning"].path)
        sales = pd.read_hdf(indata["sales"].path)
        ebit = pd.read_hdf(indata["ebit"].path)
        marketValueOfEquity = pd.read_hdf(indata["marketValueOfEquity"].path)
        
        x1f1 = op(floatingAsset, floatingLiablilities, "-", "유동자산-유동부채")
        x1 = intersectCode(targets, op(x1f1, totalAsset, "/", "x1"))
        x2 = intersectCode(targets, op(retainedEarning, totalAsset, "/", "x2"))
        x3 = intersectCode(targets, op(ebit, totalAsset, "/", "x3"))
        x4 = intersectCode(targets, op(marketValueOfEquity, liablilities, "/", "x4"))
        x5 = intersectCode(targets, op(sales, totalAsset, "/", "x5"))

        x1["dataValue"] = x1["dataValue"] * 1.2
        x2["dataValue"] = x2["dataValue"] * 1.4
        x3["dataValue"] = x3["dataValue"] * 3.3
        x4["dataValue"] = x4["dataValue"] * 0.6
        x5["dataValue"] = x5["dataValue"] * 0.999

        altmanZ = op(x1, op(x2, op(x3, op(x4, x5, "+", "v1"), "+", "v2"), "+", "v3"), "+", "altmanZ")
        altmanZ = altmanZ[altmanZ["dataValue"]>=self.minValue]
        altmanZ["code"].to_hdf(path, key='df', mode='w')
        print(altmanZ)

        # x1 = (floatingAssetDf - floatingLiablilitiesDf) / totalAssetDf
        # x2 = retainedEarningDf / totalAssetDf
        # x3 = ebitDf / totalAssetDf
        # x4 = marketValueOfEquityDf / liablilitiesDf
        # x5 = salesDf / totalAssetDf
        # altmanZ = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
        # print(altmanZ)
    
    def makePath(self):
        return f"data/simul/factor/GetStockCodeFilteringAltmanZScore-{self.date}-{pathToStr(self.targetPath)}"


class GetStockCodeFilteringMarcapPerFactorRankMinMax(BaseTask):
    """
    CurValue * factor /
    targets(종목 코드 리스트)에서 해당 팩터를 정렬하여 limit안의 Rank에 속한 종목코드 리스트를 반환한다(includeSame이 True일 경우 동점자도 포함이다)
    """
    date = luigi.OptionalParameter("")
    factors = luigi.OptionalParameter("")
    factorIds = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    isIncludeSame = luigi.BoolParameter(True)
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(float("inf"))

    def requires(self):
        year = int(self.date[:4])
        month = int(self.date[4:6])
        if month <= 4:
            factorTarget = GetFactorYearTask(year=str(year - 1), names=self.factors, dataIds=self.factorIds)
        else:
            factorTarget = GetFactorYearTask(year=str(year), names=self.factors, dataIds=self.factorIds)
        return {
            "GetFactorYearTask": factorTarget,
            "GetMarcapDayTask": GetMarcapDayTask(date=self.date, markets=self.markets, dataName="marcap", targetPath=self.targetPath)
        }

    def run(self) -> Generator:
        path = self.makeDirs()
        limit = int(self.limit)
        targets = pathToList(self.targetPath)
        indata = self.input()
        factorDf: pd.DataFrame = pd.read_hdf(indata["GetFactorYearTask"].path)
        marcapDf: pd.DataFrame = pd.read_hdf(indata["GetMarcapDayTask"].path)
        if factorDf.empty or marcapDf.empty:
            pd.DataFrame([]).to_hdf(path, key='df', mode='w')
            return
        newDf = intersectCode(targets, op(marcapDf, factorDf, "/", "marcapPerFactor"))
        newDf.sort_values(by="dataValue", ascending=self.isAscending, inplace=True)
        newDf = newDf[newDf["dataValue"]>=self.minValue]
        newDf = newDf[newDf["dataValue"]<=self.maxValue]

        if not self.isIncludeSame:
            newDf = newDf.iloc[0:int(limit)]
        else:
            newDf["rank"] = newDf["dataValue"].rank(method="min", ascending=self.isAscending)
            newDf = newDf[newDf["rank"] <= limit]
        print(newDf)
        newDf["code"].to_hdf(path, key='df', mode='w')
        # newDf.to_hdf(path, key='df', mode='w')
        # print(newDf)
        # print(path)

    def makePath(self) -> str:
        return f"data/simul/factor/GetStockCodeFilteringMarcapPerFactorRankMinMax-{self.date}-{self.isAscending}-{self.isIncludeSame}-{self.limit}-{self.minValue}-{self.maxValue}-{encMd5(f'{self.factors}{self.markets}{pathToStr(self.targetPath)}')}"

class GetStockCodeFilteringFactorPerStockNumRankMinMax(BaseTask):
    """
    CurValue * factor /
    targets(종목 코드 리스트)에서 해당 팩터를 정렬하여 limit안의 Rank에 속한 종목코드 리스트를 반환한다(includeSame이 True일 경우 동점자도 포함이다)
    """
    date = luigi.OptionalParameter("")
    factors = luigi.OptionalParameter("")
    factorIds = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    isIncludeSame = luigi.BoolParameter(True)
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(float("inf"))

    def requires(self):
        year = int(self.date[:4])
        month = int(self.date[4:6])
        if month <= 4:
            factorTarget = GetFactorYearTask(year=str(year - 1), names=self.factors, dataIds=self.factorIds)
        else:
            factorTarget = GetFactorYearTask(year=str(year), names=self.factors, dataIds=self.factorIds)
        return {
            "GetFactorYearTask": factorTarget,
            "GetMarcapDayTask": GetMarcapDayTask(date=self.date, markets=self.markets, dataName="number", targetPath=self.targetPath)
        }

    def run(self) -> Generator:
        path = self.makeDirs()
        limit = int(self.limit)
        targets = pathToList(self.targetPath)
        indata = self.input()
        factorDf: pd.DataFrame = pd.read_hdf(indata["GetFactorYearTask"].path)
        marcapDf: pd.DataFrame = pd.read_hdf(indata["GetMarcapDayTask"].path)
        if factorDf.empty or marcapDf.empty:
            pd.DataFrame([]).to_hdf(path, key='df', mode='w')
            return
        newDf = intersectCode(targets, op(factorDf, marcapDf, "/", "FactorPerStockNum"))
        newDf.sort_values(by="dataValue", ascending=self.isAscending, inplace=True)
        newDf = newDf[newDf["dataValue"]>=self.minValue]
        newDf = newDf[newDf["dataValue"]<=self.maxValue]

        if not self.isIncludeSame:
            newDf = newDf.iloc[0:int(limit)]
        else:
            newDf["rank"] = newDf["dataValue"].rank(method="min", ascending=self.isAscending)
            newDf = newDf[newDf["rank"] <= limit]
        print(newDf)
        newDf["code"].to_hdf(path, key='df', mode='w')
        # newDf.to_hdf(path, key='df', mode='w')
        # print(newDf)
        # print(path)

    def makePath(self) -> str:
        return f"data/simul/factor/GetStockCodeFilteringFactorPerStockNumRankMinMax-{self.date}-{self.isAscending}-{self.isIncludeSame}-{self.limit}-{self.minValue}-{self.maxValue}-{encMd5(f'{self.factors}{self.markets}{pathToStr(self.targetPath)}')}"


class GetStockCodeFilteringMarcapDataMinMax(BaseTask):
    date = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    dataName = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    isIncludeSame = luigi.BoolParameter(True)
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(float("inf"))

    def requires(self):
        return {
            "GetMarcapDayTask": GetMarcapDayTask(date=self.date, markets=self.markets, dataName=self.dataName, targetPath=self.targetPath)
        }
    
    def run(self) -> Generator:
        path = self.makeDirs()
        limit = int(self.limit)
        targets = pathToList(self.targetPath)
        indata = self.input()
        marcapDf: pd.DataFrame = pd.read_hdf(indata["GetMarcapDayTask"].path)
        if marcapDf.empty:
            pd.DataFrame([]).to_hdf(path, key='df', mode='w')
            return
        newDf = marcapDf[marcapDf["code"].isin(targets)]
        newDf.sort_values(by="dataValue", ascending=self.isAscending, inplace=True)
        newDf = newDf[newDf["dataValue"]>=self.minValue]
        newDf = newDf[newDf["dataValue"]<=self.maxValue]

        if not self.isIncludeSame:
            newDf = newDf.iloc[0:int(limit)]
        else:
            newDf["rank"] = newDf["dataValue"].rank(method="min", ascending=self.isAscending)
            newDf = newDf[newDf["rank"] <= limit]
        print(newDf)
        newDf["code"].to_hdf(path, key='df', mode='w')