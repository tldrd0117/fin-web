
from fastapi import APIRouter

from app.module.locator import Locator

from app.service.UserService import UserService
from app.service.FactorService import FactorService
from app.model.dto import FactorDataResponse

router = APIRouter(prefix="/factor")
userService: UserService = Locator.getInstance().get(UserService)
factorService: FactorService = Locator.getInstance().get(FactorService)


@router.get("/get")
async def getFactorData(code: str, year: str, month: str, source: str) -> FactorDataResponse:
    li = await factorService.getFactor(code, year, month, source)
    return FactorDataResponse(**{
        "list": li,
        "count": len(li)
    })
