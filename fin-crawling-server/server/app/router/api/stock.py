
from fastapi import APIRouter

from app.module.locator import Locator

from app.service.api.UserApiService import UserApiService
from app.service.api.StockApiService import StockApiService
from app.model.dto import StockMarketCapitalResponse

router = APIRouter(prefix="/stock")
userService: UserApiService = Locator.getInstance().get(UserApiService)
stockService: StockApiService = Locator.getInstance().get(StockApiService)


@router.get("/marcap")
async def getStockData(market: str, startDate: str, endDate: str) -> StockMarketCapitalResponse:
    li = await stockService.getStockData(market, startDate, endDate)
    return StockMarketCapitalResponse(**{
        "list": li,
        "count": len(li)
    })