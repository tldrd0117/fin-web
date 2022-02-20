
from fastapi import APIRouter
from app.tasks.my_module import TestTask, SubTask, GetFactorYearTask, GetStockMonthTask, GetMarcap, GetStockFilteredByFactor
import luigi
import json

router = APIRouter(prefix="/test")


@router.get("/hello")
async def hello() -> dict:
    return {"message": "Hello World"}


@router.get("/task")
async def getStockData() -> dict:
    # result = luigi.build([GetStockMonthTask(market="kospi", year="2021", month="1")], workers=2)
    # result = luigi.build([GetFactorYearTask(year="2008", name="재무활동")], workers=2)
    # result = luigi.build([GetMarcap(market="kospi", year="2021", month="1")], workers=2)
    market = json.dumps(["kospi"])
    result = luigi.build([GetStockFilteredByFactor(market=market, startDate="20171201", endDate="20180131", factor="재무활동", minValue=-float("inf"), maxValue=0.0)], workers=2)
    return result
