import luigi
from app.tasks.stockTasks import GetStockCodeFilteringAltmanZScore, GetMarcapCodes,\
    GetStockCodeFilteringByVarientRank, GetStockCodeFilteringByFactorRankAndMinMax
import json
import pandas as pd

class TaskService:
    def __init__(self) -> None:
        pass

    def simulate(self, date: str):
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]

        markets = json.dumps(["kospi", "kosdaq"])
        task = GetMarcapCodes(markets=markets, year=year, month=month)
        luigi.build([task], workers=1, detailed_summary=True)
        targetPath = task.outputOfPath()

        task = GetStockCodeFilteringAltmanZScore(date=date, targetPath=targetPath, markets=markets)
        luigi.build([task], workers=1, detailed_summary=True)
        targetPath = task.outputOfPath()

        factors = json.dumps(["roe"])
        markets = json.dumps(["kospi", "kosdaq"])
        task = GetStockCodeFilteringByFactorRankAndMinMax(date=date,
            factors=factors,
            markets=markets, 
            isAscending=False,
            limit=3000,
            minValue=0.00000001,
            targetPath=targetPath)
        luigi.build([task], workers=1, detailed_summary=True)
        targetPath = task.outputOfPath()

        factors = json.dumps(["영업이익률"])
        markets = json.dumps(["kospi", "kosdaq"])
        task = GetStockCodeFilteringByFactorRankAndMinMax(date=date,
            factors=factors,
            markets=markets, 
            isAscending=False,
            limit=3000,
            minValue=0.00000001,
            targetPath=targetPath)
        luigi.build([task], workers=1, detailed_summary=True)
        targetPath = task.outputOfPath()

        factors = json.dumps(["ebit"])
        markets = json.dumps(["kospi", "kosdaq"])
        task = GetStockCodeFilteringByFactorRankAndMinMax(date=date,
            factors=factors,
            markets=markets, 
            isAscending=False,
            limit=3000,
            minValue=0.00000001,
            targetPath=targetPath)
        luigi.build([task], workers=1, detailed_summary=True)
        targetPath = task.outputOfPath()

        factors = json.dumps(["당기순이익률"])
        markets = json.dumps(["kospi", "kosdaq"])
        task = GetStockCodeFilteringByFactorRankAndMinMax(date=date,
            factors=factors,
            markets=markets, 
            isAscending=False,
            limit=3000,
            minValue=3,
            targetPath=targetPath)
        luigi.build([task], workers=1, detailed_summary=True)
        targetPath = task.outputOfPath()
        targets = task.outputOfList()
        print(targets)
        print(len(targets))

        markets = json.dumps(["kospi", "kosdaq"])
        task = GetStockCodeFilteringByVarientRank(date=date,
            limit=1000,
            isAscending=True,
            markets=markets, 
            targetPath=targetPath)
        luigi.build([task], workers=1, detailed_summary=True)
        targets = task.outputOfList()
        print(targets)
        print(len(targets))


        
