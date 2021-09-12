from __future__ import annotations
from typing import Any, Callable, List, Optional
from asyncio.events import AbstractEventLoop
import asyncio
from uvicorn.config import logger

from app.model.task import TaskPoolInfo

DEFAULT_POOL_SIZE = 8


class Task(object):
    def __init__(self, func: Callable, param: Any = {}) -> None:
        super().__init__()
        self.func = func
        self.param = param
        self.loop: Optional[AbstractEventLoop] = None

    async def run(self, taskPool: TaskPool, pool: Pool) -> None:
        print("run")
        if self.loop:
            self.param["taskPool"] = taskPool
            self.param["pool"] = pool
            await self.loop.create_task(self.func(**self.param))


class Pool(object):
    def __init__(self) -> None:
        super().__init__()
        self.isRun = False
    
    def setTask(self, task: Task) -> None:
        self.task = task
    
    def run(self, taskPool: TaskPool) -> None:
        self.isRun = True
        self.poolTask = asyncio.ensure_future(self.task.run(taskPool, self))
    
    def cancel(self) -> None:
        self.isRun = False
        if self.poolTask and not self.poolTask.cancelled():
            self.poolTask.cancel()
        

class TaskPool(object):
    def __init__(self, notifyCallback: Callable, poolSize: int = DEFAULT_POOL_SIZE) -> None:
        super().__init__()
        self.taskPool: List[Pool] = []
        self.poolSize = poolSize
        self.notifyCallback = notifyCallback
    
    def addTaskPool(self, pool: Pool, isNotify: bool = True) -> Pool:
        self.taskPool.append(pool)
        print(f"addTaskPool:{self.poolCount()}")
        return pool
    
    def removeTaskPool(self, pool: Pool, isNotify: bool = True) -> None:
        self.taskPool.remove(pool)
        if isNotify:
            self.updatePoolInfo()
    
    def poolCount(self) -> int:
        return len(self.taskPool)
    
    def runCount(self) -> int:
        return len(list(filter(lambda pool: pool.isRun, self.taskPool)))
    
    def updatePoolInfo(self) -> None:
        if self.notifyCallback:
            self.notifyCallback()


class TaskRunner(object):
    def __init__(self) -> None:
        super().__init__()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.loop = asyncio.get_running_loop()
        self.pool = TaskPool(notifyCallback=self.notifyRmOnPool)
        self.notifyCallback = None
        # self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    
    def getPoolInfo(self) -> TaskPoolInfo:
        return TaskPoolInfo(**{
                "poolSize": self.pool.poolSize,
                "poolCount": self.pool.poolCount(),
                "runCount": self.pool.runCount(),
                "queueCount": self.queue.qsize()
            })

    def updatePoolInfo(self) -> None:
        print(f"poolCount:{self.pool.poolCount()}, runCount:{self.pool.runCount()}, queueCount:{self.queue.qsize()}")
        logger.info(f"runCount:{self.pool.runCount()}, queueCount:{self.queue.qsize()}")
        if self.notifyCallback:
            self.notifyCallback(TaskPoolInfo(**{
                "poolSize": self.pool.poolSize,
                "poolCount": self.pool.poolCount(),
                "runCount": self.pool.runCount(),
                "queueCount": self.queue.qsize()
            }))
    
    def notifyPutOnQueue(self) -> None:
        self.loop.create_task(self.notifyToPool())
    
    def notifyRmOnPool(self) -> None:
        if self.queue.qsize() > 0:
            self.loop.create_task(self.notifyToPool())
        else:
            self.updatePoolInfo()
    
    async def notifyToPool(self) -> None:
        try:
            print(f"notifyToPool:{self.pool.poolCount()}")
            if self.queue.qsize() > 0 and (self.pool.poolSize - self.pool.poolCount()) > 0:
                pool = self.pool.addTaskPool(Pool(), False)
                task: Task = await asyncio.wait_for(self.queue.get(), timeout=1)
                if task:
                    pool.setTask(task)
                    pool.run(self.pool)
                else:
                    self.pool.removeTaskPool(pool, False)
            # if self.pool.poolSize > self.queue.qsize() and self.pool.poolCount() >= self.queue.qsize():
            #     print("exit")
            # elif self.pool.poolSize > self.pool.poolCount() and self.queue.qsize() > 0:
            #     pool = self.pool.addTaskPool(Pool(), False)
            #     print(f"before qsize:{self.queue.qsize()}")
            #     task: Task = await asyncio.wait_for(self.queue.get(), timeout=1)
            #     print(f"after qsize:{self.queue.qsize()}")
            #     if task:
            #         pool.setTask(task)
            #         pool.run(self.pool)
            #     else:
            #         self.pool.removeTaskPool(pool, False)
        except asyncio.TimeoutError as e:
            print(f"timeout:{str(e)}")
            self.pool.removeTaskPool(pool, False)
        finally:
            self.updatePoolInfo()

    def put(self, task: Task) -> None:
        task.loop = self.loop
        self.loop.create_task(self._put(task))

    async def _put(self, task: Task) -> None:
        await self.queue.put(task)
        self.notifyPutOnQueue()
        