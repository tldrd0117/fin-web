
from app.tasks.stockTasks import GetStockRangeTask, GetSeibroDividendTask, GetSeibroStockNumTask, GetAdjustedStockRangeTask, GetMarcapCodes
import luigi
import json
import pandas as pd

import matplotlib.font_manager as fm
import platform
import matplotlib.pyplot as plt

# poetry run python -m pytest -s tests/test_graph.py

# def test_seibroStockNum() -> None:
#     startDate = "20180101"
#     endDate = "20190101"
#     targetJson =  json.dumps(["005930"])
#     task = GetSeibroStockNumTask(startDate=startDate, endDate=endDate, targetJson=targetJson)
#     luigi.build([task], workers=1, detailed_summary=True)
#     path = task.output().path
#     result = pd.read_hdf(path)
#     print(result)


# def test_seibroDiviend() -> None:
#     startDate = "20180101"
#     endDate = "20190101"
#     targetJson =  json.dumps(["005930"])
#     task = GetSeibroDividendTask(startDate=startDate, endDate=endDate, targetJson=targetJson)
#     luigi.build([task], workers=1, detailed_summary=True)
#     path = task.output().path
#     result = pd.read_hdf(path)
#     print(result)

def getMarcap() -> None:
    markets = json.dumps(["kospi", "kosdaq"])
    year = "2018"
    month = "01"
    task = GetMarcapCodes(markets=markets, year=year, month=month)
    luigi.build([task], workers=1, detailed_summary=True)
    path = task.output().path
    result = pd.read_hdf(path).to_list()
    return path

def test_GetMergedStockRangTask() -> None:
    pd.set_option('display.float_format', str)
    markets = json.dumps(["kospi"])
    startDate = "20180101"
    endDate = "20190101"
    # targetJson =  json.dumps(["005930", "005380"])
    # targetJson =  json.dumps(["005380"])
    task = GetAdjustedStockRangeTask(markets=markets, startDate=startDate, endDate=endDate, targetPath=getMarcap())
    luigi.build([task], workers=1, detailed_summary=True)
    path = task.output().path
    result = pd.read_hdf(path)
    print(path)
    print(result)

def load():
    import pandas as pd
    pd.read_hdf("../data/stock/range/GetMergedStockRangTask-20180101-20190101-2188a9192d42c6a47f0d46bcb9e4de73")

# def test_GetMarcapData() -> None:
#     pd.set_option('display.float_format', str)
#     markets = json.dumps(["kospi"])
#     startDate = "20180101"
#     endDate = "20190101"
#     targetJson =  json.dumps(["005930"])
#     task = GetStockRangeTask(markets=markets, startDate=startDate, endDate=endDate, targetJson=targetJson)
#     luigi.build([task], workers=1, detailed_summary=True)
#     path = task.output().path
#     result = pd.read_hdf(path)

#     result["date"] = pd.to_datetime(result["date"])
#     result.replace("", float("NaN"), inplace=True)
#     result.dropna(subset = ["close"], inplace=True)   
#     result["close"] = result["close"].astype(int)
#     result =result[["date", "close"]]
#     result = result.set_index("date")
#     print(result)
#     # print(result.shift(1))

#     # if platform.system()=='Darwin':
#     #     path = '/Library/Fonts/Arial Unicode.ttf'
#     # else:
#     #     path = 'C:/Windows/Fonts/malgun.ttf'

#     # print(result)

#     # plot = result.plot(figsize = (18,12), fontsize=12)
#     # fontProp = fm.FontProperties(fname=path, size=18)
#     # plot.legend(prop=fontProp)
#     # plt.show()

