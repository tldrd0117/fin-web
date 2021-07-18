
from typing import Dict, List
from app.datasource.StockMongoDataSource import StockMongoDataSource
import asyncio


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    mongod = StockMongoDataSource(host="localhost", port="8082")
    data = mongod.getAllTaskState("marcap")
    compDict: Dict = {}
    count: Dict = {}
    for one in data:
        for idx, taskDate in enumerate(one["tasks"]):
            if taskDate in compDict.keys():
                if compDict[taskDate]["ret"] == 1 or one["tasksRet"][idx] == 1:
                    compDict[taskDate] = {"date": taskDate, "ret": 1}
            else:
                year = taskDate[0:4]
                if year in count.keys():
                    count[year] = count[year] + 1
                else:
                    count[year] = 1
                compDict[taskDate] = {"date": taskDate, "ret": one["tasksRet"][idx]}
    collect: List = list(compDict.values())
    collect = sorted(collect, key=lambda x: x["date"])
    print(collect)
    print(count)
    # try:
    #     taskRepository.taskRunner.loop.run_forever()
    # except KeyboardInterrupt:
    #     taskRepository.taskRunner.loop.close()


# pytest -s test_stock_mongo_data_source.py
def test() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
