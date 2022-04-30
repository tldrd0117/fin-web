from typing import List
from app.base.BaseComponent import BaseComponent
from app.model.dto import FactorData
from app.repo.FactorRepository import FactorRepository

class FactorApiService(BaseComponent):

    def onComponentResisted(self) -> None:
        self.factorRepository = self.get(FactorRepository)
        return super().onComponentResisted()

    async def getFactor(self, code: str, year: str, month: str, source: str) -> List[FactorData]:
        return await self.factorRepository.getFactor(code, year, month, source)
    
    async def getDividendFactor(self, dividendCode: str, startDate: str, endDate: str, code: str):
        return
    
    async def getStockNumFactor(self, reason: str, startDate: str, endDate: str, corpName: str, stockType: str):
        return