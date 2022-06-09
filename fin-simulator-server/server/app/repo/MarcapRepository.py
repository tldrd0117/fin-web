import json
from typing import List
import pandas as pd
import luigi
from app.tasks.stockTasks import GetAdjustedStockRangeTask, GetMarcapCodes
from app.utils.dateutils import getCurrentDate

class MarcapRepository(object):
    marcapDf: pd.DataFrame
    def __init__(self) -> None:
        pass
        # self.loadInit()
    
    def loadInit(self) -> None:
        markets = json.dumps(["kospi", "kosdaq"])
        task = GetAdjustedStockRangeTask(startDate="19700101", endDate=getCurrentDate(),\
            markets=markets, targetPath=self.getMarcapCodePath())
        luigi.build([task], workers=8, detailed_summary=True)
        self.marcapDf: pd.DataFrame = task.outputOfpd()
    

    def getMarcapCodePath(self):
        markets = json.dumps(["kospi", "kosdaq"])
        task = GetMarcapCodes(markets=markets)
        luigi.build([task], workers=1, detailed_summary=True)
        path = task.output().path
        return path
    

    def getMarcapByDate(self, date: str):
        return self.marcapDf[self.marcapDf["date"]==date]
    


