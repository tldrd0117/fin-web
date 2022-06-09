import json
import luigi
from app.tasks.stockTasks import GetMarcapCodes, UpdateAdjustedStockTask
from app.utils.dateutils import getCurrentDate

# poetry run python -m pytest -s tests/test_adjustedMarcap.py

def getMarcapCodePath():
    markets = json.dumps(["kospi", "kosdaq"])
    task = GetMarcapCodes(markets=markets)
    luigi.build([task], workers=1, detailed_summary=True)
    path = task.output().path
    return path


def test_UpdateAdjustedStockTask():
    markets = json.dumps(["kospi"])
    startDate = "19700101"
    endDate = getCurrentDate()
    task = UpdateAdjustedStockTask(markets=markets, startDate=startDate, endDate=endDate, targetPath=getMarcapCodePath())
    luigi.build([task], workers=1, detailed_summary=True)
