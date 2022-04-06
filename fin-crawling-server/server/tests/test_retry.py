import asyncio
from app.util.AsyncUtil import asyncRetry, asyncRetryNonBlock


async def retried(data: str) -> None:
    print(data)
    raise Exception("er")


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    try:
        await asyncRetryNonBlock(3, 1, retried, "hello")
    except Exception as e:
        print("error!")
        raise e
        # print(e)


# pytest -s test_retry.py
def test() -> None:
    print("run test")
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
    except Exception as e:
        print(e)