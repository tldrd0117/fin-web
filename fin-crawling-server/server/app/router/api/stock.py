
from fastapi import APIRouter, WebSocket

from app.module.locator import Locator

from app.service.UserService import UserService
from app.service.StockService import StockService
from app.model.dto import StockMarketCapitalResponse

router = APIRouter(prefix="/stock")
userService: UserService = Locator.getInstance().get(UserService)
stockService: StockService = Locator.getInstance().get(StockService)


@router.get("/marcap")
async def getStockData(market: str, startDate: str, endDate: str) -> StockMarketCapitalResponse:
    li = stockService.getStockData(market, startDate, endDate)
    return StockMarketCapitalResponse(**{
        "list": li,
        "count": len(li)
    })