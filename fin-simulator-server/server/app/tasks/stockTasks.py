
from time import sleep
from typing import Dict, Generator, List
import luigi
from luigi.contrib.mongodb import MongoTarget
from pymongo import MongoClient
import pandas as pd
from dotenv import dotenv_values
import os
import json
import hashlib
import sys
from app.utils.factorutils import op, intersectCode


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
    exact = luigi.BoolParameter(False)

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
            if self.exact:
                query.append({
                    "dataName": self.name
                })
            else:
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
        df["_id"] = df["_id"].astype(str)
        df["createdAt"] = df["createdAt"].astype(str)
        df["updatedAt"] = df["updatedAt"].astype(str)
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


class GetMarcapData(BaseTask):
    markets = luigi.OptionalParameter("")
    year = luigi.OptionalParameter("")
    month = luigi.OptionalParameter("")
    day = luigi.OptionalParameter("")
    dataName = luigi.OptionalParameter("")

    def makeQuery(self) -> Dict:
        query = {}
        markets = json.loads(self.markets)
        if len(markets) > 0:
            query["$or"] = list(map(lambda market: {"market": market}, markets))
        if len(self.month) > 0:
            month = str(self.month).zfill(2)
        if len(self.month) > 0:
            day = str(self.day).zfill(2)
        query["date"] = {"$regex": f"^{self.year}{month}{day}", "$options": "i"}
        print(query)
        return query

    def run(self) -> Generator:
        path = self.makeDirs()
        target = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = target.get_collection()
        cursor = collection.find(self.makeQuery())
        df = pd.DataFrame(list(cursor))
        if len(self.dataName) > 0:
            newDf = pd.DataFrame()
            newDf["code"] = df["code"]
            newDf["dataYear"] = df["date"].apply(lambda date: date[0:4])
            newDf["dataMonth"] = df["date"].apply(lambda date: date[4:6])
            newDf["dataDay"] = df["date"].apply(lambda date: date[6:8])
            newDf["dataName"] = self.dataName
            newDf["dataValue"] = df["marcap"].apply(lambda num: float(num))
            newDf["name"] = df["name"]
            newDf.to_hdf(path, key='df', mode='w')
        else:
            df.to_hdf(path, key='df', mode='w')
    
    def makePath(self) -> str:
        result = hashlib.md5(f'{self.markets}'.encode())
        return f'data/marcap/day/GetMarcapData-{self.year}-{self.month}-{self.day}-{self.dataName}-{result.hexdigest()}'


class GetMarcapCodes(BaseTask):
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
        return f'data/marcap/codes/GetMarcapCodes-{self.year}-{self.month}-{result.hexdigest()}'


class GetStockCodeFilteringByFactorMinMax(BaseTask):
    date = luigi.OptionalParameter("")
    factor = luigi.OptionalParameter("")
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(float("inf"))
    markets = luigi.OptionalParameter("")
    targets = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        year = int(self.date[:4])
        month = int(self.date[4:6])
        markets = json.loads(self.markets)
        if len(self.targets) > 0:
            targets = json.loads(self.targets)
        marcapOutput = yield GetMarcapCodes(markets=self.markets, year=int(year), month=month)
        targets = pd.read_hdf(marcapOutput.path).to_list()

        factorTarget = None
        if month <= 4:
            factorTarget = yield GetFactorYearTask(year=str(year - 1), name=self.factor)
        else:
            factorTarget = yield GetFactorYearTask(year=str(year), name=self.factor)
        factorDf: pd.DataFrame = pd.read_hdf(factorTarget.path)
        if factorDf.empty:
            return
        newDf = factorDf[factorDf["code"].isin(targets)]
        filteredDf = newDf[newDf["dataValue"] >= self.minValue]
        filteredDf = filteredDf[filteredDf["dataValue"] <= self.maxValue]
        filteredDf.to_hdf(path, key='df', mode='w')
        print(filteredDf)
        print(path)

    def makePath(self) -> str:
        result = hashlib.md5(f'{self.targets}'.encode())
        return f"data/simul/factor/GetStockFilteredByFactor-{self.date}-{self.factor}-{self.minValue}-{self.maxValue}-{result.hexdigest()}"


class GetStockCodeFilteringByFactorRank(BaseTask):
    date = luigi.OptionalParameter("")
    factor = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targets = luigi.OptionalParameter("")
    ascending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    includeSame = luigi.BoolParameter(True)

    def run(self) -> Generator:
        path = self.makeDirs()
        year = int(self.date[:4])
        month = int(self.date[4:6])
        markets = json.loads(self.markets)
        limit = int(self.limit)
        if len(self.targets) > 0:
            targets = json.loads(self.targets)
        marcapOutput = yield GetMarcapCodes(markets=self.markets, year=int(year), month=month)
        targets = pd.read_hdf(marcapOutput.path).to_list()

        factorTarget = None
        if month <= 4:
            factorTarget = yield GetFactorYearTask(year=str(year - 1), name=self.factor)
        else:
            factorTarget = yield GetFactorYearTask(year=str(year), name=self.factor)
        factorDf: pd.DataFrame = pd.read_hdf(factorTarget.path)
        if factorDf.empty:
            return
        newDf = factorDf[factorDf["code"].isin(targets)]
        newDf.sort_values(by="dataValue", ascending=self.ascending, inplace=True)
        if not self.includeSame:
            newDf = newDf.iloc[0:int(limit)]
        else:
            newDf["rank"] = newDf["dataValue"].rank(method="min", ascending=self.ascending)
            newDf = newDf[newDf["rank"] <= limit]
            
        newDf.to_hdf(path, key='df', mode='w')
        print(newDf)
        print(path)

    def makePath(self) -> str:
        result = hashlib.md5(f'{self.markets}{self.targets}'.encode())
        return f"data/simul/factor/GetStockCodeFilteringByFactorRank-{self.date}-{self.factor}-{self.ascending}-{self.limit}-{result.hexdigest()}"


class GetStockFilteringAltmanZScore(BaseTask):
    date = luigi.OptionalParameter("")
    targets = luigi.OptionalParameter("")

    def requires(self):
        year = int(self.date[:4])
        month = int(self.date[4:6])
        day = int(self.date[6:])
        markets = json.dumps(["kospi", "kosdaq"])
        if month <= 4:
            factorYear = str(year - 1)
        else:
            factorYear = str(year)
        return {
            "floatingAsset": GetFactorYearTask(year=(factorYear), name="유동자산", exact=True),
            "floatingLiablilities": GetFactorYearTask(year=(factorYear), name="유동부채", exact=True),
            "totalAsset": GetFactorYearTask(year=(factorYear), name="자산", exact=True),
            "liablilities": GetFactorYearTask(year=(factorYear), name="부채", exact=True),
            "retainedEarning": GetFactorYearTask(year=(factorYear), name="이익잉여금", exact=True),
            "sales": GetFactorYearTask(year=(factorYear), name="매출액", exact=True),
            "ebit": GetFactorYearTask(year=(factorYear), name="ebit", exact=True),
            "marketValueOfEquity": GetMarcapData(year=str(year), month=str(month), day=str(day), markets=markets, dataName="marcap")
        }


    def run(self) -> None:
        indata = self.input()
        targets = json.loads(self.targets)

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
        print(altmanZ)

        # x1 = (floatingAssetDf - floatingLiablilitiesDf) / totalAssetDf
        # x2 = retainedEarningDf / totalAssetDf
        # x3 = ebitDf / totalAssetDf
        # x4 = marketValueOfEquityDf / liablilitiesDf
        # x5 = salesDf / totalAssetDf
        # altmanZ = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
        # print(altmanZ)
    
    def makePath(self):
        result = hashlib.md5(f'{self.targets}'.encode())
        return f"data/simul/factor/GetStockFilteringAltmanZScore-{self.date}-{result.hexdigest()}"
