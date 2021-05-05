from .base.DTO import DTO


class StockCrawlingRunCrawlingDTO(DTO):
    @staticmethod
    def create(driverAddr, market, startDateStr, endDateStr, taskId, taskUniqueId):
        dto = StockCrawlingRunCrawlingDTO()
        dto.driverAddr = driverAddr
        dto.market = market
        dto.startDateStr = startDateStr
        dto.endDateStr = endDateStr
        dto.taskId = taskId
        dto.taskUniqueId = taskUniqueId
        return dto
        