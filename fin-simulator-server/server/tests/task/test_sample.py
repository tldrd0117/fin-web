
from app.tasks.stockTasks import GetStockCodeFilteringByVarientRank, GetStockDayTask, GetMarcapCodes, GetStockCodeFilteringByFactorMinMax, GetStockCodeFilteringByFactorRank, GetStockCodeFilteringAltmanZScore
import luigi
import json
import pandas as pd


def test_dataframe() -> None:
    data = pd.DataFrame([1,1,1,1,2,2,2,2,3,3,3,3])
    data["rank"] = data.rank(method="min", ascending=True)
    print(data[data["rank"]<=6])
# poetry run python -m pytest -s

def test_GetMarcap() -> None:
    markets = json.dumps(["kospi", "kosdaq"])
    year = "2015"
    month = "11"
    task = GetMarcapCodes(markets=markets, year=year, month=month)
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
#     task = GetStockCodeFilteringAltmanZScore(date="20151123", targets=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)


# def test_GetStockDayTask() -> None:
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockDayTask(date="20151123", markets=markets, targets=test_GetMarcap())
#     luigi.build([task], workers=1, detailed_summary=True)


def test_GetStockCodeFilteringByVarientRank() -> None:
    markets = json.dumps(["kospi", "kosdaq"])
    task = GetStockCodeFilteringByVarientRank(date="20151123", markets=markets, targets=test_GetMarcap())
    luigi.build([task], workers=1, detailed_summary=True)



    
   
