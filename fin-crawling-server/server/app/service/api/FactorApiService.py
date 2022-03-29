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