
from time import sleep
from typing import Any, Dict, Generator, List
import luigi
from luigi.contrib.mongodb import MongoTarget
from pymongo import MongoClient
import pandas as pd
from dotenv import dotenv_values
import os
import json
import hashlib
import sys
from app.utils.dateutils import moveMonth
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
        return luigi.LocalTarget(self.makePath())
    
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
        return MongoCollectionTarget(client, self.index, self.collection)


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
        return f'data/stock/month/stock-marcap-{self.market}-{self.year}-{self.month}'


class GetStockDayTask(BaseTask):
    """
    몽고디비에서 일을 기준으로 시가총액 데이터를 가져온다
    """
    date = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")

    def makeQuery(self) -> Dict:
        query = {"$and":[]}
        markets = json.loads(self.markets)
        if len(markets) > 0:
            query["$and"].append({"$or":list(map(lambda market: {"market": market}, markets))})
        query["$and"].append({"date":self.date})
        print(query)
        return query

    def run(self) -> Generator:
        path = self.makeDirs()
        targets = pathToList(self.targetPath)
        client = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = client.get_collection()
        cursor = collection.find(self.makeQuery())
        df = pd.DataFrame(list(cursor))
        df["_id"] = df["_id"].astype(str)
        df = df[df["code"].isin(targets)]
        df.to_hdf(path, key='df', mode='w')
        print(df)

    def makePath(self) -> str:
        return f'data/stock/day/GetStockDayTask-{self.date}-{encMd5(f"{self.markets}{pathToStr(self.targetPath)}")}'


class GetStockRangeTask(BaseTask):
    """
    몽고디비에서 한달을 기준으로 시가총액 데이터를 가져온다
    """
    startDate = luigi.OptionalParameter("")
    endDate = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    targetJson = luigi.OptionalParameter("")

    def run(self) -> Generator:
        path = self.makeDirs()
        if len(self.targetJson) > 0:
            targets = json.loads(self.targetJson)
        else:
            targets = pathToList(self.targetPath)
        markets = json.loads(self.markets)
        client = yield MongoGetCollectionTask(index="stock", collection="marcap")
        collection = client.get_collection()
        cursor = collection.find({
            "$and": [{
                        "date": {"$gte": self.startDate, "$lte": self.endDate}
                }, 
                {
                    "$or": list(map(lambda market: {"market": market}, markets))
                },
                
            ]
        })
        df = pd.DataFrame(list(cursor))
        df = df[df["code"].isin(targets)]
        df["_id"] = df["_id"].astype(str)
        df.to_hdf(path, key='df', mode='w')
        print(df)
    
    def makePath(self) -> str:
        return f'data/stock/range/GetStockRangeTask-{self.startDate}-{self.endDate}-{encMd5(f"{self.markets}{pathToStr(self.targetPath)}")}'


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
        return f""


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
        print(df)
        # errors를 coerce로 하면 숫자로 못바꾸는 항목은 NaN으로 설정
        df["_id"] = df["_id"].astype(str)
        df["createdAt"] = df["createdAt"].astype(str)
        df["updatedAt"] = df["updatedAt"].astype(str)
        df["dataValue"] = pd.to_numeric(df["dataValue"], errors="coerce")
        df.dropna(subset=['dataValue'])
        df.to_hdf(path, key='df', mode='w')
        print(df["dataName"].drop_duplicates())
        print(df["dataId"].drop_duplicates())
    
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
        if len(self.dataName) > 0:
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
        return f'data/marcap/codes/GetMarcapCodes-{self.year}-{self.month}-{result.hexdigest()}'


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

#
class GetFilteringMarcapDataPerFactor(BaseTask):
    date = luigi.OptionalParameter("")
    markets = luigi.OptionalParameter("")
    type1 = luigi.OptionalParameter("")
    type2 = luigi.OptionalParameter("")
    dataName1 = luigi.OptionalParameter("")
    dataName2 = luigi.OptionalParameter("")
    op = luigi.OptionalParameter("")
    targetPath = luigi.OptionalParameter("")
    isAscending = luigi.BoolParameter(True)
    limit = luigi.IntParameter(sys.maxsize)
    minValue = luigi.FloatParameter(-float("inf"))
    maxValue = luigi.FloatParameter(-float("inf"))
    isIncludeSame = luigi.BoolParameter(True)


    def getTask(self, type, dataName):
        data = None
        if type == "marcap":
            data = GetMarcapDayTask(date=self.date, markets=self.markets, targetPath=self.targetPath, dataName=dataName)
        elif type == "factor":
            year = int(self.date[:4])
            month = int(self.date[4:6])
            dataNameArr = json.dumps([dataName])
            if month <= 4:
                data = GetFactorYearTask(year=str(year - 1), names=dataNameArr, dataIds=dataNameArr)
            else:
                data = GetFactorYearTask(year=str(year), names=dataNameArr, dataIds=dataNameArr)
        return data

    def requires(self):
        return {
            "data1": self.getTask(self.type1, self.dataName1),
            "data2": self.getTask(self.type2, self.dataName2),
        }
    
    def run(self):
        path = self.makeDirs()
        indata = self.input()
    
    def makePath(self):
        md5 = encMd5(f"{self.markets}{pathToStr(self.targetPath)}")
        return f"data/simul/factor/GetFilteringMarcapDataPerFactor-{self.date}-{self.type1}-{self.dataName1}-{self.op}-{self.type2}-{self.dataName2}-{md5}"


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
            "floatingAsset": GetFactorYearTask(year=(factorYear), name="유동자산", exact=True),
            "floatingLiablilities": GetFactorYearTask(year=(factorYear), name="유동부채", exact=True),
            "totalAsset": GetFactorYearTask(year=(factorYear), name="자산", exact=True),
            "liablilities": GetFactorYearTask(year=(factorYear), name="부채", exact=True),
            "retainedEarning": GetFactorYearTask(year=(factorYear), name="이익잉여금", exact=True),
            "sales": GetFactorYearTask(year=(factorYear), name="매출액", exact=True),
            "ebit": GetFactorYearTask(year=(factorYear), name="ebit", exact=True),
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

        # x1 = (floatingAssetDf - floatingLiablilitiesDf) / totalAssetDf
        # x2 = retainedEarningDf / totalAssetDf
        # x3 = ebitDf / totalAssetDf
        # x4 = marketValueOfEquityDf / liablilitiesDf
        # x5 = salesDf / totalAssetDf
        # altmanZ = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
        # print(altmanZ)
    
    def makePath(self):
        return f"data/simul/factor/GetStockCodeFilteringAltmanZScore-{self.date}-{pathToStr(self.targetPath)}"
