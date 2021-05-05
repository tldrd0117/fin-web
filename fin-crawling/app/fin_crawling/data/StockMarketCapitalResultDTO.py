from .StockMarketCapitalDTO import StockMarketCapitalDTO
from collections import deque
from pathlib import Path
from .base.DTO import DTO


class StockMarketCapitalResultDTO(DTO):
    def __init__(self) -> None:
        self.data: deque = deque()
        self.date: str = ""
        self.result: str = "fail"

    def readData(self, path: str, index: str) -> None:
        lines = []
        with open(path, "r", encoding="utf-8") as f:
            p = Path(f.name)
            self.date = p.stem
            lines = f.readlines()
        
        for i in range(1, len(lines)):
            marcap = StockMarketCapitalDTO()
            marcap.setData(lines[i], self.date, index)
            self.data.append(marcap.toDict())
        