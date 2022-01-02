def getMonthFromReprtCode(reportCode: str) -> int:
    if reportCode == "11013":
        return 3
    elif reportCode == "11012":
        return 6
    elif reportCode == "11014":
        return 9
    elif reportCode == "11011":
        return 12
    return -1
