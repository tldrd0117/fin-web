from app.repo.TasksRepository import taskRepository, Task
import asyncio


async def taskWorker(data: str) -> None:
    print(f"taskWorker:{data}")
    await asyncio.sleep(1)
    print(f"taskWorker:{data} 1 seconds")


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    task1 = Task(taskWorker, "new1")
    task2 = Task(taskWorker, "new2")
    task3 = Task(taskWorker, "new3")
    task4 = Task(taskWorker, "new4")
    taskRepository.createTaskRunner(loop)
    taskRepository.runTask(task1)
    await asyncio.sleep(1)
    taskRepository.runTask(task2)
    await asyncio.sleep(1)
    taskRepository.runTask(task3)
    await asyncio.sleep(1)
    taskRepository.runTask(task4)
    
    # try:
    #     taskRepository.taskRunner.loop.run_forever()
    # except KeyboardInterrupt:
    #     taskRepository.taskRunner.loop.close()


# pytest -s test_task_repository.py
def test() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
