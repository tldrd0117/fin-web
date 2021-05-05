from .base.DTO import DTO
from datetime import datetime


class StockMarketCapitalDTO(DTO):
    # 종목코드,종목명,종가,대비,등락률,시가,고가,저가,거래량,거래대금,시가총액,상장주식수
    def setData(self, strData: str, date: str, market: str) -> None:
        data = strData.replace('"', '').split(",")
        self.date = date
        self.market = market
        self.code = data[0].strip()
        self.name = data[1].strip()
        self.close = data[2].strip()
        self.diff = data[3].strip()
        self.percent = data[4].strip()
        self.open = data[5].strip()
        self.high = data[6].strip()
        self.low = data[7].strip()
        self.volume = data[8].strip()
        self.price = data[9].strip()
        self.marcap = data[10].strip()
        self.number = data[11].strip()
        self.createdAt = datetime.today()
        self.updatedAt = ""
    
    def __str__(self) -> str:
        return str(self.__dict__)
    