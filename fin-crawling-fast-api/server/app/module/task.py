
from typing import Any, Callable, Optional
from asyncio.events import AbstractEventLoop
import asyncio
from uvicorn.config import logger


class Task(object):
    def __init__(self, func: Callable, param: Any = {}) -> None:
        super().__init__()
        self.func = func
        self.param = param
        self.loop: Optional[AbstractEventLoop] = None

    async def run(self) -> None:
        print("taskRun")
        # self.func(self.loop, self.param)
        if self.loop:
            self.loop.create_task(self.func(**self.param))


class TaskRunner(object):
    def __init__(self) -> None:
        super().__init__()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.loop = asyncio.get_running_loop()
        # self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    
    def run(self) -> None:
        print("run")
        self.loop.create_task(self._run())

    def put(self, task: Task) -> None:
        task.loop = self.loop
        self.loop.create_task(self._put(task))

    async def _run(self) -> None:
        while True:
            print("running")
            task: Task = await self.queue.get()
            self.loop.create_task(task.run())

    async def _put(self, task: Task) -> None:
        print("put")
        await self.queue.put(task)