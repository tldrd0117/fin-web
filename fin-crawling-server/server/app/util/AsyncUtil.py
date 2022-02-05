import asyncio
from typing import Any, Callable, Dict, List


def retry(count: int, gen: Callable, *args: tuple, **kwargs: Dict[str, Any]) -> Any:
    async def func(count: int) -> Any:
        latestError = None
        for i in range(count):
            try:
                return await gen(*args, **kwargs)
            except Exception as e:
                latestError = e
                print(e)
                pass
        if latestError is not None:
            print(latestError)
            raise latestError
    return asyncio.create_task(func(count))


async def sleepNonBlock(delay: float, loop: asyncio.AbstractEventLoop = None) -> Any:
    return asyncio.create_task(asyncio.sleep(delay, loop=loop))


async def asyncRetry(count: int, delay: int, asyncFunction: Callable, *args: tuple, **kwargs: Dict[str, Any]) -> Any:
    latestError = None
    for i in range(count):
        try:
            return await asyncFunction(*args, **kwargs)
        except asyncio.CancelledError as e:
            # 취소 시에는 바로 중단
            raise e
        except Exception as e:
            latestError = e
            await asyncio.sleep(delay)
    if latestError is not None:
        raise latestError
    return None


async def asyncRetryNonBlock(count: int, delay: int, asyncFunction: Callable, *args: tuple, **kwargs: Dict[str, Any]) -> Any:
    latestError = None
    for i in range(count):
        try:
            return await asyncio.create_task(asyncFunction(*args, **kwargs))
        except asyncio.CancelledError as e:
            # 취소 시에는 바로 중단
            raise e
        except Exception as e:
            latestError = e
            await asyncio.sleep(delay)
    if latestError is not None:
        raise latestError
    return None


def batch(iterable: Any, n: int = 1) -> Any:
    count = len(iterable)
    for ndx in range(0, count, n):
        yield iterable[ndx:min(ndx + n, count)]


async def batchFunction(batchCount: int, batchArray: List, asyncFunction: Callable, *args: tuple, **kwargs: Dict[str, Any]) -> Any:
    data = []
    for step in batch(batchArray, batchCount):
        data.extend(await asyncio.create_task(asyncFunction(step, *args, **kwargs)))
    return data