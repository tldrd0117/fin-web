from app.module.task import Pool, TaskPool
from app.repo.TasksRepository import TasksRepository, Task
from app.datasource.StockMongoDataSource import StockMongoDataSource
import asyncio


async def taskWorker(data: str, time: int, pool: Pool, taskPool: TaskPool) -> None:
    print(f"taskWorker:{data}")
    await asyncio.sleep(time)
    print(f"taskWorker:{data} {str(time)} seconds")
    taskPool.removeTaskPool(pool)


async def taskWorker2() -> None:
    print(f"taskWorker2")
    await asyncio.sleep(1)


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    mongod = StockMongoDataSource(host="localhost", port="8082")
    taskRepository = TasksRepository(mongod)
    # taskRepository.createTaskRunner()
    
    for index in range(10):
        task = Task(taskWorker, {"data": "new"+str(index), "time": 1})
        taskRepository.runTask(task)
    # try:
    #     taskRepository.taskRunner.loop.run_forever()
    # except KeyboardInterrupt:
    #     taskRepository.taskRunner.loop.close()


# pytest -s test_task_runner.py
def test() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()