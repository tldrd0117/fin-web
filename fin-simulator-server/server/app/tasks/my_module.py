
from time import sleep
from typing import Dict, Generator, List
import luigi
from luigi.contrib.mongodb import MongoTarget
from pymongo import MongoClient
import pandas as pd
from dotenv import dotenv_values
import os
import json

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
        return luigi.LocalTarget(self.makePath())
    
    def makePath(self) -> str:
        pass

    def makeDirs(self) -> str:
        path = self.makePath()
        normpath = os.path.normpath(path)
        parentfolder = os.path.dirname(normpath)
        if parentfolder:
            try:
                os.makedirs(parentfolder)
            except OSError:
                pass
        return path


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
    index = luigi.OptionalParameter("")
    collection = luigi.OptionalParameter("")

    def output(self) -> MongoCollectionTarget:
        host = config["mongodbHost"]
        port = config["mongodbPort"]
        userName = config["mongodbUserName"]
        password = config["mongodbPassword"]
        path = f'mongodb://{userName}:{password}@{host}:{port}'
        client = MongoClient(path)
        return MongoCollectionTarget(client, self.index, self.collection)


class GetStockMonthTask(BaseTask):
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
        df.to_hdf(path, key='df', mode='w')
        print(df)
    
    def makePath(self) -> str:
        return f'data/stock/month/stock-marcap-{self.market}-{self.year}-{self.month}'


class GetStockRangeTask(BaseTask):
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    market = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        target = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = target.get_collection()
        cursor = collection.find({"$and": [{"date": {"$gte": self.startDate, "$lte": self.endDate}}, {"market": self.market}]})
        df = pd.DataFrame(list(cursor))
        df.to_hdf(path, key='df', mode='w')
        print(df)

    def makePath(self) -> str:
        return f'data/stock/range/stock-marcap-{self.market}-{self.startDate}-{self.endDate}'


class GetFactorYearTask(BaseTask):
    year = luigi.OptionalParameter("")
    month = luigi.OptionalParameter("12")
    name = luigi.OptionalParameter("")

    def makeAndQuery(self) -> List:
        query = []
        if len(self.year) > 0:
            query.append({
                "dataYear": "{:.1f}".format(int(self.year))
            })
        if len(self.month) > 0:
            query.append({
                "dataMonth": self.month
            })
        if len(self.name) > 0:
            query.append({
                "dataName": {"$regex": self.name}
            })
        print(query)
        return query

    def run(self) -> Generator:
        path = self.makeDirs()
        target = yield MongoGetCollectionTask(index="stock", collection="factor")
        collection = target.get_collection()
        cursor = collection.find({"$and": self.makeAndQuery()})
        
        df = pd.DataFrame(list(cursor))
        # errors를 coerce로 하면 숫자로 못바꾸는 항목은 NaN으로 설정
        df["dataValue"] = pd.to_numeric(df["dataValue"], errors="coerce")
        df.dropna(subset=['dataValue'])
        df.to_hdf(path, key='df', mode='w')
        print(df)
    
    def makePath(self) -> str:
        path = 'data/factor/fnguide/year/factor-fnguide'
        strYear = str(self.year)
        strMonth = str(self.month)
        strName = str(self.name)
        if len(strYear) > 0:
            path = path + f"-{strYear}"
        if len(strMonth) > 0:
            path = path + f"-{strMonth}"
        if len(strName) > 0:
            path = path + f"-{strName}"
        return path


class GetMarcap(BaseTask):
    market = luigi.OptionalParameter("")
    year = luigi.OptionalParameter("")
    month = luigi.OptionalParameter("")

    def makeQuery(self) -> Dict:
        query = {}
        if len(self.market) > 0:
            query["market"] = self.market
        if len(self.year) > 0:
            month = ""
            if len(self.month) > 0:
                month = str(self.month).zfill(2)
            query["date"] = {"$regex": f"^{self.year}{month}", "$options": "i"}
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
        return f'data/marcap/month/marcap-{self.market}-{self.year}-{self.month}'


class GetStockFilteredByFactor(BaseTask):
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    factor = luigi.OptionalParameter("")
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(float("inf"))
    market = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        startYear = int(self.startDate[:4])
        startMonth = int(self.startDate[4:6])
        endYear = int(self.endDate[:4])
        endMonth = int(self.endDate[4:6])
        markets = json.loads(self.market)

        for market in markets:
            for year in range(startYear, endYear + 1):
                print(str(year))
                yStartMonth = 1
                yEndMonth = 12
                if year == startYear:
                    yStartMonth = startMonth
                if year == endYear:
                    yEndMonth = endMonth
                factorTarget = yield GetFactorYearTask(year=year, name=self.factor)
                factorDf: pd.DataFrame = pd.read_hdf(factorTarget.path)
                if factorDf.empty:
                    continue
                for month in range(yStartMonth, yEndMonth + 1):
                    target = yield GetMarcap(market=market, year=int(year), month=month)
                    marcapDf = pd.read_hdf(target.path).tolist()
                    newDf = factorDf[factorDf["code"].isin(marcapDf)]
                    filteredDf = newDf[newDf["dataValue"] >= self.minValue]
                    filteredDf = filteredDf[filteredDf["dataValue"] <= self.maxValue]
                    print(filteredDf)

    def makePath(self) -> str:
        return f"data/simul/factor/GetStockFilteredByFactor-{self.startDate}-{self.endDate}-{self.factor}-{self.minValue}-{self.maxValue}"
    
