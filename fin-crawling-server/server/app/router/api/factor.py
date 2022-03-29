
from fastapi import APIRouter

from app.module.locator import Locator

from app.service.api.UserApiService import UserApiService
from app.service.api.FactorApiService import FactorApiService
from app.model.dto import FactorDataResponse

router = APIRouter(prefix="/factor")
userService: UserApiService = Locator.getInstance().get(UserApiService)
factorService: FactorApiService = Locator.getInstance().get(FactorApiService)


@router.get("/get")
async def getFactorData(code: str, year: str, month: str, source: str) -> FactorDataResponse:
    li = await factorService.getFactor(code, year, month, source)
    return FactorDataResponse(**{
        "list": li,
        "count": len(li)
    })
