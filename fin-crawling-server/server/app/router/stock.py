from typing import List
from fastapi import APIRouter

from app.module.locator import Locator

from app.service.UserService import UserService
from app.service.StockService import StockService
from app.model.dto import StockMarketCapital


router = APIRouter(prefix="/stock")
userService: UserService = Locator.getInstance().get(UserService)
stockService: StockService = Locator.getInstance().get(StockService)


@router.get("/marcap")
async def getStockData(market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
    return stockService.getStockData(market, startDate, endDate)
