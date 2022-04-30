
from app.tasks.stockTasks import GetStockRangeTask
import luigi
import json
import pandas as pd

import matplotlib.font_manager as fm
import platform
import matplotlib.pyplot as plt

# poetry run python -m pytest -s tests/test_graph.py

def test_GetMarcapData() -> None:
    pd.set_option('display.float_format', str)
    markets = json.dumps(["kospi"])
    startDate = "20180101"
    endDate = "20190101"
    targetJson =  json.dumps(["005930"])
    task = GetStockRangeTask(markets=markets, startDate=startDate, endDate=endDate, targetJson=targetJson)
    luigi.build([task], workers=1, detailed_summary=True)
    path = task.output().path
    result = pd.read_hdf(path)

    result["date"] = pd.to_datetime(result["date"])
    result.replace("", float("NaN"), inplace=True)
    result.dropna(subset = ["close"], inplace=True)   
    result["close"] = result["close"].astype(int)
    result =result[["date", "close"]]
    result = result.set_index("date")
    print(result)
    # print(result.shift(1))

    # if platform.system()=='Darwin':
    #     path = '/Library/Fonts/Arial Unicode.ttf'
    # else:
    #     path = 'C:/Windows/Fonts/malgun.ttf'

    # print(result)

    # plot = result.plot(figsize = (18,12), fontsize=12)
    # fontProp = fm.FontProperties(fname=path, size=18)
    # plot.legend(prop=fontProp)
    # plt.show()

