
from app.tasks.stockTasks import GetMarcapCodes, GetStockCodeFilteringByFactorMinMax, GetStockCodeFilteringByFactorRank, GetStockFilteringAltmanZScore
import luigi
import json
import pandas as pd


# def test_dataframe() -> None:
#     data = pd.DataFrame([1,1,1,1,2,2,2,2,3,3,3,3])
#     data["rank"] = data.rank(method="min", ascending=True)
#     print(data[data["rank"]<=6])
# poetry run python -m pytest -s

# def test_GetMarcap() -> None:
#     markets = json.dumps(["kospi", "kosdaq"])
#     year = "2015"
#     month = "11"
#     task = GetMarcapCodes(markets=markets, year=year, month=month)
#     luigi.build([task], workers=1, detailed_summary=True)
#     result = pd.read_hdf(task.output().path).to_list()
#     assert 2020 == len(result)


# def test_GetStockCodeFilteringByFactorMinMax() -> None:
#     date = "201511"
#     factor = "영업활동"
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringByFactorMinMax(date=date, factor=factor, markets=markets, minValue=0)
#     luigi.build([task], workers=1, detailed_summary=True)
#     resultDf = pd.read_hdf(task.output().path)
#     result = resultDf["code"].to_list()
#     assert 1291 == len(result)


# def test_GetStockCodeFilteringByFactorRank() -> None:
#     date = "201511"
#     factor = "영업활동"
#     markets = json.dumps(["kospi", "kosdaq"])
#     task = GetStockCodeFilteringByFactorRank(date=date, factor=factor, markets=markets, ascending=False, limit=50)
#     luigi.build([task], workers=1, detailed_summary=True)
#     resultDf = pd.read_hdf(task.output().path)
#     result = resultDf["code"].to_list()
#     print(resultDf)
#     print(result)


# def test_FactorOperation() -> None:
#     year1 = "2015"
#     year2 = "2016"
#     factor1 = "영업"
#     factor2 = "영업"
#     operation = "+"
#     task = FactorOperation(year1=year1, year2=year2, factor1=factor1, factor2=factor2, operation=operation)
#     luigi.build([task], workers=1, detailed_summary=True)
#     resultDf = pd.read_hdf(task.output().path)


def test_GetStockFilteringAltmanZScore() -> None:
    markets = json.dumps(["kospi", "kosdaq"])
    year = "2015"
    month = "11"
    task = GetMarcapCodes(markets=markets, year=year, month=month)
    luigi.build([task], workers=1, detailed_summary=True)
    result = pd.read_hdf(task.output().path).to_list()

    task = GetStockFilteringAltmanZScore(date="20151123", targets=json.dumps(result))
    luigi.build([task], workers=1, detailed_summary=True)


    
   
