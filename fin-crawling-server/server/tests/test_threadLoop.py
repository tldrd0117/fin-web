from app.module.task import Pool, TaskPool
from app.repo.TasksRepository import TasksRepository, Task
from app.datasource.StockMongoDataSource import StockMongoDataSource
import asyncio
from concurrent.futures import ThreadPoolExecutor


def taskWorker2() -> None:
    print(f"taskWorker2")
    # await asyncio.sleep(1)

async def tasks(loop: asyncio.AbstractEventLoop):
    th = ThreadPoolExecutor(max_workers=8)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)
    await loop.run_in_executor(th, taskWorker2)


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    loop.run_in_executor(th, taskWorker2)
    loop.run_in_executor(th, taskWorker2)
    loop.run_in_executor(th, taskWorker2)
    loop.run_in_executor(th, taskWorker2)


# pytest -s test_threadLoop.py
def test() -> None:
    print("run test")
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()