import asyncio
from typing import Any, Callable, Dict


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


async def asyncRetry(count: int, delay: int, asyncFunction: Callable, *args: tuple, **kwargs: Dict[str, Any]) -> Any:
    latestError = None
    for i in range(count):
        try:
            return await asyncFunction(*args, **kwargs)
        except Exception as e:
            latestError = e
            await asyncio.sleep(delay)
    if latestError is not None:
        raise latestError
    return None