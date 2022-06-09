
from app.tasks.stockTasks import GetStockCodeFilteringByVarientRank, GetStockDayTask, GetMarcapCodes, GetStockCodeFilteringByFactorRankAndMinMax, GetStockCodeFilteringAltmanZScore, GetStockCodeFilteringMarcapPerFactorRankMinMax
import luigi
import json
import pandas as pd
from app.utils.dateutils import getDateArr

# poetry run python -m pytest -s tests/test_sample.py

def test_dataframe() -> None:
    data = pd.DataFrame([1,1,1,1,2,2,2,2,3,3,3,3])
    data["rank"] = data.rank(method="min", ascending=True)
    print(data[data["rank"]<=6])

def test_GetMarcap() -> None:
    markets = json.dumps(["kospi", "kosdaq"])
    year = "2015"
    month = "11"
    # task = GetMarcapCodes(markets=markets, year=year, month=month)
    task = GetMarcapCodes(markets=markets)
    luigi.build([task], workers=1, detailed_summary=True)
    path = task.output().path
    result = pd.read_hdf(path).to_list()
    return path


# def test_GetStockCodeFilteringByFactorMinMax() -> None:
#     date = "201511"
#     factor = "영업활동"
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringByFactorMinMax(date=date, factor=factor, markets=markets, minValue=0, targets=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)
#     resultDf = pd.read_hdf(task.output().path)
#     result = resultDf["code"].to_list()
#     assert 1291 == len(result)


# def test_GetStockCodeFilteringByFactorRank() -> None:
#     date = "201511"
#     factor = "영업활동"
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringByFactorRank(date=date, factor=factor, markets=markets, ascending=False, limit=50, targets=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)
#     resultDf = pd.read_hdf(task.output().path)
#     result = resultDf["code"].to_list()
#     print(resultDf)
#     print(result)


# def test_GetStockCodeFilteringAltmanZScore() -> None:
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringAltmanZScore(date="20151123", targetPath=test_GetMarcap(), markets=markets)
#     luigi.build([task], workers=1, detailed_summary=True)


# def test_GetStockDayTask() -> None:
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockDayTask(date="20151123", markets=markets, targets=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)


# def test_GetStockCodeFilteringByVarientRank() -> None:
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringByVarientRank(date="20151123", markets=markets, targets=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)

# def test_GetStockCodeFilteringByFactorRankAndMinMax() -> None:
#     date = "20151101"
#     factors = json.dumps(["영업활동으로인한현금흐름"])
#     factorIds = json.dumps(["ifrs-full_CashFlowsFromUsedInOperatingActivities"])
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringByFactorRankAndMinMax(date=date,
#         factors=factors,
#         factorIds=factorIds, 
#         markets=markets, 
#         isAscending=False, 
#         # limit=50, 
#         targetPath=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)
#     resultDf = pd.read_hdf(task.output().path)
#     result = resultDf["code"].to_list()
#     print(resultDf)
#     print(result)
#     print(len(result))

def test_GetStockCodeFilteringMarcapPerFactorRankMinMax() -> None:
    date = "20151123"
    factors = json.dumps(["영업활동으로인한현금흐름"])
    factorIds = json.dumps(["ifrs-full_CashFlowsFromUsedInOperatingActivities"])
    markets = json.dumps(["kospi", "kosdaq"])
    task = GetStockCodeFilteringMarcapPerFactorRankMinMax(date=date,
        factors=factors,
        factorIds=factorIds, 
        markets=markets, 
        isAscending=True,
        limit=50,
        minValue=0,
        targetPath=test_GetMarcap())
    luigi.build([task], workers=1, detailed_summary=True)
    resultDf = pd.read_hdf(task.output().path)
    # result = resultDf["code"].to_list()
    print(resultDf)
    # print(result)
    print(len(resultDf))



    
   
